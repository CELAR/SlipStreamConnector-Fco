
from slipstream.cloudconnectors.CloudClientCommand import CloudClientCommand
from flexiant.FlexiantClientCloud import FlexiantClientCloud


class FlexiantCommand(CloudClientCommand):

    def __init__(self):
        self.PROVIDER_NAME = FlexiantClientCloud.cloudName
        super(FlexiantCommand, self).__init__()

    def _setCommonOptions(self):
        self.parser.add_option('--cust-uuid', dest='customerUUID',
                help='The UUID of the Customer',
                default='', metavar='CUST_UUID')

        self.parser.add_option('--cust-username', dest='customerUsername',
                help='Customer Username',
                default='', metavar='CUST_USERNAME')

        self.parser.add_option('--cust-password', dest='customerPassword',
                help='Customer Password',
                default='', metavar='CUST_PASSWORD')

        self.parser.add_option('--api-host', dest='endpoint',
                help='Where the API lives',
                default='', metavar='API_HOST')

    def _checkOptions(self):
        # check options, except context script as it isn't set if running an image
        if not all((self.options.imageUUID, self.options.customerUUID,
                    self.options.customerUsername, self.options.customerPassword,
                    self.options.endpoint, self.options.networkType,
                    )):
            self.parser.error('Some options were not given values. '
                              'All options are mandatory.')
        self.checkOptions()

    def _setUserInfo(self):
        self.userInfo[self.PROVIDER_NAME + '.username'] = self.options.customerUsername
        self.userInfo[self.PROVIDER_NAME + '.password'] = self.options.customerPassword
        self.userInfo[self.PROVIDER_NAME + '.user.uuid'] = self.options.customerUUID
        self.userInfo[self.PROVIDER_NAME + '.endpoint'] = self.options.endpoint

