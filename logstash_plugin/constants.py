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
WHICH_YUM = '/usr/bin/which yum'
WHICH_APT = '/usr/bin/which apt-get'


DEFAULT_LOGSTASH_CONFIG_DIRECTORY = '/etc/logstash/conf.d/'
YUM_RPM_URL = 'https://packages.elasticsearch.org/GPG-KEY-elasticsearch'
YUM_REPO_PATH = '/etc/yum.repos.d/logstash.repo'
YUM_REPO_CONTENT = """
[logstash-1.4]
name=Logstash repository for 1.4.x packages
baseurl=http://packages.elasticsearch.org/logstash/1.4/centos
gpgcheck=1
gpgkey=http://packages.elasticsearch.org/GPG-KEY-elasticsearch
enabled=1
"""
APT_KEY_URL = 'https://packages.elasticsearch.org/GPG-KEY-elasticsearch'
APT_DEB_STR = \
    'http://packages.elasticsearch.org/logstash/1.4/debian stable main'
