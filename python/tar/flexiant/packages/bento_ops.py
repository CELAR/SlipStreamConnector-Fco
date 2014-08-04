""" Bento Ops """
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


def create_deployment_template(bento_client, template_name, vdc_uuid):
    template_skeleton = bento_client.factory.create('deploymentTemplate')
    template_skeleton.resourceName = template_name
    template_skeleton.vdcUUID = vdc_uuid
    bento_result = bento_client.service.createDeploymentTemplate(template_skeleton)
    template_uuid = bento_result.itemUUID
    return template_uuid

def modify_deployment_template(bento_client,template_data):
    bento_result = bento_client.service.modifyDeploymentTemplate(template_data)
#    print "Bento modify Result:"
#    print bento_result
    status = bento_result.resourceState
    return status

def deploy_template(bento_client, template_data, inst_name):
    template_data.resourceName = inst_name
    template_data.resourceType = 'DEPLOYMENT_INSTANCE'
    deploy_result = bento_client.service.deployTemplate(template_data)
#    print "deploy result:"
#    print deploy_result
    instance_uuid = deploy_result.itemUUID
    return instance_uuid

def modify_deployment_instance(bento_client, inst_data):
    bento_result = bento_client.service.modifyDeploymentInstance(inst_data)
    bento_result
    return bento_result

def create_deployment_template_from_instance(bento_client, instance_uuid):
    bento_result = bento_client.service.createDeploymentTemplateFromInstance(instance_uuid)
    template_uuid = bento_result.itemUUID
    return template_uuid

def dry_run_template(bento_client, template_data):
    dryrun_result = bento_client.service.dryRunTemplate(template_data)
#    print "bento dry run results"
#    print dryrun_result
    return dryrun_result

def change_template_instance_status(bento_client, inst_uuid, new_status, safe):
    status_result = bento_client.service.changeDeploymentInstanceStatus(inst_uuid, new_status, safe)   
    return status_result


def wait_for_instance(bento_client, res_uuid, status, time_limit):
    """ check resource has reached state """
    sf = bento_client.factory.create('searchFilter')
    #create filter conditions object
    fc1 = bento_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = res_uuid
    sf.filterConditions.append(fc1)
    fc2 = bento_client.factory.create('filterConditions')
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'status'
    fc2.value = status
    sf.filterConditions.append(fc2)
#    print "sf:"
#    print sf
    chk_result = bento_client.service.listResources(searchFilter = sf, resourceType = 'DEPLOYMENT_INSTANCE')
#    print "Check Result"
#    print chk_result
    i = 0
    # currently waiting for 100 seconds (up to 10 loops of a 10 second sleep)
    while (chk_result.totalCount == 0) and (i <= time_limit):
        print "in wait_for_instance "+status+" loop i = " + str(i) + ", count " + str(chk_result.totalCount)
        i = i + 1      
        # wait a while
        time.sleep(10)
        chk_result = bento_client.service.listResources(searchFilter = sf, resourceType = 'DEPLOYMENT_INSTANCE')
    if chk_result.totalCount == 1:
        return_val = 0
    else: 
        return_val = 1
    return return_val


