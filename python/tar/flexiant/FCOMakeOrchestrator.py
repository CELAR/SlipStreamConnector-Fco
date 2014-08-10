#!/usr/bin/python
# This python script is used to test creating many VMs in FCO using UserAPI

import os
import sys

sys.path.insert(1, '.')

# import functions from files in packages folder
from packages.user_auth import ini_auth
from packages.vdc_ops import count_vdc
from packages.vdc_ops import create_vdc
from packages.vdc_ops import get_vdc_uuid
from packages.image_ops import count_image
from packages.image_ops import fetch_image
from packages.image_ops import get_image_uuid
from packages.image_ops import wait_for_image
# We have our own (amended) copy of this
# from packages.server_ops import create_server
from packages.server_ops import count_server
from packages.server_ops import create_nic
from packages.server_ops import add_nic_to_server
from packages.server_ops import wait_for_install
from packages.server_ops import wait_for_server
from packages.server_ops import change_server_status
from packages.server_ops import get_server_state
from packages.server_ops import get_server_data
from packages.server_ops import add_ip
from packages.resource_ops import list_resource_name
from packages.resource_ops import list_resource_type
from packages.resource_ops import list_resource
from packages.resource_ops import wait_for_resource
# from packages.transaction_ops import list_unit_transactions


import config
import argparse

# import library for SSH
# import pysftp

# import datetime for filename gen
import datetime
import time

# import configParser to read setup.ini file
# from ConfigParser import SafeConfigParser

# you can change INFO to DEBUG for (a lot) more information)
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)


def setup_test():
    """Function to set up api session, import credentials etc."""
    # Setup root login etc from config file
    auth_client = ini_auth(config.HOST_NAME, config.USER_LOGIN, config.USER_PASSWORD, config.CUST_UUID)
    return auth_client


def setup_vdc(auth_client, vdc_name):
    """Function to check for VDC Create if missing"""
    vdc_count = count_vdc(auth_client)
#    print vdc_count
    if vdc_count == 0:
        vdc_uuid = create_vdc(vdc_client=auth_client, vdc_name=vdc_name)
    else:
        vdc_uuid = get_vdc_uuid(auth_client)
    return vdc_uuid

def list_sshkeys(auth_client, customer_uuid):
    sf = auth_client.factory.create('searchFilter')
    fc1 = auth_client.factory.create('filterConditions')
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'customerUUID'
    fc1.value = customer_uuid
    sf.filterConditions.append(fc1)
    key_result_set = auth_client.service.listResources(searchFilter=None, resourceType='SSHKEY')
    print("SSHKEY for customer " + customer_uuid + " is:\n")
    print key_result_set
    print("\======== End SSHKey ==========\n")
    return key_result_set


def AddKey(auth_client, server_uuid, customerUUID, publicKey):

    print("AddKey Args: server:" + server_uuid + " customer: " + customerUUID + " publicKey:")
    print publicKey
    print("== end AddKey Args ==\n")


    key_ret = list_sshkeys(auth_client, customerUUID)


    # See how many keys are there extract number of Servers from result set
    create = True
    key_item_uuid = ""
    if (key_ret.totalCount == 0):
      msg = "No Key found for Customer with uuid " + customerUUID
      create = True
    else:
      # Key's exist; check if the one we are about to add is one of them
      print key_ret
      for x in range(0, key_ret.totalCount):
         print("---")
         print key_ret.list[x]
         print("----")
         if (key_ret.list[x].publicKey == publicKey):
            print "Customer already has key attached to their account"
            key_item_uuid = key_ret.list[x].resourceUUID
            create = False
         # else:
         #   print("Key" +  key_ret.list[x].resourceUUID + " does not match")

    # print key_result_set;
    # server_data = key_result_set.list[0]
    # print server_data
    # return server_data
    # print ret
    # print ("!!!!")

    if (create):
        print("===== Customer needs SSH key added =====")
        ssh_key = auth_client.factory.create('sshKey')
        ssh_key.publicKey = publicKey
        ssh_key.resourceType = 'SSHKEY'
        ssh_key.globalKey = False

        ssh_key.customerUUID = customerUUID
        print ssh_key;
        print("===========\n")

        add_ret = auth_client.service.createSSHKey(ssh_key)
        print add_ret
        key_item_uuid = add_ret.itemUUID

    # server_data = list_server(auth_client, server_uuid)
    # print server_data


    # Attach the key (be it existing or newly created) to the server

    attach_ret = auth_client.service.attachSSHKey(serverUUID=server_uuid, SSHKeyUUID=key_item_uuid)
    print attach_ret

    return attach_ret

def setup_image(auth_client, vdc_uuid):
    """Function to check for an image, if none set one up"""
    image_count = count_image(auth_client)
    if image_count == 0:
        image_uuid = fetch_image(image_client=auth_client, image_name=config.IMAGE_NAME,
             image_url=config.IMAGE_URL, image_user=config.IMAGE_USER,
             prod_offer_name=config.PROD_OFFER, vdc_uuid=vdc_uuid)
        wait_for_image(image_client=auth_client, image_uuid=image_uuid, status='ACTIVE')
    else:
        image_uuid = get_image_uuid(auth_client)

    return image_uuid

def get_prod_offer_uuid(server_client, prod_offer_name):
    """ Get product offer UUID when given product offer name """
    sf1 = server_client.factory.create('searchFilter')
#    print sf1
    # create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceState'
    fc1.value = 'ACTIVE'

    # debug print statement
#    print fc1
    sf1.filterConditions.append(fc1)
    fc2 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'resourceName'
    fc2.value = prod_offer_name
    sf1.filterConditions.append(fc2)

    # fc3 = server_client.factory.create('filterConditions')
    # set filter condition values
    # fc3.condition = 'IS_NOT_EQUAL_TO'
    # fc3.field = 'resourceType'
    # fc3.value = 'JOB'
    # sf1.filterConditions.append(fc3)

    print("Search Filter 1:")
    print(sf1)

    prod_offer_result_set = server_client.service.listResources(searchFilter=sf1)
    print("Prod_Offer_Result_Set:\n");
    print prod_offer_result_set
    prod_offer_result_set = server_client.service.listResources(searchFilter=sf1, resourceType="PRODUCTOFFER")

    prod_offer_uuid = prod_offer_result_set.list[0].resourceUUID
    print("Product Offer UUID for " + prod_offer_name + " is " + prod_offer_uuid)
    return prod_offer_uuid

def list_thingy(server_client, uuid, res_type):
    """ Get product offer UUID when given product offer name """
    sf1 = server_client.factory.create('searchFilter')
#    print sf1
    # create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = uuid
    # debug print statement
#    print fc1
    sf1.filterConditions.append(fc1)
    # set filter condition values
    print sf1
    result_set = server_client.service.listResources(searchFilter=sf1, resourceType=res_type)
    print result_set
    return result_set

def list_image(server_client, uuid):
    """ Get product offer UUID when given product offer name """
    sf1 = server_client.factory.create('searchFilter')
#    print sf1
    # create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = uuid
    # debug print statement
#    print fc1
    sf1.filterConditions.append(fc1)
    # set filter condition values
    print("=== Image Search filter ====")
    print sf1
    print("==========");
    result_set = server_client.service.listResources(searchFilter=sf1, resourceType="IMAGE")
    print("==== Result ====")
    print result_set
    print("=========");
    return result_set

def create_disk(server_client, prod_offer, disk_size, disk_name, vdc_uuid):
    """ Function to create disk """
    # get prod offer uuid
    prod_offer_uuid = get_prod_offer_uuid(server_client, prod_offer)
    # setup skeleton disk data structure
    skel_disk = server_client.factory.create('disk')
    skel_disk.resourceType = "DISK"
    skel_disk.productOfferUUID = prod_offer_uuid
    skel_disk.size = disk_size
    skel_disk.resourceName = disk_name
    skel_disk.resourceState = 'ACTIVE'
#    skel_disk.billingEntityUUID = be_uuid # is this needed ?
    skel_disk.vdcUUID = vdc_uuid
    disk_job = server_client.service.createDisk(skeletonDisk=skel_disk)
    disk_uuid = disk_job.itemUUID
    print("our newly created disk UUID=" + disk_uuid)
    list_thingy(server_client, disk_uuid, res_type="DISK")
    print("===========")
    return disk_uuid

def add_resource_key(auth_client, server_uuid, key_name, key_value, key_type, key_weight):
    print ("add_resource_key for server " + server_uuid + ": " + key_name + ":" + key_value)
    res_key = auth_client.factory.create('resourceKey')
    res_key.name = key_name
    res_key.type = key_type
    res_key.value = key_value
    res_key.weight = key_weight
    ret_val = auth_client.service.addKey(server_uuid, res_key)
    print "add_resource_key Return Value for server " + server_uuid + ": "
    print ret_val
    print "=========================================================="
    return ret_val


# Modified version of the one in server_ops
def create_server(server_client, customerUUID, prod_offer, image_uuid, server_name, vdc_uuid, ram_amount, cpu_count, disk_uuid, public_key, context_script):
    """ Create Server for customer """

    print "FCOMakeOrchestrator.py:create_server args:"
    print "customerUUID: " + customerUUID
    print "prod_offer: " + prod_offer
    print "image_uuid: " + image_uuid
    print "server_name: " + server_name
    print "vdc_uuid: " + vdc_uuid
    print "ram_amount: " + ram_amount
    print "cpu_count: " + str(cpu_count)
    print "disk_uuid: " + disk_uuid
    print "public_key: " + public_key
    print "context_script: " + context_script
    print "=== end FCOMakeOrchestrator.py:create_server args ==="

    # Find product offer UUID
    sf1 = server_client.factory.create('searchFilter')
    # create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceState'
    fc1.value = 'ACTIVE'

    sf1.filterConditions.append(fc1)
    fc2 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'resourceName'
    fc2.value = prod_offer
    sf1.filterConditions.append(fc2)
#    print sf1
    prod_offer_result_set = server_client.service.listResources(searchFilter=sf1, resourceType="PRODUCTOFFER")
    prod_offer_uuid = prod_offer_result_set.list[0].resourceUUID
    # Get cluster uuid
    cluster_result_set = server_client.service.listResources(resourceType="CLUSTER")
    cluster_uuid = cluster_result_set.list[0].resourceUUID
    # Get VDC uuid
    # if vdc_uuid == '':
    #    vdc_uuid = get_vdc_uuid(server_client)

    # Create server
    server_data = server_client.factory.create('server')
#    if inc_flag == 'TRUE':
#        server_data.resourceName = server_name + " " + str(server_inc)
#    else:
    server_data.resourceName = server_name
    server_data.productOfferUUID = prod_offer_uuid
    server_data.imageUUID = image_uuid
    server_data.clusterUUID = cluster_uuid
    server_data.vdcUUID = vdc_uuid
    server_data.cpu = cpu_count
    server_data.ram = ram_amount  # '512'
    disk_data = server_client.factory.create('disk')
    disk_data.resourceUUID = disk_uuid
    disk_data.resourceType = "DISK"
    disk_data.vdcUUID = vdc_uuid
    print("Disk Data:")
    print(disk_data)
    print("Server Data:")
    print(server_data)
    # server_data.disks[0] = disk_data
    disk_result = list_thingy(server_client, disk_uuid, res_type="DISK")
    # Need somne validation here because failures go undetected
    print("disky result=")
    print(disk_result)
    server_data.disks = disk_result.list[0]
    print server_data
    # disk_data.size = 20
    # How to add a second disk ?
    # server_data.disk[0].resourceUUID = disk_uuid

    # Metadata.
    print "\n context_script being fed in to server_data.resourceMetadata.publicMetadata is:\n"
    print context_script
    server_data.resourceMetadata.publicMetadata = context_script
    print "\n"

    print "--- server data ----"
    print server_data
    create_server_jobid = server_client.service.createServer(server_data)
#    print create_server_jobid

    server_uuid = create_server_jobid.itemUUID
    print "--- createServer done with UUID " + server_uuid + " -----"

    print("public_key = " + public_key)
    add_ret = AddKey(server_client, server_uuid, customerUUID, public_key)
    print("== AddKey Result ==")
    print add_ret
    print("====")
    # add_resource_key(server_client, server_uuid, "__#CloudInit","#!/bin/bash\ntouch /tmp/xxx\n","USER_KEY",0)

    # Metadata. Can only add it here once we know the server uuid
    # md = server_client.factory.create('resourceMetadata')
    # md.resourceUUID = server_uuid
    # md.publicMetadata = "This is public - set during create" + context_script
    # result = server_client.service.updateMetadata(server_uuid,md)
    # print "=== METADATA RESULT ==="
    # print result
    # print "======================="

    return server_uuid


def build_server(auth_client, customer_uuid, image_uuid, vdc_uuid, prod_offer, server_name, ram_amount, cpu_count, disk_uuid, public_key, context_script):
    """Function to create a server"""
    print "in build_server using image " + image_uuid
    server_uuid = create_server(server_client=auth_client, customerUUID=customer_uuid,
                                prod_offer=prod_offer,
                                image_uuid=image_uuid, vdc_uuid=vdc_uuid, server_name=server_name,
                                ram_amount=ram_amount, cpu_count=cpu_count,
                                disk_uuid=disk_uuid, public_key=public_key,
                                context_script=context_script)
    wait_for_install(server_client=auth_client, server_uuid=server_uuid)
    print "Calling create_nic for network " + config.NETWORK_TYPE
    nic_uuid = create_nic(server_client=auth_client, nic_count='0', network_type=config.NETWORK_TYPE, vdc_uuid=vdc_uuid)
    print "create_nic returned nic_uuid: " + nic_uuid
    wait_for_resource(res_client=auth_client, res_uuid=nic_uuid, state='ACTIVE', res_type='NIC')
    print "nic uuid: " + nic_uuid
#    add_ip(server_client=auth_client, nic_uuid=nic_uuid)
    add_nic_to_server(server_client=auth_client, server_uuid=server_uuid, nic_uuid=nic_uuid, index='1')
    time.sleep(30)  # Give nic time to add
    server_resultset = list_resource(res_client=auth_client,
    res_uuid=server_uuid, res_type='SERVER')
#    print server_resultset
    server_uuid = server_resultset.list[0].resourceUUID
    server_pw = server_resultset.list[0].initialPassword
    server_user = server_resultset.list[0].initialUser
#    server_ip = server_resultset.list[0].nics[0].ipAddresses[0].ipAddress
    server_data = [server_uuid, server_pw, server_user]
    return server_data

def start_server(auth_client, server_data):
    """Function to start server, uuid in server_data"""
    server_uuid = server_data[0]
    server_state = get_server_state(auth_client, server_uuid)
    if server_state == 'STOPPED':
        change_server_status(server_client=auth_client, server_uuid=server_uuid, state='RUNNING')
        wait_for_server(server_client=auth_client, server_uuid=server_uuid, status='RUNNING')
        time.sleep(30)  # let server become fully active
    server_resultset = get_server_data(server_client=auth_client, server_uuid=server_uuid)
    server_ip = server_resultset.list[0].nics[0].ipAddresses[0].ipAddress
    server_data.append(server_ip)
    return server_data


def stop_server(auth_client, server_data):
    """Function to stop server, uuid provided in server data"""
    server_uuid = server_data[0]
    change_server_status(server_client=auth_client, server_uuid=server_uuid, state='STOPPED')
    wait_for_server(server_client=auth_client, server_uuid=server_uuid, status='RUNNING')
    server_state = get_server_state(auth_client, server_uuid)
    return server_state


def upload_file(server_data):
    """Function to log into server and download file"""
    server_uuid = server_data[0]
    server_pw = server_data[1]
    server_user = server_data[2]
    server_ip = server_data[3]
    srv = pysftp.Connection(username=server_user, password=server_pw, host=server_ip)
    ts = time.time()
    tstamp1 = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print "Start file transfer: " + tstamp1
    srv.put(LOCAL_FILE)
    srv.close
    ts = time.time()
    tstamp2 = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print "Complete file transfer: " + tstamp2


def assert_billing(auth_client):
    """Function to check the billing for the downloaded files."""
    billing_results = list_unit_transactions(auth_client)
    print billing_results
    return billing_results



def MakeVM(image_uuid, customerUUID, customerUsername, customerPassword, endpoint, networkType,
           diskSize, ramAmount, cpuCount, public_key, isVerbose=False, contextScript=None):
    """Main Function"""

    # Actually just defines the global variables now (since all config bits are passed on the command line)
    config.get_config("")
    print("MakeVM: publicKey=" + public_key)
    config.CUST_UUID = customerUUID
    config.USER_LOGIN = customerUsername
    config.USER_PASSWORD = customerPassword
    config.HOST_NAME = endpoint
    config.NETWORK_TYPE = networkType

    # Does this need to be parameterised, or picked up by some other means ?
    config.PROD_OFFER = 'Generic Disk'

    print("MakeVM() args:\n")
    print(config.CUST_UUID)
    print(config.USER_LOGIN)
    print(config.USER_PASSWORD)
    print(config.HOST_NAME)
    print(config.NETWORK_TYPE)
    print("Memory (ramAmount):" + ramAmount)
    print("NumCPU (cpuCount):" + cpuCount)
    print("=-=-=-=-=-=-\n")
    # See what SlipStream is passing us by way of environment variables
    print("SlipStream environment:\n")
    for param in os.environ.keys():
        print "%20s %s" % (param, os.environ[param])
    print("=-=-=-=-=-=-\n")

    # ignore setup.ini as we get all the args via the command line


    auth_client = setup_test()
    vdc_uuid = setup_vdc(auth_client, 'VDC One')

    if (isVerbose):
        print "Default VDC: " + vdc_uuid

    # image_uuid = setup_image(auth_client=auth_client, vdc_uuid=vdc_uuid)
    # Utilmately, We'll pass this in from SlipStream
    # image_uuid = '99f2c947-cf15-3479-8ef5-a7bb9e4ae1e3'
    if (isVerbose):
        print("Details for image_uuid " + image_uuid + ":\n");

    img_ret = list_image(auth_client, image_uuid)
    vdc_uuid = img_ret.list[0].vdcUUID
    print("Image resides in VDC " + vdc_uuid + " so we will use that one")

    product_offer = 'Standard Server'
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    server_name = "Server " + current_time
    disk_name = "Disk 1: " + current_time

    # Generic Disk is what the product is called in v4. SD1 is still on v3.1.x, so we
    # need to use 'Standard Disk'
    # disk_uuid = create_disk(auth_client,'Generic Disk','20',disk_name,vdc_uuid)

    # Don't actually need to create a disk, as the image gets cloned and a new disk
    # is created from that, but the fact the disk we create here exists is relied on
    # by lower level code, so until that is cleaned up, leave this in place
    disk_uuid = create_disk(auth_client, 'Standard Disk', '20', disk_name, vdc_uuid)

    server_data = build_server(auth_client=auth_client, customer_uuid=customerUUID, image_uuid=image_uuid,
                               vdc_uuid=vdc_uuid, prod_offer=product_offer, server_name=server_name,
                               ram_amount=ramAmount, cpu_count=cpuCount,
                               disk_uuid=disk_uuid, public_key=public_key,
                               context_script=contextScript)

    if (isVerbose):
        print "Return from build_server() is:"
        print server_data
        print "==== End build_server() details ===="

    server_data = start_server(auth_client, server_data)

    # This is the string that SlipStream picks up to let it know that the launch has been
    # successful. Don't change it unless you also amend FCOConnector. The statement below will
    # yield a line like:
    # Server UUID and IP:6885959f-c53e-3b7d-aac2-4ff4b4327620:AAb5XUn6niUmQih9:ubuntu:109.231.122.249
    #
    # print "Server UUID and IP:"  +  ':'.join(server_data)
    print("server_data[0]=" + server_data[0]);
    print("server_data[1]=" + server_data[1]);
    print("server_data[2]=" + server_data[2]);
    print("server_data[3]=" + server_data[3]);

    # ret = "Server UUID and IP:"  +  ':'.join(server_data)

    # bodge to remove the (unused) disk we seem to have to have created
    print "Cleaning up disk" + disk_uuid
    auth_client.service.deleteResource(resourceUUID=disk_uuid, cascade=False)

    ret = dict(server_uuid=server_data[0],
             ip=server_data[3],
             password=server_data[1],
             login=server_data[2]
            )

    print ret
    return ret

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--image-id', dest='imageId', nargs='*',
                        help="The UUID of the Image")

    parser.add_argument('--cust-uuid', dest='customerUUID', nargs='*',
                        help="The UUID of the Customer")

    parser.add_argument('--cust-username', dest='customerUsername', nargs='*',
                        help="The Username of the Customer")

    parser.add_argument('--cust-password', dest='customerPassword', nargs='*',
                        help="The password for the Customer")

    parser.add_argument('--api-host', dest='endpoint', nargs='*',
                        help="Where the API lives")

    parser.add_argument('--context', dest='contextScript', nargs='*',
                        help="Context Script")

    parser.add_argument('--network-type', dest='networkType', nargs='*',
                        help="Network type")

    parser.add_argument('--verbose', dest='isVerbose', action='store_true',
                            help="Whether to print diagnostics as we go")

    parser.add_argument('--disk-size', dest='diskSize', nargs='*',
                            help="Disk size in GB")

    parser.add_argument('--cpu-count', dest='cpuCount', nargs='*',
                            help="Number of CPUs")

    parser.add_argument('--ram', dest='ramAmount', nargs='*',
                            help="RAM")

    parser.add_argument('--public-key', dest='publicKey', nargs='*',
                            help="SSH Public Key")

    cmdargs = parser.parse_args()

    # print cmdargs.imageId
    # print  cmdargs.imageId[0]

    image_uuid = cmdargs.imageId[0]

    isVerbose = cmdargs.isVerbose

    ret = MakeVM(cmdargs.imageId[0],
               cmdargs.customerUUID[0],
               cmdargs.customerUsername[0],
               cmdargs.customerPassword[0],
               cmdargs.endpoint[0],
               cmdargs.networkType[0],
               cmdargs.diskSize[0],
               cmdargs.ramAmount[0],
               cmdargs.cpuCount[0],
               cmdargs.publicKey[0],
               isVerbose,
               cmdargs.contextScript[0])

    print "FCOMakeOrchestrator(): ret is" + str(ret)
    out = "Server UUID and IP:" + ret['server_uuid']
    out = out + ":" + ret['password']
    out = out + ":" + ret['login']
    out = out + ":" + ret['ip']
    print out
