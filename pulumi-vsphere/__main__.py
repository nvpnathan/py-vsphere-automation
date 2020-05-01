import pulumi
import pulumi_vsphere

# Code Testing
#pulumi.runtime.settings._set_test_mode_enabled(True)  

# Compute parameters
dc = ['pl-dc']
clusters = ['pl-vlab-mgmt', 'pl-vlab-tkg', 'pl-vlab-workload']
cl_settings = {"drs_enabled": True, "drs_automation_level": 'fullyAutomated', "ha_enabled": True, "ha_advanced_options":{'das.IgnoreInsufficientHbDatastore':'True',
        'das.IgnoreRedundantNetWarning':'True'}, "ha_admission_control_policy": 'disabled'}

## Resource Pools
resourcePools = [['pl-pks-comp','pl-pks-mgmt','pl-terraform-vms','pl-tkg-mgmt'],['pl-tkg-workload'],[]]

## vSphere Hosts 
mgmt_Hosts = ['vlab-esx-100.vballin.com','vlab-esx-110.vballin.com','vlab-esx-120.vballin.com']
tkg_Hosts = ['lab-esx-80.vballin.com','vlab-esx-90.vballin.com']
workload_Hosts = ['vlab-esx-130.vballin.com','vlab-esx-140.vballin.com','vlab-esx-150.vballin.com']

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
def datacenters():
    for d in dc:
        datacenter = pulumi_vsphere.Datacenter(resource_name=d, name=d)
        dc_list.append(datacenter)
    return dc_list
datacenters()

## Create vSphere Cluster(s)
cluster_list = []
def cluster():
    for c in clusters:
        compCluster = pulumi_vsphere.ComputeCluster(resource_name=c, datacenter_id=dc_list[0].moid,name=c,
            drs_enabled = cl_settings["drs_enabled"],
            drs_automation_level=cl_settings["drs_automation_level"],
            ha_enabled = cl_settings["ha_enabled"],
            ha_advanced_options = cl_settings["ha_advanced_options"],
            ha_admission_control_policy = 'disabled')
        cluster_list.append(compCluster)
    return cluster_list
cluster()

## Create Virtual Distributed Switches
dvs_list = []
def vds():
    for sw in dvs:
        vds = pulumi_vsphere.DistributedVirtualSwitch(resource_name=sw.get('name'), name=sw.get('name'), 
        datacenter_id=dc_list[0].moid, version=sw.get('version'), max_mtu='1600')
        dvs_list.append(vds)
    return dvs_list 
vds()

## Create MGMT DVS PortGroups
mgmtPGs_list = []
def mgmtPG():
    for pg in mgmtPGs:
        mgmtpg = pulumi_vsphere.DistributedPortGroup(resource_name=pg.get('name'), name=pg.get('name'), 
        distributed_virtual_switch_uuid=dvs_list[0].id, vlan_id=pg.get('vlan'))
        mgmtPGs_list.append(mgmtpg)
    return mgmtPGs_list
mgmtPG()

## Create COMP DVS PortGroups
compPGs_list = []
def compPG():
    for pg in compPGs:
        mgmtpg = pulumi_vsphere.DistributedPortGroup(resource_name=pg.get('name'), name=pg.get('name'), 
        distributed_virtual_switch_uuid=dvs_list[1].id, vlan_id=pg.get('vlan'), vlan_ranges=pg.get('vlan_range'))
        mgmtPGs_list.append(mgmtpg)
    return mgmtPGs_list
compPG()

# Get Hosts
mgmtHosts_list = []
def get_mgmtHosts():
    for host in mgmt_Hosts:
        hosts = pulumi_vsphere.get_host(datacenter_id=dc_list[0].moid, name=host, opts=None)
        mgmtHosts_list.append(hosts)
    return mgmtHosts_list
#get_mgmtHosts()

tkgHosts_list = []
def get_tkgHosts():
    for host in tkg_Hosts:
        hosts = pulumi_vsphere.get_host(datacenter_id=dc_list[0].moid, name=host, opts=None)
        tkgHosts_list.append(hosts)
    return tkgHosts_list
#get_tkgHosts()

workloadHosts_list = []
def get_workloadHosts():
    for host in workload_Hosts:
        hosts = pulumi_vsphere.get_host(datacenter_id=dc_list[0].moid, name=host, opts=None)
        workloadHosts_list.append(hosts)
    return workloadHosts_list
#get_workloadHosts()

## Create vSphere Resource Pools
clusterRPs = dict(zip(cluster_list, resourcePools))
for k, v in clusterRPs.items():
    for i in v:
        rps = pulumi_vsphere.ResourcePool(resource_name=i, name=i, parent_resource_pool_id=k.resource_pool_id)
