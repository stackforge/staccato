"""
SQLAlchemy models for staccato data
"""

import uuid

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import PickleType
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base

from staccato.openstack.common import timeutils


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

    id = Column(String(36), primary_key=True,
                default=lambda: str(uuid.uuid4()))
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
    source_opts = Column(PickleType())
    dest_opts = Column(PickleType())
    executor_uuid = Column(String(512), nullable=True)


def register_models(engine):
    models = (XferRequest,)
    for model in models:
        model.metadata.create_all(engine)
