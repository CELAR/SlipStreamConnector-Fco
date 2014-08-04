""" UserAPI test script executed per user """
# This script manages the calling of the specific userAPI test functions
# e.g. creating VDC, servers etc.
# This script will check that the customer has a VDC, images and servers
# If any of theses items are missing they will be created
# Once all these items are available the script will run for a number of iterations
# each iteration a random activity will be activated (e.g. start server)

# import functions from suds
from suds.client import Client
from suds.transport.https import HttpAuthenticated

# import functions from random
import random

# test suite scripts
import user_auth
import vdc_ops
import image_ops
import server_ops
import resource_ops

# constants for VDC
MAIN_VDC_NAME = "test vdc"

#Constants for image
IMAGE_NAME = "Ubuntu 10.04 KVM"
IMAGE_URL = "http://repo.flexiant.com/images/private/kvm/ubuntu10.04.img.gz"
IMAGE_USER = "ubuntu"
IMAGE_LOGIN = "a-valid-user"
IMAGE_PW = "secret"
IMAGE_DISK_PROD_OFFER = '20 GB Image Disk'
#Constants for Server
PROD_OFFER = "0.5 GB / 1 CPU"
SERVER_NAME = "Server"

def pick_a_server(pick_client):
    """ Function to randomly select an existing server and action a random event """
    # pick a server
    server_count = server_ops.count_server(pick_client)
    # pick an action
    server_selected = random.randint(1,server_count)
    server_uuid = server_ops.get_server_uuid(pick_client,server_selected)
    server_name = server_ops.get_server_name(pick_client,server_uuid)
    server_status = server_ops.get_server_state(pick_client, server_uuid)
    print "server name: "+ server_name
    if server_status == "STOPPED":
        #     if server stopped then
        server_action = random.randint(1,6)
        if server_action == 1:
            #         start server
            print "option 1 start server"
            server_ops.change_server_status(pick_client, server_uuid, "RUNNING")
        if server_action == 2:
            #         delete server
            print "option 2 delete server"
            resource_ops.delete_resource(pick_client, server_uuid, True)
            resource_ops.wait_for_resource_delete(pick_client, server_uuid)
        if server_action == 3:
            #         add a disk
            print "option 3 add a disk"
        if server_action == 4:
            #         detach a disk
            print "option 4 detach a disk"
        if server_action == 5:
            #         add a nic
            print "option 5 add a nic"
        if server_action == 6:
            #         remove a nic
            print "option 6 remove a nic"
    elif server_status == "RUNNING":
            #     if server started then
            #         stop server 5-B-1
            print "option stop server"
            server_ops.change_server_status(pick_client, server_uuid, "STOPPED")
    else:
         print "Untested state"


def wait_for_server_install(wait_client, server_uuid):
        server_created = server_ops.wait_for_install(wait_client, server_uuid)
        if server_created == 1:
            print "Problem installing server, check platform."
        else:
            print "server installed ok."
        return server_created


def user_test_main(main_creds):
    # authenticate
#    print main_creds
    main_client = user_auth.auth(main_creds)
#    print main_client
    #start testing
    vdc_count = vdc_ops.count_vdc(main_client)
    if vdc_count > 0:
        print "VDC check ok : " + str(vdc_count) + " VDC(s)"
    else:
        print "No VDCs : " + str(vdc_count) + " VDC(s)"
        vdc_uuid = vdc_ops.create_vdc(vdc_client=main_client,
        vdc_count=vdc_count, vdc_name=MAIN_VDC_NAME)
    image_count = image_ops.count_image(main_client)
    if image_count > 0:
        print "Image check ok : " + str(image_count) + " image(s)"
    else:
        print "No Images : " + str(image_count) + " image(s)"
        image_ops.fetch_image(image_client=main_client, image_count=image_count, image_name=IMAGE_NAME, image_url=IMAGE_URL,
             image_user=IMAGE_USER, image_login=IMAGE_LOGIN, image_pw=IMAGE_PW, prod_offer_name=IMAGE_DISK_PROD_OFFER, vdc_uuid=vdc_uuid)
    server_count = server_ops.count_server(main_client)
    if server_count > 0:
        print "Server check ok : " + str(server_count) + " server(s)"
    else:
        print "No Servers : " + str(server_count) + " server(s)"
        image_inc = image_count + 1
#        image_search = IMAGE_NAME + " " + str(image_inc)
        image_search = ""
        image_uuid = image_ops.get_image_uuid(main_client, image_search)
#        print "image UUID: " + image_uuid
        server_uuid = server_ops.create_server(server_client=main_client, server_count=server_count,
        prod_offer=PROD_OFFER, image_uuid=image_uuid, server_name=SERVER_NAME)
        print "Server created: " + server_uuid
        create_return = wait_for_server_install(main_client, server_uuid)
    # Start doing some random activities, if the number of options increase,
    # so should the random range
#    rnd_option =  random.randint(1,10)
    rnd_option = 4
    if rnd_option == 1:
        print"Create new VDC"
        vdc_count = vdc_ops.count_vdc(main_client)
        vdc_uuid = vdc_ops.create_vdc(main_client, vdc_count, MAIN_VDC_NAME)
    elif rnd_option == 2:
        print "Add a new image"
        vdc_count = vdc_ops.count_vdc(main_client)
        rnd_val = random.randint(1, vdc_count)
        vdc_list = resource_ops.list_resource_type(main_client, "VDC")
        vdc_uuid = vdc_list.list[rnd_val].resourceUUID
        image_count = image_ops.count_image(main_client)
        image_ops.fetch_image(main_client, image_count, IMAGE_NAME, IMAGE_URL,
             IMAGE_USER, IMAGE_LOGIN, IMAGE_PW, IMAGE_DISK_PROD_OFFER, vdc_uuid)
    elif rnd_option == 3:
        print "Add a new network"
        print "option 3 new network"
    elif rnd_option == 4:
        print "Add a new server"
        image_count = image_ops.count_image(main_client)
#        image_search = IMAGE_NAME + " " + str(image_count)
        image_search = ""
        image_uuid = image_ops.get_image_uuid(main_client, image_search)
        server_count = server_ops.count_server(main_client)
        server_uuid = server_ops.create_server(server_client=main_client, server_count=server_count,
             prod_offer=PROD_OFFER, image_uuid=image_uuid, server_name=SERVER_NAME)
        create_return = wait_for_server_install(main_client, server_uuid)
    elif rnd_option >= 5 and rnd_option <= 10:
        print "Use existing server"
        pick_a_server(main_client)
    else:
        print "option out of bounds"




