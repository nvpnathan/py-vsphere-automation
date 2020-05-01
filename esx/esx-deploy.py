import json
import os
import platform
import yaml

currentDirectory = os.getcwd()

host_os = platform.system()
homedir = os.getenv('HOME')
print("HOMEDIR is ", homedir)


yaml_file = open(homedir+"/vcsa-params.yaml")
cfg_yaml = yaml.load(yaml_file, Loader=yaml.Loader)
print(cfg_yaml["ESXI_HOSTS"])

esx_ips = cfg_yaml["ESXI_HOSTS"]


'''
# Deploy 
if host_os == 'Darwin':
    deployvcsa = f'"{VC_ISO_MOUNT}/VMware VCSA/vcsa-cli-installer/mac/vcsa-deploy" \
    install --verbose --accept-eula --acknowledge-ceip \
    --no-ssl-certificate-verification --skip-ovftool-verification \
    {tempfile}'
'''


for index, ip in enumerate(esx_ips, start=1):
    vmname = cfg_yaml["ESX_VM_NAME_PREFIX"]+str(index)
    hostname = cfg_yaml["ESX_VM_HOSTNAME_PREFIX"]+str(index)
    print("\n Working on ESX host #", index)
    print("Hostname ", hostname)
    print("VMName ", vmname)
    print("IP ", ip)

    deployesx = f'"ovftool" --acceptAllEulas --datastore="nfs-ubuntu-01" --name={vmname} --net:"VM Network"="VM 1525" \
                --ipAllocationPolicy="fixedAllocatedPolicy" --powerOn --prop:"guestinfo.hostname"={hostname}  \
                --prop:"guestinfo.ipaddress"={ip} --prop:"guestinfo.netmask"="255.255.255.128" \
                --prop:"guestinfo.gateway"="10.173.13.125" --prop:"guestinfo.vlan"="0" --prop:"guestinfo.dns"="10.173.13.90" \
                --prop:"guestinfo.domain"="tpmlab.vmware.com" --prop:"guestinfo.ntp" --prop:"guestinfo.ssh"=True \
                --prop:"guestinfo.createvmfs"=True {homedir}/Downloads/Nested_ESXi7.0_Appliance_Template_v1.ova \
                vi://{cfg_yaml["ESX_TARGET_VCSA_SSO_USER"]}:{cfg_yaml["ESX_TARGET_VCSA_SSO_PASS"]}@vcsa.tpmlab.vmware.com/Datacenter/host/Nested-PKS'

    try:

        os.system(deployesx)
        print("Finished ESXi host #", index)

    except:
        print("FAILED on ESXi host #", index)
