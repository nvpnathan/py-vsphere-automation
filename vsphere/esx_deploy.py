#!/usr/bin/env python

"""

"""
import os
import platform
import yaml

currentDirectory = os.getcwd()

host_os = platform.system()
homedir = os.getenv('HOME')
print("HOMEDIR is ", homedir)


yaml_file = open(homedir+"/vsphere_config.yaml")
cfg_yaml = yaml.load(yaml_file, Loader=yaml.Loader)
print(cfg_yaml["ESX_IPS"])
esx_ips = cfg_yaml["ESX_IPS"]
esx_network = cfg_yaml["VC_PORTGROUP"]
dns = cfg_yaml["VC_DNS_SERVERS"][0]
vm_prefix = cfg_yaml["ESX_VM_NAME_PREFIX"]
hostname_prefix = cfg_yaml["ESX_VM_HOSTNAME_PREFIX"]


def deploy(esx_ips,vm_prefix,hostname_prefix, dns):
    esxhosts_deployed = []
    for index, ip in enumerate(esx_ips, start=1):
        vmname = vm_prefix + str(index)
        hostname = hostname_prefix + str(index)
        print("\n Working on ESX host #", index)
        print("Hostname ", hostname)
        print("VMName ", vmname)
        print("IP ", ip)

        deployesx = f'"ovftool"  --acceptAllEulas --datastore="nfs-ubuntu-01" --name={vmname} --net:"VM Network"="{cfg_yaml["VC_PORTGROUP"]}" \
        --ipAllocationPolicy="fixedAllocatedPolicy" --powerOn --memorySize:"*"=16192 --numberOfCpus:"*"=8  \
        --prop:"guestinfo.hostname"={hostname} --prop:"guestinfo.ipaddress"={ip} --prop:"guestinfo.netmask"={cfg_yaml["ESX_NETMASK"]} \
        --prop:"guestinfo.gateway"={cfg_yaml["ESX_GATEWAY"]} --prop:"guestinfo.vlan"={cfg_yaml["VLAN"]} --prop:"guestinfo.dns"={dns} \
        --prop:"guestinfo.domain"={cfg_yaml["DOMAIN"]} --prop:"guestinfo.ntp"={cfg_yaml["NTP_SERVER"]} --prop:"guestinfo.ssh"=True \
        --prop:"guestinfo.createvmfs"=True {cfg_yaml["ESX_ISO_PATH"]} \
        vi://{cfg_yaml["ESX_TARGET_VCSA_SSO_USER"]}:{cfg_yaml["ESX_TARGET_VCSA_SSO_PASS"]}@vcsa.tpmlab.vmware.com/?ip={cfg_yaml["VC_ESX_HOST"]}'

        try:

            print(deployesx, "\n")
            os.system(deployesx)
            print("Finished ESXi host #", index)
            esxhosts_deployed.append(hostname)
        except:
            print("FAILED on ESXi host #", index)
    return esxhosts_deployed

def main():
    hosts = deploy(esx_ips, vm_prefix, hostname_prefix, dns)
    print("Successfully deployed the following ESX hosts ", hosts)

# Start program if run standalone
if __name__ == '__main__':
    main()
