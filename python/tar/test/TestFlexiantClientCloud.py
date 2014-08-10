import os
import unittest

from flexiant.FlexiantClientCloud import FlexiantClientCloud
from slipstream.ConfigHolder import ConfigHolder
from slipstream.NodeDecorator import (RUN_CATEGORY_DEPLOYMENT,
                                      KEY_RUN_CATEGORY)


class TestFlexiantClientCloud(unittest.TestCase):

    def setUp(self):
        os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = 'Test'
        self.ch = ConfigHolder(config={'foo': 'bar'}, context={'foo': 'bar'})
        self.ch.set(KEY_RUN_CATEGORY, RUN_CATEGORY_DEPLOYMENT)

    def test_FcoClientCloudInit(self):
        fco = FlexiantClientCloud(self.ch)
        assert fco
        assert fco.run_category == RUN_CATEGORY_DEPLOYMENT
