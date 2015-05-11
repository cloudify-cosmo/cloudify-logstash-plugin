########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

# Built in Imports
import os
import tempfile

# Third party Imports
from fabric.api import run, put

# Cloudify Imports
import utils
from cloudify import ctx
from cloudify import exceptions
from constants import (
    DEFAULT_LOGSTASH_CONFIG_DIRECTORY,
    DEFAULT_CONFIG_FILE_PATH,
    DEFAULT_PACKAGES
    )


def install(java_path='java', package_source=None, **_):
    """installs logstash

    This will check whether java is executable and then install logstash

    Properties:
    java_path - the path java can be found in.
    logstash_source - the url from which to download the logstash package file
    """

    if not utils.verify_is_executable(java_path + ' -version'):
        raise exceptions.NonRecoverableError(
            '{0} is not executable.'.format(java_path))

    ctx.logger.debug('Attempting to install Logstash.')

    pkg_url = package_source if package_source \
        else DEFAULT_PACKAGES[utils.get_package_type_for_distro()]

    pkg_file_name = pkg_url.split('/')[-1]
    pkg_ext = os.path.splitext(pkg_file_name)

    if pkg_ext in ('deb'):
        output = run('wget -q -O- {0} | dpkg --install - '.format(pkg_url))
    elif pkg_ext in ('rpm'):
        output = run('curl -sSL {0} | rpm -ivh - '.format(pkg_url))
    else:
        raise exceptions.NonRecoverableError(
            'Unsupported package_source. '
            'Only deb and rpm supported at this time.')

    if output and getattr(output, 'return_code') != 0:
        raise exceptions.NonRecoverableError(
            'Unable to install Logstash: {0}'.format(output))

    ctx.logger.info('Installed Logstash.')


def configure(config_source, **_):
    """ Copies the provided config file to the config path on the host."""

    mkdirs = \
        'if [ ! -d {0} ]; then mkdir -p {0}; fi'.format(
            DEFAULT_LOGSTASH_CONFIG_DIRECTORY)

    downloaded_file = utils.download_resource(config_source, tempfile.mktemp())
    output = run(mkdirs)

    if getattr(output, 'return_code') != 0:
        raise exceptions.NonRecoverableError(
            'Unable to copy configuration to server" {0}'.format(output))

    ctx.logger.debug('Copying config to {0}'.format(DEFAULT_CONFIG_FILE_PATH))
    put(downloaded_file, DEFAULT_CONFIG_FILE_PATH)


def start(**_):
    """starts logstash daemon"""
    ctx.logger.debug('Attempting to start Logstash.')
    output = run('sudo service logstash start')
    if getattr(output, 'return_code') != 0:
        raise exceptions.NonRecoverableError(
            'Unable to start Logstash: {0}'.format(output))


def stop(**_):
    """stops logstash daemon"""
    ctx.logger.debug('Attempting to stop Logstash.')
    output = run('sudo service logstash stop')
    if getattr(output, 'return_code') != 0:
        raise exceptions.NonRecoverableError(
            'Unable to stop Logstash: {0}'.format(output))
