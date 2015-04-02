########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
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


import os

import utils
from cloudify import ctx
from cloudify.decorators import operation
from jingen import Jingen
from cloudify import exceptions


DEFAULT_PATH = os.path.expanduser('~/logstash')
DEFAULT_CONFIG_DESTINATION_PATH = os.path.join(DEFAULT_PATH, 'logstash.conf')
DEFAULT_TAR_DESTINATION_PATH = os.path.join(DEFAULT_PATH, 'logstash.tar.gz')
DEFAULT_PACKAGES = {
    'tar': 'https://download.elasticsearch.org/logstash/logstash/logstash-1.4.2.tar.gz',  # NOQA
    'rpm': 'https://download.elasticsearch.org/logstash/logstash/packages/centos/logstash-1.4.2-1_2c0f5a1.noarch.rpm',  # NOQA
    'deb': 'https://download.elasticsearch.org/logstash/logstash/packages/debian/logstash_1.4.2-1-2c0f5a1_all.deb',  # NOQA
}


@operation
def install(java_path='java', package_source=None, **_):
    """installs logstash

    This will check whether java is executable and then install logstash

    Properties:
    java_path - the path java can be found in.
    logstash_source - the url from which to download the logstash package file
    """
    def install_from_tar():
        """installs logstash from a tar.gz file"""
        raise NotImplementedError()

    def install_from_package(path):
        """installs logstash from a deb/rpm package"""
        utils.install_package(path)

    if not utils.verify_is_executable(java_path + ' -version'):
        # a better exception message.
        raise exceptions.NonRecoverableError('{0} is not executable.'.format(
            java_path))
    pkg_url = package_source if package_source \
        else DEFAULT_PACKAGES[utils.get_package_type_for_distro()]
    # pkg_url = https://logstash-1.4.2-1_2c0f5a1.noarch.rpm
    pkg_file_name = pkg_url.split('/')[-1]
    # pkg_file_name = logstash-1.4.2-1_2c0f5a1.noarch.rpm
    # consider using mkdtemp
    pkg_file_path = os.path.join('/tmp', pkg_file_name)
    # pkg_file_path = /tmp/logstash-1.4.2-1_2c0f5a1.noarch.rpm
    pkg_ext = os.path.splitext(pkg_file_name)
    # pkg_ext = rpm
    pkg_destination = utils.download_resource(pkg_url, pkg_file_path)
    if pkg_ext in ('rpm', 'deb'):
        install_from_package(pkg_destination, pkg_ext)
        ctx.instance.runtime_properties['from_package'] = True
    elif pkg_ext == 'tar.gz':
        install_from_tar()
        ctx.instance.runtime_properties['from_package'] = False
    os.remove(pkg_destination)


def apply_rabbit_broker(file_path):
    vars = {"MGMT_IP": ctx.get_management_ip()}
    jingen = Jingen(
        template_file=file_path,
        vars_source=vars,
        output_file=file_path,
        template_dir=os.path.dirname(file_path),
        make_file=True)
    try:
        jingen.generate()
    except:
        ctx.logger.debug(
            'Template could not be generated. Assuming no template.')


@operation
def configure(config_source,
              config_destination=DEFAULT_CONFIG_DESTINATION_PATH, **_):
    """Configures logstash by retrieving its config file and injecting
    the Manager's IP to logstash.conf.
    """
    if ctx.instance.runtime_properties['from_package']:
        config_destination = '/logstash/conf.d/logstash.conf'
        ctx.logger.debug('Since we are installing using a package, the '
                         'default configuration path will be used: {0}'.format(
                             config_destination))
    else:
        utils.mkdir(os.path.dirname(config_destination))
    config_path = utils.download_resource(config_source, config_destination)
    apply_rabbit_broker(config_path)


@operation
def start(**_):
    """starts the process"""
    utils.sudo('service logstash start')
    # logstash_path = logstash_config.get('logstash_path', DEFAULT_PATH)
    # conf_dst = logstash_config.get(
    #     'conf_destination', DEFAULT_CONFIG_DESTINATION_PATH)
    # if logstash_config('java_path'):
    #     os.environ['JAVA_HOME'] = logstash_config['java_path']
    # logstash_binary = os.path.join(logstash_path, 'bin/logstash')
    # cmd = 'nohup ' + logstash_binary + ' -f ' + conf_dst
    # utils._run(cmd)


@operation
def stop(**kwargs):
    """stops the process"""
    utils.sudo('service logstash stop')
