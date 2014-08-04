#!/usr/bin/python
#
# This python script is used to test creating many VMs in FCO using UserAPI

#It uses an initialisation file: setup.ini for api session credentials



# import functions from files in packages folder
from flexiant.packages.user_auth import ini_auth
from flexiant.packages.vdc_ops import count_vdc
from flexiant.packages.vdc_ops import create_vdc
from flexiant.packages.vdc_ops import get_vdc_uuid
from flexiant.packages.image_ops import count_image
from flexiant.packages.image_ops import fetch_image
from flexiant.packages.image_ops import get_image_uuid
from flexiant.packages.image_ops import wait_for_image
from flexiant.packages.server_ops import create_server
from flexiant.packages.server_ops import count_server
from flexiant.packages.server_ops import wait_for_install
from flexiant.packages.server_ops import wait_for_server
from flexiant.packages.resource_ops import list_resource_name
from flexiant.packages.resource_ops import list_resource_type
from flexiant.packages.resource_ops import list_resource
from flexiant.packages.resource_ops import wait_for_resource


# import library for SSH
#import pysftp

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

import flexiant.config as config
import argparse

def setup_test():
    """Function to set up api session, import credentials etc."""
    #Setup root login etc from config file
    auth_client = ini_auth(config.HOST_NAME, config.USER_LOGIN, config.USER_PASSWORD, config.CUST_UUID)
    return auth_client


def list_server(auth_client, server_uuid):
    sf = auth_client.factory.create('searchFilter')
    fc1 = auth_client.factory.create('filterConditions')
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'   
    fc1.value = server_uuid
    sf.filterConditions.append(fc1)
    server_result_set = auth_client.service.listResources(searchFilter = sf,resourceType = 'SERVER')
    #extract number of Servers from result set
    if (server_result_set.totalCount == 0):
      msg = "ERROR: Server with uuid " + server_uuid + " not found."
      return msg
    
    print server_result_set;
    server_data = server_result_set.list[0]
    print server_data
    return server_data

def main():
    """Main Function"""

    # Actually just defines the global variables now (since all config bits are passed on the command line)
    config.get_config("")    
    
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
                                                    
    #parser.add_argument('--bar',nargs='*',action=BarAction,help="Bar! : Must be used after --foo")

    cmdargs=parser.parse_args()
        
    server_uuid = cmdargs.serverId[0]    
    config.CUST_UUID     = cmdargs.customerUUID[0]
    config.USER_LOGIN    = cmdargs.customerUsername[0] 
    config.USER_PASSWORD = cmdargs.customerPassword[0]
    config.HOST_NAME     = cmdargs.apiHost[0]
    isVerbose            = cmdargs.isVerbose

    # better late than never
    if (isVerbose):
        print (cmdargs)
    
    # Does this need to be parameterised, or picked up by some other means ?
    config.PROD_OFFER = 'Generic Disk'


    auth_client = setup_test()

    server_data = list_server(auth_client, server_uuid)

    print server_data

    server_name = server_data.resourceName
    server_state = server_data.status
    print("Server Name: '" + server_name + "' is " + server_state)
    ip_address = server_data.nics[0].ipAddresses[0].ipAddress
    print("Server " + server_name + " has IP Address " + ip_address)

if __name__ == "__main__":
    main()


