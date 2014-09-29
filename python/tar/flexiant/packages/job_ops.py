""" Job Ops """
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


def get_job(job_client, job_uuid):
    """ show data for specific job """
    # setup search filter object
    sf = job_client.factory.create('searchFilter')
    #create filter conditions object
    fc = job_client.factory.create('filterConditions')
    # set filter condition values
    fc.condition = 'IS_EQUAL_TO'
    fc.field = 'resourceUUID'
    fc.value = job_uuid
    sf.filterConditions.append(fc)
#    print sf
    # call to listBillingEntities service with search filter
    job_data = job_client.service.listResources(searchFilter=sf,
                                                resourceType="JOB")
#    print job_data
    return job_data


def wait_for_job(job_client, job_uuid, status, time_limit):
    """ check resource has reached state """
    sleep_time = 5
    loop_limit = (time_limit / sleep_time ) + 1
    sf = job_client.factory.create('searchFilter')
    #create filter conditions object
    fc1 = job_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = job_uuid
    sf.filterConditions.append(fc1)
    fc2 = job_client.factory.create('filterConditions')
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'status'
    fc2.value = status
    sf.filterConditions.append(fc2)
#    print "sf:"
#    print sf
    chk_result = job_client.service.listResources(searchFilter=sf,
                                                  resourceType='JOB')
#    print "Check Result"
    #print chk_result
    i = 0

    # Try for at least the specified time_limit
    while (chk_result.totalCount == 0) and (i <= loop_limit):
        print "in wait_for_job " + status + " loop i = " + str(i) +  ", count " + str(chk_result.totalCount)
        i = i + 1
        # wait a while
        time.sleep(sleep_time)
        chk_result = job_client.service.listResources(searchFilter=sf,
                                                      resourceType='JOB')
        #print chk_result                                              

    if chk_result.totalCount == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val
