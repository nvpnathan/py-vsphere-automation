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


```shell
wget https://download3.vmware.com/software/vmw-tools/nested-esxi/Nested_ESXi7.0_Appliance_Template_v1.ova ~


vcsa-deploy.py
```

