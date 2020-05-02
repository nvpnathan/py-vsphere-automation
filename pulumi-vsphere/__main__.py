import pulumi
import pulumi_vsphere
import ssl
import socket
import hashlib
# Code Testing
pulumi.runtime.settings._set_test_mode_enabled(True)  

# Compute parameters
dc = ['pl-dc']
cl_settings = {"drs_enabled": True, "drs_automation_level": 'fullyAutomated', "ha_enabled": True, "ha_advanced_options":{'das.IgnoreInsufficientHbDatastore':'True',
        'das.IgnoreRedundantNetWarning':'True'}, "ha_admission_control_policy": 'disabled'}

## VM Folders
vm_Folders = ['pl-packer-templates', 'pl-tkg-vms', 'pl-terraform-vms']

## Clusters, Resource Pools and Hosts
all_hosts = [{'cluster': 'pl-vlab-mgmt', 'clusterObject': '',
              'resourcePools': ['pl-pks-comp','pl-pks-mgmt','pl-terraform-vms','pl-tkg-mgmt'],
              'hosts': [{'name':'esx1.vballin.com', 'thumbprint': ''},
                        {'name':'esx2.vballin.com', 'thumbprint': ''}]},
             {'cluster': 'pl-vlab-tkg', 'clusterObject': '',
              'resourcePools': ['pl-tkg-workload'],
              'hosts': [{'name':'esx3.vballin.com', 'thumbprint': ''}]},
             {'cluster': 'pl-vlab-workload', 'clusterObject': '',
              'resourcePools': [],
              'hosts': [{'name':'esx4.vballin.com', 'thumbprint': ''}]}
            ]

# Network parameters
## Distributed Virtual Switches
dvs = [
    {'name':'pl-mgmt','version': '6.5.0'}, 
    {'name':'pl-tkg'}
    ]

## MGMT DVS Portgroups
mgmtPGs = [
    {'name':'pl-vlab-mgmt', 'vlan': '64'},
    {'name':'pl-vlab-dmz', 'vlan': '69'},
    {'name':'pl-vlab-esxi', 'vlan': '79'},
    {'name':'pl-vlab-tkg-mgmt', 'vlan': '72'}]

## COMP DVS Portgroups
compPGs = [
    {'name':'pl-edge-tunnel', 'vlan_range': [{'minVlan': '0', 'maxVlan': '4094'}]},
    {'name':'pl-edge-uplink', 'vlan_range': [{'minVlan': '0', 'maxVlan': '4094'}]},
    {'name':'pl-esxi-mgmt', 'vlan': '0'},
    {'name':'pl-tkg-mgmt', 'vlan': '64'}]

## Create Datacenter(s)
dc_list = []
def create_datacenters():
    for d in dc:
        datacenter = pulumi_vsphere.Datacenter(resource_name=d, name=d)
        dc_list.append(datacenter)
    return dc_list
create_datacenters()

## Create vSphere Cluster(s)
cluster_list = []
def create_cluster():
    for x in all_hosts:
        cluster = [x['cluster']]
        for n in cluster:
            compCluster = pulumi_vsphere.ComputeCluster(resource_name=n, datacenter_id=dc_list[0].moid,name=n,
                drs_enabled = cl_settings["drs_enabled"],
                drs_automation_level=cl_settings["drs_automation_level"],
                ha_enabled = cl_settings["ha_enabled"],
                ha_advanced_options = cl_settings["ha_advanced_options"],
                ha_admission_control_policy = 'disabled')
            x.update(clusterObject = compCluster)
    return cluster_list
create_cluster()

## Create Virtual Distributed Switches
dvs_list = []
def create_vds():
    for sw in dvs:
        vds = pulumi_vsphere.DistributedVirtualSwitch(resource_name=sw.get('name'), name=sw.get('name'), 
        datacenter_id=dc_list[0].moid, version=sw.get('version'), max_mtu='1600')
        dvs_list.append(vds)
    return dvs_list 
create_vds()

## Create MGMT DVS PortGroups
mgmtPGs_list = []
def create_mgmtPG():
    for pg in mgmtPGs:
        mgmtpg = pulumi_vsphere.DistributedPortGroup(resource_name=pg.get('name'), name=pg.get('name'), 
        distributed_virtual_switch_uuid=dvs_list[0].id, vlan_id=pg.get('vlan'))
        mgmtPGs_list.append(mgmtpg)
    return mgmtPGs_list
create_mgmtPG()

## Create COMP DVS PortGroups
create_compPGs_list = []
def create_compPG():
    for pg in compPGs:
        mgmtpg = pulumi_vsphere.DistributedPortGroup(resource_name=pg.get('name'), name=pg.get('name'), 
        distributed_virtual_switch_uuid=dvs_list[1].id, vlan_id=pg.get('vlan'), vlan_ranges=pg.get('vlan_range'))
        mgmtPGs_list.append(mgmtpg)
    return mgmtPGs_list
create_compPG()

## Retrieve ESXi thumbprint to add to vCenter
def get_esxi_thumbprint():
    for x in all_hosts:
        host = x['hosts']
        for n in host:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                wrappedSocket = ssl.wrap_socket(sock)
                wrappedSocket.connect((n['name'], 443))
                der_cert_bin = wrappedSocket.getpeercert(True)
                thumb_sha1 = hashlib.sha1(der_cert_bin).hexdigest()
                thumb = ':'.join(a+b for a,b in zip(thumb_sha1[::2], thumb_sha1[1::2]))
                n.update(thumbprint = thumb)
    return 
get_esxi_thumbprint()

## Add Hosts to to vCenter and Clusters
all_host_list = []
def add_allHosts():
    for x in all_hosts:
        cluster = x['clusterObject']
        host = x['hosts']
        for n in host:
            hosts = pulumi_vsphere.Host(resource_name=n['name'], hostname=n['name'], cluster=cluster, username='root', password='VMware1!', thumbprint=n['thumbprint'], force=True)
            all_host_list.append(hosts)
    return 
add_allHosts()

## Create Resource Pools
rp_list = []
def create_clusterRP():
    for r in all_hosts:
        rp = r['resourcePools']
        clobject = r['clusterObject']
        for i in rp:
            rps = pulumi_vsphere.ResourcePool(resource_name=i, name=i, parent_resource_pool_id=clobject.resource_pool_id)
        rp_list.append(rps)
    return rp_list
create_clusterRP()

## Create vSphere Folders
folder_list = []
def create_folders():
    for f in vm_Folders:
        folders = pulumi_vsphere.Folder(resource_name=f, path=f, type='vm', datacenter_id=dc_list[0].moid)
        folder_list.append(folders)
    return folder_list
create_folders()
