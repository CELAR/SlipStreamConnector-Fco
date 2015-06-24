import logging
import requests
import json
import time

logging.getLogger("requests").setLevel(logging.WARNING)
isVerbose = False


def getToken(endpoint, username, cust_uuid, password):
    tokenURL = "%srest/user/current/authentication" % endpoint
    apiUserName = username + "/" + cust_uuid
    tokenPayload = {'automaticallyRenew':'True'}
    tokenRequest = requests.get(tokenURL, params=tokenPayload,
                                 auth=(apiUserName, password))
    if not tokenRequest.ok:
        raise Exception("Failed contacting %s with %s (%s)" % (
            tokenURL, tokenRequest.reason, tokenRequest.status_code))
    token = tokenRequest.content
    tokenObj = json.loads(token)
    return tokenObj['publicToken']

def rest_create_nic(auth_parms, cluster_uuid, network_type, network_uuid, vdc_uuid, nic_count):

    createURL = auth_parms['endpoint'] + "rest/user/current/resources/nic"

    # See comment in get_nic_uuid() for rationale
    if network_type.lower() == 'public':
        network_type = 'IP'

    # Generate a semi-menaningful name for the NIC
    nic_name = "NIC-" + network_type + "-" + str(nic_count)

    nic = {   "clusterUUID": cluster_uuid,
             "networkType" : network_type,
             "resourceType" : "NIC",
             "networkUUID" : network_uuid,
             "resourceName" : nic_name,
             "vdcUUID" : vdc_uuid
         }

    payload = nic

    if (isVerbose):
        print(payload)
    payload_as_string = json.JSONEncoder().encode(payload)

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.post(createURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
#    print(res.content)
    print("==============================================================")

    if (isVerbose):
        print(res.url)
        print("res=" + str(res))
        print res.content
    # print res.status_code

    # Status 202 (accepted) is good
    if (res.status_code == requests.codes.accepted):
      # print("Done")
      response = json.loads(res.content)
      # print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

def create_network(auth_parms, cluster_uuid, network_type, vdc_uuid, nic_count):

    createURL = auth_parms['endpoint'] + "rest/user/current/resources/network"

    # See comment in get_nic_uuid() for rationale
    if network_type.lower() == 'public':
        network_type = 'IP'


    ntwk = {  "clusterUUID": cluster_uuid,
             "networkType" : network_type,
             "resourceType" : "NETWORK",
             "resourceName" : "xxx",
             "vdcUUID" : vdc_uuid
         }

    payload = ntwk

    print(payload)
    payload_as_string = json.JSONEncoder().encode(payload)

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.post(createURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
#    print(res.content)
    print("==============================================================")

    print(res.url)

    print("res=" + str(res))
    print res.content
    # print res.status_code

    # Status 202 (accepted) is good
    if (res.status_code == requests.codes.accepted):
      # print("Done")
      response = json.loads(res.content)
      print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""


def get_nic_uuid(auth_parms, netTypeSought, cluster_uuid):
    """ function to find a nic of the desired type """

    sf = { "searchFilter" :
           { "filterConditions": [{"condition": "IS_EQUAL_TO",
                                   "field": "resourceState",
                                   "value": ["ACTIVE"]
                                  }
                                 ]
           }
        }

    queryLimit = {"from":0,
                  "loadChildren":False,
                  "maxRecords":200,
                  "to":200
                  }

    payload = {"queryLimit":queryLimit,
              "searchFilter":sf
            }

    network_result_set = rest_list_resource(auth_parms, res_type="network", payload=sf)

    print network_result_set
    ourNet = ""

    # SlipStream passes Public as a Network Type, but this is not what FCO knows as Public. See
    # http://docs.flexiant.com/display/DOCS/SOAP+networkType - what we actually need is IP, because that's the only
    # one of the two that gets the IP address assigned up front, and thus allows the rest of the code to continue
    if netTypeSought.lower() == 'public':
        netTypeSought = 'IP'

    for l in range(0, network_result_set['totalCount']):
        ntwk = network_result_set['list'][l]
        print ntwk
        print "Network type is: " + ntwk['networkType'] + " " + ntwk['resourceUUID'] + " in Cluster " + ntwk['clusterUUID']
        # Correct Cluster ?
        if ntwk['clusterUUID'] == cluster_uuid:
            print("Correct Cluster, at least !")
            # Exact match ?
            if ntwk['networkType'].lower() == netTypeSought.lower():
                ourNet = ntwk['resourceUUID']

    print "Will use: " + ourNet
    return ourNet

def create_nic(auth_parms, nic_count, network_type, cluster_uuid, vdc_uuid):
    """ function to create a nic """

    network_uuid = get_nic_uuid(auth_parms, network_type, cluster_uuid)
    print ("create_nic - network_uuid is:" + network_uuid)

    if (network_uuid == ''):
        network_uuid = create_network(auth_parms, cluster_uuid, network_type, vdc_uuid, nic_count)
        print("Created network " + network_uuid)


    nic_result_set = rest_create_nic(auth_parms, cluster_uuid, network_type, network_uuid, vdc_uuid, nic_count)

#    print "nic result set"
#    print nic_result_set
    nic_uuid = nic_result_set['itemUUID']
    return nic_uuid

# REST API call - createImage. It needs the Image object initialized with details  
def rest_create_image(auth_parms, baseUUID, clusterUUID, vdcUUID, size, default_user = "ubuntu"):
    createURL = auth_parms['endpoint'] + "rest/user/current/resources/image"
    imageData = { "baseUUID": baseUUID,
             "clusterUUID" : clusterUUID,
             "ctSupport" : False,
             "resourceName" : "ImageX",
             "resourceType" : "IMAGE",
             "vdcUUID" : vdcUUID,
             "vmSupport" : True,
             "size" : size,
             "defaultUser" : default_user,
             "genPassword" : True
         }

    payload = imageData

    print("REST - Create Image input:")
    print imageData

    print(payload)
    payload_as_string = json.JSONEncoder().encode(payload)

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.post(createURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
#    print(res.content)
    print("==============================================================")

    print(res.url)

    print("res=" + str(res))
    print res.content
    # print res.status_code

    # Status 202 (accepted) is good
    if (res.status_code == requests.codes.accepted):
      # print("Done")
      response = json.loads(res.content)
      print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

def list_image(auth_params, uuid):
    """ Get Image details """

    # Setup serach filter
    sf = { "searchFilter" :
          { "filterConditions": [{"condition": "IS_EQUAL_TO",
                                  "field": "resourceUUID",
                                  "value": [uuid]
                                 }
                                ]
          }
        }

    if (isVerbose):
        print("sf=")
        print sf
        print("---")

    result_set = rest_list_resource(auth_params, "image", sf)

    if result_set['totalCount'] == 0:
        raise RuntimeError("Image " + uuid + " not found or you do not have permissions to use it")

    print("==== Image Result ====")
    print result_set
    print("=========");
    # return just the first element (there was only one, right ?), otheriwse we end up doing e.g. img_ret['list'][0]['vdcUUID']
    # all over the place
    return result_set['list'][0]

def rest_list_resource(auth_parms, res_type, payload):
    print auth_parms
    theURL = auth_parms['endpoint'] + "rest/user/current/resources/" + res_type + "/list"
    print theURL

    if payload != None:
        payload_as_string = json.JSONEncoder().encode(payload);
        print("payload_as_string=" + payload_as_string)
    # Note we use data= and not params= here
    # See: http://requests.readthedocs.org/en/v1.0.1/user/quickstart/
    #
    # Also, we need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}

    print("theURL=" + theURL)
    if payload != None:
        res = requests.get(theURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
    else:
        res = requests.get(theURL, auth=(auth_parms['token'], ''), headers=headers)

    # Status 200 is good
    if (res.status_code == requests.codes.ok):
        # print("Done")
        # print("res.content=" + str(res.content))

        response = json.loads(res.content)
        # print "response=" + str(response)

        print("count=" + str(response['totalCount']))
        return response

    # Something went wrong. Pick out the status code
    woops = "Error - HTTP status code: " + str(res.status_code)
    raise RuntimeError(woops)

def rest_change_server_status(auth_parms, server_uuid, new_state):

    URL = auth_parms['endpoint'] + "rest/user/current/resources/server/" + server_uuid + "/change_status"

    payload = {  "newStatus": new_state,
                "safe" : True
            }

    print(payload)
    payload_as_string = json.JSONEncoder().encode(payload)

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.put(URL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
#    print(res.content)

    print(res.url)

    # Status 200 is good
    if (res.status_code == requests.codes.ok):
      # print("Done")
      response = json.loads(res.content)
      # print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

def get_prod_offer_uuid(auth_parms, prod_offer_name):
    """ Get product offer UUID when given product offer name """
    sf = { "searchFilter" :
          { "filterConditions": [{"condition": "IS_EQUAL_TO",
                                  "field": "resourceState",
                                  "value": ["ACTIVE"]
                                 },
                                 {"condition": "IS_EQUAL_TO",
                                  "field": "resourceName",
                                  "value": [prod_offer_name]
                                 }
                                ]
          }
        }


    print("Product Offer Search Filter:")
    print(sf)

    prod_offer_result_set = rest_list_resource(auth_parms, res_type="productoffer", payload=sf)

    print("Prod_Offer_Result_Set:\n");
    print prod_offer_result_set

    po = prod_offer_result_set['list'][0]
    prod_offer_uuid = po['resourceUUID']
    print("Product Offer UUID for " + prod_offer_name + " is " + prod_offer_uuid)
    return prod_offer_uuid

def list_sshkeys(auth_parms, customer_uuid):
    sf = { "searchFilter" :
          { "filterConditions": [{"condition": "IS_EQUAL_TO",
                                  "field": "customerUUID",
                                  "value": [customer_uuid]
                                 }
                                ]
          }
        }

    key_result_set = rest_list_resource(auth_parms, res_type="sshkey", payload=sf)
    print("SSHKEY for customer " + customer_uuid + " is:\n")
    print key_result_set
    print("\======== End SSHKey ==========\n")
    return key_result_set

def create_sshkey(auth_parms, public_key, public_key_name):

    createURL = auth_parms['endpoint'] + "rest/user/current/resources/sshkey"

    ssh_key = {  "publicKey": public_key,
#             "resourceName" : public_key_name,
             "resourceType" : "SSHKEY",
             "globalKey" : False
         }

    payload = ssh_key


    print(payload)
    payload_as_string = json.JSONEncoder().encode(payload)

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.post(createURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
#    print(res.content)
    print("==============================================================")


    # Status 202 (accepted) is good
    if (res.status_code == requests.codes.accepted):
      # print("Done")
      response = json.loads(res.content)
      # print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

def attach_ssh_key(auth_parms, server_uuid, sshkey_uuid):

    attachURL = auth_parms['endpoint'] + "rest/user/current/resources/server/" + server_uuid + "/sshkey/" + sshkey_uuid + "/attach"

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}

    res = requests.put(attachURL, auth=(auth_parms['token'], ''), headers=headers)

    # Status 200 is good
    if (res.status_code == requests.codes.ok):
      # print("Done")
      response = json.loads(res.content)
      # print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

def add_nic_to_server(auth_parms, server_uuid, nic_uuid, index):
    """ Function to add NIC to server """
    attachURL = auth_parms['endpoint'] + "rest/user/current/resources/server/" + server_uuid + "/nic/" + nic_uuid + "/attach"

    payload = {"index": index}

    payload_as_string = json.JSONEncoder().encode(payload)

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}

    res = requests.put(attachURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)

    # Status 202 (Accepted) is good as it means the job will at least be attempted
    if (res.status_code == requests.codes.accepted):
      # print("Done")
      response = json.loads(res.content)
      print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

    # return ret_val

def attach_disk(auth_parms, server_uuid, disk_uuid, index):

    attachURL = auth_parms['endpoint'] + "rest/user/current/resources/server/" + server_uuid + "/disk/" + disk_uuid + "/attach"

    payload = {"index": index}
    payload_as_string = json.JSONEncoder().encode(payload)

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.put(attachURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
#    print(res.content)
    print("==============================================================")


    print(res.url)

    print("res=" + str(res))
    print res.content
    # print res.status_code

    # Status 200 is good
    if (res.status_code == requests.codes.ok):
      # print("Done")
      response = json.loads(res.content)
      # print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

def detach_disk(auth_parms, server_uuid, disk_uuid):
    detachURL = auth_parms['endpoint'] + "rest/user/current/resources/server/" + server_uuid + "/disk/" + disk_uuid + "/detach"

    # payload = {"index": index}
    # payload_as_string = json.JSONEncoder().encode(payload)
    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.put(detachURL, data='', auth=(auth_parms['token'], ''), headers=headers)
    print(res.content)
    print("==============================================================")
    print(res.url)
    print("res=" + str(res))
    print res.content
    print res.status_code

    # Status 200 is good
    if (res.status_code == requests.codes.ok):
      print("Done")
      response = json.loads(res.content)
      print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)
    return ""

def wait_for_job(auth_parms, job_uuid, status, time_limit):
    """ check resource has reached state """
    print("Begin wait_for_job on resource " + job_uuid + " reaching status " + status + " at " + time.strftime("%Y-%m-%d %H:%M:%S"))
    sleep_time = 5
    loop_limit = (time_limit / sleep_time) + 1

    # create search filter, with embedded filter conditions
    sf = { "searchFilter" :
           { "filterConditions": [{"condition": "IS_EQUAL_TO",
                                   "field": "resourceUUID",
                                   "value": [job_uuid]
                                  },
                                  {"condition": "IS_EQUAL_TO",
                                   "field": "status",
                                   "value": [status]
                                  }
                                 ]
           }
        }

#    print sf
    chk_result = rest_list_resource(auth_parms, res_type="job", payload=sf)
#    print "Check Result"
    # print chk_result
    i = 0

    # Try for at least the specified time_limit
    while (chk_result['totalCount'] == 0) and (i <= loop_limit):
        print "in wait_for_job " + status + " loop i = " + str(i) + ", count " + str(chk_result['totalCount'])
        i = i + 1
        # wait a while
        time.sleep(sleep_time)
        chk_result = rest_list_resource(auth_parms, res_type="job", payload=sf)
        # print chk_result

    print("End wait_for_job on resource " + job_uuid + " reaching status " + status + " at " + time.strftime("%Y-%m-%d %H:%M:%S"))
    if chk_result['totalCount'] == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val


def wait_for_install(auth_parms, server_uuid):
    print("Begin wait_for_install for server " + server_uuid + " at " + time.strftime("%Y-%m-%d %H:%M:%S"))
    """ Check Server has completed creation """

    sf = { "searchFilter" :
           { "filterConditions": [{"condition": "IS_EQUAL_TO",
                                   "field": "resourceUUID",
                                   "value": [server_uuid]
                                  },
                                  {"condition": "IS_EQUAL_TO",
                                   "field": "resourceState",
                                   "value": ["ACTIVE"]
                                  }
                                 ]
           }
        }

#    print sf

    server_created = rest_list_resource(auth_parms, res_type="server", payload=sf)
#    print server_created
    i = 0
#    print "server created count:" + str(server_created.totalCount)
    # currently waiting for 100 seconds (up to 10 loops of a 10 second sleep)
    while (server_created['totalCount'] < 1) and (i <= 10):
        print "in wait_for_install loop i = " + str(i) + ", count " + str(server_created['totalCount'])
        i = i + 1
        # wait a while
        time.sleep(10)
        server_created = rest_list_resource(auth_parms, res_type="server", payload=sf)
#        print "server created count:" + str(server_created.totalCount)
    print "wait_for_install - created count is: " + str(server_created['totalCount'])
    print("End wait_for_install for server " + server_uuid + " at " + time.strftime("%Y-%m-%d %H:%M:%S"))
    if server_created['totalCount'] == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val

def list_resource_by_uuid(auth_parms, uuid, res_type):
    """ Get details for the specified resource """

    # create search filter for s resource of the specified UUID
    sf = { "searchFilter" :
           { "filterConditions": [{"condition": "IS_EQUAL_TO",
                                   "field": "resourceUUID",
                                   "value": [uuid]
                                  }
                                 ]
           }
        }

#    print sf
    result = rest_list_resource(auth_parms, res_type, payload=sf)

    # Potentially could be a list of resources ?. Just return the lot, the caller can sort out whether it
    # expects one, or multiple
    print result
    return result

def get_server_state(auth_parms, server_uuid):
    # Function to get server state given server uuid

    server_resultset = list_resource_by_uuid(auth_parms, uuid=server_uuid, res_type='SERVER')
#    print server_result_set
    server_status = server_resultset['list'][0]['status']
#    print "server status: " + server_status
    return server_status

def get_first_vdc_in_cluster(auth, cluster_uuid):
    # Function to find the first VDC the user has in the specified cluster

    # Get a list of all VDCs the user has
    vdc_result_set = rest_list_resource(auth_parms=auth, res_type="vdc", payload=None)
    print("=== VDC RESULT SET ===")
    print vdc_result_set

    # Find the VDC that is in the same Cluster as the Image
    for l in range(0, vdc_result_set['totalCount']):
        # print(" resourceUUID: " + vdc_result_set.list[l].resourceUUID)
        vdc = vdc_result_set['list'][l]
        resourceUUID = vdc['resourceUUID']
        clusterUUID = vdc['clusterUUID']
        print(" resourceUUID: " + resourceUUID)
        print("  clusterUUID: " + clusterUUID)
        if (clusterUUID == cluster_uuid):
            print("get_first_vdc_in_cluster returns: " + resourceUUID)
            return resourceUUID

    print("================== ===")
    return ""

def rest_create_server(auth_parms, server_name, server_po_uuid, image_uuid, cluster_uuid, vdc_uuid, cpu_count,
                       ram_amount, boot_disk_po_uuid, context_script):

    createURL = auth_parms['endpoint'] + "rest/user/current/resources/server"

# "clusterUUID": cluster_uuid,
    server_json = {
             "resourceName" : server_name,
             "productOfferUUID": server_po_uuid,
             "imageUUID" : image_uuid,
             "clusterUUID" : cluster_uuid,
             "vdcUUID": vdc_uuid,
             "cpu": cpu_count,
             "ram": ram_amount,
             "disks":[{"iso": False,
                       # "resourceName": "the disk"
                       "resourceType" : "DISK",
                       "resourceUUID" : boot_disk_po_uuid,
                       "size" : 20,
                       "vdcUUID": vdc_uuid,
                       # "productOfferUUID": disk_po_uuid
                      }],
             "resourceType" : "SERVER",
             "resourceMetadata":{"publicMetadata": context_script},
             # "serverCapabilities": ["CLONE", "CHILDREN_PERSIST_ON_DELETE", "CHILDREN_PERSIST_ON_REVERT"],
            }

    payload = server_json

    print(payload)
    payload_as_string = json.JSONEncoder().encode(payload)

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.post(createURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
#    print(res.content)
    print("==============================================================")


    print(res.url)

    print("res=" + str(res))
    print res.content
    # print res.status_code

    # Status 202 (Accepted) is good
    if (res.status_code == requests.codes.accepted):
      # print("Done")
      response = json.loads(res.content)
      # print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

def rest_create_disk(auth_parms, vdc_uuid, disk_po_uuid, disk_name, disk_size):

    createURL = auth_parms['endpoint'] + "rest/user/current/resources/disk"

# "clusterUUID": cluster_uuid,

    disk = {  "iso" : False,
             "resourceName" : disk_name,
             "resourceType" : "DISK",
             "size" : disk_size,
             "storageCapabilities": ["CLONE", "CHILDREN_PERSIST_ON_DELETE", "CHILDREN_PERSIST_ON_REVERT"],
             "vdcUUID": vdc_uuid,
             "productOfferUUID": disk_po_uuid
         }

    payload = disk


    print(payload)
    payload_as_string = json.JSONEncoder().encode(payload)


    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.post(createURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
#    print(res.content)
    print("==============================================================")


    print(res.url)

    print("res=" + str(res))
    print res.content
    # print res.status_code

    # Status 202 (Accepted) is good
    if (res.status_code == requests.codes.accepted):
      # print("Done")
      response = json.loads(res.content)
      # print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

def create_vdc(auth, cluster_uuid, vdc_name):

    createURL = auth['endpoint'] + "rest/user/current/resources/vdc"

    vdc = {  "clusterUUID": cluster_uuid,
             "resourceName" : vdc_name,
             "resourceType" : "VDC",
         }

    payload = vdc
    print(payload)
    payload_as_string = json.JSONEncoder().encode(payload)

    # Need to set the content type, because if we don't the payload is just silently ignored
    headers = {'content-type': 'application/json'}
    res = requests.post(createURL, data=payload_as_string, auth=(auth['token'], ''), headers=headers)

    # print("res=" + str(res))
    # print res.content
    # print res.status_code

    # Status 201=2 (accepted) is good
    if (res.status_code == requests.codes.accepted):
      # print("Done")
      response = json.loads(res.content)
      # print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""


def wait_for_resource(auth_parms, res_uuid, state, res_type):
    """ check resource has reached desired state """
    sf = { "searchFilter" :
           { "filterConditions": [{"condition": "IS_EQUAL_TO",
                                   "field": "resourceUUID",
                                   "value": [res_uuid]
                                  },
                                  {"condition": "IS_EQUAL_TO",
                                   "field": "resourceState",
                                   "value": [state]
                                  }
                                 ]
           }
        }


#   print sf

    res_result = rest_list_resource(auth_parms, res_type=res_type, payload=sf)
#    print "Res Result"
#    print res_result
    i = 0
    # currently waiting for 100 seconds (up to 10 loops of a 10 second sleep)
    while (res_result['totalCount'] == 0) and (i <= 10):
        print "in wait_for_resource " + state + " loop i = " + str(i) + ", count " + str(res_result['totalCount'])
        i = i + 1
        # wait a while
        time.sleep(10)
        res_result = rest_list_resource(auth_parms, res_type=res_type, payload=sf)

    print("wait_for_resource for uuid " + res_uuid + " state " + state + " returned count of " + str(res_result['totalCount']))
    if res_result['totalCount'] == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val

def wait_for_server(auth_parms, server_uuid, state):
    """ Check Server has completed creation """

    print("Begin wait_for_server for server " + server_uuid + " at " + time.strftime("%Y-%m-%d %H:%M:%S"))

    # Similar to wait_for_resource(), except here we look at status, not resourceState
    sf = { "searchFilter" :
           { "filterConditions": [{"condition": "IS_EQUAL_TO",
                                   "field": "resourceUUID",
                                   "value": [server_uuid]
                                  },
                                  {"condition": "IS_EQUAL_TO",
                                   "field": "status",
                                   "value": [state]
                                  }
                                 ]
           }
        }

#    print sf

    server_result = rest_list_resource(auth_parms, res_type="server", payload=sf)

    i = 0
    while (server_result['totalCount'] < 1) and (i <= 24):
        print "in wait_for_server loop i = " + str(i) + ", count " + str(server_result['totalCount'])
        i = i + 1
        # wait a while
        time.sleep(5)
        server_result = rest_list_resource(auth_parms, res_type="server", payload=sf)

    print("wait_for_server(): exit after " + str(i) + " tries")
    print("End wait_for_server for server " + server_uuid + " at " + time.strftime("%Y-%m-%d %H:%M:%S"))
    if server_result['totalCount'] == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val

def change_server_status(auth_parms, server_uuid, state):
    """ Change status of server, and return success once it reaches that state """

    rest_change_server_status(auth_parms, server_uuid, state)

    server_result = wait_for_server(auth_parms, server_uuid, state)
    if server_result == 1:
        print "Problem changing server status, check platform, server uuid: " + server_uuid
    else:
        print "server status changed ok, server uuid: " + server_uuid
    return server_result


def list_servers(endpoint, username, cust_uuid, password):
    """Returns list of server objects (dictionaries).
    endpoint : API base URL.
    """
    token = getToken(endpoint, username, cust_uuid, password)
    servers = _list_servers(endpoint, token)
    return servers['list']


def _list_servers(endpoint, token):
    listURL = endpoint + "rest/user/current/resources/server/list"
    queryLimit = {"from": 0,
                  "to": 200,
                  "maxRecords": 200,
                  "loadChildren": True}
    payload_as_string = json.JSONEncoder().encode({"queryLimit": queryLimit})
    headers = {'content-type': 'application/json'}
    res = requests.get(listURL, data=payload_as_string, auth=(token, ''), headers=headers)
    if res.status_code == requests.codes.ok:
        return json.loads(res.content)
    else:
        raise RuntimeError("Error - HTTP status code: " + str(res.status_code))
   
def rest_delete_resource(auth_parms, resource_uuid, res_type):
    attachURL = auth_parms['endpoint'] + "rest/user/current/resources/" + res_type + "/" + resource_uuid
    cascade = { "cascade": True }
    payload = cascade
    print(payload)
    payload_as_string = json.JSONEncoder().encode(payload)
    headers = {'content-type': 'application/json'}
    res = requests.delete(attachURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)
    print(res.content)
    print("==============================================================")

    print(res.url)

    print("res=" + str(res))
    print res.content
    print res.status_code

    # Status 200 is good
    if (res.status_code == requests.codes.ok):
      print("Done")
      response = json.loads(res.content)
      print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    return ""
 
def modify_cpu_ram(auth_parms, server_uuid, server_name, cluster_uuid, vdc_uuid, cpu_count, ram_amount, server_po_uuid):
    attachURL = auth_parms['endpoint'] + "rest/user/current/resources/server/" + server_uuid

    server = {
              "resourceName" : server_name,
              "clusterUUID" : cluster_uuid,
              "vdcUUID" : vdc_uuid,
              "cpu" : cpu_count,
              "ram" : ram_amount,
              "productOfferUUID" : server_po_uuid,
              "resourceType" : "SERVER"
            }

    print "REST - modify server input:"
    print server

    payload = server

    print payload
    payload_as_string = json.JSONEncoder().encode(payload)
    headers = {'content-type': 'application/json'}
    res = requests.put(attachURL, data=payload_as_string, auth=(auth_parms['token'], ''), headers=headers)

    print("==============================================================")
    print(res.url)
    print res.content
    print res.status_code

    # Status 200 is good
    if (res.status_code == requests.codes.ok):
      response = json.loads(res.content)
      # print "response=" + str(response)
      return response

    # Something went wrong. Pick out the status code and message
    response = json.loads(res.content)

    # print(response['message'] + " (error code: " + response['errorCode'] + ")")
    return ""

