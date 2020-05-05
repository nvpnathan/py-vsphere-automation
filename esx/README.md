# Deploying nested ESXi hypervisors as Virtual Machines


## Requirements

- This repo including the esx-deploy.py
- ESXi 7.0 OVA from William Lam's Blog
- ovftool installed
- Target(parent) physical ESXi host must be version 6.7 or higher

## Automated Install with esx-deploy.py.
To deploy the nested ESXi 7.0 hosts, the deployment script needs following information which should be set in ~/vcsa-params.yaml in following format: NOTE: The script will install as many ESXi hosts as you have listed under ESXI_HOSTS by IP Address.

``` yaml
ESXI_HOSTS:
  - '10.172.209.63'
  - '10.172.209.64'

### Section for esx-deploy.py
ESX_VM_NAME_PREFIX: "py-ovadeploy-"
ESX_VM_HOSTNAME_PREFIX: "py-esx7-"
ESX_TARGET_VCSA_SSO_USER: "administrator@vsphere.local"
ESX_TARGET_VCSA_SSO_PASS: "Some Password"
```

Run the esx-deploy.py script
```shell
pwd
/Users/<user>/gitHub/py-vsphere-automation
python3 ./esx/esx-deploy.py
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
ovftool --acceptAllEulas --datastore="nfs-ubuntu-01" --name="esx7-ovftool-04" --net:"VM Network"="VM 1525" \
--ipAllocationPolicy="fixedAllocatedPolicy" --powerOn --prop:"guestinfo.hostname"="ovf-vcsa-hostname"  \
--prop:"guestinfo.ipaddress"="10.173.13.92" --prop:"guestinfo.netmask"="255.255.255.128" \
--prop:"guestinfo.gateway"="10.173.13.125" --prop:"guestinfo.vlan"="0" --prop:"guestinfo.dns"="10.173.13.90" \
--prop:"guestinfo.domain"="tpmlab.vmware.com" --prop:"guestinfo.ntp" --prop:"guestinfo.ssh"=True \
--prop:"guestinfo.createvmfs"=True ./Nested_ESXi7.0_Appliance_Template_v1.ova vi://vcsa.tpmlab.vmware.com/Datacenter/host/Nested-PKS

Opening OVA source: ./Nested_ESXi7.0_Appliance_Template_v1.ova
The manifest validates
Enter login information for target vi://vcsa.tpmlab.vmware.com/
Username: administrator@vsphere.local
Password: ********
Opening VI target: vi://administrator%40vsphere.local@vcsa.tpmlab.vmware.com:443/Datacenter/host/Nested-PKS
Deploying to VI: vi://administrator%40vsphere.local@vcsa.tpmlab.vmware.com:443/Datacenter/host/Nested-PKS
Disk progress: 1%
```
