""" VDC Ops """
# import functions from suds
from suds.client import Client
from suds.transport.https import HttpAuthenticated

#import from other FCO python scripts
from resource_ops import list_resource_type

# import system functions
import sys
import string

#you can change INFO to DEBUG for (a lot) more information)
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)


def count_vdc(vdc_client):
    """ count VDCs for customer """
    # setup search filter object
    sf = vdc_client.factory.create('searchFilter')
#    print sf
    #create filter conditions object
    fc = vdc_client.factory.create('filterConditions')
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
    vdc_result_set = vdc_client.service.listResources(searchFilter=sf,
                                                      resourceType="VDC")
    #extract number of VDCs from result set
#    print vdc_result_set
    vdc_count = vdc_result_set.totalCount
    return vdc_count


def create_vdc(vdc_client, vdc_name, vdc_count=1000000):
    """ Create VDC for customer """
#    print "vdc_count " + str(vdc_count)
    # Get cluster uuid
    cluster_result_set = list_resource_type(res_client=vdc_client,
                                            res_type="CLUSTER")
    print cluster_result_set
    if cluster_result_set.totalCount == 0:
        print "Error No Cluster setup"
        sys.exit(1)
    cluster_uuid = cluster_result_set.list[0].resourceUUID
    # Create vdc
    vdc_data = vdc_client.factory.create('vdc')
    if vdc_count == 10000000:
        vdc_data.vdcName = vdc_name
        vdc_data.resourceName = vdc_name
    else:
        vdc_inc = vdc_count + 1
        vdc_data.vdcName = vdc_name + " " + str(vdc_inc)
        vdc_data.resourceName = vdc_name + " " + str(vdc_inc)
    vdc_data.clusterUUID = cluster_uuid
#    print vdc_data
    create_vdc_jobid = vdc_client.service.createVDC(vdc_data)
#    print create_vdc_jobid
    return create_vdc_jobid.itemUUID


def get_vdc_uuid(vdc_client, vdc_name='x'):
    """ Get VDC UUID or return none """
    # setup search filter object
    sf = vdc_client.factory.create('searchFilter')
    #create filter conditions object
    fc1 = vdc_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceState'
    fc1.value = 'ACTIVE'
    # debug print statement
#    print fc1
    sf.filterConditions.append(fc1)
    if vdc_name != 'x':
        fc2 = vdc_client.factory.create('filterConditions')
        # set filter condition values
        fc2.condition = 'IS_EQUAL_TO'
        fc2.field = 'resourceName'
        fc2.value = vdc_name
        sf.filterConditions.append(fc2)
#    print sf
    # call to listBillingEntities service with search filter
    vdc_result_set = vdc_client.service.listResources(searchFilter=sf,
                                                      resourceType="VDC")
    #extract number of VDCs from result set
#    print "VDC result set"
#    print vdc_result_set
    if vdc_result_set.totalCount != 0:
        vdc_uuid = vdc_result_set.list[0].resourceUUID
    else:
        vdc_uuid = 0
    return vdc_uuid


def get_first_vdc_in_cluster(auth_client, cluster_uuid):
    # Function to find the first VDC the user has in the specified cluster

    # Get a list of all VDCs the user has
    vdc_result_set = auth_client.service.listResources(resourceType="VDC")
    print("=== VDC RESULT SET ===")
    print vdc_result_set

    # Find the VDC that is in the same Cluster as the Image
    for l in range(0, vdc_result_set.totalCount):
        print(" resourceUUID: " + vdc_result_set.list[l].resourceUUID)
        print("  clusterUUID: " + vdc_result_set.list[l].clusterUUID)
        if (vdc_result_set.list[l].clusterUUID == cluster_uuid):
            print("get_first_vdc_in_cluster returns: " +
                  vdc_result_set.list[l].resourceUUID)
            return vdc_result_set.list[l].resourceUUID

    print("================== ===")
    return ""
