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
import unittest
import subprocess

from cloudify.workflows import local

DEFAULT = """
input { stdin { type => "stdin-type"}}
output { stdout { debug => true debug_format => "json"}}
"""

LOGSTASH = """
inputs {
    generator {
        tags => ["event"]
        count => 0
        message => "Test Event Message"
    }
    generator {
        tags => ["log"]
        count => 0
        message => "Test Log Message"
    }
}

outputs {
    rabbitmq {
        if "event" in [tags] {
            exchange => ""
            exchange_type => "direct"
            key => "cloudify-events"
            host => "MGMT_IP"
            durable => "true"
            exclusive => "false"
        }
    }
    rabbitmq {
        if "log" in [tags] {
            exchange => ""
            exchange_type => "direct"
            key => "cloudify-logs"
            host => "MGMT_IP"
            durable => "true"
            exclusive => "false"
        }
    }
    stdout {}
}
"""


class TestPlugin(unittest.TestCase):

    def setUp(self):
        # build blueprint path
        blueprint_path = os.path.join(os.path.dirname(__file__),
                                      'blueprint', 'blueprint.yaml')

        # inject input from test
        inputs = {}

        # setup local workflow execution environment
        self.env = local.init_env(blueprint_path,
                                  name=self._testMethodName,
                                  inputs=inputs)

    def test_install(self):

        # execute install workflow
        self.env.execute('install', task_retries=10)

        logstash_started = subprocess.call(
            "sudo service logstash status", shell=True)

        self.assertIn('started', logstash_started)

        with open('/etc/logstash/conf.d/default', 'r') as default:
            self.assertEqual(default.read(), DEFAULT)

        with open('/etc/logstash/conf.d/logstash.conf', 'r') as logstash:
            self.assertEqual(logstash.read(), LOGSTASH)

    def test_uninstall(self):
        # execute install workflow
        self.env.execute('uninstall', task_retries=10)

        logstash_stopped = subprocess.call(
            "sudo service logstash status", shell=True)
        self.assertNotIn('started', logstash_stopped)
