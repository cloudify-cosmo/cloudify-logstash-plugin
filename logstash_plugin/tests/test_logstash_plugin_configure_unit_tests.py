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

from cloudify import exceptions
from logstash_plugin import tasks
from cloudify.state import current_ctx
from logstash_test_utils import (
    LogstashTestUtils,
    DEFAULT_LOGSTASH_CONFIG_PATH
)


class TestLogstashPluginConfigureUnitTests(LogstashTestUtils):

    def test_configure_template_no_path(self):
        """ Tests that if conf.type is template,
            but conf.path is empty then an error will be raised.
        """

        ERROR = \
            'logstash property conf.path ' \
            'cannot be empty if conf.type is "template".'

        ctx = self.get_mock_context(
            'test_configure_template_no_path')
        current_ctx.set(ctx=ctx)
        ctx.node.properties['conf']['type'] = 'template'
        ex = self.assertRaises(
            exceptions.NonRecoverableError,
            tasks.configure,
            ctx.node.properties['conf'],
            ctx=ctx)
        self.assertIn(ERROR, ex.message)

    def test_configure_static_no_path_or_inline(self):
        """ Tests that if conf.type is static,
            but conf.path is empty then an error will be raised.
        """

        ERROR = \
            'either logstash property conf.path ' \
            'or conf.inline are required when conf.type is "static".'

        ctx = self.get_mock_context(
            'test_configure_static_no_path_or_inline')
        current_ctx.set(ctx=ctx)
        ctx.node.properties['conf']['type'] = 'static'
        ex = self.assertRaises(
            exceptions.NonRecoverableError,
            tasks.configure,
            ctx.node.properties['conf'],
            ctx=ctx)
        self.assertIn(ERROR, ex.message)

    def test_configure_neither_static_nor_template(self):
        """ Tests that if conf.type is not static or template,
            then an error will be raised.
        """

        ERROR = \
            'logstash property conf.type ' \
            'can only be "template" or "static".'

        ctx = self.get_mock_context(
            'test_configure_neither_static_nor_template')
        current_ctx.set(ctx=ctx)
        ex = self.assertRaises(
            exceptions.NonRecoverableError,
            tasks.configure,
            ctx.node.properties['conf'],
            ctx=ctx)
        self.assertIn(ERROR, ex.message)

    def test_configure_template(self):
        """ Tests that if template is given,
            then a NotImplementedError will be raised.
        """

        ctx = self.get_mock_context(
            'test_configure_neither_static_nor_template')
        current_ctx.set(ctx=ctx)
        ctx.node.properties['conf']['type'] = 'template'
        ctx.node.properties['conf']['path'] = \
            DEFAULT_LOGSTASH_CONFIG_PATH
        ex = self.assertRaises(
            NotImplementedError,
            tasks.configure,
            ctx.node.properties['conf'],
            ctx=ctx)
        self.assertIn('', ex.message)
