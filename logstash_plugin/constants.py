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

import os

DEFAULT_LOGSTASH_CONFIG_DIRECTORY = '/etc/logstash/conf.d/'
DEFAULT_CONFIG_FILE_PATH = os.path.join(
    DEFAULT_LOGSTASH_CONFIG_DIRECTORY,
    'logstash.conf')
DEFAULT_PACKAGE_BASE_URL = \
    'https://download.elasticsearch.org/logstash/logstash/'
DEFAULT_PACKAGES = {
    'tar': '{0}logstash-1.4.2.tar.gz'.format(DEFAULT_PACKAGE_BASE_URL),
    'rpm': '{0}packages/centos/logstash-1.4.2-1_2c0f5a1.noarch.rpm'
           .format(DEFAULT_PACKAGE_BASE_URL),
    'deb': '{0}packages/debian/logstash_1.4.2-1-2c0f5a1_all.deb'
           .format(DEFAULT_PACKAGE_BASE_URL)
}
