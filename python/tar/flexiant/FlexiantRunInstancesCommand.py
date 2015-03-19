#!/usr/bin/env python

from slipstream.command.RunInstancesCommand import RunInstancesCommand
from flexiant.FlexiantCommand import FlexiantCommand
from flexiant.FlexiantClientCloud import FlexiantClientCloud


class FlexiantRunInstances(RunInstancesCommand, FlexiantCommand):

    CPU_KEY = 'cpu'
    RAM_KEY = 'ram'

    def get_connector_class(self):
        return FlexiantClientCloud

    def __init__(self):
        super(FlexiantRunInstances, self).__init__()

    def set_cloud_specific_options(self, parser):
        FlexiantCommand.set_cloud_specific_options(self, parser)

        self.parser.add_option('--' + self.CPU_KEY, dest=self.CPU_KEY,
                               help='Number of CPUs.',
                               default='', metavar='CPU')

        self.parser.add_option('--' + self.RAM_KEY, dest=self.RAM_KEY,
                               help='RAM in GB.',
                               default='', metavar='RAM')

    def get_cloud_specific_node_inst_cloud_params(self):
        return {'cpu': self.get_option(self.CPU_KEY),
                'ram': self.get_option(self.RAM_KEY)}

    def get_cloud_specific_user_cloud_params(self):
        return FlexiantCommand.get_cloud_specific_user_cloud_params(self)

    def get_cloud_specific_mandatory_options(self):
        return FlexiantCommand.get_cloud_specific_mandatory_options(self) + \
            [self.CPU_KEY, self.RAM_KEY]
