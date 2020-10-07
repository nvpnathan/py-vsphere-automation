# Setup vSphere nested environment for vSphere 7 with Kubernetes


## Install Requirements

- This repo 
- Python 3.6.x +
- Python libraries - pyyaml, pyvmomi, vsanapiutils
- VCSA 7.0 Appliance ISO
- ESXi 7.0 OVA from William Lam's Blog
- ovftool installed
- Target(parent) physical ESXi host must be version 6.7 or higher
- YAML Configuration file placed in $HOME
- DNS A record added for the VC_SYSTEM_NAME FQDN on the DNS Server that is configured in VC_DNS_SERVERS.
- Valid NTP Clock source configured in NTP_SERVER.

IMPORTANT:  The VCSA will not come online without an A record that it can use to resolve itself upon boot.

### vSphere Requirements


## Creating updating parameters in the YAML Configuration file.

To deploy the VCSA appliance the deployment script needs following information which should be set in ~/vsphere_config.yaml in following format:

``` yaml
### COMMON SETTINGS
VLAN: '0'                   # VLAN not currently used.
DOMAIN: 'domain.com'
NTP_SERVER: 'time.vmware.com'
PARENT_VC: 'vcsa.domain.com'

### NESTED VCSA DEPLOYMENT DATA
VC_ESX_HOST: '172.18.209.63'       # Parent ESX host to deploy the VCSA Appliance
VC_ESXI_USR: 'root'               # Parent ESX host username
VC_ESXI_PWD: 'apassword'           # Parent ESX host password
VC_ESXI_DATASTORE: '63-datastore1'   # Parent ESX host Datastore for the VCSA Appliance
VC_DEPLOYMENT_SIZE: 'tiny'
VC_THIN_PROVISION: True
VC_NET_MODE: 'static'
VC_NAME: 'py-vcsa7-2'               # VCSA VM Name
VC_SYSTEM_NAME: 'python-vcsa2.domain.com'    # VCSA FQDN MUST ADD A Rec to DNS
VC_IP: '172.16.13.235'                      # VCSA IP
VC_NETMASK: '25'
VC_DNS_SERVERS:
  - '172.16.13.90'
  - '8.8.8.8'
VC_GATEWAY: '172.16.13.253'
VC_PORTGROUP: 'VLAN 1526'
VC_ROOT_PWD: 'apassword'
VC_SSH_ENABLED:  True
VC_SSO_USER: 'administrator@vsphere.local'
VC_SSO_PWD: 'apassword'
VC_SSO_DOMAIN: 'vsphere.local'
CEIP_ENABLED:  False
VC_ISO_PATH: '/Users/kraust/Downloads/VMware-VCSA-all-7.0.0-15952498.iso'
VC_ISO_MOUNT: "/tmp/tmp_iso"    # VCSA ISO Mount Point where script is run
VC_DATACENTER: 'python-tmp-dc'
VC_CLUSTER:  'Python Cluster'


### Section for esx-deploy.py
ESX_VM_NAME_PREFIX: "py-esx7-"
ESX_VM_HOSTNAME_PREFIX: "py-esx7-"
ESX_TARGET_VCSA_SSO_USER: "administrator@vsphere.local"
ESX_TARGET_VCSA_SSO_PASS: "apassword"
ESX_IPS:
  - '172.16.13.167'
  - '172.16.13.168'
ESX_NETMASK: '255.255.255.128'
ESX_GATEWAY: '172.16.13.253'
ESX_ISO_PATH: '/Users/kraust//Downloads/Nested_ESXi7.0_Appliance_Template_v1.ova'
ESX_DATASTORE: '63-datastore1'

### Section for VDS & DVPG
VDS_NAME: 'wcp-vds-1'
VDS_UPLINK: 'vmnic1'
VDS_PG1_NAME: 'management-vm'
VDS_PG1_VLAN: 100
VDS_PG2_NAME: 'tep-edge'
VDS_PG2_VLAN: 102
VDS_PG3_NAME: 'ext-uplink-edge'
VDS_PG3_VLAN: 103

### Section for NSX-T 3.0 Deployment

### Section for WCP Supervisor Cluster Deployment
WCP_SIZE: tiny
WCP_MASTERVMNET: 
WCP_MASTERSTARTINGIP:
WCP_MASTERMASK:
WCP_MASTERGATEWAY: 
WCP_STORAGEPOLICY:


```

## Install 

Once you have created your $HOME/vsphere_config.yaml, you can create an entire new nested vSphere environment with the following command.

```shell
python3 ./vsphere/setup_vsphere.py
```

