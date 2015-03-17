from slipstream.command.CloudClientCommand import CloudClientCommand
from flexiant.FlexiantClientCloud import FlexiantClientCloud


class FlexiantCommand(CloudClientCommand):

    ENDPOINT_KEY = 'endpoint'
    USER_UUID_KEY = 'user.uuid'

    def __init__(self):
        super(FlexiantCommand, self).__init__()

    def get_connector_class(self):
        return FlexiantClientCloud

    def set_cloud_specific_options(self, parser):
        parser.add_option('--' + self.ENDPOINT_KEY, dest=self.ENDPOINT_KEY,
                          help='Cloud endpoint',
                          default='', metavar='ENDPOINT')

        parser.add_option('--' + self.USER_UUID_KEY, dest=self.USER_UUID_KEY,
                          help='User UUID',
                          default='', metavar='UUID')

    def get_cloud_specific_user_cloud_params(self):
        return {self.ENDPOINT_KEY: self.get_option(self.ENDPOINT_KEY),
                self.USER_UUID_KEY: self.get_option(self.USER_UUID_KEY)}

    def get_cloud_specific_mandatory_options(self):
        return [self.ENDPOINT_KEY,
                self.USER_UUID_KEY]
