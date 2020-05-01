# Deploying nested ESXi hypervisors as Virtual Machines


## Manual Install with ovftool Requirements

- This repo including the vcsa-deploy.py
- ESXi 7.0 OVA from William Lams
- ovftool - version

### vSphere Requirements
- vSphere 7.0 with a physical ESXi 7.0 Host


## ---FUTURE--- Creating the YAML Configuration file.

``` yaml

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
ovftool --acceptAllEulas --datastore="nfs-ubuntu-01" --name="esx7-ipAllocationPolicy-03" \
--net:"VM Network"="VM 1525" --ipAllocationPolicy="fixedAllocatedPolicy" --powerOn \
--prop:"guestinfo.hostname"="ovf-vcsa-hostname"  --prop:"guestinfo.ipaddress"="10.173.13.92" \
--prop:"guestinfo.netmask" --prop:"guestinfo.gateway"="10.173.13.125" --prop:"guestinfo.vlan"="0" \
--prop:"guestinfo.dns"="10.173.13.90" --prop:"guestinfo.domain"="tpmlab.vmware.com" \
--prop:"guestinfo.ntp" --prop:"guestinfo.ssh"=True --prop:"guestinfo.createvmfs"=True ./Nested_ESXi7.0_Appliance_Template_v1.ova vi://vcsa.tpmlab.vmware.com/Datacenter/host/Nested-PKS

Opening OVA source: ./Nested_ESXi7.0_Appliance_Template_v1.ova
The manifest validates
Enter login information for target vi://vcsa.tpmlab.vmware.com/
Username: administrator@vsphere.local
Password: ********
Opening VI target: vi://administrator%40vsphere.local@vcsa.tpmlab.vmware.com:443/Datacenter/host/Nested-PKS
Deploying to VI: vi://administrator%40vsphere.local@vcsa.tpmlab.vmware.com:443/Datacenter/host/Nested-PKS
Disk progress: 1%
```
