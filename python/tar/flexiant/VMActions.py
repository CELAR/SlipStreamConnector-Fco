#!/usr/bin/python
#

from packages.user_auth import ini_auth
from packages.server_ops import list_server
from packages.resource_ops import list_resource_name
from packages.resource_ops import list_resource_type
from packages.resource_ops import list_resource
from packages.server_ops import wait_for_server
from packages.server_ops import get_server_state
from packages.server_ops import change_server_status

# import datetime for filename gen
import datetime
import time

# you can change INFO to DEBUG for (a lot) more information)
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)

import config
import argparse


def setup():
    """Function to set up api session, import credentials etc."""
    auth_client = ini_auth(config.HOST_NAME, config.USER_LOGIN, config.USER_PASSWORD, config.CUST_UUID)
    return auth_client

def stop_server(auth_client, server_uuid):
    """Function to stop server"""
    # Chevk it's state first, as it is an error to stop it when it is already stopped (or in any other state
    # apart from running. 
    server_state = get_server_state(auth_client, server_uuid)
    
    if (server_state == 'STARTING'):
        print("Server appears to be starting; waiting until it has completed before stopping")
        ret = wait_for_server(server_client=auth_client, server_uuid=server_uuid, status='RUNNING')
        if (ret != 0):
            raise Exception("Server not in RUNNING state, cannot be stopped")
                        
        server_state = get_server_state(auth_client, server_uuid)
        # Fall-thru if the server made it to running state
        #print("fall-thru")
    
    if (server_state == 'RUNNING'):
        change_server_status(server_client=auth_client, server_uuid=server_uuid, state='STOPPED')

    # Check we actually made it to STOPPED state
    ret = wait_for_server(server_client=auth_client, server_uuid=server_uuid, status='STOPPED')
    if (ret != 0):
        raise Exception("Server failed to STOP") 
        
    server_state = get_server_state(auth_client, server_uuid)
    return server_state

def WaitUntilVMRunning(server_uuid, customerUUID, customerUsername, customerPassword, endpoint, isVerbose=False):
    config.get_config("")

    config.CUST_UUID = customerUUID
    config.USER_LOGIN = customerUsername
    config.USER_PASSWORD = customerPassword
    config.HOST_NAME = endpoint
    # config.NETWORK_TYPE  = networkType

    auth_client = setup()
    server_state = get_server_state(auth_client, server_uuid)
    
    if (server_state != 'RUNNING'):
        ret = wait_for_server(server_client=auth_client, server_uuid=server_uuid, status='RUNNING')
        if (ret != 0):
            raise Exception("Server did not get to RUNNING state")

    return server_state
    

def StopVM(server_uuid, customerUUID, customerUsername, customerPassword, endpoint, isVerbose=False):

    # Actually just defines the global variables now (since all config bits are passed on the command line)
    config.get_config("")

    config.CUST_UUID = customerUUID
    config.USER_LOGIN = customerUsername
    config.USER_PASSWORD = customerPassword
    config.HOST_NAME = endpoint
    # config.NETWORK_TYPE  = networkType

    auth_client = setup()
    server_state = stop_server(auth_client, server_uuid)
    return server_state

if __name__ == "__main__":
    """Main Function"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--server-uuid', dest='serverId', nargs='*',
                        help="The UUID of the Server")

    parser.add_argument('--cust-uuid', dest='customerUUID', nargs='*',
                        help="The UUID of the Customer")

    parser.add_argument('--cust-username', dest='customerUsername', nargs='*',
                        help="The Username of the Customer")

    parser.add_argument('--cust-password', dest='customerPassword', nargs='*',
                        help="The UUID of the Customer")

    parser.add_argument('--api-host', dest='apiHost', nargs='*',
                        help="WHere the API lives")

    parser.add_argument('--verbose', dest='isVerbose', action='store_true',
                            help="Whether to print diagnostics as we go")

    cmdargs = parser.parse_args()

    server_uuid = cmdargs.serverId[0]
    print cmdargs
    ret = StopVM(cmdargs.serverId[0],
               cmdargs.customerUUID[0],
               cmdargs.customerUsername[0],
               cmdargs.customerPassword[0],
               cmdargs.apiHost[0],
               cmdargs.isVerbose)


