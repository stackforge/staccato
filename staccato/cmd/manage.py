"""
Staccato Management Utility
"""
import sys

from oslo.config import cfg

from staccato.common import config
import staccato.db
import staccato.db.migration

CONF = cfg.CONF


def do_db_version():
    """Print database's current migration level"""
    print staccato.db.migration.db_version(CONF)


def do_upgrade():
    staccato.db.migration.upgrade(CONF, CONF.command.version)


def do_downgrade():
    staccato.db.migration.downgrade(CONF, CONF.command.version)


def do_version_control():
    staccato.db.migration.version_control(CONF, CONF.command.version)


def do_db_sync():
    staccato.db.migration.db_sync(CONF,
                                  CONF.command.version,
                                  CONF.command.current_version)


def add_command_parsers(subparsers):
    parser = subparsers.add_parser('db_version')
    parser.set_defaults(func=do_db_version)

    parser = subparsers.add_parser('upgrade')
    parser.set_defaults(func=do_upgrade)
    parser.add_argument('version', nargs='?')

    parser = subparsers.add_parser('downgrade')
    parser.set_defaults(func=do_downgrade)
    parser.add_argument('version')

    parser = subparsers.add_parser('version_control')
    parser.set_defaults(func=do_version_control)
    parser.add_argument('version', nargs='?')

    parser = subparsers.add_parser('db_sync')
    parser.set_defaults(func=do_db_sync)
    parser.add_argument('version', nargs='?')
    parser.add_argument('current_version', nargs='?')


def main():
    conf = config.get_config_object_no_parse()

    command_opt = cfg.SubCommandOpt('command',
                                    title='Commands',
                                    help='Available commands',
                                    handler=add_command_parsers)
    conf.register_cli_opt(command_opt)
    config.parse_config_object(conf, args=sys.argv[1:], skip_global=True)

if __name__ == '__main__':
    main()
