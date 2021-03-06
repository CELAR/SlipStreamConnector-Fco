#!/usr/bin/python
#
#

import os
import sys
import socket
import errno

sys.path.insert(1, '.')

import slipstream.exceptions.Exceptions as Exceptions

from packages.fco_rest import add_nic_to_server
from packages.fco_rest import attach_disk
from packages.fco_rest import attach_ssh_key
from packages.fco_rest import change_server_status
from packages.fco_rest import create_nic
from packages.fco_rest import create_sshkey
from packages.fco_rest import create_vdc
from packages.fco_rest import getToken
from packages.fco_rest import get_first_vdc_in_cluster
from packages.fco_rest import get_prod_offer_uuid
from packages.fco_rest import get_server_state
from packages.fco_rest import list_image
from packages.fco_rest import list_resource_by_uuid
from packages.fco_rest import list_sshkeys
from packages.fco_rest import rest_create_disk
from packages.fco_rest import rest_create_server
from packages.fco_rest import wait_for_install
from packages.fco_rest import wait_for_job
from packages.fco_rest import wait_for_resource
from packages.fco_rest import get_prod_offer
from packages.fco_rest import modify_cpu_ram

import config
import argparse
import datetime
import time

def create_vdc_in_cluster(auth, cluster_uuid):
    """ Create VDC for customer """
    ts = time.time()
    vdc_name = "VDC " + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    vdc_ret = create_vdc(auth, cluster_uuid, vdc_name)

    print("=== VDC Creation job ===")
    print vdc_ret
    print("========================")

    return vdc_ret['itemUUID']

def AddKey(auth_parms, server_uuid, customerUUID, publicKey):

    print("AddKey Args: server:" + server_uuid + " customer: " + customerUUID + " publicKey:")
    print publicKey
    print("== end AddKey Args ==\n")

    key_ret = list_sshkeys(auth_parms, customerUUID)

    # See how many keys are there extract number of Servers from result set
    create = True
    key_item_uuid = ""
    if (key_ret['totalCount'] == 0):
      create = True
    else:
      # Key's exist; check if the one we are about to add is one of them
      print key_ret
      for x in range(0, key_ret['totalCount']):
         print("---")
         print key_ret['list'][x]
         print("----")
         if (key_ret['list'][x]['publicKey'] == publicKey):
            print "Customer already has key attached to their account"
            key_item_uuid = key_ret['list'][x]['resourceUUID']
            create = False
         # else:
         #   print("Key" +  key_ret.list[x].resourceUUID + " does not match")

    if (create):
        print("===== Customer needs SSH key added =====")
        public_key_name = ''
        add_ret = create_sshkey(auth_parms, publicKey, public_key_name)
        print add_ret
        key_item_uuid = add_ret['itemUUID']


    # Attach the key (be it existing or newly created) to the server
    attach_ret = attach_ssh_key(auth_parms, server_uuid=server_uuid, sshkey_uuid=key_item_uuid)
    print attach_ret

    return attach_ret

def validate_ram_cpu_size(auth_parms, prod_offer, cpu_size, ram_size):
    # Check if the cpu and ram input is negative
    if ((int(cpu_size) <= 0) or ((int(ram_size) <= 0))):
        raise Exceptions.ExecutionException("CPU and RAM amount should be greater than 0")

    prod_offer = get_prod_offer(auth_parms, prod_offer)
    prod_component = prod_offer['componentConfig']
    print prod_component

    prod_conf_cpu = prod_component[0]['productConfiguredValues']
    validator_cpu = prod_conf_cpu[0]
    validateString_cpu = validator_cpu['validator']['validateString']
    validateStringList_cpu = validateString_cpu.split("-")

    print 'Valid CPU Core for product offer: '
    print validateString_cpu

    cpu_allowed = False
    # For the Standard disk PO the validateString returned is: 1-10.
    # Validation will fail if the format changes.
    if (int(cpu_size) >= int(validateStringList_cpu[0]) and int(cpu_size) <= int(validateStringList_cpu[1])):
        cpu_allowed = True

    if (cpu_allowed != True):
        raise Exceptions.ExecutionException("Invalid disk size for the product offer. Valid Disk sizes: %s" %validateString_cpu)

    prod_conf_ram = prod_component[1]['productConfiguredValues']
    validator_ram = prod_conf_ram[0]
    validateString_ram = validator_ram['validator']['validateString']
    validateStringList_ram = validateString_ram.split(",")

    print 'Valid RAM amount for product offer: '
    print validateString_ram

    ram_allowed = False
    for size in validateStringList_ram:
        if (int(size) == int(ram_size)):
                ram_allowed = True

    if (ram_allowed != True):
        raise Exceptions.ExecutionException("Invalid disk size for the product offer. Valid Disk sizes: %s" %validateString_ram)


def resize_cpu_ram(auth_parms, vm_uuid, serverName, clusterUUID, vdcUUID, cpu, ram):
    """ Function to resize the server """
    product_offer = 'Standard Server'
    server_po_uuid = get_prod_offer_uuid(auth_parms, product_offer)

    if (server_po_uuid == ""):
        raise Exceptions.ExecutionException("No '" + product_offer + "' Product Offer found")

    if(server_po_uuid != ""):
        # Modify the server
        modify_cpu_ram(auth_parms, vm_uuid, serverName, clusterUUID, vdcUUID, cpu, ram, server_po_uuid)


def validate_disk_size(auth_parms, prod_offer, disk_size, disk_name, vdc_uuid):
    prod_offer = get_prod_offer(auth_parms, prod_offer)
    prod_component = prod_offer['componentConfig']
    print prod_component

    prod_conf = prod_component[0]['productConfiguredValues']
    validator = prod_conf[0]
    validateString = validator['validator']['validateString']
    validateStringList = validateString.split(",")

    print 'Valid Disk Size for product offer: '
    print validateString

    allowed = False
    for size in validateStringList:
        if (int(size) == disk_size):
                allowed = True

    if (allowed != True):
        raise Exceptions.ExecutionException("Invalid disk size for the product offer. Valid Disk sizes: %s" %validateString)

def create_disk(auth_parms, prod_offer, disk_size, disk_name, vdc_uuid):
    """ Function to create disk """

    # get product offer uuid for the disk in question
    prod_offer_uuid = get_prod_offer_uuid(auth_parms, prod_offer)

    disk_job = rest_create_disk(auth_parms, vdc_uuid, prod_offer_uuid, disk_name, disk_size)

    disk_uuid = disk_job['itemUUID']
    print("our newly created disk UUID=" + disk_uuid)

    # Check the job completes
    status = wait_for_job(auth_parms, disk_job['resourceUUID'], "SUCCESSFUL", 90)
    if (status != 0):
        raise Exceptions.ExecutionException("Failed to add create disk (uuid=" + disk_uuid + ")")

    return disk_uuid
#

def build_server(auth_parms, customer_uuid, image_uuid, vdc_uuid, server_po_uuid, boot_disk_po_uuid,
                server_name, ram_amount, cpu_count, networkType, cluster_uuid, public_key, context_script):
    """Function to create a server"""

    print "FCOMakeOrchestrator.py:build_server args:"
    print "customer_uuid: " + customer_uuid
    print "image_uuid: " + image_uuid
    print "cluster_uuid: " + cluster_uuid
    print "vdc_uuid: " + vdc_uuid
    print "server_po_uuid: " + server_po_uuid
    print "boot_disk_po_uuid:" + boot_disk_po_uuid,
    print "server_name: " + server_name
    print "ram_amount: " + ram_amount
    print "cpu_count: " + str(cpu_count)
    print "public_key: " + public_key
    print "context_script: " + context_script
    print "=== end FCOMakeOrchestrator.py:build_server args ==="


    create_server_job = rest_create_server(auth_parms, server_name, server_po_uuid, image_uuid,
                                             cluster_uuid, vdc_uuid, cpu_count,
                                             ram_amount, boot_disk_po_uuid, context_script)
#    print create_server_jobid

    server_uuid = create_server_job['itemUUID']
    print "--- createServer done with UUID " + server_uuid + " -----"


    print("public_key = " + public_key)
    #
    # The public_key arg might be a list of public keys, separated by cr/lf. So split
    # the list and process each key individually
    for single_key in public_key.splitlines():
        print("Processing key: " + single_key)
        add_ret = AddKey(auth_parms, server_uuid, customer_uuid, single_key)
        print("== AddKey Result ==")
        print add_ret
        print("====")

    wait_for_install(auth_parms, server_uuid=server_uuid)

    # Add NIC to server
    print "Calling create_nic for network " + networkType
    nic_uuid = create_nic(auth_parms=auth_parms, nic_count='0', network_type=networkType,
                          cluster_uuid=cluster_uuid, vdc_uuid=vdc_uuid)
    print "create_nic returned nic_uuid: " + nic_uuid
    wait_for_resource(auth_parms=auth_parms, res_uuid=nic_uuid, state='ACTIVE', res_type='nic')
    print "nic uuid: " + nic_uuid

    add_nic_response = add_nic_to_server(auth_parms=auth_parms, server_uuid=server_uuid, nic_uuid=nic_uuid, index='1')

    # Wait on the addNic job completing
    status = wait_for_job(auth_parms, add_nic_response['resourceUUID'], "SUCCESSFUL", 90)
    if (status != 0):
        raise Exceptions.ExecutionException("Failed to add NIC to server")

    # Lookup server properties to get UUID, and password, that have been assigned to it
    server_resultset = list_resource_by_uuid(auth_parms, uuid=server_uuid, res_type='SERVER')
    server = server_resultset['list'][0]

#    print server_resultset
    server_uuid = server['resourceUUID']
    server_pw = server['initialPassword']
    server_user = server['initialUser']
#    server_ip = server_resultset.list[0].nics[0].ipAddresses[0].ipAddress
    server_data = [server_uuid, server_pw, server_user]
    return server_data

def is_ssh_port_open(server_ip, max_wait):
#    cli=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ok = 0
    poll_interval = 5
    limit = max_wait / poll_interval  # number of times to retry (approximately)
    while ok == 0 and limit > 0:
        try:
            s = socket.create_connection((server_ip, 22), poll_interval)
            s.close()
            ok = 1
            print str(time.time()) + " Connected\n"
#        except socket.timeout, msg:
#            print "zzzz:" + str(msg)

        except socket.error, msg:
            limit = limit - 1
            print str(time.time()) + " fail: '" + str(msg[0]) + "'"  # + " " + msg[1]
            # ECONNREFUSED is good, because it means the machine is likely on it's way up. Of course,
            # that could be the permanent state of affairs, but we only care if the machine is booted
            # - by the time the real connection happens, ssh should be in a state where it can accept
            # connections.
            if (str(msg[0]) == str(errno.ECONNREFUSED)):
               ok = 1

    print("SSH probe complete with " + str(limit) + " tries left (ok=" + str(ok) + ")")

def start_server(auth_parms, server_data):
    """Function to start server, uuid in server_data"""
    server_uuid = server_data[0]
    server_state = get_server_state(auth_parms, server_uuid)
    if server_state == 'STOPPED':
        rc = change_server_status(auth_parms=auth_parms, server_uuid=server_uuid, state='RUNNING')
        # change_server_status() waits on the server getting to the requested state, so we don't
        # need to call wait_for_server() here. However, we do (1) need to check the status and (2)
        # wait on the server actually being accessible (as opposed to having a RUNNING state in
        # FCO, which really just means that the underlying kvm process has started).
        #
        # 1. Check rc (0 is good)
        if (rc != 0):
            raise Exceptions.ExecutionException("Failed to put server " + server_uuid + " in to running state")


    server_resultset = list_resource_by_uuid(auth_parms, uuid=server_uuid, res_type='SERVER')
    print("Server result set is:")
    print server_resultset

    server_ip = server_resultset['list'][0]['nics'][0]['ipAddresses'][0]['ipAddress']  # yuk
    print("server IP=" + server_ip)

    # Step 2. Wait on it being accessible. It is possible that the server doesn't have ssh installed,
    # or it is firewalled, so don't fail here if we can't connect, just carry on and let
    # the caller deal with any potential issue. The alternative is a hard-coded sleep, or
    # trying a ping (platform specific and/or root privs needed).
    is_ssh_port_open(server_ip, 30)

    server_data.append(server_ip)
    return server_data

def MakeVM(image_uuid, customerUUID, customerUsername, customerPassword, endpoint, networkType,
           extra_disk_size, ramAmount, vmName, cpuCount, public_key, isVerbose=False, contextScript=None):
    """Main Function"""

    # Actually just defines the global variables now (since all config bits are passed on the command line)
    config.get_config("")
    config.CUST_UUID = customerUUID
    config.USER_LOGIN = customerUsername
    config.USER_PASSWORD = customerPassword
    config.HOST_NAME = endpoint
    config.NETWORK_TYPE = networkType

    # Does this need to be parameterised, or picked up by some other means ?
    config.PROD_OFFER = 'Generic Disk'

    if (isVerbose):
        print("MakeVM() args:\n")
        print(config.CUST_UUID)
        print(config.USER_LOGIN)
        print(config.USER_PASSWORD)
        print(config.HOST_NAME)
        print(config.NETWORK_TYPE)
        print("MakeVM: publicKey=" + public_key)
        print("Memory (ramAmount):" + ramAmount)
        print("NumCPU (cpuCount):" + cpuCount)
        print("extra_disk_size: " + str(extra_disk_size))
        print("=-=-=-=-=-=-\n")
        # See what SlipStream is passing us by way of environment variables
        print("SlipStream environment:\n")
        for param in os.environ.keys():
            print "%20s %s" % (param, os.environ[param])
        print("=-=-=-=-=-=-\n")

    # Authenticate to the FCO API, getting a token for furture use
    token = getToken(endpoint, customerUsername, customerUUID, customerPassword)

    auth = dict(endpoint=endpoint, token=token)


    print("Details for image_uuid " + image_uuid + ":\n");

    img_ret = list_image(auth, image_uuid)
    vdc_uuid_for_image = img_ret['vdcUUID']
    # if (isVerbose):
    print("vdc_uuid_for_image is " + vdc_uuid_for_image)

    cluster_uuid_for_image = img_ret['clusterUUID']
    print("cluster_uuid_for_image is " + cluster_uuid_for_image)

    customer_vdc_uuid = get_first_vdc_in_cluster(auth, cluster_uuid_for_image)
    # if (isVerbose):
    print("The VDC to use is: " + customer_vdc_uuid)

    # Setup VDC in this cluster if user doesn't have one
    if (customer_vdc_uuid == ''):
        vdc_uuid = create_vdc_in_cluster(auth, cluster_uuid_for_image)
        if (isVerbose):
            print("VDC we created is " + vdc_uuid)
        customer_vdc_uuid = vdc_uuid

    # Sanity check that we have a VDC to work with
    if (customer_vdc_uuid == ''):
       raise Exceptions.ExecutionException("No VDC to create the server in !")

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    if vmName == None:
        server_name = "VM " + current_time
    else:
        server_name = vmName

    # Get the Product Offer UUID of the Standard Server product
    product_offer = 'Standard Server'
    server_po_uuid = get_prod_offer_uuid(auth, product_offer)
    if (server_po_uuid == ""):
        raise Exceptions.ExecutionException("No '" + product_offer + "' Product Offer found")

    # Base the boot disk on the PO of the same size storage disk as the Image must have been; that way
    # we can be reasonably sure it will exist.
    image_disk_po_name = str(img_ret['size']) + " GB Storage Disk"
    boot_disk_po_uuid = get_prod_offer_uuid(auth, image_disk_po_name)
    if (boot_disk_po_uuid == ""):
        raise Exceptions.ExecutionException("No suitable disk product offer found  (expected a '" + image_disk_po_name + "' PO)")

    # Create the additional disk (if any). We'll attach it later.
    disk_name = "Disk " + current_time + " #2"
    print("extra_disk_size = " + str(extra_disk_size))
    extra_disk_uuid = ""
    if (int(extra_disk_size) > 0):
        print("Creating additional volatile disk")
        extra_disk_uuid = create_disk(auth, 'Standard Disk', extra_disk_size, disk_name, customer_vdc_uuid)


    server_data = build_server(auth_parms=auth, customer_uuid=customerUUID,
                               image_uuid=image_uuid,
                               vdc_uuid=customer_vdc_uuid,
                               server_po_uuid=server_po_uuid, boot_disk_po_uuid=boot_disk_po_uuid,
                               server_name=server_name,
                               ram_amount=ramAmount, cpu_count=cpuCount,
                               networkType=networkType,
                               cluster_uuid=cluster_uuid_for_image,
                               public_key=public_key,
                               context_script=contextScript)

    if (isVerbose):
        print "Return from build_server() is:"
        print server_data
        print "==== End build_server() details ===="


    # If we created an extra disk, attach it now
    if (extra_disk_uuid != ""):
        attach_disk(auth_parms=auth, server_uuid=server_data[0], disk_uuid=extra_disk_uuid, index='2')

    server_data = start_server(auth_parms=auth, server_data=server_data)

    # This is the string that SlipStream picks up to let it know that the launch has been
    # successful. Don't change it unless you also amend FCOConnector. The statement below will
    # yield a line like:
    # Server UUID and IP:6885959f-c53e-3b7d-aac2-4ff4b4327620:AAb5XUn6niUmQih9:ubuntu:109.231.122.249
    #
    # print "Server UUID and IP:"  +  ':'.join(server_data)
    if (isVerbose):
        print("server_data[0]=" + server_data[0]);
        print("server_data[1]=" + server_data[1]);
        print("server_data[2]=" + server_data[2]);
        print("server_data[3]=" + server_data[3]);

    # ret = "Server UUID and IP:"  +  ':'.join(server_data)

    ret = dict(server_uuid=server_data[0],
             ip=server_data[3],
             password=server_data[1],
             login=server_data[2]
            )

    if (isVerbose):
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

    parser.add_argument('--vm-name', dest='vmName', nargs='*',
                                help="What to call the VM")

    cmdargs = parser.parse_args()

    # print cmdargs.imageId
    # print  cmdargs.imageId[0]

    image_uuid = cmdargs.imageId[0]

    isVerbose = cmdargs.isVerbose

    # if (isVerbose):
    #    # We can turn on debugging by explicitly importing http_client and setting it's debug level
    #    try:
    #        import http.client as http_client
    #    except ImportError:
    #    # Python 2
    #        import httplib as http_client
    #
    #    http_client.HTTPConnection.debuglevel = 1

    ret = MakeVM(cmdargs.imageId[0],
               cmdargs.customerUUID[0],
               cmdargs.customerUsername[0],
               cmdargs.customerPassword[0],
               cmdargs.endpoint[0],
               cmdargs.networkType[0],
               cmdargs.diskSize[0],
               cmdargs.ramAmount[0],
               cmdargs.vmName[0],
               cmdargs.cpuCount[0],
               cmdargs.publicKey[0],
               isVerbose,
               cmdargs.contextScript[0])

    # print "FCOMakeOrchestrator(): ret is" + str(ret)
    # out = "Server UUID and IP:" + ret['server_uuid']
    # out = out + ":" + ret['password']
    # out = out + ":" + ret['login']
    # out = out + ":" + ret['ip']
    # print out


