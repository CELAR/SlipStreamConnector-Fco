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


def wait_for_job(job_client, job_uuid, status, time_limit):
    """ check resource has reached state """
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
#    print chk_result
    i = 0
    # currently waiting for 100 seconds (up to 10 loops of a 10 second sleep)
    while (chk_result.totalCount == 0) and (i <= time_limit):
        print "in wait_for_job " + status + " loop i = " + str(i) +
        ", count " + str(chk_result.totalCount)
        i = i + 1
        # wait a while
        time.sleep(10)
        chk_result = job_client.service.listResources(searchFilter=sf,
                                                      resourceType='JOB')
    if chk_result.totalCount == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val
