#!/usr/bin/python
#

from packages.fco_rest import getToken
from packages.fco_rest import rest_create_image
from packages.fco_rest import list_resource_by_uuid


# import datetime for filename gen
import sys
import datetime
import time

# you can change INFO to DEBUG for (a lot) more information)
import logging
#REST logging
logging.getLogger("requests").setLevel(logging.WARNING)

import config
import argparse


def setup():
    """Function to set up api session, import credentials etc."""
    token = getToken(config.HOST_NAME, config.USER_LOGIN, config.CUST_UUID, config.USER_PASSWORD)
    auth_client = dict(endpoint=config.HOST_NAME, token=token)
    return auth_client

def image_disk(auth_client, server_uuid, default_user, diskIndex):
    # Details of the server
    print("Details for the server we will Image:")
    print("============================")
    server_resultset = list_resource_by_uuid(auth_client, server_uuid, res_type='SERVER')
    for l in range(0, server_resultset['totalCount']):
        server = server_resultset['list'][l]

    #baseUUID = server['resourceUUID']
    clusterUUID = server['clusterUUID']
    vdcUUID = server['vdcUUID']
    # Image should be same size as the source disk
    disk = server['disks'][diskIndex]
    size = disk['size']
    baseUUID = disk['resourceUUID']

    print("Create Image input:")
    response = rest_create_image(auth_client, baseUUID, clusterUUID, vdcUUID, size, default_user)
    print("=============================")
    print response
    print("Details for newly created image:")
    createdImage = list_resource_by_uuid(auth_client, response['itemUUID'],"IMAGE")
    for l in range(0, createdImage['totalCount']):
        image = createdImage['list'][l]

    print image
    sys.stdout.flush()
    return image

def ImageDisk(server_uuid, diskIndex, customerUUID, customerUsername, customerPassword, endpoint, default_user="ubuntu", isVerbose=False):

    # Actually just defines the global variables now (since all config bits are passed on the command line)
    config.get_config("")

    config.CUST_UUID = customerUUID
    config.USER_LOGIN = customerUsername
    config.USER_PASSWORD = customerPassword
    config.HOST_NAME = endpoint

    auth_client = setup()

    image_state = image_disk(auth_client, server_uuid, default_user, 0)
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

    parser.add_argument('--default-user', dest='defaultUser', nargs='*',
                            help="Default user to assign to the image")             
    
    parser.add_argument('--action', dest='actionRequested', nargs='*',
                            help="Which action to perform")                            

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
                   cmdargs.defaultUser[0],
                   cmdargs.isVerbose)
        print ret


