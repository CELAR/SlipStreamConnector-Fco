#!/usr/bin/python
# 
# List VMs owned by the specified customer, and their state

from flexiant.packages.user_auth import ini_auth

import flexiant.config as config
import argparse


def setup_test():
    """Function to set up api session, import credentials etc."""
    auth_client = ini_auth(config.HOST_NAME, config.USER_LOGIN, config.USER_PASSWORD, config.CUST_UUID)
    return auth_client

def list_customer_servers(auth_client, customer_uuid):
    sf = auth_client.factory.create('searchFilter')
    fc1 = auth_client.factory.create('filterConditions')
    qf = auth_client.factory.create('queryLimit')
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'customerUUID'   
    fc1.value = customer_uuid    
    sf.filterConditions.append(fc1)
    qf.loadChildren = False
    
    server_result_set = auth_client.service.listResources(searchFilter = sf, queryLimit=qf, resourceType = 'SERVER')

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
    
        
    auth_client = setup_test()        

    list_customer_servers(auth_client=auth_client, customer_uuid=config.CUST_UUID)
    
if __name__ == "__main__":
    main()


