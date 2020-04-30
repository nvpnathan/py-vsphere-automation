import pulumi
import pulumi_vsphere

dc = ['pl-dc', 'pl-dc2']
clusters = ['pl-mgmt', 'pl-comp']
dvs = ['pl-mgmt-dvs','pl-comp-dvs']

cl_settings = {"drs_enabled": True, "drs_automation_level": 'fullyAutomated', "ha_enabled": True, "ha_advanced_options":{'das.IgnoreInsufficientHbDatastore':'True',
        'das.IgnoreRedundantNetWarning':'True'}, "ha_admission_control_policy": 'disabled'}

dc_list = []
def datacenters():
    for d in dc:
        datacenter = pulumi_vsphere.Datacenter(resource_name=d, name=d)
        dc_list.append(datacenter)
    return dc_list

datacenters()

for sw in dvs:
    vds = pulumi_vsphere.DistributedVirtualSwitch(resource_name=sw, name=sw, datacenter_id=dc_list[0].moid)

for c in clusters:
    compCluster = pulumi_vsphere.ComputeCluster(resource_name=c, datacenter_id=dc_list[0].moid,name=c,
        drs_enabled = cl_settings["drs_enabled"],
        drs_automation_level=cl_settings["drs_automation_level"],
        ha_enabled = cl_settings["ha_enabled"],
        ha_advanced_options = cl_settings["ha_advanced_options"],
        ha_admission_control_policy = 'disabled')


