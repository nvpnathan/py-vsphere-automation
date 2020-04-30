import pulumi
import pulumi_vsphere

dc = ['pl-dc']
cluster = ['pl-vlab-mgmt', 'pl-vlab-tkg', 'pl-vlab-workload']
dvs = [
    {'name':'pl-mgmt-dvs','version': '6.5.0'}, 
    {'name':'pl-comp-dvs'}
    ]
dvsPortgroups = []

cl_settings = {"drs_enabled": True, "drs_automation_level": 'fullyAutomated', "ha_enabled": True, "ha_advanced_options":{'das.IgnoreInsufficientHbDatastore':'True',
        'das.IgnoreRedundantNetWarning':'True'}, "ha_admission_control_policy": 'disabled'}

dc_list = []
def datacenters():
    for d in dc:
        datacenter = pulumi_vsphere.Datacenter(resource_name=d, name=d)
        dc_list.append(datacenter)
    return dc_list
datacenters()

dvs_list = []
def vds():
    for sw in dvs:
        vds = pulumi_vsphere.DistributedVirtualSwitch(resource_name=sw.get('name'), name=sw.get('name'), datacenter_id=dc_list[0].moid,
        version=sw.get('version'), max_mtu='1600')
        dvs_list.append(vds)
    return dvs_list 
vds()

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
