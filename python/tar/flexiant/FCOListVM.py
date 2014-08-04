#!/usr/bin/python
#
# This python script is used to test creating many VMs in FCO using UserAPI

#It uses an initialisation file: setup.ini for api session credentials

from packages.user_auth import ini_auth
from packages.server_ops import list_server
from packages.resource_ops import list_resource_name
from packages.resource_ops import list_resource_type
from packages.resource_ops import list_resource

#import datetime for filename gen
import datetime
import time

#you can change INFO to DEBUG for (a lot) more information)
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)

import config
import argparse

def setup_test():
    """Function to set up api session, import credentials etc."""
    #Setup root login etc from config file
    auth_client = ini_auth(config.HOST_NAME, config.USER_LOGIN, config.USER_PASSWORD, config.CUST_UUID)
    return auth_client


def ListVM(server_uuid, customerUUID, customerUsername, customerPassword, endpoint, isVerbose=False):

    # Actually just defines the global variables now (since all config bits are passed on the command line)
    config.get_config("")    

    config.CUST_UUID     = customerUUID
    config.USER_LOGIN    = customerUsername
    config.USER_PASSWORD = customerPassword
    config.HOST_NAME     = endpoint
    #config.NETWORK_TYPE  = networkType

    auth_client = setup_test()

    print ("ListVM args: " + server_uuid + ":" +  customerUUID + ":" + customerUsername, + ":" + customerPassword + ":" + endpoint)

    server_data = list_server(auth_client, server_uuid)
    print server_data
    return server_data

if __name__ == "__main__":
    """Main Function"""

    
    parser=argparse.ArgumentParser()
    parser.add_argument('--server-uuid', dest='serverId',nargs='*',
                        help="The UUID of the Server")

    parser.add_argument('--cust-uuid', dest='customerUUID',nargs='*',
                        help="The UUID of the Customer")                        

    parser.add_argument('--cust-username', dest='customerUsername',nargs='*',
                        help="The Username of the Customer")                        

    parser.add_argument('--cust-password', dest='customerPassword',nargs='*',
                        help="The UUID of the Customer")                        
                        
    parser.add_argument('--api-host', dest='apiHost',nargs='*',
                        help="WHere the API lives")                        

    parser.add_argument('--verbose', dest='isVerbose',action='store_true',
                            help="Whether to print diagnostics as we go")
                                                    
    cmdargs=parser.parse_args()
        
    server_uuid = cmdargs.serverId[0]    
    print cmdargs
    ret=ListVM(cmdargs.serverId[0], 
               cmdargs.customerUUID[0], 
               cmdargs.customerUsername[0], 
               cmdargs.customerPassword[0], 
               cmdargs.apiHost[0], 
               cmdargs.isVerbose)


