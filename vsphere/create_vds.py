"""
Adapted from: https://raw.githubusercontent.com/reubenur-rahman/vmware-pyvmomi-examples/master/create_dvs_and_dvport_group.py
From vmware/pyvmomi-community-samples
"""

import atexit
import time
import yaml
import os

from pyVmomi import vim, vmodl
from pyVim import connect
from pyVim.connect import Disconnect

homedir = os.getenv('HOME')
yaml_file = open(homedir+"/vcsa-params.yaml")
config = yaml.load(yaml_file, Loader=yaml.Loader)

inputs = {'vcenter_ip': config['VC_IP'],
          'vcenter_password': config['VC_SSO_PWD'],
          'vcenter_user': 'administrator@vsphere.local',
          'datacenter': config['VC_DATACENTER'],
          'cluster': config['VC_CLUSTER'],
          'dvs_name': config['VDS_NAME'],
          'dvs_host_uplink': config['VDS_UPLINK'],
          'dvs_pg1_name': config['VDS_PG1_NAME'],
          'dvs_pg1_vlan': config['VDS_PG1_VLAN'],
          'dvs_pg2_name': config['VDS_PG2_NAME'],
          'dvs_pg2_vlan': config['VDS_PG2_VLAN'],
          'dvs_pg3_name': config['VDS_PG3_NAME'],
          'dvs_pg3_vlan': config['VDS_PG3_VLAN'],
          }

def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def wait_for_task(task, actionName='job', hideResult=False):
    """
    Waits and provides updates on a vSphere task
    """

    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(2)

    if task.info.state == vim.TaskInfo.State.success:
        if task.info.result is not None and not hideResult:
            out = '%s completed successfully, result: %s' % (actionName, task.info.result)
            print(out)
        else:
            out = '%s completed successfully.' % actionName
            print(out)
    else:
        out = '%s did not complete successfully: %s' % (actionName, task.info.error)
        raise task.info.error
        print(out)

    return task.info.result

def create_dvSwitch(si, content, network_folder, cluster):

    pnic_specs = []
    dvs_host_configs = []
    uplink_port_names = []
    dvs_create_spec = vim.DistributedVirtualSwitch.CreateSpec()
    dvs_config_spec = vim.dvs.VmwareDistributedVirtualSwitch.ConfigSpec()
    dvs_config_spec.name = inputs['dvs_name']
    dvs_config_spec.maxMtu = 1600
    dvs_config_spec.uplinkPortPolicy = vim.DistributedVirtualSwitch.NameArrayUplinkPortPolicy()
    hosts = cluster.host

    for host in cluster.host:
        print(host.name)

    for x in range(len(hosts)):
        uplink_port_names.append("Uplink %d" % x)  ## Changed to (Uplink x) so NSX Install will work
    for host in hosts:
        print("Working on host", host.name)
        dvs_config_spec.uplinkPortPolicy.uplinkPortName = uplink_port_names
        dvs_config_spec.maxPorts = 2000
        pnic_spec = vim.dvs.HostMember.PnicSpec()
        pnic_spec.pnicDevice = inputs['dvs_host_uplink']
        pnic_specs.append(pnic_spec)
        dvs_host_config = vim.dvs.HostMember.ConfigSpec()
        dvs_host_config.operation = vim.ConfigSpecOperation.add
        dvs_host_config.host = host
        dvs_host_configs.append(dvs_host_config)
        dvs_host_config.backing = vim.dvs.HostMember.PnicBacking()
        dvs_host_config.backing.pnicSpec = pnic_specs
        dvs_config_spec.host = dvs_host_configs

    dvs_create_spec.configSpec = dvs_config_spec
    dvs_create_spec.productInfo = vim.dvs.ProductSpec(version='7.0.0')

    task = network_folder.CreateDVS_Task(dvs_create_spec)
    wait_for_task(task, si)
    print("- Successfully created DVS ", inputs['dvs_name'])
    return get_obj(content, [vim.DistributedVirtualSwitch], inputs['dvs_name'])



def add_dvPort_group(si, dv_switch, dv_pg_name, dv_pg_vlan):
    print("Creating DV Port Group")
    dv_pg_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
    dv_pg_spec.name = dv_pg_name
    dv_pg_spec.numPorts = 32
    dv_pg_spec.type = vim.dvs.DistributedVirtualPortgroup.PortgroupType.earlyBinding

    dv_pg_spec.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
    dv_pg_spec.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()

    # BELOW USED TO set to a SPECIFIC ID
    dv_pg_spec.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
    dv_pg_spec.defaultPortConfig.vlan.vlanId = dv_pg_vlan

    # 2 LINES BELOW USED FOR TRUNK PORTS to CARRY ALL
    # dv_pg_spec.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec()
    # dv_pg_spec.defaultPortConfig.vlan.vlanId = [vim.NumericRange(start=1, end=4094)]
    dv_pg_spec.defaultPortConfig.securityPolicy.allowPromiscuous = vim.BoolPolicy(value=True)
    dv_pg_spec.defaultPortConfig.securityPolicy.forgedTransmits = vim.BoolPolicy(value=True)

    dv_pg_spec.defaultPortConfig.vlan.inherited = False
    dv_pg_spec.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(value=False)
    dv_pg_spec.defaultPortConfig.securityPolicy.inherited = False

    task = dv_switch.AddDVPortgroup_Task([dv_pg_spec])
    wait_for_task(task, si)
    print("- Successfully created DV Port Group ", dv_pg_name)

def main():
    # TEMP DEBUG
    print("Inputs for program are: ")
    for i in inputs:
        print("    ", i, inputs[i])
        if inputs[i] == None:
            print("Missing a required value for ",  i)

    try:
        si = None
        try:
            print("Trying to connect to VCENTER SERVER . . .")
            si = connect.SmartConnectNoSSL('https', inputs['vcenter_ip'], 443, inputs['vcenter_user'], inputs['vcenter_password'])
        except IOError as e:
            pass
            atexit.register(Disconnect, si)

        print("Connected to VCENTER SERVER !")

        content = si.RetrieveContent()
        datacenter = get_obj(content, [vim.Datacenter], inputs['datacenter'])
        cluster = get_obj(content, [vim.ClusterComputeResource], inputs['cluster'])
        print("Cluster Name is ",cluster.name)
        network_folder = datacenter.networkFolder

        # Create DV Switch
        dv_switch = create_dvSwitch(si, content, network_folder, cluster)

        """
        mtu_spec = vim.dvs.VmwareDistributedVirtualSwitch()
        mtu_spec.name = "mtu Setting"
        mtu_spec.maxMtu = 2000
        """

        # Add port group to this switch for management traffic
        add_dvPort_group(si, dv_switch, inputs['dvs_pg1_name'], inputs['dvs_pg1_vlan'])
        # Add port group to this switch for management traffic
        add_dvPort_group(si, dv_switch, inputs['dvs_pg2_name'], inputs['dvs_pg2_vlan'])
        # Add port group to this switch for management traffic
        add_dvPort_group(si, dv_switch, inputs['dvs_pg3_name'], inputs['dvs_pg3_vlan'])

    except vmodl.MethodFault as e:
        print("Caught vmodl fault: %s" % e.msg)
        return 1
    except Exception as e:
        print("Caught exception: %s" % str(e))
        return 1


# Start program if run standalone
if __name__ == '__main__':
    main()
