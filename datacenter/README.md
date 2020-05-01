### vSphere Requirements

The VCSA Appliance needs to be deployed already

## Creating the YAML Configuration file.

To deploy the VCSA appliance the deployment script needs following environment variables set:

``` 
export VCENTER_IP ='192.168.44.86'                                  # IP for VCSA Appliance
export VCENTER_PW = 'passforvc'
export VCENTER_USER ='administrator@vsphere.local'

```


Once you have exported the 3 ENV VARS you can create a new Datacenter and Cluster with DRS & HA enabled with the following command.

```shell
create_dc_cluster.py
```
