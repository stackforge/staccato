import os

from migrate.versioning import api as versioning_api
try:
    from migrate.versioning import exceptions as versioning_exceptions
except ImportError:
    from migrate import exceptions as versioning_exceptions
from migrate.versioning import repository as versioning_repository

from staccato.common import exceptions
import staccato.openstack.common.log as logging

LOG = logging.getLogger(__name__)


def db_version(CONF):
    """
    Return the database's current migration number

    :retval version number
    """
    repo_path = get_migrate_repo_path()
    sql_connection = CONF.sql_connection
    try:
        return versioning_api.db_version(sql_connection, repo_path)
    except versioning_exceptions.DatabaseNotControlledError, e:
        msg = (_("database '%(sql_connection)s' is not under "
                 "migration control") % locals())
        raise exceptions.StaccatoDataBaseException(msg)


def upgrade(CONF, version=None):
    """
    Upgrade the database's current migration level

    :param version: version to upgrade (defaults to latest)
    :retval version number
    """
    db_version(CONF)  # Ensure db is under migration control
    repo_path = get_migrate_repo_path()
    sql_connection = CONF.sql_connection
    version_str = version or 'latest'
    LOG.info(_("Upgrading %(sql_connection)s to version %(version_str)s") %
             locals())
    return versioning_api.upgrade(sql_connection, repo_path, version)


def downgrade(CONF, version):
    """
    Downgrade the database's current migration level

    :param version: version to downgrade to
    :retval version number
    """
    db_version()  # Ensure db is under migration control
    repo_path = get_migrate_repo_path()
    sql_connection = CONF.sql_connection
    LOG.info(_("Downgrading %(sql_connection)s to version %(version)s") %
             locals())
    return versioning_api.downgrade(sql_connection, repo_path, version)


def version_control(CONF, version=None):
    """
    Place a database under migration control
    """
    sql_connection = CONF.sql_connection
    try:
        _version_control(CONF, version)
    except versioning_exceptions.DatabaseAlreadyControlledError, e:
        msg = (_("database '%(sql_connection)s' is already under migration "
               "control") % locals())
        raise exceptions.StaccatoDataBaseException(msg)


def _version_control(CONF, version):
    """
    Place a database under migration control

    This will only set the specific version of a database, it won't
    run any migrations.
    """
    repo_path = get_migrate_repo_path()
    sql_connection = CONF.sql_connection
    if version is None:
        version = versioning_repository.Repository(repo_path).latest
    return versioning_api.version_control(sql_connection, repo_path, version)


def db_sync(CONF, version=None, current_version=None):
    """
    Place a database under migration control and perform an upgrade

    :retval version number
    """
    sql_connection = CONF.sql_connection
    try:
        _version_control(CONF, current_version or 0)
    except versioning_exceptions.DatabaseAlreadyControlledError, e:
        pass

    if current_version is None:
        current_version = int(db_version(CONF))
    if version is not None and int(version) < current_version:
        downgrade(CONF, version=version)
    elif version is None or int(version) > current_version:
        upgrade(CONF, version=version)


def get_migrate_repo_path():
    """Get the path for the migrate repository."""
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        'migrate_repo')
    if not os.path.exists(path):
        raise exceptions.StaccatoMisconfigurationException(
            "The path % should exist." % path)
    return path
