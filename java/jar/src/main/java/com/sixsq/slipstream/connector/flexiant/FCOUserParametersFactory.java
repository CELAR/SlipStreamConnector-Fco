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

import com.sixsq.slipstream.connector.UserParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.ParameterType;

public class FCOUserParametersFactory extends UserParametersFactoryBase {


	
	final static String PARAM_CUSTOMER_UUID = "user.uuid";	
	private static String CUSTOMER_UUID_INSTRUCTIONS = "Your Flexiant Customer UUID. This can be found on the Settings tab under 'Your API Details' "
	        + "section.";

	final static String PARAM_CUSTOMER_EMAIL = "user.email";
	private static String CUSTOMER_EMAIL_INSTRUCTIONS = "The e-mail address you are known by on this Flexiant instance. "
			+ "Used in conjunction with your Customer UUID and password to authenticate to the API";
	
	final static String PARAM_CUSTOMER_PASSWORD = "user.password";
	private static String CUSTOMER_PASSWORD_INSTRUCTIONS = "Your Flexiant password";
	
	//final static String USER_UUID = "user.uuid";
	final static String REGION_PARAMETER_NAME = "region";
	final static String FCO_USER_ENDPOINT = "fco.user.endpoint";

	//public static String MARKETPLACE_ENDPOINT_PARAMETER_NAME = "marketplace.endpoint";
	//public static String MESSAGING_TYPE_PARAMETER_NAME = "messaging.type";
	//public static String MESSAGING_ENDPOINT_PARAMETER_NAME = "messaging.endpoint";
	public static String MESSAGING_QUEUE_PARAMETER_NAME = "messaging.queue";
	
	public FCOUserParametersFactory(String connectorInstanceName)
			throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		// These fields appear on the <url>/user/username page under the
		// Flexiant tab e.g. DO NOT change the KEY_PARAMETER_NAME and
		// SECRET_PARAMETER_NAME (the parent class expects them to be 
		// named as such)
		
		putMandatoryParameter(KEY_PARAMETER_NAME, "Flexiant account username",
				ParameterType.RestrictedString);

		putMandatoryPasswordParameter(SECRET_PARAMETER_NAME,
				"Flexiant account password");
		
		putParameter(PARAM_CUSTOMER_UUID, "", 	"Customer UUID", 	CUSTOMER_UUID_INSTRUCTIONS, true);
//		putParameter(PARAM_CUSTOMER_EMAIL, "",	"Customer E-Mail",  CUSTOMER_EMAIL_INSTRUCTIONS, true);
		
//		putMandatoryPasswordParameter(PARAM_CUSTOMER_PASSWORD,		"Password",	CUSTOMER_PASSWORD_INSTRUCTIONS);
		
		//putParameter(KEYPAIR_NAME_PARAMETER_NAME,	"Keypair Name (required to submit to EC2)", true);
	}
}
