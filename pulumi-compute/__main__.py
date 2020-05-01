import pulumi
import pulumi_vsphere

# Code Testing
#pulumi.runtime.settings._set_test_mode_enabled(True)  

# Compute parameters
dc = ['pl-dc']
cluster = ['pl-vlab-mgmt', 'pl-vlab-tkg', 'pl-vlab-workload']
cl_settings = {"drs_enabled": True, "drs_automation_level": 'fullyAutomated', "ha_enabled": True, "ha_advanced_options":{'das.IgnoreInsufficientHbDatastore':'True',
        'das.IgnoreRedundantNetWarning':'True'}, "ha_admission_control_policy": 'disabled'}

# Network parameters
dvs = [
    {'name':'pl-mgmt-dvs','version': '6.5.0'}, 
    {'name':'pl-comp-dvs'}
    ]

mgmtPGs = [
    {'name':'pl-vlab-mgmt', 'vlan': '64'},
    {'name':'pl-vlab-dmz', 'vlan': '69'},
    {'name':'pl-vlab-esxi', 'vlan': '79'},
    {'name':'pl-vlab-tkg-mgmt', 'vlan': '72'}]

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
def clusters():
    for c in cluster:
        compCluster = pulumi_vsphere.ComputeCluster(resource_name=c, datacenter_id=dc_list[0].moid,name=c,
            drs_enabled = cl_settings["drs_enabled"],
            drs_automation_level=cl_settings["drs_automation_level"],
            ha_enabled = cl_settings["ha_enabled"],
            ha_advanced_options = cl_settings["ha_advanced_options"],
            ha_admission_control_policy = 'disabled')
        cluster_list.append(compCluster)
    return cluster_list
clusters()

## Create Virtual Distributed Switches
dvs_list = []
def vds():
    for sw in dvs:
        vds = pulumi_vsphere.DistributedVirtualSwitch(resource_name=sw.get('name'), name=sw.get('name'), 
        datacenter_id=dc_list[0].moid, version=sw.get('version'), max_mtu='1600')
        dvs_list.append(vds)
    return dvs_list 
vds()

mgmtPGs_list = []
def mgmtPG():
    for pg in mgmtPGs:
        mgmtpg = pulumi_vsphere.DistributedPortGroup(resource_name=pg.get('name'), name=pg.get('name'), 
        distributed_virtual_switch_uuid=dvs_list[0].id, vlan_id=pg.get('vlan'))
        mgmtPGs_list.append(mgmtpg)
    return mgmtPGs_list

mgmtPG()

compPGs_list = []
def compPG():
    for pg in compPGs:
        mgmtpg = pulumi_vsphere.DistributedPortGroup(resource_name=pg.get('name'), name=pg.get('name'), 
        distributed_virtual_switch_uuid=dvs_list[1].id, vlan_id=pg.get('vlan'), vlan_ranges=pg.get('vlan_range'))
        mgmtPGs_list.append(mgmtpg)
    return mgmtPGs_list

compPG()