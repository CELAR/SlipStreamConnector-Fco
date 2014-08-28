#!/usr/bin/python
#

from packages.user_auth import ini_auth
from packages.server_ops import list_server
from packages.resource_ops import list_resource_name
from packages.resource_ops import list_resource_type
from packages.resource_ops import list_resource

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

def image_disk(auth_client, server_uuid, diskIndex):
    # Details of the server
    print("Details for the server we will Image:")
    res=list_server(auth_client, server_uuid)
    print("============================")
    
    # Image it's disk
    print("===")
    print res.disks[diskIndex]
    print("===")
    image_data = auth_client.factory.create('image')
    image_data.baseUUID = res.disks[diskIndex].resourceUUID
    image_data.vmSupport = True
    image_data.defaultUser="ubuntu"
    image_data.genPassword = True
    image_data.size = 20
    print("Create Image input:")
    print image_data
    
    job_ret = auth_client.service.createImage(image_data)
    print job_ret
    print("Details for newly created image:")
    newimg_ret = list_resource(auth_client, job_ret.itemUUID,"IMAGE")
    print newimg_ret.list[0]
    return newimg_ret.list[0]

def ImageDisk(server_uuid, diskIndex, customerUUID, customerUsername, customerPassword, endpoint, isVerbose=False):

    # Actually just defines the global variables now (since all config bits are passed on the command line)
    config.get_config("")

    config.CUST_UUID = customerUUID
    config.USER_LOGIN = customerUsername
    config.USER_PASSWORD = customerPassword
    config.HOST_NAME = endpoint

    auth_client = setup()
    
    image_state = image_disk(auth_client, server_uuid, 0)
    return image_state

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

    parser.add_argument('--action', dest='actionRequested', nargs='*',
                            help="WHat to do")                            

    cmdargs = parser.parse_args()

    server_uuid = cmdargs.serverId[0]
    print cmdargs
    
    if (cmdargs.actionRequested[0] == "ImageDisk"):
        ret = ImageDisk(cmdargs.serverId[0],
                   0,
                   cmdargs.customerUUID[0],
                   cmdargs.customerUsername[0],
                   cmdargs.customerPassword[0],
                   cmdargs.apiHost[0],
                   cmdargs.isVerbose)
        print ret

