import os
import unittest
import time
import traceback
from mock import Mock

from slipstream import util

from slipstream.ConfigHolder import ConfigHolder
from slipstream.SlipStreamHttpClient import UserInfo
from flexiant.FlexiantClientCloud import getConnector, getConnectorClass
from slipstream.NodeInstance import NodeInstance
from slipstream.NodeDecorator import NodeDecorator, \
                                     RUN_CATEGORY_DEPLOYMENT, \
                                     RUN_CATEGORY_IMAGE, KEY_RUN_CATEGORY


CONFIG_FILE = os.path.join(os.path.dirname(__file__),
                           'pyunit.credentials.properties')
# Example configuration file.
"""
[Test]
verboseLevel = 1

General.ssh.public.key = ssh-rsa abc

network = Public
multiplicity = 1

# cloud
flexiant.user.uuid = foo
flexiant.username = bar
flexiant.password = bax
flexiant.endpoint = https://cp.sd1.flexiant.net:4442/
# image
flexiant.imageid = 81aef2d3-0291-38ef-b53a-22fcd5418e60
flexiant.image.platform = centos
flexiant.image.loginuser = root
flexiant.ram = 1024
flexiant.cpu = 1"""


def publish_vm_info(self, vm, node_instance):
    # pylint: disable=unused-argument, protected-access
    print '%s, %s' % (self._vm_get_id(vm), self._vm_get_ip(vm))


class TestFlexiantClientCloud(unittest.TestCase):

    def setUp(self):
        cn = getConnectorClass().cloudName

        os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = cn
        os.environ['SLIPSTREAM_BOOTSTRAP_BIN'] = 'http://example.com/bootstrap'
        os.environ['SLIPSTREAM_DIID'] = \
            '%s-1234-1234-1234-123456789012' % str(int(time.time()))[2:]

        if not os.path.exists(CONFIG_FILE):
            raise Exception('Configuration file %s not found.' % CONFIG_FILE)

        self.ch = ConfigHolder(configFile=CONFIG_FILE, context={'foo': 'bar'})
        self.ch.verboseLevel = int(self.ch.verboseLevel)

        self.user_info = UserInfo(cn)
        self.user_info['General.ssh.public.key'] = self.ch.config['General.ssh.public.key']
        self.user_info[cn + '.user.uuid'] = self.ch.config[cn + '.user.uuid']
        self.user_info[cn + '.username'] = self.ch.config[cn + '.username']
        self.user_info[cn + '.password'] = self.ch.config[cn + '.password']
        self.user_info[cn + '.endpoint'] = self.ch.config[cn + '.endpoint']

        node_name = 'test_node'

        self.multiplicity = int(self.ch.config['multiplicity'])

        self.node_instances = {}
        for i in range(1, self.multiplicity + 1):
            node_instance_name = node_name + '.' + str(i)
            self.node_instances[node_instance_name] = NodeInstance({
                NodeDecorator.NODE_NAME_KEY: node_name,
                NodeDecorator.NODE_INSTANCE_NAME_KEY: node_instance_name,
                'cloudservice': cn,
                'image.description': 'This is a test image.',
                'image.platform': self.ch.config[cn + '.image.platform'],
                'image.id': self.ch.config[cn + '.imageid'],
                cn + '.ram': self.ch.config[cn + '.ram'],
                cn + '.cpu': self.ch.config[cn + '.cpu'],
                'network': self.ch.config['network']
            })

        self.node_instance = NodeInstance({
            NodeDecorator.NODE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            NodeDecorator.NODE_INSTANCE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            'cloudservice': cn,
            'image.description': 'This is a test image.',
            'image.platform': self.ch.config[cn + '.image.platform'],
            'image.loginUser': self.ch.config[cn + '.image.loginuser'],
            'image.id': self.ch.config[cn + '.imageid'],
            cn + '.ram': self.ch.config[cn + '.ram'],
            cn + '.cpu': self.ch.config[cn + '.cpu'],
            'network': self.ch.config['network'],
            'image.prerecipe':
"""#!/bin/sh
set -e
set -x

ls -l /tmp
dpkg -l | egrep "nano|lvm" || true
""",
                'image.packages': ['lvm2', 'nano'],
                'image.recipe':
"""#!/bin/sh
set -e
set -x

dpkg -l | egrep "nano|lvm" || true
lvs
"""
        })

    def tearDown(self):
        os.environ.pop('SLIPSTREAM_CONNECTOR_INSTANCE')
        os.environ.pop('SLIPSTREAM_BOOTSTRAP_BIN')
        os.environ.pop('SLIPSTREAM_DIID')
        self.client = None
        self.ch = None

    def _init_connector(self, run_category=RUN_CATEGORY_DEPLOYMENT):
        self.ch.set(KEY_RUN_CATEGORY, run_category)
        self.client = getConnector(self.ch)
        self.client._publish_vm_info = Mock()

    def xtest_1_startWaitRunningStopImage(self):
        self._init_connector()
        self._start_wait_running_stop_images()

    def xtest_2_buildImage(self):
        self._init_connector(run_category=RUN_CATEGORY_IMAGE)

        try:
            instances_details = self.client.start_nodes_and_clients(
                self.user_info, {NodeDecorator.MACHINE_NAME: self.node_instance})

            assert instances_details
            assert instances_details[0][NodeDecorator.MACHINE_NAME]

            new_id = self.client.build_image(self.user_info, self.node_instance)

            assert new_id
        finally:
            self.client.stop_deployment()

        print('Deregistering image %s ... ' % new_id)
        self.client.deregister_image(new_id)
        print('Done.')

    def test_3_addDisk(self):
        self._init_connector()
        try:
            print('Node instances: %s' %self.node_instances.values())
            self.client.start_nodes_and_clients(self.user_info, self.node_instances)
            for node_instance in self.node_instances.values():
		node_instance.set_cloud_parameters({'disk.attach.size': 20})
                disk_name = self.client.attach_disk(node_instance);
                assert disk_name
        except Exception as e:
	    print(traceback.format_exc())
	finally:
             self.client.stop_deployment()
        print('Done.')

    def _start_wait_running_stop_images(self):

        try:
            self.client.start_nodes_and_clients(self.user_info, self.node_instances)

            util.printAndFlush('Instances started\n')

            vms = self.client.get_vms()
            assert len(vms) == self.multiplicity

            for vm in vms.values():
                self.client._wait_vm_in_state_running_or_timeout(vm['id'])

            time.sleep(2)
        finally:
            self.client.stop_deployment()

if __name__ == '__main__':
    unittest.main()
