package com.sixsq.slipstream.connector.flexiant;

import com.sixsq.slipstream.connector.AbstractDiscoverableConnectorService;
import com.sixsq.slipstream.connector.Connector;

public class FCODiscoverableConnectorService extends AbstractDiscoverableConnectorService {
    public FCODiscoverableConnectorService() {
        super(FCOConnector.CLOUD_SERVICE_NAME);
    }

    public Connector getInstance(String instanceName) {
        return new FCOConnector(instanceName);
    }
}
