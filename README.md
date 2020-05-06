## py-vsphere-automation

End to end rapid deployment tool for vSphere 7 with Kubernetes for demo, poc, or workshop purposes. Will deploy and configure a nested multi ESXi, VCSA, and WCP environment with python. 

### Instructions to deploy the environment.
Coming Soon . . . 

### Parameters file used for all individual component scripts.
This fille should be stored in $HOME on a Linux or OSX system where the scripts will be run from.
'''yaml
### COMMON SETTINGS
VLAN: '0'
DOMAIN: 'alab.somewhere.com'
NTP_SERVER: 'time.somewhere.com'
PARENT_VC: 'vcsa.alab.somewhere.com'

### NESTED VCSA DEPLOYMENT DATA
VC_ESX_HOST: '10.18.209.63'
VC_ESXI_USR: 'root'
VC_ESXI_PWD: 'VMware1!'
VC_ESXI_DATASTORE: '63-datastore1'
VC_DEPLOYMENT_SIZE: 'tiny'
VC_THIN_PROVISION: True
VC_NET_MODE: 'static'
VC_NAME: 'py-vcsa7'
VC_SYSTEM_NAME: 'python-vcsa.somewhere.com'
VC_IP: '10.18.13.166'
VC_NETMASK: '25'
VC_DNS_SERVERS:
  - '10.18.13.90'
  - '8.8.8.8'
VC_GATEWAY: '10.18.13.253'
VC_PORTGROUP: 'SOME_PG'
VC_ROOT_PWD: 'password!'
VC_SSH_ENABLED:  True
VC_SSO_USER: 'administrator@vsphere.local'
VC_SSO_PWD: 'password!'
VC_SSO_DOMAIN: 'vsphere.local'
CEIP_ENABLED:  False
VC_ISO_PATH: '/Users/bob/Downloads/VMware-VCSA-all-7.0.0-15952498.iso'
VC_ISO_MOUNT: "/tmp/tmp_iso"

VC_DATACENTER: 'python-tmp-dc'
VC_CLUSTER:  'Python Cluster'


### Section for esx-deploy.py
ESX_VM_NAME_PREFIX: "py-esx7-"
ESX_VM_HOSTNAME_PREFIX: "py-esx7-"
ESX_TARGET_VCSA_SSO_USER: "administrator@vsphere.local"
ESX_TARGET_VCSA_SSO_PASS: "password!"
ESX_IPS:
  - '10.18.13.167'
  - '10.18.13.168'
ESX_NETMASK: '255.255.255.128'
ESX_GATEWAY: '10.18.13.253'
ESX_ISO_PATH: '/Users/bob/Downloads/Nested_ESXi7.0_Appliance_Template_v1.ova'
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
'''

## Python Automation individual components
The individual steps can be used and run individually for other use cases. Follow links below to just run a specific step.
1. [Nested ESXi 7 OVA deployment](esx/README.md)
2. [VCSA Appliance Deployment](vcsa/README.md)
3. [Datacenter & Cluster Creation & Adding Hosts](datacenter/README.md)
4. [Distributed Switch & DVPG Creation](vds/README.md)
5. Coming Soon-Mount NFS Datastore(nfs/README.md)
6. Coming Soon-NSX Deployment(nsx/NSX-Deployment.md)
7. Coming Soon-Install NSX Logical Configuration(nsx/NSX-Logical.md)
8. Coming Soon-Install WCP (wcp/README.md)
