import json
import os
import platform
from vcsavars import *
#print(os.environ)

currentDirectory = os.getcwd()

host_os = platform.system()

if host_os == 'Darwin':
    os.system(f"mkdir {VC_ISO_MOUNT}")
    os.system(f"hdiutil mount {VC_ISO_PATH} -mountroot {VC_ISO_MOUNT}")
    with open(f'{VC_ISO_MOUNT}/VMware VCSA/vcsa-cli-installer/templates/install/embedded_vCSA_on_ESXi.json') as json_file:
        data = json.load(json_file)
elif host_os == 'Linux':
    os.system(f"mkdir {VC_ISO_MOUNT}")
    os.system(f"sudo mount -o loop {VC_ISO_PATH} {VC_ISO_MOUNT}")
    with open(f'{VC_ISO_MOUNT}/vcsa-cli-installer/templates/install/embedded_vCSA_on_ESXi.json') as json_file:
        data = json.load(json_file)
else:
    print(f"Unfortunately {host_os} is not supported")

data['new_vcsa']['esxi']['hostname'] = ESXI_HOST
data['new_vcsa']['esxi']['username'] = ESXI_USR
data['new_vcsa']['esxi']['password'] = ESXI_PWD
data['new_vcsa']['esxi']['datastore'] = ESXI_DATASTORE
data['new_vcsa']['esxi']['deployment_network'] = VC_PORTGROUP
data['new_vcsa']['appliance']['thin_disk_mode'] = bool(VC_THIN_PROVISION)
data['new_vcsa']['appliance']['deployment_option'] = VC_DEPLOYMENT_SIZE
data['new_vcsa']['appliance']['name'] = VC_NAME
data['new_vcsa']['network']['mode'] = VC_NET_MODE
data['new_vcsa']['network']['ip'] = VC_IP
data['new_vcsa']['network']['dns_servers'] = [VC_DNS_SERVER]
data['new_vcsa']['network']['prefix'] = VC_NETMASK
data['new_vcsa']['network']['gateway'] = VC_GATEWAY
data['new_vcsa']['network']['system_name'] = VC_SYSTEM_NAME
data['new_vcsa']['os']['password'] = VC_ROOT_PWD
data['new_vcsa']['os']['ntp_servers'] = VC_NTP_SERVER
data['new_vcsa']['os']['ssh_enable'] = bool(VC_SSH_ENABLED)
data['new_vcsa']['sso']['password'] = VC_SSO_PWD
data['new_vcsa']['sso']['domain_name'] = VC_SSO_DOMAIN
data['ceip']['settings']['ceip_enabled'] =  bool(CEIP_ENABLED)

print(data)

with open ('vc.json', 'w') as fp:
    json.dump(data, fp, indent=4)

# Deploy 
if host_os == 'Darwin':
    deployvcsa = f'"{VC_ISO_MOUNT}/VMware VCSA/vcsa-cli-installer/mac/vcsa-deploy" \
    install --verbose --accept-eula --acknowledge-ceip \
    --no-ssl-certificate-verification --skip-ovftool-verification \
    {currentDirectory}/vc.json'
elif host_os == 'Linux':
    deployvcsa = f'{VC_ISO_MOUNT}/vcsa-cli-installer/lin64/vcsa-deploy \
    install --verbose --accept-eula --acknowledge-ceip \
    --no-ssl-certificate-verification --skip-ovftool-verification \
    {currentDirectory}/vc.json'

os.system(deployvcsa)

# Unmount
os.system("umount /tmp/tmp_iso")
os.system("rmdir /tmp/tmp_iso")