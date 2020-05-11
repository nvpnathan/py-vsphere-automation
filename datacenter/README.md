###  Requirements

The VCSA Appliance and ESXi hosts need to be deployed already

###  What the script does
- Creates a new Datacenter with name from (VC_DATACENTER: )
- Creates a new Cluster with name (VC_CLUSTER: )
- Adds ESXi hosts to the Cluster as set in (ESX_IPS: )
- Configure's HA / DRS

### Update the YAML Configuration file.

To deploy the VCSA appliance the deployment script needs following environment variables set:

``` yaml
### COMMON SETTINGS
VLAN: '0'                   # VLAN not currently used
DOMAIN: 'domain.com'
NTP_SERVER: 'time.domain.com'
PARENT_VC: 'vcsa.domain.com'

### NESTED VCSA DEPLOYMENT DATA
VC_ESX_HOST: '10.172.208.163'       # Parent ESX host to deploy the VCSA Appliance
VC_ESXI_USR: 'root'               # Parent ESX host username
VC_ESXI_PWD: 'pass'           # Parent ESX host password
VC_ESXI_DATASTORE: '63-datastore1'   # Parent ESX host Datastore for the VCSA Appliance
VC_DEPLOYMENT_SIZE: 'tiny'
VC_THIN_PROVISION: True
VC_NET_MODE: 'static'
VC_NAME: 'py-vcsa7'               # VCSA VM Name
VC_SYSTEM_NAME: 'python-vcsa.domain.com'    # VCSA Hostname
VC_IP: '10.173.133.66'                      # VCSA IP
VC_NETMASK: '25'
VC_DNS_SERVERS:
  - '10.173.133.190'
  - '8.8.8.8'
VC_GATEWAY: '10.173.133.153'
VC_PORTGROUP: 'VLAN 1526'
VC_ROOT_PWD: 'pass'
VC_SSH_ENABLED:  True
VC_SSO_USER: 'administrator@vsphere.local'
VC_SSO_PWD: 'pass'
VC_SSO_DOMAIN: 'vsphere.local'
CEIP_ENABLED:  False
VC_ISO_PATH: '/Users/user/Downloads/VMware-VCSA-all-7.0.0-15952498.iso'
VC_ISO_MOUNT: "/tmp/tmp_iso"    # VCSA ISO Mount Point where script is run
VC_DATACENTER: 'python-tmp-dc'
VC_CLUSTER:  'Python Cluster'
```

### ## Install Requirements Run the DC creation script.
Once you have exported the 3 ENV VARS you can create a new Datacenter and Cluster with DRS & HA enabled with the following command.

```shell
create_dc_cluster.py
```
