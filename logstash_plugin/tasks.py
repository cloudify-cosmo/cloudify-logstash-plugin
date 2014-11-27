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
import exceptions

from cloudify import ctx
from cloudify.decorators import operation
import utils
# from cloudify import exceptions

DEFAULT_PATH = os.path.expanduser('~/logstash')
DEFAULT_CONFIG_DESTINATION_PATH = os.path.join(DEFAULT_PATH, 'logstash.conf')
DEFAULT_TAR_DESTINATION_PATH = os.path.join(DEFAULT_PATH, 'logstash.tar.gz')
DEFAULT_PACKAGES = {
    'tar': 'https://download.elasticsearch.org/logstash/logstash/logstash-1.4.2.tar.gz',  # NOQA
    'rpm': 'https://download.elasticsearch.org/logstash/logstash/packages/centos/logstash-1.4.2-1_2c0f5a1.noarch.rpm',  # NOQA
    'deb': 'https://download.elasticsearch.org/logstash/logstash/packages/debian/logstash_1.4.2-1-2c0f5a1_all.deb',  # NOQA
}


@operation
def install(logstash_config, **kwargs):
    """installs logstash

    This will check whether java is executable and then install logstash

    Properties:
    java_path - the path java can be found in.
    logstash_url - the url from which to download the logstash package file
    """
    utils.verify_is_executable(
        logstash_config.get('java_path', 'java') + ' -version')
    pkg_url = logstash_config.get(
        'logstash_url', DEFAULT_PACKAGES[utils.get_package_type_for_distro()])
    pkg_file_name = pkg_url.split('/')[-1]
    pkg_file_path = os.path.join(DEFAULT_PATH, pkg_file_name)
    pkg_ext = os.path.splitext(pkg_file_name)
    utils.download_file(pkg_url, pkg_file_path)
    if pkg_ext in ('rpm', 'deb'):
        _install_from_package(pkg_file_path)
    elif pkg_ext == 'tar.gz':
        _install_from_tar(pkg_file_path, logstash_config)
    os.remove(pkg_file_path)


def _install_from_tar(path, logstash_config):
    """installs logstash from a tar.gz file"""
    # utils.untar(path, logstash_config.get('logstash_path', DEFAULT_PATH))
    raise NotImplementedError()


def _install_from_package(path):
    """installs logstash from a deb/rpm package"""
    utils.install_package(path)


@operation
def configure(logstash_config, **kwargs):
    """configures logstash by retrieving its config file"""
    conf_src = logstash_config.get('config_source')
    if not conf_src:
        raise exceptions.NonRecoverableError(
            'logstash config file not supplied.')

    conf_dst = logstash_config.get(
        'config_destination', DEFAULT_CONFIG_DESTINATION_PATH)
    utils.mkdir(conf_dst)
    ctx.download_resource(conf_src, conf_dst)


@operation
def start(logstash_config, **kwargs):
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
