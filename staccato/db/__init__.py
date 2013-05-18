import logging
import time

import sqlalchemy
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql.expression as sql_expression

from staccato.db import migration, models
import staccato.openstack.common.log as os_logging
from staccato.common import exceptions
from staccato.db import models
import staccato.xfer.constants as constants


LOG = os_logging.getLogger(__name__)


class StaccatoDB(object):

    def __init__(self, CONF, autocommit=True, expire_on_commit=False):
        self.CONF = CONF
        self.engine = _get_db_object(CONF)
        self.maker = sa_orm.sessionmaker(bind=self.engine,
                                         autocommit=autocommit,
                                         expire_on_commit=expire_on_commit)

    def get_sessions(self):
        return self.maker()

    def get_new_xfer(self,
                     srcurl,
                     dsturl,
                     src_module_name,
                     dst_module_name,
                     start_ndx=0,
                     end_ndx=-1,
                     read_info=None,
                     write_info=None,
                     session=None):

        if session is None:
            session = self.get_sessions()

        with session.begin():
            xfer_request = models.XferRequest()
            xfer_request.srcurl = srcurl
            xfer_request.dsturl = dsturl
            xfer_request.src_module_name = src_module_name
            xfer_request.dst_module_name = dst_module_name
            xfer_request.start_ndx = start_ndx
            xfer_request.next_ndx = start_ndx
            xfer_request.end_ndx = end_ndx
            xfer_request.state = "STATE_NEW"

            session.add(xfer_request)
            session.flush()

        return xfer_request

    def save_db_obj(self, db_obj, session=None):
        if session is None:
            session = self.get_sessions()

        with session.begin():
            session.add(db_obj)
            session.flush()

    def lookup_xfer_request_by_id(self, xfer_id, session=None):
        if session is None:
            session = self.get_sessions()

        with session.begin():
            query = session.query(models.XferRequest)\
                       .filter(models.XferRequest.id == xfer_id)
            xfer_request = query.one()

        return xfer_request

    def get_all_ready(self, limit=None, session=None):
        if session is None:
            session = self.get_sessions()

        with session.begin():
            query = session.query(models.XferRequest)\
                       .filter(
                sql_expression.or_(models.XferRequest.state == constants.State.STATE_NEW,
                                   models.XferRequest.state == constants.State.STATE_ERROR))
            if limit is not None:
                query = query.limit(limit)
            xfer_requests = query.all()
        return xfer_requests

    def delete_db_obj(self, db_obj, session=None):
        if session is None:
            session = self.get_sessions()

        with session.begin():
            session.delete(db_obj)
            session.flush()


def _get_db_object(CONF):
    sqlalchemy.engine.url.make_url(CONF.sql_connection)
    engine_args = {
        'pool_recycle': CONF.sql_idle_timeout,
        'echo': False,
        'convert_unicode': True}

    try:
        engine = sqlalchemy.create_engine(CONF.sql_connection, **engine_args)
        engine.connect = wrap_db_error(engine.connect, CONF)
        engine.connect()
    except Exception, err:
        msg = _("Error configuring registry database with supplied "
                "sql_connection '%s'. "
                "Got error:\n%s") % (CONF.sql_connection, err)
        LOG.error(msg)
        raise

    if CONF.db_auto_create:
        LOG.info(_('auto-creating staccato registry DB'))
        models.register_models(engine)
        try:
            migration.version_control(CONF)
        except exceptions.StaccatoDataBaseException:
            # only arises when the DB exists and is under version control
            pass
    else:
        LOG.info(_('not auto-creating staccato registry DB'))

    return engine


def is_db_connection_error(args):
    """Return True if error in connecting to db."""
    # NOTE(adam_g): This is currently MySQL specific and needs to be extended
    #               to support Postgres and others.
    conn_err_codes = ('2002', '2003', '2006')
    for err_code in conn_err_codes:
        if args.find(err_code) != -1:
            return True
    return False


def wrap_db_error(f, CONF):
    """Retry DB connection. Copied from nova and modified."""
    def _wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except sqlalchemy.exc.OperationalError, e:
            if not is_db_connection_error(e.args[0]):
                raise

            remaining_attempts = CONF.sql_max_retries
            while True:
                LOG.warning(_('SQL connection failed. %d attempts left.'),
                            remaining_attempts)
                remaining_attempts -= 1
                time.sleep(CONF.sql_retry_interval)
                try:
                    return f(*args, **kwargs)
                except sqlalchemy.exc.OperationalError, e:
                    if (remaining_attempts == 0 or
                        not is_db_connection_error(e.args[0])):
                        raise
                except sqlalchemy.exc.DBAPIError:
                    raise
        except sqlalchemy.exc.DBAPIError:
            raise
    _wrap.func_name = f.func_name
    return _wrap
