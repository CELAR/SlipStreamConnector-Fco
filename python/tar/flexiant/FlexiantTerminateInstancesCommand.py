
from slipstream.command.TerminateInstancesCommand import TerminateInstancesCommand
from flexiant.FlexiantCommand import FlexiantCommand
from flexiant.FlexiantClientCloud import FlexiantClientCloud


class FlexiantTerminateInstances(TerminateInstancesCommand, FlexiantCommand):

    def __init__(self):
        super(FlexiantTerminateInstances, self).__init__()

    def get_connector_class(self):
        return FlexiantClientCloud
