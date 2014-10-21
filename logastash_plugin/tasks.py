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
import requests
import tarfile
import subprocess

from cloudify import ctx
from cloudify.decorators import operation
from cloudify import exceptions

DEFAULT_PATH = os.path.expanduser('~/logstash')
DEFAULT_CONFIG_DESTINATION_PATH = os.path.join(DEFAULT_PATH, 'logstash.conf')
DEFAULT_TAR_DESTINATION_PATH = os.path.join(DEFAULT_PATH, 'logstash.tar.gz')
DEFAULT_LOGSTASH_URL = 'https://download.elasticsearch.org/logstash/logstash/logstash-1.4.2.tar.gz'  # NOQA


@operation
def install(logstash_config, **kwargs):
    _check_java_exists(logstash_config)
    if logstash_config.get('tar_url'):
        _tar = DEFAULT_TAR_DESTINATION_PATH
        _download_file(logstash_config['tar_url'], _tar)
        _untar(_tar, logstash_config.get('logstash_path', DEFAULT_PATH))


@operation
def configure(logstash_config, **kwargs):
    conf_src = logstash_config.get('conf_source')
    if not conf_src:
        raise exceptions.NonRecoverableError(
            'logstash config file not supplied.')

    # TODO: make this configurable
    conf_dst = logstash_config.get(
        'conf_destination', DEFAULT_CONFIG_DESTINATION_PATH)
    _mkdir(conf_dst)
    ctx.download_resource(conf_src, conf_dst)


@operation
def start(logstash_config, **kwargs):
    logstash_path = logstash_config.get('logstash_path', DEFAULT_PATH)
    conf_dst = logstash_config.get(
        'conf_destination', DEFAULT_CONFIG_DESTINATION_PATH)
    # TODO: find a way to run using provided java path
    logstash_binary = os.path.join(logstash_path, 'bin/logstash')
    cmd = logstash_binary + ' -f ' + conf_dst
    _run(cmd)


def _untar(source, destination):
    if not tarfile.is_tarfile(source):
        raise exceptions.NonRecoverableError(
            '{0} is not a tar file.'.format(source))
    # with tarfile.open(source, 'r:gz') as tar:
    #     tar.extractall(destination)

    # after this logstash now available at ~/logstash/bin/logstash
    _run('tar -xzvf {0} -C {1} --strip-components=1'.format(
        source, destination))


def _run(ctx, cmd):
    """executes a command

    :param string cmd: command to execute
    """
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    ctx.logger.debug('stdout: {0}'.format(stdout))
    ctx.logger.debug('stderr: {0}'.format(stderr))
    p.stdout = stdout
    p.strerr = stderr
    return p


def _mkdir(path):
    if not os.path.isdir(os.path.dirname(path)):
        ctx.logger.debug('creating directory: {0}'.format(path))
        try:
            os.makedirs(os.path.dirname(path))
        except Exception as ex:
            raise exceptions.NonRecoverableError(
                'failed to create directory: {0}. ({1})'.format(
                    path, ex.message))
    else:
        ctx.logger.debug('directory already exists: {0}'.format(path))


def _check_java_exists(logstash_config):
    ctx.logger.debug('checking to see if java exists.')
    java_path = logstash_config.get('java_path', 'java')
    java_nexists = os.system('{0} -version'.format(java_path))
    if java_nexists:
        raise exceptions.NonRecoverableError('{0} is not executable'.format(
            java_path))


def _download_file(url, destination):
    ctx.logger.debug('downloading {0} to {1}...'.format(url, destination))
    destination = destination if destination else url.split('/')[-1]
    r = requests.get(url, stream=True)
    if not r.status_code == 200:
        raise exceptions.NonRecoverableError(
            'failed to download file: {0}'.format(url))
    with open(destination, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
