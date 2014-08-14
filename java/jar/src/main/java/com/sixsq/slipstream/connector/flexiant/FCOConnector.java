package com.sixsq.slipstream.connector.flexiant;

/*
 * +=================================================================+
 * SlipStream Example Cloud Connector
 * =====
 * Copyright (C) 2013 SixSq Sarl (sixsq.com)
 * =====
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * -=================================================================-
 */

import java.io.IOException;
import java.util.Iterator;
import java.util.Map;
import java.util.Properties;
import java.util.logging.Logger;

import com.sixsq.slipstream.configuration.Configuration;
import com.sixsq.slipstream.connector.CliConnectorBase;
import com.sixsq.slipstream.connector.Connector;
import com.sixsq.slipstream.credentials.Credentials;
import com.sixsq.slipstream.exceptions.ConfigurationException;
import com.sixsq.slipstream.exceptions.InvalidElementException;
import com.sixsq.slipstream.exceptions.ServerExecutionEnginePluginException;
import com.sixsq.slipstream.exceptions.SlipStreamClientException;
import com.sixsq.slipstream.exceptions.SlipStreamException;
import com.sixsq.slipstream.exceptions.SlipStreamInternalException;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.DeploymentModule;
import com.sixsq.slipstream.persistence.ImageModule;
import com.sixsq.slipstream.persistence.Module;
import com.sixsq.slipstream.persistence.ModuleCategory;
import com.sixsq.slipstream.persistence.ModuleParameter;
import com.sixsq.slipstream.persistence.Node;
import com.sixsq.slipstream.persistence.Run;
import com.sixsq.slipstream.persistence.ServiceConfigurationParameter;
import com.sixsq.slipstream.persistence.User;
import com.sixsq.slipstream.persistence.UserParameter;
import com.sixsq.slipstream.util.ProcessUtils;

/*

 */
public class FCOConnector extends CliConnectorBase {

	// The name of the cloud service.
	public static final String CLOUD_SERVICE_NAME = "flexiant";
	// So we can see what is going on
	private final static Logger log = Logger.getLogger(FCOConnector.class.getName());

	private final static String INSTALL_PATH = "/opt/slipstream/connectors/bin";

	/**
	 * Python module with the corresponding client cloud connector. This should
	 * be set as CLOUDCONNECTOR_PYTHON_MODULENAME environment variable when
	 * provisioning the Orchestrator VM in launch() method. See OpenStackConnector
	 * and StratusLabConnector connectors.
	 */
	//public static final String CLOUDCONNECTOR_PYTHON_MODULENAME = "slipstream.cloudconnectors.flexiant.FlexiantClientCloud";
	public static final String CLOUDCONNECTOR_PYTHON_MODULENAME = "flexiant.FlexiantClientCloud";

	public FCOConnector() {
		//super(CLOUD_SERVICE_NAME);
		this(CLOUD_SERVICE_NAME);
	}

	public FCOConnector(String instanceName) {
		super(instanceName);
		log.info("FCOConnector(" + instanceName + ")");
	}

	public Connector copy(){
		return new FCOConnector(getConnectorInstanceName());
	}

	public String getCloudServiceName() {
		return CLOUD_SERVICE_NAME;
	}
	/**
	 * The implementation flow is usually as follows
	 *  - initialize cloud driver
	 *  - launch Orchestrator VM
	 *  - get cloud ID and IP of the Orchestrator VM
	 *  - update Run with the Orchestrator cloud ID and IP
	 *
	 * See OpenStackConnector and StratusLabConnector connector classes for the
	 * implementation hints.
	 *
	 * @param run
	 *            for which corresponding virtual machines must be launched
	 * @param user
	 *            owner of the run
	 * @throws SlipStreamException
	 */
	public Run launch(Run run, User user) throws SlipStreamException {

		if (run != null){
			log.info("Run.description:" + run.getDescription());
			log.info("Run.Name:" + run.getName());
		}

		validate(run, user);

		String command;
		try {
			command = getRunInstanceCommand(run, user);
		} catch (IOException e) {
			throw (new SlipStreamException(
					"Failed getting run instance command", e));
		}
//		log.info("Command is: " + command);

		String result;
		String[] commands = { "sh", "-c", command };
		try {
			result = ProcessUtils.execGetOutput(commands);
		} catch (IOException e) {
			e.printStackTrace();
			throw (new SlipStreamInternalException(e));
		} finally {
			deleteTempSshKeyFile();
		}

		// On success, the startup script (is expected to) spit out
		// just a UUID and it's IP address. We return just a bit more than
		// that so pull out the bits we need
		log.info("Launch gave us back: " + result);
		
		String[] instanceData = parseRunInstanceResult(result);

		log.info("instanceData: " + instanceData[0] + " " + instanceData[1]);

		updateInstanceIdAndIpOnRun(run,
								   instanceData[0],		// instance UUID
								   instanceData[1]		// ipAddress
								   );

//		log.info("instanceData: updated");
		return run;
	}

	public void terminate(Run run, User user) throws SlipStreamException {

		log.info("Terminating all FCO instances.");

		String command = INSTALL_PATH + "/destroy-vm.py "
						+ getRequiredParams(user)
						;
		// 	Need to check what getCloudNodeInstanceIds() returns for FCO with multiple VMs
		for (String id : getCloudNodeInstanceIds(run)) {
			String[] commands = { "sh", "-c", command + " --server-uuid " + id };
			log.info("kill uuid " + id);
			try {
				ProcessUtils.execGetOutput(commands);
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	private String createContextualizationData(Run run, User user)
			throws ConfigurationException, InvalidElementException,
			ValidationException {

		if (run != null){
			log.info("Orchestartion Context: " + isInOrchestrationContext(run));
		}

		String cookie = getCookieForEnvironmentVariable(user.getName(), run.getUuid());

		Configuration configuration = Configuration.getInstance();

		String verbosityLevel = getVerboseParameterValue(user);

		String nodename = Run.MACHINE_NAME;
        if(isInOrchestrationContext(run)){
        	nodename = getOrchestratorName(run);
        }

		// Context string needs to be wrapped in CDATA[] to get it past Jade validation, and
		// the whole thing needs to be single-quoted to stop the shell trying to interpret
		// parts of the data too....
		String contextualization ="'";
		contextualization += "<celar-code><![CDATA[";

		contextualization += "export SLIPSTREAM_DIID=" + run.getName() + "#";
		contextualization += "export SLIPSTREAM_SERVICEURL=" + configuration.baseUrl
				+ "#";
		contextualization += "export SLIPSTREAM_NODENAME=" + nodename
				+ "#";
		contextualization += "export SLIPSTREAM_CATEGORY="
				+ run.getCategory().toString() + "#";
		contextualization += "export SLIPSTREAM_USERNAME=" + user.getName() + "#";

		contextualization += "export SLIPSTREAM_COOKIE=" + cookie + "#";

		contextualization += "export SLIPSTREAM_VERBOSITY_LEVEL=" + verbosityLevel
				+ "#";
		contextualization += "export SLIPSTREAM_CLOUD=" + getCloudServiceName() + "#";
		contextualization += "export SLIPSTREAM_CONNECTOR_INSTANCE="
				+ getConnectorInstanceName() + "#";

		contextualization += "export SLIPSTREAM_BUNDLE_URL="
				+ configuration
						.getRequiredProperty("slipstream.update.clienturl")
				+ "#";

		contextualization += "export CLOUDCONNECTOR_BUNDLE_URL="
				+ configuration
						.getRequiredProperty(constructKey("update.clienturl"))
				+ "#";

		contextualization += "export CLOUDCONNECTOR_PYTHON_MODULENAME="
				+ CLOUDCONNECTOR_PYTHON_MODULENAME + "#";

		contextualization += "export SLIPSTREAM_BOOTSTRAP_BIN="
				+ configuration
						.getRequiredProperty("slipstream.update.clientbootstrapurl")
				+ "#";

		contextualization += "export SLIPSTREAM_REPORT_DIR=" + SLIPSTREAM_REPORT_DIR;

		contextualization += "#" + constructInstallDependenciesCommand();
		contextualization += "#" + constructScriptExecCommand(run);
		contextualization += "]]></celar-code>";	// Close <!CData[[...
		contextualization += "'";					// Close single quotes we've wrapped around the entire context script

		String xmlSafecontextualization = contextualization.replaceAll("&","&amp;");
		log.info("Contextulization is:" + xmlSafecontextualization);

		return xmlSafecontextualization;

	}

	private String constructScriptExecCommand(Run run) throws ConfigurationException, ValidationException {

		Configuration configuration = Configuration.getInstance();

		String bootstrap = "/tmp/slipstream.bootstrap";
		String bootstrapUrl = configuration
				.getRequiredProperty("slipstream.update.clientbootstrapurl");

		String mode = " ";
        if(isInOrchestrationContext(run)){
        	mode = " slipstream-orchestrator ";
        }

		return "SCRIPT_EXEC=\"sleep 15; mkdir -p " + SLIPSTREAM_REPORT_DIR
				+ "; wget --no-check-certificate -O " + bootstrap + " "
				+ bootstrapUrl + " > " + SLIPSTREAM_REPORT_DIR
				+ "/orchestrator.slipstream.log 2>&1 && chmod 0755 "
				+ bootstrap + "; " + bootstrap + mode + " >> "
				+ SLIPSTREAM_REPORT_DIR + "/orchestrator.slipstream.log 2>&1\""
				+ "#eval ${SCRIPT_EXEC}";  // N.B. The # character is needed for the Perl split() to latch on to
	}

	private String constructInstallDependenciesCommand() throws ConfigurationException {

		String log = "/tmp/slipstream_deps_$$.log";

		return "INSTALL_EXEC=\"test -x /usr/bin/apt-get  && "
				+ "apt-get update " + " >" + log + " 2>&1"
				+ " && apt-get -y install python-suds "  + " >" + log + " 2>&1\""
				+ "#eval ${INSTALL_EXEC}";  // N.B. The # character is needed for the Perl split() to latch on to
	}

//	private String[] parseResult(String result)
//			throws SlipStreamClientException {
//
//		final String completedMsg = "Server UUID and IP:";
//
//		log.info("parseResult: result is" + result);
//
//		if (result == null){
//			throw (new SlipStreamClientException("Got null result for launch command"));
//		}
//
//		int n = result.indexOf(completedMsg);
//		log.info("parseReuslt: n is " + n);
//
//		if (n > -1){
//			String res = result.substring(completedMsg.length()+n);
//			log.info("parseResult(): " + res);
//			String[] parts = res.trim().split(":");
//
//			// Should be four elements, as the substring() junked the "Server UUID..." part
//			if (parts.length == 4){
//				String[] answer = new String[2];
//
//				answer[0] = parts[0];	// Server UUID
//				answer[1] = parts[3];	// Server IP
//				log.info("Server UUID plus IP: " + answer[0] + " " + answer[1]);
//				return answer;
//			}
//		}
//
//		// Assume it was an error if we didn't see the string that
//		// tells us what the server UUID and IP were
//
//		throw (new SlipStreamClientException("Error returned by launch command. Got: " + result));
//
//	}

	private void validate(Run run, User user) throws ValidationException, SlipStreamException {
		validateCredentials(user);
//		validateUserSshPublicKey(user);
//		validateMarketplaceEndpoint(user);
		validateLaunch(run, user);
	}

	protected void validateBaseParameters(User user) throws ValidationException {
		String errorMessageLastPart = ". Please contact your SlipStream administrator.";

		String endpoint = getEndpoint(user);
		if (endpoint == null || "".equals(endpoint)) {
			throw (new ValidationException("Cloud Endpoint cannot be empty. "+ errorMessageLastPart));
		}

		// Do we need to check the FCO UUID is set here ?
	}

	protected String getInstanceType(Run run, User user) throws ValidationException{
		return (isInOrchestrationContext(run)) ?
				user.getParameter(constructKey(FCOUserParametersFactory.ORCHESTRATOR_INSTANCE_TYPE_PARAMETER_NAME)).getValue() :
				getInstanceType( ImageModule.load(run.getModuleResourceUrl()) );
	}

	protected String getCustomerUUID(User user) throws ValidationException{
		String s = 	user.getParameter(constructKey(FCOUserParametersFactory.PARAM_CUSTOMER_UUID)).getValue();
		return s;
	}

	private void validateLaunch(Run run, User user)
			throws ConfigurationException, SlipStreamClientException, ServerExecutionEnginePluginException{
		validateCredentials(user);
		validateBaseParameters(user);

		// Any more validation needed here ?
	}

	// This needs to invoke a script which lists ALL VMs for the customer and
	// output them in the format:
	//
	// id         state       <- header line
	// nnnn       STATE      <- nnnn=id (assume uuid), STATE=RUNNING/STOPPED etc
	//
	// Note the headee line - this is required as it will be stripped later
	public Properties describeInstances(User user) throws SlipStreamException {

		validateUserParams(user);

		String command = INSTALL_PATH + "/fco-list-vms-for-customer.py "
				+ getRequiredParams(user)
				;

		String result;
		String[] commands = { "sh", "-c", command };

		try {
			result = ProcessUtils.execGetOutput(commands);
		} catch (IOException e) {
			e.printStackTrace();
			throw (new SlipStreamInternalException(e));
		}

		Properties p;
		try{
			p = parseDescribeInstanceResult(result);
		}
		catch (SlipStreamException e){
			// So we can see if parseDescribeInstanceResult() fails
			log.info("" + e.getLocalizedMessage());
			throw(e);
		}
//		System.out.println("=== Properties being returned by FCOConnector =====");
//		p.list(System.out);
//		System.out.println("=== End Properties being returned by FCOConnector =====");
		return p;
	}

	@Override
	public Credentials getCredentials(User user) {
		return new FCOCredentials(user, getConnectorInstanceName());
	}

	@Override
	public Map<String, UserParameter> getUserParametersTemplate()
			throws ValidationException{
		return new FCOUserParametersFactory(getConnectorInstanceName()).getParameters();
	}

	@Override
	public Map<String, ModuleParameter> getImageParametersTemplate()
			throws ValidationException {
		Map<String, ModuleParameter> map = new FCOImageParametersFactory(getConnectorInstanceName())
		.getParameters();
		log.info("Map: " + map);

		//Map<String, String> map = new HashMap<String, String>();
		for (Iterator<String> iterator = map.keySet().iterator(); iterator.hasNext();) {
		    String key = (String) iterator.next();
		    log.info("" + key + ": " + map.get(key).getSafeValue());
		}

		return map;
	}

	@Override
	public Map<String, ServiceConfigurationParameter> getServiceConfigurationParametersTemplate()
			throws ValidationException {
		return new FCOSystemConfigurationParametersFactory(getConnectorInstanceName())
				.getParameters();
	}

	protected String getNetworkType(Run run) throws ValidationException{
		log.info("In getNetworkType()");
		log.info("Run Type is " + run.getType());
		if (isInOrchestrationContext(run)) {
			log.info("Done getNetworkType() - return IP as isInOrchestrationContext() is true");
			return "IP";	// Public Virtual IP
		} else {
			ImageModule machine = ImageModule.load(run.getModuleResourceUrl());
			String s = machine.getParameterValue(ImageModule.NETWORK_KEY, null);
			log.info("Done getNetworkType() with type " + s);
			return s;
		}
	}

	@Override
	protected String constructKey(String key) throws ValidationException {
		log.info("In constructKey()");
		return new FCOUserParametersFactory(getConnectorInstanceName()).constructKey(key);
	}

	private String getVmName(Run run) {
		return isInOrchestrationContext(run) ? getOrchestratorName(run)
				: "vm";
	}

	private String getRequiredParams(User user) throws ValidationException
	{
		String args = " --cust-uuid " +  getCustomerUUID(user)
					+ " --cust-username " +  getKey(user)
					+ " --cust-password " + getSecret(user)
					+ " --api-host " + getEndpoint(user)
					+ " ";

		return args;
	}

	private String getRunInstanceCommand(Run run, User user)
			throws InvalidElementException, ValidationException,
			SlipStreamClientException, IOException, ConfigurationException,
			ServerExecutionEnginePluginException {

		log.info("In getRunInstanceCommand()");

		String context = createContextualizationData(run, user);
		String publicSshKey = getPublicSshKey(run, user);
		String imageId = getImageId(run, user);
		String vmName = getVmName(run);
		String ramMb = null;
		String cpuCount = null;
		ImageModule image = null;

//		String extraDisksCommand = getExtraDisksCommand(run);

		log.info("Some Parameter Values:\n");
		log.info("Mod Cat: " + run.getCategory());
		if (run.getCategory() == ModuleCategory.Image){
			image = ImageModule.load(run.getModuleResourceUrl());
			ramMb = getRam(image);
			cpuCount = getCpu(image);
			log.info("RAM from image is: " + ramMb);
			log.info("CPU from image is: " + cpuCount);
		}
		else if (run.getCategory() == ModuleCategory.Deployment){
			Module module = run.getModule();

            for (Node node : ((DeploymentModule) module).getNodes().values()){
            	log.info("Node Description: " + node.getDescription());
            	image = node.getImage();
            	ramMb = getRam(image);
            	cpuCount = getCpu(image);
            	log.info("RAM from Deployment image is: " + ramMb);
            	log.info("CPU from Deployment image is: " + cpuCount);

            }
		}

		// Path needs to match that in python/rpm/pom.xml
		return INSTALL_PATH + "/fco-run-instance "
				+ getRequiredParams(user)
				+ " --image-uuid " + imageId
				+ " --network-type " + getNetworkType(run)
//				+ " --quiet "
				+ " --public-key '" + publicSshKey + "'"
//  			+ " -u " + getKey(user)
				//+ " -p "
				+ " --context " + context
				+ " --vm-name " + vmName + ":" + run.getName()
				+ " --disk-size " + "50"
				+ " --ram " + ramMb
				+ " --cpu " + cpuCount
//				+  + extraDisksCommand
				;
	}

	protected void validateUserParams(User user) throws ValidationException {
		String errorMessageLastPart = getErrorMessageLastPart(user);

		if (user == null ){
			throw (new ValidationException(
					"Cloud User details cannot be null"
							+ errorMessageLastPart));
		}

		if (getKey(user) == null) {
			throw (new ValidationException(
					"Cloud Username cannot be empty"
							+ errorMessageLastPart));
		}
		if (getSecret(user) == null) {
			throw (new ValidationException(
					"Cloud Password cannot be empty"
							+ errorMessageLastPart));
		}
	}

}
