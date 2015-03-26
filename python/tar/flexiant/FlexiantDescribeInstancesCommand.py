from slipstream.command.DescribeInstancesCommand import DescribeInstancesCommand
from flexiant.FlexiantCommand import FlexiantCommand


class FlexiantDescribeInstances(DescribeInstancesCommand, FlexiantCommand):

    def __init__(self):
        super(FlexiantDescribeInstances, self).__init__()

    def _vm_get_state(self, cc, vm):
        return cc._vm_get_state(vm)

    def get_initialization_extra_kwargs(self):
        return {'run_instance': False}
