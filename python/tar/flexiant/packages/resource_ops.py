""" Resource Ops """
# import functions from suds
from suds.client import Client
from suds.transport.https import HttpAuthenticated

#import required for sleep function
import time

#you can change INFO to DEBUG for (a lot) more information)
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)

def delete_resource(res_client, res_uuid, cascade_flag):
    """ Function to delete resources """
    res_client.service.deleteResource(resourceUUID = res_uuid, cascade = cascade_flag)


def list_resource_name(res_client, res_name, res_type):
    """Function to list resources with supplied resourceName"""
    sf = res_client.factory.create('searchFilter')
    fc1 = res_client.factory.create('filterConditions')
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceName'
    fc1.value = res_name
    sf.filterConditions.append(fc1)
    res_result_set = res_client.service.listResources(searchFilter = sf,resourceType = res_type)
    return res_result_set


def list_resource_type(res_client, res_type):
    """ Function to get list of resources of a certain type """
    res_result_set = res_client.service.listResources(resourceType = res_type)
    return res_result_set


def list_resource_limit(res_client, res_type, query_limit):
    """ Function to get list of resources of a certain type """
    res_result_set = res_client.service.listResources(queryLimit=query_limit,
         resourceType=res_type)
    return res_result_set

def list_maxrecord_resource_type(res_client, res_type, max_record):
    """ Function to get list of resources of a certain type """
    ql = res_client.factory.create('queryLimit')
    ql.maxRecords = max_record
    ql.loadChildren = False
    res_result_set = res_client.service.listResources(resourceType = res_type, queryLimit = ql)
    return res_result_set


def list_resource(res_client, res_uuid, res_type):
    """ Function to get one resource's data """
    sf = res_client.factory.create('searchFilter')
    fc1 = res_client.factory.create('filterConditions')
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = res_uuid
    sf.filterConditions.append(fc1)
    res_result_set = res_client.service.listResources(searchFilter = sf,resourceType = res_type)
    return res_result_set



def wait_for_resource_delete(res_client, res_uuid):
    """ check resource has deleted """
    sf = res_client.factory.create('searchFilter')
    # debug print statement	
#    print sf
    #create filter conditions object
    fc1 = res_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = res_uuid
    sf.filterConditions.append(fc1)
#    print "sf:"
#    print sf
    res_result = res_client.service.listResources(searchFilter = sf)
    i = 0
#    print "server created count:" + str(server_created.totalCount)
    # currently waiting for 100 seconds (up to 10 loops of a 10 second sleep)
    while (res_result.totalCount == 1) and (i <= 10):
        print "in wait_for_resource_delete loop i = " + str(i) + ", count " + str(res_result.totalCount)
        i = i + 1
        # wait a while
        time.sleep(10)
        res_result = res_client.service.listResources(searchFilter = sf)
    if res_result.totalCount == 0:
        return_val = 0
    else:
        return_val = 1
    return return_val


def wait_for_resource(res_client, res_uuid, state, res_type):
    """ check resource has reached state """
    sf = res_client.factory.create('searchFilter')
    # debug print statement	
#    print sf
    #create filter conditions object
    fc1 = res_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = res_uuid
    sf.filterConditions.append(fc1)
    fc2 = res_client.factory.create('filterConditions')
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'resourceState'
    fc2.value = state
    sf.filterConditions.append(fc2)
#    print "sf:"
#    print sf
    res_result = res_client.service.listResources(searchFilter = sf, resourceType = res_type)
#    print "Res Result"
#    print res_result
    i = 0
    # currently waiting for 100 seconds (up to 10 loops of a 10 second sleep)
    while (res_result.totalCount == 0) and (i <= 10):
        print "in wait_for_resource "+state+" loop i = " + str(i) + ", count " + str(res_result.totalCount)
        i = i + 1
        # wait a while
        time.sleep(10)
        res_result = res_client.service.listResources(searchFilter = sf, resourceType = res_type)

    print("wait_for_resource for uuid " + res_uuid + " state " + state + " returned count of " +  str(res_result.totalCount))        
    if res_result.totalCount == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val


def add_resource_key(res_client, res_uuid, key_name, key_value, key_type, key_weight):
    """ This function will add a question to a server """
    res_key = res_client.factory.create('resourceKey')
    res_key.resourceUUID = res_uuid
    res_key.name = key_name
    res_key.type = key_type
    res_key.value = key_value
    res_key.weight = key_weight
    print "key to be added:"
    print res_key
    ret_val = res_client.service.addKey(res_uuid, res_key)
#    print "Return Value:"
#    print ret_val
    return ret_val

def remove_resource_key(res_client, res_uuid, res_key_name):
    """ Remove a resource key """
    # setup resourceKey object	
    key = res_client.factory.create('resourceKey')
    # debug print statement	
#    print key
    # set filter condition values
    key.resourceUUID = res_uuid
    key.name = res_key_name
    # debug print statement
#    print key
    # call to addKey
    key_result_set = res_client.service.removeKey(res_uuid,key)
#    print key_result_set
    return key_result_set


def publish_resource(res_client, res_uuid, tag, excl_flag):
    """Function to publish resources, mainly images and bento templates"""
    worked_flag = res_client.service.publishResource(resourceUUID=res_uuid,
         publishTo=tag, exclude=excl_flag)
    print worked_flag
    return worked_flag


def revoke_resource(res_client, res_uuid, tag, excl_flag):
    """Function to revoke published resources, mainly images and bento"""
    worked_flag = res_client.service.revokeResource(resourceUUID=res_uuid,
         publishTo=tag, exclude=excl_flag)
    print worked_flag
    return worked_flag

