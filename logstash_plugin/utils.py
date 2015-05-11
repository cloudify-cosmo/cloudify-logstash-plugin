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
import requests
import platform

# Cloudify Imports
from cloudify import ctx
from cloudify import exceptions


def get_distro():
    ctx.logger.debug('identifying distribution...')
    distro = platform.dist()[0]
    ctx.logger.debug('distro identified: {0}'.format(distro))


def get_package_type_for_distro(distro=get_distro()):
    ctx.logger.debug('identifying package type for distro')
    if distro.lower() in ['ubuntu', 'debian']:
        return 'deb'
    elif distro.lower() in ['centos', 'redhat', 'fedora']:
        return 'rpm'
    else:
        return None


def verify_is_executable(execute):
    ctx.logger.debug('Verifying that {0} is executable.'.format(execute))
    if os.system('{0}'.format(execute)):
        return False
    return True


def download_resource(url, destination):
    ctx.logger.debug('downloading {0} to {1}...'.format(url, destination))
    split = url.split('://')
    schema = split[0]
    if schema in ['http', 'https']:
        response = requests.get(url, stream=True)
        if not response.status_code == 200:
            raise exceptions.NonRecoverableError(
                'Failed downloading resource: {0}'
                ' (''status code: {1})'.format(url, response.status_code))
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return destination
    else:
        return ctx.download_resource(url)
