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
import subprocess

# Cloudify Imports
from cloudify import ctx
from cloudify.decorators import operation
from cloudify import exceptions
from constants import (
    WHICH_YUM,
    WHICH_APT,
    YUM_RPM_URL,
    YUM_REPO_PATH,
    YUM_REPO_CONTENT,
    APT_KEY_URL,
    APT_DEB_STR
)


@operation
def start(command, **_):
    """starts logstash daemon"""

    ctx.logger.info('Attempting to start log transport service.')

    output = _run(command)

    if output != 0:
        raise exceptions.NonRecoverableError(
            'Unable to start log transport service: {0}'.format(output))


@operation
def stop(command, **_):
    """stops logstash daemon"""

    ctx.logger.info('Attempting to stop log transport service.')

    output = _run(command)

    if output != 0:
        raise exceptions.NonRecoverableError(
            'Unable to stop log transport service: {0}'.format(output))


@operation
def install(**_):
    """ Installs Logstash """

    ctx.logger.info('Attempting to install log transport service.')

    _install_log_stash()


def _install_log_stash():

    if _run(WHICH_YUM) == 0:
        _install_on_centos()
    elif _run(WHICH_APT) == 0:
        _install_on_ubuntu()
    else:
        raise exceptions.NonRecoverableError(
            'Unable to install, because host is '
            'neither a Ubuntu, nor a CentOS host.')


def _install_on_centos():

    ctx.logger.info(
        'Host is a CentOS host. Installing Logstash via yum.')

    _run('rpm --import {0}'.format(YUM_RPM_URL))
    _run('sudo /bin/cat > {0} <<-EOM '
         '{1} EOM'.format(YUM_REPO_PATH, YUM_REPO_CONTENT))
    _run('sudo /usr/bin/yum -y install logstash')


def _install_on_ubuntu():

    ctx.logger.info(
        'Host is an Ubuntu host. Installing Logstash via apt.')

    _run('/usr/bin/wget -qO - {0} | sudo apt-key add -'.format(APT_KEY_URL))
    _run('/bin/echo "deb {0}" | '
         'sudo /usr/bin/tee -a /etc/apt/sources.list'.format(APT_DEB_STR))
    _run('sudo /usr/bin/apt-get update')
    _run('sudo /usr/bin/apt-get -y install logstash')


def _run(command):

    command_as_list = command.split()

    ctx.logger.info('Running: {0}.'.format(command))
    ctx.logger.info('Sending: {0}.'.format(command_as_list))

    try:
        p = subprocess.Popen(
            command_as_list, stdout=subprocess.PIPE, shell=True)
    except Exception as e:
        raise exceptions.NonRecoverableError(
            'Failed: {0}.'.format(str(e)))

    try:
        out, err = p.communicate()
    except Exception as e:
        raise exceptions.NonRecoverableError(
            'Failed: {0}.'.format(str(e)))
    finally:
        ctx.logger.info(
            'RAN: {0}. OUT: {1}. ERR: {2}. Code: {3}.'.format(
                command, out, err, p.returncode))

    return p.returncode
