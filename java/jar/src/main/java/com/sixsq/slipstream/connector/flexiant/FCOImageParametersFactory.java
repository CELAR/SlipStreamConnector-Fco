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

import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.factory.ModuleParametersFactoryBase;
import com.sixsq.slipstream.persistence.Run;

public class FCOImageParametersFactory extends ModuleParametersFactoryBase {

	private final static Logger log = Logger.getLogger(FCOImageParametersFactory.class.getName());
	private final String DISK_PARAMETER_NAME = "disk.size";

	public FCOImageParametersFactory(String connectorInstanceName)
			throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		log.info("In initReferenceParameters()");

		putMandatoryParameter(Run.RAM_PARAMETER_NAME, Run.RAM_PARAMETER_NAME, "Amount of RAM, in MB");
		putMandatoryParameter(Run.CPU_PARAMETER_NAME, Run.CPU_PARAMETER_NAME, Run.CPU_PARAMETER_DESCRIPTION);
//		putEnumParameter(ImageModule.INSTANCE_TYPE_KEY, "Cloud instance type",
//				InstanceType.getValues(), INSTANCE_TYPE_DEFAULT, true);
//		putEnumParameter(DISKSBUS_TYPE_KEY, "VM disks bus type",
//				DisksBusType.getValues(), DISKSBUS_TYPE_DEFAULT, true);

		log.info("Done initReferenceParameters()");
	}
}
