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

# Built in imports
from subprocess import Popen, PIPE

# Cloudify imports
from cloudify import ctx
from cloudify import exceptions


def run(command):

    command_as_list = command.split()

    ctx.logger.info(command_as_list)

    try:
        run = Popen(command_as_list, stdout=PIPE)
    except Exception as e:
        raise exceptions.NonRecoverableError(
            'Unable to run command. Error {0}'.format(str(e)))

    try:
        output = run.communicate()
    except Exception as e:
        raise exceptions.NonRecoverableError(
            'Unable to run command. Error {0}'.format(str(e)))
    finally:
        ctx.logger.debug(
            'RAN: {0}. OUT: {1}. Code: {2}.'.format(
                command, output, run.returncode))

    return run
