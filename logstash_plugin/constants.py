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

ELATIC_CO_BASE_URL = 'http://download.elastic.co/logstash/' \
                     'logstash/packages/'
DEFAULT_RPM_URL = 'centos/logstash-1.5.0-1.noarch.rpm'
DEFAULT_DEB_URL = 'debian/logstash_1.5.0-1_all.deb'
INSTALLED_UBUNTU = 'out=`/usr/bin/dpkg --get-selections logstash`'
INSTALLED_CENTOS = 'out=`rpm -qa logstash'
