#!/usr/bin/python
#
#
# This python script is used to test creating many VMs in FCO using UserAPI

# It uses an initialisation file: setup.ini for api session credentials
import sys

# import functions from files in packages folder
from packages.fco_rest import getToken
from packages.fco_rest import wait_for_server
from packages.fco_rest import list_resource_by_uuid
from packages.fco_rest import rest_delete_resource
from VMActions import StopVM

# For config settings
import config
import argparse

# import datetime for filename gen
import datetime
import time

# you can change INFO to DEBUG for (a lot) more information)
import logging
logging.getLogger("requests").setLevel(logging.WARNING)

def setup_test():
    """Function to set up api session, import credentials etc."""
    token = getToken(config.HOST_NAME, config.USER_LOGIN, config.CUST_UUID, config.USER_PASSWORD)
    auth_client = dict(endpoint=config.HOST_NAME, token=token)
    return auth_client


def DestroyVM(server_uuid, customerUUID, customerUsername, customerPassword, endpoint, isVerbose=False):
    # Actually just defines the global variables now (since all config bits are passed on the command line)
    print "Start of DestroyVM"
    config.get_config("")

    config.CUST_UUID = customerUUID
    config.USER_LOGIN = customerUsername
    config.USER_PASSWORD = customerPassword
    config.HOST_NAME = endpoint

    auth_client = setup_test()

    StopVM(server_uuid, customerUUID, customerUsername, customerPassword, endpoint, isVerbose=False)
    result = rest_delete_resource(auth_client, server_uuid, "SERVER")

    print "rest_delete_resource() result is:"
    print result
    print "------"
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

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

    parser.add_argument('--server-uuid', dest='serverUUID', nargs='*',
                           help="UUID of the Server to be destroyed")

    cmdargs = parser.parse_args()

    isVerbose = cmdargs.isVerbose

    ret = DestroyVM(cmdargs.serverUUID[0],
               cmdargs.customerUUID[0],
               cmdargs.customerUsername[0],
               cmdargs.customerPassword[0],
               cmdargs.endpoint[0],
               isVerbose)

    print "FCODestroy(): ret is" + str(ret)
    out = "Server UUID and IP:" + ret['server_uuid']
    out = out + ":" + ret['password']
    out = out + ":" + ret['login']
    out = out + ":" + ret['ip']
    print out

