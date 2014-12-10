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

import java.util.logging.Logger;

import com.sixsq.slipstream.connector.SystemConfigurationParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;

public class FCOSystemConfigurationParametersFactory extends
		SystemConfigurationParametersFactoryBase {

	private final static Logger log = Logger.getLogger(FCOSystemConfigurationParametersFactory.class.getName());
    public final static String FCO_ORCHESTRATOR_CPU_CORES = "orchestrator.CPU_CORES";
    public final static String FCO_ORCHESTRATOR_RAM       = "orchestrator.RAM";

	public FCOSystemConfigurationParametersFactory(String connectorInstanceName)
			throws ValidationException {
		super(connectorInstanceName);
	}

	protected void initReferenceParameters() throws ValidationException {

		super.initReferenceParameters();

		// We just need an end-point, so can just use the inherited method instead of
		// using putMandatoryParameter() explicitly
		putMandatoryEndpoint();

//		putMandatoryParameter(
//		constructKey(FCOUserParametersFactory.FCO_USER_ENDPOINT),
//		"FCO User API Endpoint", "https://cp.sd1.flexiant.net:4442/");

//		putMandatoryOrchestratorInstanceType();
//
		putMandatoryParameter(constructKey("update.clienturl"),
				"URL with the cloud client specific connector (Sys Config)");

		putMandatoryParameter(constructKey(FCOSystemConfigurationParametersFactory.FCO_ORCHESTRATOR_CPU_CORES),
				"Number of CPU Cores for the Orchestrator VM");

		putMandatoryParameter(constructKey(FCOSystemConfigurationParametersFactory.FCO_ORCHESTRATOR_RAM),
				"Number of GB RAM for the Orchestrator");
//
//		putMandatoryParameter(
//				constructKey(FCOUserParametersFactory.SECURITY_GROUP_PARAMETER_NAME),
//				"Orchestrator security group", "default");

//		putMandatoryParameter(
//				constructKey(FCOUserParametersFactory.FCO_ADMIN_ENDPOINT),
//				"FCO Admin Endpoint", "https://cp.sd1.flexiant.net:4443/");

		log.info("Done initReferenceParameters()");
	}

}
