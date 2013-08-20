"""
Staccato Management Utility
"""
import sys

from oslo.config import cfg

from staccato.common import config
import staccato.db
import staccato.db.migration


def do_db_version(conf):
    """Print database's current migration level"""
    print staccato.db.migration.db_version(conf)


def do_upgrade(conf):
    staccato.db.migration.upgrade(conf, conf.command.version)


def do_downgrade(conf):
    staccato.db.migration.downgrade(conf, conf.command.version)


def do_version_control(conf):
    staccato.db.migration.version_control(conf, conf.command.version)


def do_db_sync(conf):
    staccato.db.migration.db_sync(conf,
                                  conf.command.version,
                                  conf.command.current_version)


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

command_opt = cfg.SubCommandOpt('command',
                                title='Commands',
                                help='Available commands',
                                handler=add_command_parsers)

cfg.CONF.register_cli_opt(command_opt)


def main():
    conf = config.get_config_object_no_parse()
    conf.register_cli_opt(command_opt)
    conf = config.parse_config_object(conf, skip_global=False)

    conf.command.func(conf)


if __name__ == '__main__':
    main()
