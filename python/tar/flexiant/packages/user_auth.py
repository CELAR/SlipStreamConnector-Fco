# import functions from suds
from suds.client import Client
from suds.transport.https import HttpAuthenticated


#you can change INFO to DEBUG for (a lot) more information)
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)


def auth(creds_auth):
    """auth function authenticates against https service"""
#    print "creds"
#    print creds[0]
#    print creds[1]
#    print creds[2]
    #URL containing WSDL - used to prep list of available services
    url = 'https://' + creds_auth[0] + ':4442/?wsdl'
#    print url
    # setup credentials for use on login call
    credentials = dict(username=creds_auth[1], password=creds_auth[2])
#    print credentials
    # t is the transport to be used (https - see suds import line above)
    t = HttpAuthenticated(**credentials)
    # actual call to login to web service
    client = Client(url, location='https://' + creds_auth[0] + ':4442/',
         transport=t)
#    print client
    return client


def ini_auth(endpoint, user_name, pass_word, cust_UUID):
    """auth function authenticates against https service"""
    #URL containing WSDL - used to prep list of available services
    #url = 'https://' + host_name + ':4442/?wsdl'
    url = endpoint + '?wsdl'
#    print url
    login_name = user_name + "/" + cust_UUID
    # setup credentials for use on login call
    credentials = dict(username=login_name, password=pass_word)
#    print credentials
    # t is the transport to be used (https - see suds import line above)
    t = HttpAuthenticated(**credentials)
    # actual call to login to web service
#    client = Client(url, location='https://' + host_name + ':4442/',
#         transport=t)
    client = Client(url, location=endpoint, transport=t)

#    print client
    return client
