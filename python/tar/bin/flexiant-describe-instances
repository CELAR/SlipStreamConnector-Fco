#!/usr/bin/python
# 
# List VMs owned by the specified customer, and their state

import json
import requests

import argparse


# We can turn on debugging by explicitly importing http_client and setting it's debug level
#try:
#    import http.client as http_client
#except ImportError:
#    # Python 2
#    import httplib as http_client
#http_client.HTTPConnection.debuglevel = 1


def getToken(endpoint, username, cust_uuid, password):
    tokenURL = "%srest/user/current/authentication" % endpoint
    apiUserName = username + "/" + cust_uuid
    tokenPayload = {'automaticallyRenew':'True'}
    tokenRequest = requests.get(tokenURL,
                                params=tokenPayload,
                                auth=(apiUserName, password))
                                
    token = tokenRequest.content
    tokenObj = json.loads(token)
    return tokenObj['publicToken']


def list_servers(endpoint, token, password, username, cust_uuid):
     
    listURL = endpoint + "rest/user/current/resources/server/list"
    
    apiUserName = username + "/" + cust_uuid    
        
    false = False
    # No point adding a FCO searchFilter since the user can only see their own VMs
    queryLimit = {"from":0,
                  "loadChildren":false,
                  "maxRecords":200,
                  "to":200
                  } 

    payload= {"queryLimit":queryLimit
            }
    #print("payload=" + str(payload))
    
    payload_as_string = json.JSONEncoder().encode(payload);
    #print(payload_as_string);

    # Note we use data= and not params= here
    # See: http://requests.readthedocs.org/en/v1.0.1/user/quickstart/
    #
    # Also, we need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}    

    res = requests.get(listURL, data=payload_as_string, auth=(token,''), headers=headers)

    # Status 200 is good
    if (res.status_code == requests.codes.ok):
      #print("Done")
      response = json.loads(res.content)
      #print "response=" + str(response)
      return response
      
    # Something went wrong. Pick out the status code
    
    woops = "Error - HTTP status code: " + str(res.status_code)
    raise RuntimeError(woops)
#    return ""

        
def main():
    """Main Function"""
    
    parser=argparse.ArgumentParser()

    parser.add_argument('--cust-uuid', dest='customerUUID',nargs='*',
                        help="The UUID of the Customer")                        

    parser.add_argument('--cust-username', dest='customerUsername',nargs='*',
                        help="The Username of the Customer")                        

    parser.add_argument('--cust-password', dest='customerPassword',nargs='*',
                        help="The UUID of the Customer")                        
                        
    parser.add_argument('--api-host', dest='apiHost',nargs='*',
                        help="WHere the API lives")                        

    parser.add_argument('--verbose', dest='isVerbose',action='store_true',
                            help="Whether to print diagnostics as we go")
                                                    

    cmdargs=parser.parse_args()
        
    isVerbose            = cmdargs.isVerbose

    # better late than never
    #if (isVerbose):
    #    print (cmdargs)
       
    apiToken = getToken(cmdargs.apiHost[0], 
                        cmdargs.customerUsername[0], 
                        cmdargs.customerUUID[0],
                        cmdargs.customerPassword[0])
                        
    #print("apiToken = " + apiToken)    
    response = list_servers(cmdargs.apiHost[0], apiToken, cmdargs.customerPassword[0], 
                            cmdargs.customerUsername[0], cmdargs.customerUUID[0])
    print "UUID                                  State"
    for server in response['list']:
        print server['resourceUUID'] + " " + server['status']

if __name__ == "__main__":
    main()


