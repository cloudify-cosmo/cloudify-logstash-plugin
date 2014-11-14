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
DEFAULT_LOGSTASH_URL = 'https://download.elasticsearch.org/logstash/logstash/logstash-1.4.2.tar.gz'  # NOQA


@operation
def install(logstash_config, **kwargs):
    """installs logstash

    This will check whether java is executable and then install logstash

    Properties:
    java_path - the path java can be found in.
    logstash_url - the url from which to download the logstash package file
    """
    utils.check_java_exists(logstash_config.get('java_path', 'java'))
    pkg_url = logstash_config.get('logstash_url', DEFAULT_LOGSTASH_URL)
    pkg_file_name = pkg_url.split('/')[-1]
    pkg_file_path = os.path.join(DEFAULT_PATH, pkg_file_name)
    pkg_ext = os.path.splitext(pkg_file_name)
    utils.download_file(pkg_url, pkg_file_path)
    if pkg_ext == 'tar.gz':
        _install_from_tar(logstash_config)
    elif pkg_ext in ('rpm', 'deb'):
        _install_from_package(pkg_file_path)


def _install_from_tar():
    # tar_url = logstash_config.get('logstash_url', DEFAULT_LOGSTASH_URL)
    # tar_path = DEFAULT_TAR_DESTINATION_PATH
    # destination = tar if tar else url.split('/')[-1]
    # utils.untar(tar_path, logstash_config.get('logstash_path', DEFAULT_PATH))
    raise NotImplementedError()


def _install_from_package(path):
    utils.install_package(path)


@operation
def configure(logstash_config, **kwargs):
    conf_src = logstash_config.get('conf_source')
    if not conf_src:
        raise exceptions.NonRecoverableError(
            'logstash config file not supplied.')

    # TODO: make this configurable
    conf_dst = logstash_config.get(
        'conf_destination', DEFAULT_CONFIG_DESTINATION_PATH)
    utils.mkdir(conf_dst)
    ctx.download_resource(conf_src, conf_dst)


@operation
def start(logstash_config, **kwargs):
    logstash_path = logstash_config.get('logstash_path', DEFAULT_PATH)
    conf_dst = logstash_config.get(
        'conf_destination', DEFAULT_CONFIG_DESTINATION_PATH)
    if logstash_config('java_path'):
        os.environ['JAVA_HOME'] = logstash_config['java_path']
    logstash_binary = os.path.join(logstash_path, 'bin/logstash')
    cmd = 'nohup ' + logstash_binary + ' -f ' + conf_dst
    utils._run(cmd)
