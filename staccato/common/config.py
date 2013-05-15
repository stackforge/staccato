import logging
from oslo.config import cfg
import json

from staccato.version import version_info as version

common_opts = [
    cfg.ListOpt('protocol_plugins',
                default=['staccato.protocols.file.FileProtocol',
                         ]),
    cfg.StrOpt('sql_connection',
               default='sqlite:///staccato.sqlite',
               secret=True,
               metavar='CONNECTION',
               help='A valid SQLAlchemy connection string for the registry '
               'database.  Default: %(default)s'),
    cfg.IntOpt('sql_idle_timeout', default=3600,
               help=_('Period in seconds after which SQLAlchemy should '
                      'reestablish its connection to the database.')),
    cfg.IntOpt('sql_max_retries', default=60,
               help=_('The number of times to retry a connection to the SQL'
                      'server.')),
    cfg.IntOpt('sql_retry_interval', default=1,
               help=_('The amount of time to wait (in seconds) before '
                      'attempting to retry the SQL connection.')),
    cfg.BoolOpt('db_auto_create', default=False,
                help=_('A boolean that determines if the database will be '
                       'automatically created.')),
    cfg.BoolOpt('db_auto_create', default=False,
                help=_('A boolean that determines if the database will be '
                       'automatically created.')),

    cfg.StrOpt('log_level',
               default='INFO',
               help='',
               dest='str_log_level'),
    cfg.StrOpt('protocol_policy', default='staccato-protocols.json',
               help=''),
]


def _log_string_to_val(conf):
    str_lvl = conf.str_log_level.lower()

    val = logging.INFO
    if str_lvl == 'error':
        val = logging.ERROR
    elif str_lvl == 'warn' or str_lvl == 'warning':
        val = logging.WARN
    elif str_lvl == "DEBUG":
        val = logging.DEBUG
    setattr(conf, 'log_level', val)


def get_config_object(args=None, usage=None, default_config_files=None):
    conf = cfg.ConfigOpts()
    conf.register_opts(common_opts)
    conf(args=args,
         project='staccato',
         version=version.cached_version_string(),
         usage=usage,
         default_config_files=default_config_files)
    _log_string_to_val(conf)

    return conf


def get_protocol_policy(conf):
    protocol_conf_file = conf.protocol_policy
    if protocol_conf_file is None:
        # TODO log a warning
        return {}
    policy = json.load(open(protocol_conf_file, 'r'))
    return policy
