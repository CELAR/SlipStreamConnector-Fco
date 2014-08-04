#!/usr/bin/python
# 
# List VMs owned by the specified customer, and their state

import os

from flexiant.packages.user_auth import ini_auth

import flexiant.config as config
import argparse


#import datetime for filename gen
import datetime
import time

# import configParser to read setup.ini file
#from ConfigParser import SafeConfigParser

#you can change INFO to DEBUG for (a lot) more information)
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)


def setup_test():
    """Function to set up api session, import credentials etc."""
    auth_client = ini_auth(config.HOST_NAME, config.USER_LOGIN, config.USER_PASSWORD, config.CUST_UUID)
    return auth_client

def list_customer_servers(auth_client, customer_uuid):
    sf = auth_client.factory.create('searchFilter')
    fc1 = auth_client.factory.create('filterConditions')
    fc1.condition = 'IS_EQUAL_TO'
    #fc1.field = 'resourceUUID'   
    #fc1.value = server_uuid
    fc1.field = 'customerUUID'   
    fc1.value = customer_uuid    
    sf.filterConditions.append(fc1)
    server_result_set = auth_client.service.listResources(searchFilter = sf,resourceType = 'SERVER')
    #extract number of Servers from result set
    if (server_result_set.totalCount == 0):
      msg = "ERROR: No servers found for customer with UUID '" + customer_uuid + "'"
      return msg

    print "UUID                                  State"
    for x in xrange(0, server_result_set.totalCount):
        server_data = server_result_set.list[x]
        #print("Server Data:")
        #print(server_data)
        server_uuid = server_data.resourceUUID
        server_name = server_data.resourceName
        server_state = server_data.status
        #ip_address = server_data.nics[0].ipAddresses[0].ipAddress        
        print "" + server_uuid + "  " + server_state

    return
        
def main():
    """Main Function"""

    # define global variables



    # Actually just defines the global variables now (since all config bits are passed on the command line)
    config.get_config("")    
    
    parser=argparse.ArgumentParser()

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
        
    config.CUST_UUID     = cmdargs.customerUUID[0]
    config.USER_LOGIN    = cmdargs.customerUsername[0] 
    config.USER_PASSWORD = cmdargs.customerPassword[0]
    config.HOST_NAME     = cmdargs.apiHost[0]
    isVerbose            = cmdargs.isVerbose

    # better late than never
    if (isVerbose):
        print (cmdargs)
    
        
    # See what SlipStream is passing us by way of environment variables
    #for param in os.environ.keys():
    #    print "%20s %s" % (param,os.environ[param])    
    

    # ignore setup.ini as we get all the args via the command line

    
    auth_client = setup_test()        

    list_customer_servers(auth_client=auth_client, customer_uuid=config.CUST_UUID)
    
if __name__ == "__main__":
    main()


