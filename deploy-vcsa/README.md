# Deploying the VCSA Appliance


## Install Requirements

- This repo including the vcsa-deploy.py
- Python 3.6.x +
- Python libraries - pyyaml, pyvmomi, vim, platform
- VCSA Appliance ISO
- YAML Configuration file placed in $HOME

### vSphere Requirements

The VCSA Appliance needs to be deployed onto an existing ESXi Host.

## Creating the YAML Configuration file.

To deploy the VCSA appliance the deployment script needs following information which should be set in ~/vcsa-params.yaml in following format:

``` yaml
ESXI_HOSTS:                                             # ESX hosts to be managed by VCSA
  - '10.172.209.63'                                     # First Host will have VCSA deployed onto it.
  - '10.172.209.64'
ESXI_USR: 'root'                                        # Username for all ESXi hosts
ESXI_PWD: 'VMware1!'                                    # Password for all ESXi hosts
ESXI_DATASTORE: '63-datastore2'                         # Datastore to deploy VCSA VM onto
VC_DEPLOYMENT_SIZE: 'tiny'
VC_THIN_PROVISION: True
VC_NET_MODE: 'static'
VC_NAME: 'python-vcsa'                                  # VM Name for VCSA Appliance
VC_SYSTEM_NAME: 'python-vcsa.tpmlab.vmware.com'         # Network Hostname
VC_IP: '10.173.13.166'                                  # IP for VCSA Appliance
VC_NETMASK: '25'
VC_DNS_SERVERS:
  - '10.173.13.90'
  - '8.8.8.8'
VC_GATEWAY: '10.173.13.253'
VC_NTP_SERVER: '10.173.13.90'
VC_PORTGROUP: 'VLAN 1526'
VC_ROOT_PWD: 'VMware1!'
VC_SSH_ENABLED:  True
VC_SSO_PWD: 'VMware1!'
VC_SSO_DOMAIN: 'vsphere.local'
CEIP_ENABLED:  False
VC_ISO_PATH: '/Users/kraust/Downloads/VMware-VCSA-all-7.0.0-15952498.iso'
VC_ISO_MOUNT: "/tmp/tmp_iso"
```


Once you have created your $HOME/vcsa-params.yaml, you can deploy the VCSA appliance with the following command.

```shell
vcsa-deploy.py
```

