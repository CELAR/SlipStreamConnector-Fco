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

import com.sixsq.slipstream.credentials.Credentials;
import com.sixsq.slipstream.connector.CredentialsBase;
import com.sixsq.slipstream.exceptions.InvalidElementException;
import com.sixsq.slipstream.exceptions.SlipStreamRuntimeException;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.User;

public class FCOCredentials extends CredentialsBase implements Credentials {

	private final static Logger log = Logger.getLogger(FCOCredentials.class.getName());
	
	public FCOCredentials(User user, String connectorInstanceName) {
		super(user);
		log.info("In FCOCredentials()");
		log.info("connectorInstanceName=" + connectorInstanceName==null?"NULL":connectorInstanceName );
		
		try {
			cloudParametersFactory = new FCOUserParametersFactory(connectorInstanceName);
		} catch (ValidationException e) {
			e.printStackTrace();
			throw (new SlipStreamRuntimeException(e));
		}
		log.info("Done FCOCredentials()");		
	}

	public String getKey() throws InvalidElementException {
		return getParameterValue(FCOUserParametersFactory.KEY_PARAMETER_NAME);
	}

	public String getSecret() throws InvalidElementException {
		return getParameterValue(FCOUserParametersFactory.SECRET_PARAMETER_NAME);
	}

}
