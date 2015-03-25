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


import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

import javax.xml.bind.DatatypeConverter;

import com.sixsq.slipstream.configuration.Configuration;
import com.sixsq.slipstream.connector.CliConnectorBase;
import com.sixsq.slipstream.connector.Connector;
import com.sixsq.slipstream.credentials.Credentials;
import com.sixsq.slipstream.exceptions.ConfigurationException;
import com.sixsq.slipstream.exceptions.InvalidElementException;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.ImageModule;
import com.sixsq.slipstream.persistence.ModuleParameter;
import com.sixsq.slipstream.persistence.Run;
import com.sixsq.slipstream.persistence.ServiceConfigurationParameter;
import com.sixsq.slipstream.persistence.User;
import com.sixsq.slipstream.persistence.UserParameter;

/*

 */
public class FCOConnector extends CliConnectorBase {

	private final static Logger log = Logger.getLogger(FCOConnector.class.getName());

	public static final String CLOUD_SERVICE_NAME = "flexiant";
	public static final String CLOUDCONNECTOR_PYTHON_MODULENAME = "flexiant.FlexiantClientCloud";

	public FCOConnector() {
		this(CLOUD_SERVICE_NAME);
	}

	public FCOConnector(String instanceName) {
		super(instanceName != null ? instanceName : CLOUD_SERVICE_NAME);
	}

	public Connector copy(){
		return new FCOConnector(getConnectorInstanceName());
	}

	@Override
	public String getCloudServiceName() {
		return CLOUD_SERVICE_NAME;
	}


	@Override
    protected String getCloudConnectorPythonModule() {
		return CLOUDCONNECTOR_PYTHON_MODULENAME;
    }

	@Override
    protected Map<String, String> getConnectorSpecificUserParams(User user) throws ConfigurationException,
            ValidationException {
		Map<String, String> userParams = new HashMap<String, String>();
		userParams.put("endpoint", getEndpoint(user));
		userParams.put("user.uuid", getCustomerUUID(user));
		return userParams;
    }

	@Override
    protected Map<String, String> getConnectorSpecificLaunchParams(Run run, User user) throws ConfigurationException,
            ValidationException {
		Map<String, String> instanceSize = new HashMap<String, String>();
		ImageModule image = ImageModule.load(run.getModuleResourceUrl());
		instanceSize.put("cpu", getCpu(image));
		instanceSize.put("ram", getRam(image));
		return instanceSize;
    }

//	private String createContextualizationData(Run run, User user)
//			throws ConfigurationException, InvalidElementException,
//			ValidationException {
//
//		if (run != null){
//			log.info("Orchestartion Context: " + isInOrchestrationContext(run));
//		}
//
//		String cookie = getCookieForEnvironmentVariable(user.getName(), run.getUuid());
//
//		Configuration configuration = Configuration.getInstance();
//
//		String verbosityLevel = getVerboseParameterValue(user);
//
//		String nodename = Run.MACHINE_NAME;
//        if(isInOrchestrationContext(run)){
//        	nodename = getOrchestratorName(run);
//        }
//
//		String sepChar = "\n";
//
//        String contextualization ="#!/bin/sh" + sepChar;
//
//
//		contextualization += "export SLIPSTREAM_DIID=" + run.getName() + sepChar;
//		contextualization += "export SLIPSTREAM_SERVICEURL=" + configuration.baseUrl
//				+ sepChar;
//		contextualization += "export SLIPSTREAM_NODENAME=" + nodename
//				+ sepChar;
//		contextualization += "export SLIPSTREAM_CATEGORY="
//				+ run.getCategory().toString() + sepChar;
//		contextualization += "export SLIPSTREAM_USERNAME=" + user.getName() + sepChar;
//
//		contextualization += "export SLIPSTREAM_COOKIE=" + cookie + sepChar;
//
//		contextualization += "export SLIPSTREAM_VERBOSITY_LEVEL=" + verbosityLevel
//				+ sepChar;
//		contextualization += "export SLIPSTREAM_CLOUD=" + getCloudServiceName() + sepChar;
//		contextualization += "export SLIPSTREAM_CONNECTOR_INSTANCE="
//				+ getConnectorInstanceName() + sepChar;
//
//		contextualization += "export SLIPSTREAM_BUNDLE_URL="
//				+ configuration.getRequiredProperty("slipstream.update.clienturl")
//				+ sepChar;
//
//		contextualization += "export CLOUDCONNECTOR_BUNDLE_URL="
//				+ configuration
//						.getRequiredProperty(constructKey("update.clienturl"))
//				+ sepChar;
//
//		contextualization += "export CLOUDCONNECTOR_PYTHON_MODULENAME="
//				+ CLOUDCONNECTOR_PYTHON_MODULENAME + sepChar;
//
//		contextualization += "export SLIPSTREAM_BOOTSTRAP_BIN="
//				+ configuration
//						.getRequiredProperty("slipstream.update.clientbootstrapurl")
//				+ sepChar;
//
//		contextualization += "export SLIPSTREAM_REPORT_DIR=" + SLIPSTREAM_REPORT_DIR;
//
//		contextualization += sepChar + constructInstallDependenciesCommand();
//		String base64ContextScript=DatatypeConverter.printBase64Binary(contextualization.getBytes());
//
//		String xmlSafecontextualization = "'<celar-code><![CDATA[" +
//											"echo " + base64ContextScript +
//											"|base64 -d |tee /tmp/fco-script2.sh" + "\n" +
//											"chmod 700 /tmp/fco-script2.sh\n" +
//											"/tmp/fco-script2.sh\n" +
//											"]]></celar-code>'";
//		return xmlSafecontextualization;
//
//	}
//
//	private String constructInstallDependenciesCommand() throws ConfigurationException {
//
//		String log = "/tmp/slipstream_deps_$$.log";
//
//		return "INSTALL_EXEC=\"test -x /usr/bin/apt-get  && "
//				+ "apt-get update " + " >" + log + " 2>&1"
//				+ " && apt-get -y install python-suds python-requests "  + " >" + log + " 2>&1\""
//				+ "\neval ${INSTALL_EXEC}";
//	}

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
		return user.getParameter(constructKey(FCOUserParametersFactory.PARAM_CUSTOMER_UUID)).getValue();
	}

	@Override
    protected void validateLaunch(Run run, User user) throws ValidationException{
		super.validateLaunch(run, user);
		validateBaseParameters(user);
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

	@Override
	protected String constructKey(String key) throws ValidationException {
		log.info("In constructKey()");
		return new FCOUserParametersFactory(getConnectorInstanceName()).constructKey(key);
	}

	@Override
	protected String getCpu(ImageModule image) throws ValidationException {
		String cpu = super.getCpu(image);
		if (cpu == null || cpu.isEmpty()) {
			throw new ValidationException("CPU value should be provided.");
		} else {
			checkConvertsToInt(cpu, "CPU");
			return cpu;
		}
	}

	@Override
	protected String getRam(ImageModule image) throws ValidationException {
		String ramGb = super.getRam(image);
		if (ramGb == null || ramGb.isEmpty()) {
			throw new ValidationException("RAM value should be provided.");
		} else {
			checkConvertsToInt(ramGb, "RAM");
			return ramGb;
		}
	}

	private void checkConvertsToInt(String value, String name) throws ValidationException {
		try {
			Integer.parseInt(value);
		} catch (NumberFormatException ex) {
			throw new ValidationException(name + " should be integer.");
		}
	}

    protected String getExtraDiskVolatile(ImageModule image) throws ValidationException {
    	String extraDiskSize = super.getExtraDiskVolatile(image);
    	if (extraDiskSize == null)  {
    		extraDiskSize = "";
    	}
		// Disk Size must be one of the standard sizes
		List<String> validStandardSizes = new ArrayList<String>(Arrays.asList("20", "50", "100", "150", "250", "500", "750", "1000"));
		if (!extraDiskSize.isEmpty() && !validStandardSizes.contains(extraDiskSize)) {
			throw new ValidationException("Extra volatile disk size must be one of " + validStandardSizes);
		}
        return extraDiskSize;
    }

	protected void validateUserCredentials(User user) throws ValidationException {
		super.validateCredentials(user);
		validateCustomerUUID(user);
	}

	private void validateCustomerUUID(User user) throws ValidationException {
		String customerUUID = getCustomerUUID(user);
		if (customerUUID == null || customerUUID.isEmpty()) {
			throw (new ValidationException("Customer UUID cannot be empty"
							+ getErrorMessageLastPart(user)));
		}
	}

}
