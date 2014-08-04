""" Image Ops """
# import functions from suds
from suds.client import Client
from suds.transport.https import HttpAuthenticated
import time


#you can change INFO to DEBUG for (a lot) more information)
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)


def count_image(image_client):
    """ count Images for customer """
    # setup search filter object	
    sf = image_client.factory.create('searchFilter')
    # debug print statement	
#    print sf
    #create filter conditions object
    fc = image_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc.condition = 'IS_EQUAL_TO'
    fc.field = 'resourceState'
    fc.value = 'ACTIVE'
    # debug print statement
#    print fc
    sf.filterConditions.append(fc)
#    print sf
    # call to listBillingEntities service with search filter
    image_result_set = image_client.service.listResources(searchFilter = sf, resourceType = "IMAGE")
    #extract number of Images from result set
#    print image_result_set
    image_count = image_result_set.totalCount
    return image_count


def fetch_image(image_client, image_name, image_url, image_user, prod_offer_name, vdc_uuid,
image_login='x', image_pw='x', image_count=1000000):
    """ Fetch Image for customer """
    if image_count == 1000000:
        inc_flag = 'FALSE'
    else:
        image_inc = image_count + 1
        inc_flag = 'TRUE'
    # Create image
    skel_image = image_client.factory.create('virtualResource')
    if inc_flag == 'TRUE':
        skel_image.resourceName = image_name + " " + str(image_inc)
    else:
        skel_image.resourceName = image_name
    skel_image.resourceType = "IMAGE"
    skel_image.vdcUUID = vdc_uuid
    # Get product offer uuid
    # setup search filter object	
    sf1 = image_client.factory.create('searchFilter')
    # debug print statement	
#    print sf1
    #create filter conditions object
    fc1 = image_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'description'
    fc1.value = prod_offer_name
    # debug print statement
#    print fc1
    sf1.filterConditions.append(fc1)
 #    print sf1
    prod_offer_result_set = image_client.service.listResources(searchFilter = sf1, resourceType = "PRODUCTOFFER")
    prod_offer_uuid = prod_offer_result_set.list[0].resourceUUID
    skel_image.productOfferUUID = prod_offer_uuid
    fetch_params = image_client.factory.create('fetchParameters')
    if image_pw != 'x':
        fetch_params.authPassword = image_pw
    else:
        fetch_params.authPassword = ''
    if image_login != 'x':
        fetch_params.authUserName = image_login
    else:
        fetch_params.authUserName = ''
    fetch_params.defaultUserName = image_user
    fetch_params.url = image_url
    fetch_params.genPassword = True
    fetch_params.makeImage = True
    fetch_image_jobid = image_client.service.fetchResource(skel_image, fetch_params)
    print fetch_image_jobid
    return fetch_image_jobid.itemUUID


def get_image_uuid(image_client, image_name='x'):
    """ List uuid for specified image name """
    # setup search filter object
    sf = image_client.factory.create('searchFilter')
    #create filter conditions object
    fc1 = image_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceState'
    fc1.value = 'ACTIVE'
    sf.filterConditions.append(fc1)
    if image_name != 'x':
        fc2 = image_client.factory.create('filterConditions')
        # set filter condition values
        fc2.condition = 'IS_EQUAL_TO'
        fc2.field = 'resourceName'
        fc2.value = image_name
        sf.filterConditions.append(fc2)
#    print sf
    # call to listBillingEntities service with search filter
    image_result_set = image_client.service.listResources(searchFilter = sf, resourceType = "IMAGE")
    #extract number of Images from result set
#    print "image result set"
#    print image_result_set
    if image_result_set.totalCount != 0:
        image_uuid = image_result_set.list[0].resourceUUID
    else:
        image_uuid = 0
    return image_uuid


def wait_for_image(image_client, image_uuid, status):
    """ Check Image has completed creation """
    sf = image_client.factory.create('searchFilter')
    #create filter conditions object
    fc1 = image_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = image_uuid
    sf.filterConditions.append(fc1)
    #create filter conditions object
    fc2 = image_client.factory.create('filterConditions')
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'resourceState'
    fc2.value = status
    sf.filterConditions.append(fc2)
#    print "sf:"
#    print sf
    image_result = image_client.service.listResources(searchFilter = sf, resourceType = 'IMAGE')
#    print image_created
    i = 0
#    print "image created count:" + str(image_created.totalCount)
    # currently waiting for 100 seconds (up to 10 loops of a 10 second sleep)
    while (image_result.totalCount < 1) and (i <= 60):
        print "in wait_for_image loop i = " + str(i) + ", count " + str(image_result.totalCount)
        i = i + 1
        # wait a while
        time.sleep(10)
        image_result = image_client.service.listResources(searchFilter = sf, resourceType = 'IMAGE')
#        print "image created count:" + str(image_created.totalCount)
    if image_result.totalCount == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val

def publish_image(client, res_uuid, tag, excl_flag):
    """Function to publish resources, mainly images and bento templates"""
    print res_uuid
    print tag
#    tag ='5d24945e-ae01-3200-8926-23c5cc1f5b44'
    worked_flag = client.service.publishImage(imageUUID=res_uuid,
         publishTo=tag, exclude=excl_flag)
    print worked_flag
    return worked_flag


def revoke_image(client, res_uuid, tag, excl_flag):
    """Function to revoke published resources, mainly images and bento"""
    worked_flag = client.service.revokeImage(imageUUID=res_uuid,
         publishTo=tag, exclude=excl_flag)
    print worked_flag
    return worked_flag





