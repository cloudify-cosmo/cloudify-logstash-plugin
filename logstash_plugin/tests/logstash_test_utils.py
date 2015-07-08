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

# Built-in Imports
import os
import testtools

# Cloudify Imports
from cloudify.workflows import local
from cloudify.mocks import MockCloudifyContext

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__),
                                   'blueprint/resources',
                                   'logstash.conf')

DEFAULT_UBUNTU_UNINSTALL = 'dpkg -r logstash-1.5.0-1'
DEFAULT_LOGSTASH_STOP = 'sudo service logstash stop'
DEFAULT_LOGSTASH_CONFIG_PATH = '/etc/logstash/conf.d/default'

BLUEPRINT_PATH = os.path.join(os.path.dirname(__file__),
                              'blueprint', 'blueprint.yaml')

IGNORED_LOCAL_WORKFLOW_MODULES = (
    'worker_installer.tasks',
    'plugin_installer.tasks'
)


class LogstashTestUtils(testtools.TestCase):

    def setUp(self):

        super(LogstashTestUtils, self).setUp()

    def tearDown(self):

        super(LogstashTestUtils, self).tearDown()

    def _set_up(self, inputs=None):

        self.localenv = local.init_env(
            BLUEPRINT_PATH,
            name=self._testMethodName,
            inputs=inputs,
            ignored_modules=IGNORED_LOCAL_WORKFLOW_MODULES)

    def create_inline_config(self, path):

        inline = ''

        with open(path, 'r') as f:
            for line in f.readlines():
                new = '{0}\n'.format(line)
                inline += new.rjust(10)

        return '|\n{0}'.format(inline)

    def get_inputs(self, conf_type='', conf_path='',
                   conf_destination_path='',
                   inline=''):

        inputs = {
            'conf_type': conf_type,
            'conf_path': conf_path,
            'conf_destination_path': conf_destination_path,
            'conf_inline': inline
        }

        return inputs

    def get_static_config_inputs(self, conf_path=DEFAULT_CONFIG_PATH):

        return self.get_inputs(conf_type='static', conf_path=conf_path)

    def get_template_config_inputs(self, conf_path=DEFAULT_CONFIG_PATH):

        return self.get_inputs(conf_type='template', conf_path=conf_path)

    def get_inline_config(self):

        inputs = self.get_static_config_inputs()
        inputs['inline'] = self.create_inline_config(path=DEFAULT_CONFIG_PATH)
        return inputs

    def get_config(self, conf=DEFAULT_CONFIG_PATH):

        with open(conf, 'r') as f:
            return f.read()

    def get_mock_context(self, test_name):
        """ Creates a mock context """

        test_node_id = test_name
        test_properties = {
            'conf': {
                'type': '',
                'path': '',
                'destination_path': '',
                'inline': ''
            }
        }

        operation = {
            'retry_number': 0
        }

        ctx = MockCloudifyContext(
            node_id=test_node_id,
            properties=test_properties,
            operation=operation
        )

        return ctx
