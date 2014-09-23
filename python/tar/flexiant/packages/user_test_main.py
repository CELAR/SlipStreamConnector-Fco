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


def wait_for_server_install(wait_client, server_uuid):
        server_created = server_ops.wait_for_install(wait_client, server_uuid)
        if server_created == 1:
            print "Problem installing server, check platform."
        else:
            print "server installed ok."
        return server_created


