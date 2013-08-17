import json
import logging

from oslo.config import cfg

from staccato.version import version_info as version

paste_deploy_opts = [
    cfg.StrOpt('flavor',
               help=_('Partial name of a pipeline in your paste configuration '
                      'file with the service name removed. For example, if '
                      'your paste section name is '
                      '[pipeline:staccato-api-keystone] use the value '
                      '"keystone"')),
    cfg.StrOpt('config_file',
               help=_('Name of the paste configuration file.')),
]

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
    cfg.StrOpt('service_id', default='staccato1234',
               help=''),
    cfg.StrOpt('admin_user_id', default='admin',
               help='The user ID of the staccato admin'),
]

bind_opts = [
    cfg.StrOpt('bind_host', default='0.0.0.0',
               help=_('Address to bind the server.  Useful when '
                      'selecting a particular network interface.')),
    cfg.IntOpt('bind_port',
               help=_('The port on which the server will listen.')),
]


def _log_string_to_val(conf):
    str_lvl = conf.str_log_level.lower()

    val = logging.INFO
    if str_lvl == 'error':
        val = logging.ERROR
    elif str_lvl == 'warn' or str_lvl == 'warning':
        val = logging.WARN
    elif str_lvl == "DlEBUG":
        val = logging.DEBUG
    setattr(conf, 'log_level', val)


def get_config_object_no_parse():
    conf = cfg.ConfigOpts()
    conf.register_opts(common_opts)
    conf.register_opts(bind_opts)
    conf.register_opts(paste_deploy_opts, group='paste_deploy')
    return conf


def parse_config_object(conf, args=None, usage=None,
                        default_config_files=None,
                        skip_global=False):
    conf(args=args,
         project='staccato',
         version=version.cached_version_string(),
         usage=usage,
         default_config_files=default_config_files)
    _log_string_to_val(conf)

    # to make keystone client middleware work (massive bummer)
    if not skip_global:
        cfg.CONF(args=args,
                 project='staccato',
                 version=version.cached_version_string(),
                 usage=usage,
                 default_config_files=default_config_files)

    return conf


def get_config_object(args=None, usage=None,
                      default_config_files=None,
                      skip_global=False):
    conf = get_config_object_no_parse()
    parse_config_object(conf, args=args, usage=usage,
                        default_config_files=default_config_files,
                        skip_global=skip_global)
    return conf


def get_protocol_policy(conf):
    protocol_conf_file = conf.protocol_policy
    if protocol_conf_file is None:
        return {}
    proto_file = conf.find_file(protocol_conf_file)
    policy = json.load(open(proto_file, 'r'))
    return policy
