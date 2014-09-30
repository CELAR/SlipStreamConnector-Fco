""" Server Ops """
# import functions from suds
from suds.client import Client
from suds.transport.https import HttpAuthenticated

#import required for sleep function
import time

#you can change INFO to DEBUG for (a lot) more information)
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)


def count_server(server_client):
    """ count Images for customer """
    # call to listBillingEntities service with search filter
    server_result_set = server_client.service.listResources(resourceType = "SERVER")
    #extract number of Servers from result set
#    print server_result_set
    server_count = server_result_set.totalCount
    return server_count


def get_vdc_uuid(server_client):
    """ function to retrieve first VDC in list """
    vdc_result_set = server_client.service.listResources(resourceType="VDC")
    vdc_uuid = vdc_result_set.list[0].resourceUUID
    return vdc_uuid

def get_nic_uuid(auth_client, netTypeSought, cluster_uuid):
    """ function to find a nic of the desired type """
    sf2 = auth_client.factory.create('searchFilter')
    fc3 = auth_client.factory.create('filterConditions')
    ql =  auth_client.factory.create('queryLimit')
    fc3.condition = 'IS_EQUAL_TO'
    fc3.field = 'resourceState'
    fc3.value = 'ACTIVE'
    sf2.filterConditions.append(fc3)
    ql.maxRecords = 200
    ql.loadChildren = False    # We don't need all the details
    network_result_set = auth_client.service.listResources(searchFilter = sf2, queryLimit=ql, resourceType = "NETWORK")

    print network_result_set
    ourNet = ""
    for l in range(0, network_result_set.totalCount):
        print "Network type is: "  + network_result_set.list[l].networkType + " " + network_result_set.list[l].resourceUUID + " in Cluster " + network_result_set.list[l].clusterUUID
        # Correct Cluster ?
        if network_result_set.list[l].clusterUUID == cluster_uuid:
            print("Correct Cluster, at least !")
            # Exact match ?
            if network_result_set.list[l].networkType.lower() == netTypeSought.lower():
                ourNet = network_result_set.list[l].resourceUUID
            # If Network Type being sought is Public, IP is also a valid choice, if we haven't already seen a more exact match
            if ourNet == "" and netTypeSought.lower() == 'public' and network_result_set.list[l].networkType.lower() == 'ip':
                 ourNet = network_result_set.list[l].resourceUUID

    print "Will use: " + ourNet
    return ourNet


def create_nic(server_client, nic_count, network_type, cluster_uuid, vdc_uuid):
    """ function to create a nic """
    network_uuid = get_nic_uuid(server_client, network_type, cluster_uuid)
    print ("create_nic - network_uuid is:" + network_uuid)
    if (network_uuid == ''):
        network_uuid=create_network(server_client, nic_count, network_type, cluster_uuid, vdc_uuid)
        print("Created network " + network_uuid)
        
    nic_data = server_client.factory.create('nic')
    nic_data.resourceType = 'NIC'
    nic_data.clusterUUID = cluster_uuid    
    nic_data.networkUUID = network_uuid
    nic_data.vdcUUID     = vdc_uuid    
    nic_data.resourceName = "nic" + str(nic_count)
    nic_data.networkType = network_type  

    print "Calling createNetworkInterface:"
    print nic_data
    
    nic_result_set = server_client.service.createNetworkInterface(nic_data)
#    print "nic results set"
#    print nic_result_set
    nic_uuid = nic_result_set.itemUUID
    print nic_result_set
    print "++++++++++++++"
    return nic_uuid

def create_network(server_client, net_count, network_type, cluster_uuid, vdc_uuid):
    """ function to create a network """
    net_data = server_client.factory.create('network')
    net_data.resourceType = 'NETWORK'
    net_data.clusterUUID = cluster_uuid    
    net_data.vdcUUID     = vdc_uuid    
    net_data.resourceName = "net" + str(net_count)
    net_data.networkType = network_type.upper()

    print "Calling createNetwork:"
    print net_data
    
    net_result_set = server_client.service.createNetwork(net_data)
#    print "net results set"
#    print net_result_set
    net_uuid = net_result_set.itemUUID
    print net_result_set
    print "++++++++++++++"
    return net_uuid


def add_nic_to_server(server_client, server_uuid, nic_uuid, index):
    """ Function to add NIC to server """
#    print "index: " + str(index)
    ret_val = server_client.service.attachNetworkInterface(server_uuid, nic_uuid, index)
    return ret_val


def add_ip(server_client, nic_uuid, nic_ip='0.0.0.0'):
    """Function to add IP to nic"""
    if nic_ip == '0.0.0.0':
        auto = 'TRUE'
        add_ip_results = server_client.service.addIP(networkInterfaceUUID=nic_uuid,
        auto=auto)
    else:
        auto = 'FALSE'
        add_ip_results = server_client.service.addIP(networkInterfaceUUID=nic_uuid,
        ipAddress=nic_ip, auto=auto)
#    ip_address = add_ip_results.ip_address
    return add_ip_results

def get_prod_offer_uuid(server_client, prod_offer_name):
    """ Get product offer UUID when given product offer name """
    sf1 = server_client.factory.create('searchFilter')
#    print sf1
    #create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceState'
    fc1.value = 'ACTIVE'
    # debug print statement
#    print fc1
    sf1.filterConditions.append(fc1)
    fc2 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'description'
    fc2.value = prod_offer_name
    sf1.filterConditions.append(fc2)

    print("Search Filter for Product Offer " + prod_offer_name)
    print(sf1)    
                                    
    prod_offer_result_set = server_client.service.listResources(searchFilter = sf1, resourceType = "PRODUCTOFFER")
    prod_offer_uuid = prod_offer_result_set.list[0].resourceUUID
    return prod_offer_uuid


def create_server(server_client, prod_offer, image_uuid, server_name, vdc_uuid,
     server_count=1000000):
    """ Create Server for customer """
    if server_count == 1000000:
        inc_flag = 'FALSE'
    else:
        server_inc = server_count + 1
        inc_flag = 'TRUE'
    # Find product offer UUID
    sf1 = server_client.factory.create('searchFilter')
    #create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceState'
    fc1.value = 'ACTIVE'
    # debug print statement
#    print fc1
    sf1.filterConditions.append(fc1)
    fc2 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'resourceName'
    fc2.value = prod_offer
    sf1.filterConditions.append(fc2)
#    print sf1
    prod_offer_result_set = server_client.service.listResources(searchFilter = sf1, resourceType = "PRODUCTOFFER")
    print prod_offer_result_set
    prod_offer_uuid = prod_offer_result_set.list[0].resourceUUID
    # Get cluster uuid
    cluster_result_set = server_client.service.listResources(resourceType = "CLUSTER")
    cluster_uuid = cluster_result_set.list[0].resourceUUID
    # Get VDC uuid
    if vdc_uuid == '':
        vdc_uuid = get_vdc_uuid(server_client)
    # Create server
    server_data = server_client.factory.create('server')
    if inc_flag == 'TRUE':
        server_data.resourceName = server_name + " " + str(server_inc)
    else:
        server_data.resourceName = server_name
    server_data.productOfferUUID = prod_offer_uuid
    server_data.imageUUID = image_uuid
    server_data.clusterUUID = cluster_uuid
    server_data.vdcUUID = vdc_uuid
    server_data.cpu = '1'
    server_data.ram = '512'
    disk_data = server_client.factory.create('DISK')
    #disk_data = server_client.factory.create('disk')    
    disk_data.size = 20
    server_data.disk = disk_data
    print "server data in create_server:"
    print server_data
    print "that's at: "  +   strftime("%Y-%m-%d %H:%M:%S", gmtime())
    create_server_jobid = server_client.service.createServer(server_data)
#    print create_server_jobid
    server_uuid = create_server_jobid.itemUUID
    print "server_client.service.createServer returned server_uuid: " + server_uuid
    return server_uuid


def fetch_server(server_client, prod_offer, image_url, server_name, vdc_uuid,
     server_count=1000000):
    """ fetch Server for customer """
    if server_count == 1000000:
        inc_flag = 'FALSE'
    else:
        server_inc = server_count + 1
        inc_flag = 'TRUE'
    # Find product offer UUID
    sf1 = server_client.factory.create('searchFilter')
    #create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceState'
    fc1.value = 'ACTIVE'
    # debug print statement
#    print fc1
    sf1.filterConditions.append(fc1)
    fc2 = server_client.factory.create('filterConditions')
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'resourceName'
    fc2.value = prod_offer
    sf1.filterConditions.append(fc2)
#    print sf1
    prod_offer_result_set = server_client.service.listResources(searchFilter = sf1, resourceType = "PRODUCTOFFER")
    prod_offer_uuid = prod_offer_result_set.list[0].resourceUUID
    # Get cluster uuid
    cluster_result_set = server_client.service.listResources(resourceType = "CLUSTER")
    cluster_uuid = cluster_result_set.list[0].resourceUUID
    # Get VDC uuid
    if vdc_uuid == '':
        vdc_uuid = get_vdc_uuid(server_client)
    # Create server
    server_data = server_client.factory.create('server')
    if inc_flag == 'TRUE':
        server_data.resourceName = server_name + " " + str(server_inc)
    else:
        server_data.resourceName = server_name
    server_data.productOfferUUID = prod_offer_uuid
    server_data.imageUUID = image_uuid
    server_data.clusterUUID = cluster_uuid
    server_data.vdcUUID = vdc_uuid
    server_data.cpu = '1'
    server_data.ram = '512'
    disk_data = server_client.factory.create('DISK')
    disk_data.size = 20
    server_data.disk = disk_data
#    print "server data"
#    print server_data
    print "server_data in fetch_server at :" +  +   strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print server_data
    print "=============================--======"
    create_server_jobid = server_client.service.createServer(server_data)
#    print create_server_jobid
    server_uuid = create_server_jobid.itemUUID
    print "fetch_server returned server_uuid: " + server_uuid
    print ""  +   strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print "=============================---======"
    
    return server_uuid


def wait_for_install(server_client, server_uuid):
    """ Check Server has completed creation """
    sf = server_client.factory.create('searchFilter')
    # debug print statement	
#    print sf
    #create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = server_uuid
    sf.filterConditions.append(fc1)
    fc2 = server_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'resourceState'
    fc2.value = 'ACTIVE'
    sf.filterConditions.append(fc2)
#    print "sf:"
#    print sf
    server_created = server_client.service.listResources(searchFilter = sf, resourceType = "SERVER")
#    print server_created
    i = 0
#    print "server created count:" + str(server_created.totalCount)
    # currently waiting for 100 seconds (up to 10 loops of a 10 second sleep)
    while (server_created.totalCount < 1) and (i <= 10):
        print "in wait_for_install loop i = " + str(i) + ", count " + str(server_created.totalCount)
        i = i + 1
        # wait a while
        time.sleep(10)
        server_created = server_client.service.listResources(searchFilter = sf, resourceType = "SERVER")
#        print "server created count:" + str(server_created.totalCount)
    print "wait_for_install - created count is: " + str(server_created.totalCount)
    if server_created.totalCount == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val


def wait_for_server(server_client, server_uuid, status):
    """ Check Server has completed creation """
    sf = server_client.factory.create('searchFilter')
    # debug print statement	
#    print sf
    #create filter conditions object
    fc1 = server_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'
    fc1.value = server_uuid
    sf.filterConditions.append(fc1)
    fc2 = server_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc2.condition = 'IS_EQUAL_TO'
    fc2.field = 'status'
    fc2.value = status
    sf.filterConditions.append(fc2)
#    print "sf:"
#    print sf
    server_result = server_client.service.listResources(searchFilter = sf, resourceType = "SERVER")
#    print server_created
    i = 0
#    print "server created count:" + str(server_created.totalCount)
    while (server_result.totalCount < 1) and (i <= 24):
        print "in wait_for_server loop i = " + str(i) + ", count " + str(server_result.totalCount)
        i = i + 1
        # wait a while
        time.sleep(5)
        server_result = server_client.service.listResources(searchFilter = sf, resourceType = "SERVER")
#        print "server created count:" + str(server_created.totalCount)
    print("wait_for_server(): exit after " + str(i) + " tries")
    if server_result.totalCount == 1:
        return_val = 0
    else:
        return_val = 1
    return return_val


def get_server_uuid(server_client, server_num):
    # Function to get server uuid given server name
    # setup server return value
    ret_server = server_num - 1
    server_result_set = server_client.service.listResources(resourceType = "SERVER")
    #extract number of Servers from result set
#    print server_result_set
    server_uuid = server_result_set.list[ret_server].resourceUUID
    print "server uuid: " + server_uuid
    return server_uuid


def get_server_state(server_client, server_uuid):
    # Function to get server state given server uuid
    # setup search filter object	
    sf = server_client.factory.create('searchFilter')
    #create filter conditions object
    fc = server_client.factory.create('filterConditions')
    # set filter condition values
    fc.condition = 'IS_EQUAL_TO'
    fc.field = 'resourceUUID'
    fc.value = server_uuid
#    print fc
    sf.filterConditions.append(fc)
#    print sf
    # call to listBillingEntities service with search filter
    server_result_set = server_client.service.listResources(searchFilter = sf, resourceType = "SERVER")
    #extract number of Servers from result set
#    print server_result_set
    server_status = server_result_set.list[0].status
#    print "server status: " + server_status
    return server_status


def get_server_name(server_client, server_uuid):
    """ Function to get server state given server uuid """
    # setup search filter object
    sf = server_client.factory.create('searchFilter')
    #create filter conditions object
    fc = server_client.factory.create('filterConditions')
    # debug print statement
#    print fc
    # set filter condition values
    fc.condition = 'IS_EQUAL_TO'
    fc.field = 'resourceUUID'
    fc.value = server_uuid
    # debug print statement
#    print fc
    sf.filterConditions.append(fc)
#    print sf
    # call to listBillingEntities service with search filter
    server_result_set = server_client.service.listResources(searchFilter=sf, resourceType="SERVER")
    #extract number of Servers from result set
#    print server_result_set
    server_name = server_result_set.list[0].resourceName
    print "server name: " + server_name
    return server_name


def change_server_status(server_client, server_uuid, state):
    """ Check for status of server """
    if state == "SHUTDOWN":
        server_client.service.changeServerStatus(serverUUID=server_uuid, newStatus=state, safe=True)
    else:
       server_client.service.changeServerStatus(serverUUID=server_uuid, newStatus=state, safe=True)
    server_result = wait_for_server(server_client, server_uuid, state)
    if server_result == 1:
        print "Problem changing server status, check platform, server uuid: " + server_uuid
    else:
        print "server status changed ok, server uuid: " + server_uuid
    return server_result


def create_disk(server_client, prod_offer, disk_size, vdc_uuid):
    """ Function to create disk """
    # get prod offer uuid
    prod_offer_uuid = get_prod_offer_uuid(server_client, prod_offer)
    # setup skeleton disk data structure
    skel_disk = server_client.factory.create('disk')
    skel_disk.resourceType = "DISK"
    skel_disk.productOfferUUID = prod_offer_uuid
    skel_disk.size = disk_size
    skel_disk.vdcUUID = vdc_uuid
    disk_job = server_client.service.createDisk(skeletonDisk=skel_disk)
    disk_uuid = disk_job.itemUUID
    return disk_uuid


def add_disk_to_server(server_client, server_uuid, disk_uuid):
    """ Function to add disk to specified server """
    server_client.service.attachDisk(serverUUID=server_uuid, diskUUID=disk_uuid)


def get_server_data(server_client, server_uuid):
    """ Function to return all data for specified server """
    # setup search filter object
    sf = server_client.factory.create('searchFilter')
    #create filter conditions object
    fc = server_client.factory.create('filterConditions')
    # set filter condition values
    fc.condition = 'IS_EQUAL_TO'
    fc.field = 'resourceUUID'
    fc.value = server_uuid
#    print fc
    sf.filterConditions.append(fc)
#    print sf
    # call to listBillingEntities service with search filter
    server_result_set = server_client.service.listResources(searchFilter=sf, resourceType="SERVER")
    #extract number of Servers from result set
#    print server_result_set
    return server_result_set

def list_server(auth_client, server_uuid):
    sf = auth_client.factory.create('searchFilter')
    fc1 = auth_client.factory.create('filterConditions')
    fc1.condition = 'IS_EQUAL_TO'
    fc1.field = 'resourceUUID'   
    fc1.value = server_uuid
    sf.filterConditions.append(fc1)
    server_result_set = auth_client.service.listResources(searchFilter = sf,resourceType = 'SERVER')
    #extract number of Servers from result set
    if (server_result_set.totalCount == 0):
      msg = "ERROR: Server with uuid " + server_uuid + " not found."
      return msg

    print server_result_set;
    server_data = server_result_set.list[0]
    print server_data
    return server_data

