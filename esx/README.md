# Deploying nested ESXi hypervisors as Virtual Machines


## Manual Install with ovftool Requirements

- This repo including the vcsa-deploy.py
- ESXi 7.0 OVA from William Lams
- ovftool - version

### vSphere Requirements
- vSphere 7.0 with a physical ESXi 7.0 Host


## Creating the YAML Configuration file.

To deploy the VCSA appliance the deployment script needs following information which should be set in ~/vcsa-params.yaml in following format:

``` yaml
ESXI_HOSTS:                                             # ESX hosts to be managed by VCSA
  - '12.33.21.221'                                      # First Host will have VCSA deployed onto it.
  - '12.33.21.223'
ESXI_USR: 'root'                                        # Username for all ESXi hosts
ESXI_PWD: 'somepassword'                                # Password for all ESXi hosts
ESXI_DATASTORE: 'datastore2'                            # Datastore to deploy VCSA VM onto
VC_DEPLOYMENT_SIZE: 'tiny'
VC_THIN_PROVISION: True
VC_NET_MODE: 'static'
VC_NAME: 'python-vcsa'                                  # VM Name for VCSA Appliance
VC_SYSTEM_NAME: 'python-vcsa.domain.com'                # Network Hostname
VC_IP: '192.168.44.86'                                  # IP for VCSA Appliance
VC_NETMASK: '25'
VC_DNS_SERVERS:
  - '192.168.44.5'
  - '8.8.8.8'
VC_GATEWAY: '192.168.44.1'
VC_NTP_SERVER: '192.168.44.21'
VC_PORTGROUP: 'VLAN 1526'
VC_ROOT_PWD: 'passforesx'
VC_SSH_ENABLED:  True
VC_SSO_PWD: 'passforvc'
VC_SSO_DOMAIN: 'vsphere.local'
CEIP_ENABLED:  False
VC_ISO_PATH: '/Users/bob/VMware-VCSA-all-7.0.0-15952498.iso'
VC_ISO_MOUNT: "/tmp/tmp_iso"
```

## Manual Install with ovftool Steps

Download the ISO
```shell
wget https://download3.vmware.com/software/vmw-tools/nested-esxi/Nested_ESXi7.0_Appliance_Template_v1.ova ~
```
Download ovftool for OSX or Linux
```shell
https://my.vmware.com/group/vmware/details?productId=974&downloadGroup=OVFTOOL440
```
For OSX doubleclick the DMG file and accept security warning or override in System Preferences

Run the ovftool 
```shell
ovftool --acceptAllEulas --datastore="nfs-ubuntu-01" --name="esxi7-01" --net:"VM Network"="VM 1525" --prop:"guestinfo.hostname"="ovf-vcsa-hostname"  --prop:"guestinfo.ipaddress"="10.173.13.91" --prop:"guestinfo.netmask" --prop:"guestinfo.gateway"="10.173.13.125" --prop:"guestinfo.dns"="10.173.13.90" --prop:"guestinfo.domain"="tpmlab.vmware.com" --prop:"guestinfo.ntp" --prop:"guestinfo.ssh"=True --prop:"guestinfo.createvmfs"=True ./Nested_ESXi7.0_Appliance_Template_v1.ova vi://vcsa.tpmlab.vmware.com/Datacenter/host/Nested-PKS

Opening OVA source: ./Nested_ESXi7.0_Appliance_Template_v1.ova
The manifest validates
Enter login information for target vi://vcsa.tpmlab.vmware.com/
Username: administrator@vsphere.local
Password: ********
Opening VI target: vi://administrator%40vsphere.local@vcsa.tpmlab.vmware.com:443/Datacenter/host/Nested-PKS
Deploying to VI: vi://administrator%40vsphere.local@vcsa.tpmlab.vmware.com:443/Datacenter/host/Nested-PKS
Disk progress: 1%
```
