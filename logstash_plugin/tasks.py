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
import requests
import platform
import tempfile

# Cloudify Imports
from utils import run
from cloudify import ctx
from cloudify import exceptions
from cloudify.decorators import operation
from constants import (
    ELATIC_CO_BASE_URL,
    DEFAULT_DEB_URL,
    DEFAULT_RPM_URL,
    INSTALLED_UBUNTU,
    INSTALLED_CENTOS
)


@operation
def configure(conf, **_):
    """ Configure Logstash """

    if 'template' in conf['type']:
        if not conf.get('path'):
            raise exceptions.NonRecoverableError(
                'logstash property conf.path '
                'cannot be empty if conf.type is "template".')
        static_config = generate_static_config(conf.get('path'))
    elif 'static' in conf['type']:
        if not conf.get('path') and not conf.get('inline'):
            raise exceptions.NonRecoverableError(
                'either logstash property conf.path '
                'or conf.inline are required when conf.type is "static".')
        static_config = conf.get('path')
    else:
        raise exceptions.NonRecoverableError(
            'logstash property conf.type '
            'can only be "template" or "static".')

    upload_static_config(static_config, conf.get('destination_path'))


def generate_static_config(template_conf):

    ctx.logger.info('Generating static conf from template')

    raise NotImplementedError


def upload_static_config(static_conf, conf_path):
    """ Upload the static config to the service. """

    ctx.logger.info('Copying config to {0}'.format(conf_path))

    try:
        downloaded_file = \
            ctx.download_resource(static_conf, tempfile.mktemp())
    except Exception as e:
        raise exceptions.NonRecoverableError(
            'conf.file was not found on manager. '
            'Error: {0}.'.format(str(e)))

    run('sudo cp {0} {1}'.format(downloaded_file, conf_path))


@operation
def start(command, **_):
    """starts logstash daemon"""

    ctx.logger.debug('Attempting to start log transport service.')

    output = run(command)

    if output.returncode != 0:
        raise exceptions.NonRecoverableError(
            'Unable to start log transport service: {0}'.format(output))


@operation
def stop(command, **_):
    """stops logstash daemon"""

    ctx.logger.debug('Attempting to stop log transport service.')

    output = run(command)

    if output.returncode != 0:
        raise exceptions.NonRecoverableError(
            'Unable to stop log transport service: {0}'.format(output))


@operation
def install(package_url, **_):
    """ Installs Logstash """

    ctx.logger.debug('Attempting to install log transport service.')

    _install(platform.dist(), package_url)


def _install(platform, url):
    """ installs logstash from package """

    package_file = tempfile.mktemp()

    if not url:
        if 'Ubuntu' in platform:
            url = ELATIC_CO_BASE_URL \
                + DEFAULT_DEB_URL
            if 'install' in run(INSTALLED_UBUNTU):
                ctx.logger.info('Logstash already installed.')
                return
            install_command = 'sudo dpkg -i {0}'.format(package_file)
        elif 'Centos' in platform:
            url = ELATIC_CO_BASE_URL \
                + DEFAULT_RPM_URL
            if 'not installed' not in run(INSTALLED_CENTOS):
                ctx.logger.info('Logstash already installed.')
                return
            install_command = 'sudo rpm -Uvh {0}'.format(package_file)
    else:
        raise exceptions.NonRecoverableError(
            'Only Centos and Ubuntu supported.')

    _download_package(package_file, url)

    run(install_command)


def _download_package(package_file, url):
    """ Downloads package from url to tempfile """

    ctx.logger.debug('Downloading: {0}'.format(url))
    package = requests.get(url, stream=True)

    with open(package_file, 'wb') as f:
        for chunk in package.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
