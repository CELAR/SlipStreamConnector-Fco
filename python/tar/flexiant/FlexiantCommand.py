
from slipstream.cloudconnectors.CloudClientCommand import CloudClientCommand
from flexiant.FlexiantClientCloud import FlexiantClientCloud


class FlexiantCommand(CloudClientCommand):

    def __init__(self):
        self.PROVIDER_NAME = FlexiantClientCloud.cloudName
        super(FlexiantCommand, self).__init__()

    def _setCommonOptions(self):
        self.parser.add_option('--image-uuid', dest='imageUUID',
                help='Image UUID',
                default='', metavar='IMAGE_UUID')

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

        self.parser.add_option('--network-type', dest='networkType',
                help='Network Type',
                default='', metavar='NETWORK_TYPE')

        self.parser.add_option('--context', dest='contextScript',
                help='Context Script',
                default='', metavar='CONTEXT_SCRIPT')

        self.parser.add_option('--public-key', dest='publicKey',
                help='Public Key',
                default='', metavar='PUBLIC_KEY')

        self.parser.add_option('--vm-name', dest='vmName',
                help='VM Name',
                default='', metavar='VM_NAME')

        self.parser.add_option('--disk-size', dest='diskSize',
                help='RAM',
                default='', metavar='RAM')

        self.parser.add_option('--ram', dest='ram',
                help='RAM',
                default='', metavar='RAM')
        
        self.parser.add_option('--cpu', dest='cpu',
                help='CPU',
                default='', metavar='CPU')        

    def _checkOptions(self):
        # check options, except context script as it isn't set if running an image
        if not all((self.options.imageUUID, self.options.customerUUID,
                    self.options.customerUsername, self.options.customerPassword,
                    self.options.endpoint,self.options.networkType,
                    )):
            self.parser.error('Some options were not given values. '
                              'All options are mandatory.')
        self.checkOptions()

    def _setUserInfo(self):
        self.userInfo[self.PROVIDER_NAME + '.username'] = self.options.customerUsername
        self.userInfo[self.PROVIDER_NAME + '.password'] = self.options.customerPassword
        self.userInfo[self.PROVIDER_NAME + '.user.uuid'] = self.options.customerUUID
        self.userInfo[self.PROVIDER_NAME + '.endpoint']  = self.options.endpoint        
        self.userInfo[self.PROVIDER_NAME + '.contextScript']  = self.options.contextScript
        print "_setUserInfo:"
        l=dir(self)
        print l
        print"=====.........===="
        for property, value in vars(self).iteritems():
            print property, ": ", value
        print"=====........====="
        
