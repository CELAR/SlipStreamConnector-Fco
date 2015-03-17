import re
import time

from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector
from slipstream.NodeDecorator import KEY_RUN_CATEGORY
from flexiant.FCOMakeOrchestrator import MakeVM
from flexiant.FCODestroy import DestroyVM
from flexiant.FCOListVM import ListVM
from flexiant.ImageActions import ImageDisk
from flexiant.VMActions import StopVM
from flexiant.VMActions import WaitUntilVMRunning
from slipstream.exceptions.Exceptions import CloudError, ExecutionException
from flexiant.packages.fco_rest import list_servers


def getConnector(configHolder):
    return getConnectorClass()(configHolder)


def getConnectorClass():
    return FlexiantClientCloud


class FlexiantClientCloud(BaseCloudConnector):

    cloudName = 'flexiant'

    NODE_STATE_WAITING_SLEEP = 3
    NODE_STARTUP_TIMEOUT = 2 * 60

    def __init__(self, configHolder):
        super(FlexiantClientCloud, self).__init__(configHolder)
        self.run_category = getattr(configHolder, KEY_RUN_CATEGORY, None)
        self.verbose = (int(self.verboseLevel) > 2) and True or False

        self._set_capabilities(contextualization=True,
                               direct_ip_assignment=True,
                               orchestrator_can_kill_itself_or_its_vapp=True)
#        cloudName = self.get_cloud_service_name()
#        print("cloudName=" + cloudName)

    def _initialization(self, user_info, **kwargs):
        self.user_info = user_info

        # if self.is_deployment():
        #    self._import_keypair(user_info)
        # elif self.is_build_image():
        #    self._create_keypair_and_set_on_user_info(user_info)

    def _finalization(self, user_info):
        pass

    def _start_image(self, user_info, node_instance, vm_name):
        return self._start_image_on_flexiant(user_info, node_instance, vm_name)

    def _start_image_on_flexiant(self, user_info, node_instance, vm_name):

        self._print_detail("In _start_image_on_flexiant")
#        print("get_cloud_service_name() reports: " + self.get_cloud_service_name())
        self._print_detail("user_info: " + str(user_info))
        self._print_detail("node_instance: " + str(node_instance))

        ram, cpu = self._get_cpu_and_ram(node_instance)
        self._print_detail("ram is " + ram + ", CPU count is " + cpu)

        image_id = node_instance.get_image_id()
        self._print_detail("image ID: " + image_id)

        instance_name = self._format_instance_name(vm_name)
        self._print_detail("instance_name: " + instance_name)

        ip_type = node_instance.get_network_type()
        self._print_detail("ip_type: " + ip_type)

        context_script = self._get_context_script(node_instance)
        self._print_detail("context_script: " + context_script)

        public_key = user_info.get_public_keys()

        extra_disk_str = node_instance.get_volatile_extra_disk_size()
        try:
            extra_disk_size = int(extra_disk_str)
        except:
            extra_disk_size = 0

        self._print_detail("extra_disk_size: " + str(extra_disk_size))

        try:
            ret = MakeVM(
                image_id,
                user_info.get_cloud('user.uuid'),
                user_info.get_cloud_username(),
                user_info.get_cloud_password(),
                user_info.get_cloud_endpoint(),
                ip_type,
                extra_disk_size,
                ram,
                instance_name,
                cpu,
                public_key,
                self.verbose,
                context_script)
        except Exception as ex:
            raise CloudError('Failed to start VM from image %s with: %s' % \
                             (image_id, str(ex)))

        vm = dict(
            networkType=ip_type,
            instance=ret['server_uuid'],
            ip=ret['ip'],
            id=ret['server_uuid'],
            resourceUUID=ret['server_uuid'],
            password=ret['password'],
            login=ret['login'])

        return vm

#    def _import_keypair(self, user_info):
#        kp_name = 'ss-key-%i' % int(time.time())
#        public_key = user_info.get_public_keys()
#        try:
#            kp = ex_import_keypair_from_string(kp_name, public_key)
#        except Exception as ex:
#            raise CloudError('Cannot import the public key. Reason: %s' % ex)
#        kp_name = kp.name
#        user_info.set_keypair_name(kp_name)
#        return kp_name
#
#    def _create_keypair_and_set_on_user_info(self, user_info):
#        kp_name = 'ss-build-image-%i' % int(time.time())
#        kp = ex_create_keypair(kp_name)
#        user_info.set_private_key(kp.private_key)
#        user_info.set_keypair_name(kp.name)
#        return kp.name

    def _get_cpu_and_ram(self, node_instance):
        ram = node_instance.get_ram()
        cpu = node_instance.get_cpu()

        if ram is None:
            ram = '512'
            self._print_detail("Defaulting RAM to " + ram)

        if cpu is None:
            cpu = '1'
            self._print_detail("Defaulting CPU count to " + cpu)

        return str(ram), str(cpu)

    def _get_context_script(self, nodename):
        preExport = "<celar-code><![CDATA["
        preBoot = "echo This is the pre-boot"
        postBoot = "]]></celar-code>"
        return self._get_bootstrap_script(nodename, preExport, preBoot, postBoot)

    def _stop_deployment(self):
        ids = [vm['id'] for vm in self.get_vms().itervalues()]
        self._stop_vms_by_ids(ids)

    def _stop_vms_by_ids(self, ids):
        self._print_detail("Stopping instances: " + str(ids))
        for instance_id in ids:
            self._print_detail("Stopping instance: " + str(instance_id))
            try:
                DestroyVM(
                    instance_id,
                    self.user_info.get_cloud('user.uuid'),
                    self.user_info.get_cloud_username(),
                    self.user_info.get_cloud_password(),
                    self.user_info.get_cloud_endpoint(),
                    self.verbose)
            except Exception as ex:
                raise CloudError('Failed to destroy VM %s with: %s' % \
                                 (instance_id, str(ex)))

    def _vm_get_ip(self, vm):
        return vm['ip']

    def _vm_get_id(self, vm):
        # Allow to work with the local VM representation as well as with the
        # server object (as returned by API).
        return vm.get('id', vm['resourceUUID'])

    def _vm_get_state(self, vm):
        return vm['status']

    def _wait_vm_in_state_running_or_timeout(self, vm_id):
        self._wait_vm_in_state_or_timeout(vm_id, 'RUNNING',
                                          self.NODE_STARTUP_TIMEOUT)

    def _wait_vm_in_state_or_timeout(self, vm_id, state, timeout):
        self._print_detail("Waiting %i sec for node %s to enter state '%s'." %
                           (timeout, vm_id, state))

        vm_state = self._get_vm_state(vm_id)
        t_end = time.time() + timeout
        while vm_state != state:
            if time.time() >= t_end:
                raise CloudError("Node %s didn't reach state '%s' in %i sec." % \
                                 (vm_id, state, timeout))
            time.sleep(self.NODE_STATE_WAITING_SLEEP)
            vm_state = self._get_vm_state(vm_id)

    def _get_vm_state(self, vm_id):
        try:
            ret = ListVM(
                vm_id,
                self.user_info.get_cloud('user.uuid'),
                self.user_info.get_cloud_username(),
                self.user_info.get_cloud_password(),
                self.user_info.get_cloud_endpoint(),
                self.verbose)
        except Exception as ex:
            raise CloudError('Failed to list VM %s with: %s' % (vm_id, str(ex)))
        if not ret:
            raise CloudError('Failed to list VM %s: result is empty')

        return str(ret.status)

    def _build_image(self, user_info, node_instance):
        # TODO: implement new image build.
        #
        # self._build_image_increment(user_info, node_instance, ip)

        # super(FlexiantClientCloud, self)._build_image()
        ret = self._buildImageOnFlexiant(user_info, node_instance)
        return ret

    def _buildImageOnFlexiant(self, user_info, node_instance):
        print("_buildImageOnFlexiant:")
        print("=====================")
        print user_info
        print("----")
        print node_instance

        machine_name = node_instance.get_name()
        vm = self._get_vm(machine_name)

        print("\n vm: %s \n" % str(vm))
        ip_address = vm['ip']
        vm_uuid = vm['id']

        # Username and password need to be copied to the node info dict
        # node_instance.set('Flexiant.user', vm['login'])
        # node_instance.set('Flexiant.password', vm['password'])

        print("node_instance is now:")
        print node_instance

        print("_buildImageOnFlexiant(): ip_address=" + ip_address + ", uuid=" + vm_uuid)

        try:
            ret = WaitUntilVMRunning(
                vm_uuid,
                self.user_info.get_cloud('user.uuid'),
                self.user_info.get_cloud_username(),
                self.user_info.get_cloud_password(),
                self.user_info.get_cloud_endpoint(),
                self.verbose)
        except Exception as ex:
            raise CloudError('VM %s did not make it to running state with: %s' % (vm_uuid, str(ex)))

        print("_buildImageOnFlexiant(): VM is running")

        node_instance.set_image_attributes({'Flexiant.user': vm['login']})
        node_instance.set_image_attributes({'Flexiant.password': vm['password']})

        node_instance.set_image_attributes({'loginUser' : vm['login']})
        node_instance.set_image_attributes({'login.password' : vm['password']})

        # Temporary bodge to set password on NodeInstance object in the correct
        # place for framework code to pick it up
        vm_password = vm['password']
        print("Passing password for VM: " + vm_password)
        node_instance._NodeInstance__set(node_instance.get_cloud() + '.login.password', vm_password)

        print("node_instance before _build_image_increment() ")
        print node_instance
        print("--------")

        # Now make the changes to the image
        self._build_image_increment(user_info, node_instance, ip_address)

        # Stop the VM (needs to be stopped to image it)
        try:
            ret = StopVM(
                vm_uuid,
                self.user_info.get_cloud('user.uuid'),
                self.user_info.get_cloud_username(),
                self.user_info.get_cloud_password(),
                self.user_info.get_cloud_endpoint(),
                self.verbose)
        except Exception as ex:
            raise CloudError('Failed to stop VM %s with: %s' % (vm_uuid, str(ex)))

        # Image the VM's disk
        image_default_user = node_instance.get_username()
        try:
            ret = ImageDisk(
                vm_uuid,
                0,
                self.user_info.get_cloud('user.uuid'),
                self.user_info.get_cloud_username(),
                self.user_info.get_cloud_password(),
                self.user_info.get_cloud_endpoint(),
                image_default_user,
                self.verbose)
        except Exception as ex:
            raise CloudError('Failed to create image from disk of VM %s with: %s' % (vm_uuid, str(ex)))

        print ("UUID of new image is " + ret.resourceUUID)
        print("end _buildImageOnFlexiant()")

        return ret.resourceUUID

    def waitUntilVMRunning(self, instanceId):
        timeWait = 120
        timeStop = time.time() + timeWait
        state = ''
        while state != 'RUNNING':
            if time.time() > timeStop:
                raise ExecutionException(
                     'Timed out while waiting for instance "%s" to reach running state'
                     % instanceId)
            print("waitUntilVMRunning(): VMState is: " + state)
            time.sleep(1)
            state = self._get_vm_state(instanceId)

        print("waitUntilVMRunning(): VM is UP")

    def list_instances(self):
        servers = list_servers(self.user_info.get_cloud_endpoint(),
                               self.user_info.get_cloud_username(),
                               self.user_info.get_cloud('user.uuid'),
                               self.user_info.get_cloud_password())
        return servers

    #
    # Helper methods
    #
    def _format_instance_name(self, name):
        name = self._remove_bad_char_in_instance_name(name)
        return self._truncate_instance_name(name)

    @staticmethod
    def _truncate_instance_name(name):
        if len(name) <= 63:
            return name
        else:
            return name[:31] + '-' + name[-31:]

    @staticmethod
    def _remove_bad_char_in_instance_name(name):
        try:
            newname = re.sub(r'[^a-zA-Z0-9-]', '-', name)
            m = re.search('[a-zA-Z]([a-zA-Z0-9-]*[a-zA-Z0-9]+)?', newname)
            return m.string[m.start():m.end()]
        except:
            msg = ('Cannot handle the instance name "%s".' % name) + \
                ' Instance name can contain ASCII letters "a" through "z", ' + \
                'the digits "0" through "9", and the hyphen ("-"), must be ' + \
                'between 1 and 63 characters long, and can\'t start or end ' + \
                'with "-" and can\'t start with digit'
            raise ExecutionException(msg)
