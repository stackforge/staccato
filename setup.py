#!/usr/bin/python
# Copyright (c) 2010 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

from staccato.openstack.common import setup

requires = setup.parse_requirements()
depend_links = setup.parse_dependency_links()
project = 'staccato'

setuptools.setup(
    name=project,
    version='0.1',
    description='The Staccato project provides data transfer services '
                'to OpenStack services and users.  It is primarily used '
                'for VM image propagation.',
    license='Apache License (2.0)',
    author='OpenStack',
    author_email='openstack@lists.launchpad.net',
    url='http://staccato.openstack.org/',
    packages=setuptools.find_packages(exclude=['']),
    test_suite='nose.collector',
    cmdclass=setup.get_cmdclass(),
    include_package_data=True,
    install_requires=requires,
    dependency_links=depend_links,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: OpenStack',
    ],
    entry_points={'console_scripts':
                  ['staccato-api=staccato.cmd.api:main',
                  ]},
    py_modules=[])
