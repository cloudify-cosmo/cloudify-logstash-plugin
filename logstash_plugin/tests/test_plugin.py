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
import subprocess

from logstash_test_utils import (
    LogstashTestUtils,
    DEFAULT_UBUNTU_UNINSTALL,
    DEFAULT_LOGSTASH_STOP,
    DEFAULT_LOGSTASH_CONFIG_PATH
)
# from cloudify import ctx


class TestLogstashPlugin(LogstashTestUtils):

    def test_install_static_clean(self):
        inputs = self.get_static_config_inputs()
        self._set_up(inputs)
        self.addCleanup(subprocess.call, DEFAULT_UBUNTU_UNINSTALL)
        self.env.execute('install', task_retries=10)
        self.addCleanup(subprocess.call, DEFAULT_LOGSTASH_STOP)
        logstash_started = subprocess.call(
            "sudo service logstash status", shell=True)
        self.assertIn('started', logstash_started)
        self.addCleanup(os.remove, DEFAULT_LOGSTASH_CONFIG_PATH)
        with open(DEFAULT_LOGSTASH_CONFIG_PATH, 'r') as default:
            self.assertEqual(default.read(), self.get_config())

    def test_uninstall_static_clean(self):
        self.addCleanup(subprocess.call, DEFAULT_UBUNTU_UNINSTALL)
        self.addCleanup(subprocess.call, DEFAULT_LOGSTASH_STOP)
        self.addCleanup(os.remove, DEFAULT_LOGSTASH_CONFIG_PATH)
        inputs = self.get_static_config_inputs()
        self._set_up(inputs)
        self.env.execute('install', task_retries=10)
        self.env.execute('uninstall', task_retries=10)
        logstash_stopped = subprocess.call(
            "sudo service logstash status", shell=True)
        self.assertNotIn('started', logstash_stopped)
