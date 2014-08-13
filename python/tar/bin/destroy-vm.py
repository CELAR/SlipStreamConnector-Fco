#!/usr/bin/python
#
#

import sys

from flexiant.packages.user_auth import ini_auth
from flexiant.list_vm import list_server


# For config settings
import flexiant.config as config
import argparse

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


def setup_test():
    """Function to set up api session, import credentials etc."""
    #Setup root login etc from config file
    auth_client = ini_auth(config.HOST_NAME, config.USER_LOGIN, config.USER_PASSWORD, config.CUST_UUID)
    return auth_client

def wait_for_server(server_client, server_uuid, status):
    sf = server_client.factory.create('searchFilter')
    # debug print statement	
#    print sf
    #create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = server_uuid
    sf.filterConditions.append(fc1)
    fc2 = server_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'status'
    fc2.value = status
    sf.filterConditions.append(fc2)
#    print "sf:"
#    print sf
    server_result = server_client.service.listResources(searchFilter = sf, resourceType = "SERVER")
#    print server_created
    i = 0
#    print "server created count:" + str(server_created.totalCount)
    # currently waiting for 100 seconds (up to 10 loops of a 10 second sleep)
    while (server_result.totalCount < 1) and (i <= 10):
        print "in wait_for_server loop i = " + str(i) + ", count " + str(server_result.totalCount)
        i = i + 1
        # wait a while
        time.sleep(10)
        server_result = server_client.service.listResources(searchFilter = sf, resourceType = "SERVER")
#        print "server created count:" + str(server_created.totalCount)
    if server_result.totalCount == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val

def change_server_status(server_client, server_uuid, state):
    """ Check for status of server """
    if state == "SHUTDOWN":
        server_client.service.changeServerStatus(serverUUID=server_uuid, newStatus=state, safe=True)
    else:
        server_client.service.changeServerStatus(serverUUID=server_uuid, newStatus=state, safe=True)
    server_result = wait_for_server(server_client, server_uuid, state)
    if server_result == 1:
        print "Problem changing server status, check platform, server uuid: " + server_uuid
    else:
        print "server status changed ok, server uuid: " + server_uuid
    return server_result
                                                           
def main(argv):
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
                                                    
    parser.add_argument('--server-uuid', dest='serverUUID',nargs='*',
                           help="UUID of the Server to be destroyed")
                           
    cmdargs=parser.parse_args()
        
    config.CUST_UUID     = cmdargs.customerUUID[0]
    config.USER_LOGIN    = cmdargs.customerUsername[0] 
    config.USER_PASSWORD = cmdargs.customerPassword[0]
    config.HOST_NAME     = cmdargs.apiHost[0]
    isVerbose            = cmdargs.isVerbose
    server_uuid          = cmdargs.serverUUID[0]

    # better late than never
    if (isVerbose):
        print (cmdargs)
    
    print "Received request to destroy VM " + server_uuid + " for customer " + config.CUST_UUID


    auth_client = setup_test()
            
    # Uncomment the next few lines if we want to check for the server being in running state first
    server_data = list_server(auth_client, server_uuid)
    if (type(server_data) == str):
        if (server_data[0:5] == "ERROR"):
            print("Failed: " + server_data)
            return
      
    #server_name = server_data.resourceName
    server_state = server_data.status
    #print("Server Name: " + server_name + " is " + server_state)    
    if (server_state == 'RUNNING'):                                
        print "Stopping Server..."
        server_result = change_server_status(auth_client, server_uuid, "STOPPED")
        print server_result
    
    
    # This will DELETE any resource relating to VM - Disk, NICs, Server, the lot !
    result = auth_client.service.deleteResource(resourceUUID=server_uuid, cascade=True)
    print result
                 

if __name__ == "__main__":
    main(sys.argv)

