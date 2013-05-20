"""
SQLAlchemy models for staccato data
"""

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base

from staccato.openstack.common import timeutils
from staccato.openstack.common import uuidutils


BASE = declarative_base()


class ModelBase(object):
    """Base class for Nova and Glance Models"""
    __table_args__ = {'mysql_engine': 'InnoDB'}
    __table_initialized__ = False
    __protected_attributes__ = set([
        "created_at", "updated_at"])

    created_at = Column(DateTime, default=timeutils.utcnow,
                        nullable=False)
    updated_at = Column(DateTime, default=timeutils.utcnow,
                        nullable=False, onupdate=timeutils.utcnow)


class XferRequest(BASE, ModelBase):
    __tablename__ = 'xfer_requests'

    id = Column(String(36), primary_key=True, default=uuidutils.generate_uuid)
    srcurl = Column(String(2048), nullable=False)
    dsturl = Column(String(2048), nullable=False)
    owner = Column(String(128), nullable=False)
    src_module_name = Column(String(512), nullable=False)
    dst_module_name = Column(String(512), nullable=False)
    state = Column(Integer(), nullable=False)
    start_ndx = Column(Integer(), nullable=False, default=0)
    next_ndx = Column(Integer(), nullable=False)
    end_ndx = Column(Integer(), nullable=False, default=-1)
    # TODO add protocol specific json documents
    write_info = Column(String(512))
    read_info = Column(String(512))


def register_models(engine):
    models = (XferRequest,)
    for model in models:
        model.metadata.create_all(engine)
