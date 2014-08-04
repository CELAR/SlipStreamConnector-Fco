""" Transaction Ops """
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

def list_unit_transactions(tran_client):
    """ Function to get list of transactions """

    tran_result_set = tran_client.service.listUnitTransactions()
    return tran_result_set

def list_unit_transaction_summary(tran_client):
    """ Function to get unit transaction summary """
    tran_result_set = tran_client.service.listUnitTransactionSummary()
    return tran_result_set

def list_unit_transactions_maxrecord(tran_client, max_record):
    """ Function to get list of transactions """
    ql = tran_client.factory.create('queryLimit')
    ql.maxRecords = max_record
    ql.loadChildren = False
    tran_result_set = tran_client.service.listUnitTransactions(queryLimit = ql)
    return tran_result_set


def list_product_purchases(tran_client):
    """ Function to list product purchases for specific user"""
#    sf = res_client.factory.create('searchFilter')
#    fc1 = res_client.factory.create('filterConditions')
#    fc1.condition = 'IS_EQUAL_TO'
#    fc1.field = 'resourceName'
#    fc1.value = res_name
#    sf.filterConditions.append(fc1)
    result_set = tran_client.service.listProductPurchases()
    print result_set
    return result_set