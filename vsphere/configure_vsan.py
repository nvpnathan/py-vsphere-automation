"""
Author TKraus

Now Requires

cp vsanapiutils.py /usr/local/lib/python3.7/site-packages/vsanapiutils.py

"""

import atexit
import time
import yaml
import os
import ssl

from pyVmomi import vim, vmodl
from pyVim import connect
from pyVim.connect import Disconnect
import vsanapiutils
import vsanmgmtObjects

# vsanmgmtObjects.py should be put in the python site-packages folder for Python3

homedir = os.getenv('HOME')
yaml_file = open(homedir+"/vsphere_config.yaml")
config = yaml.load(yaml_file, Loader=yaml.Loader)

inputs = {'vcenter_ip': config['VC_IP'],
          'vcenter_password': config['VC_SSO_PWD'],
          'vcenter_user': 'administrator@vsphere.local',
          'datacenter': config['VC_DATACENTER'],
          'cluster': config['VC_CLUSTER'],
          'dvs_name': config['VDS_NAME'],
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

def CollectMultiple(content, objects, parameters, handleNotFound=True):
   if len(objects) == 0:
      return {}
   result = None
   pc = content.propertyCollector
   propSet = [vim.PropertySpec(
      type=objects[0].__class__,
      pathSet=parameters
   )]

   while result == None and len(objects) > 0:
      try:
         objectSet = []
         for obj in objects:
            objectSet.append(vim.ObjectSpec(obj=obj))
         specSet = [vim.PropertyFilterSpec(objectSet=objectSet, propSet=propSet)]
         result = pc.RetrieveProperties(specSet=specSet)
      except vim.ManagedObjectNotFound as ex:
         objects.remove(ex.obj)
         result = None

   out = {}
   for x in result:
      out[x.obj] = {}
      for y in x.propSet:
         out[x.obj][y.name] = y.val
   return out


def enable_vsan_vmknic(si, vmkernel_nic, cluster):
    tasks=[]
    # Update configuration spec for VMkernel networking
    configInfo = vim.vsan.host.ConfigInfo(
        networkInfo=vim.vsan.host.ConfigInfo.NetworkInfo(port=[
            vim.vsan.host.ConfigInfo.NetworkInfo.PortConfig(device=vmkernel_nic)
        ]))

    # Enumerate the selected VMkernel adapter for each host and add it to the list of tasks
    hostProps = CollectMultiple(si.content, cluster.host,
                                ['name', 'configManager.vsanSystem', 'configManager.storageSystem'])
    hosts = hostProps.keys()

    for host in hosts:
        print('Enable vSAN traffic on host {} with {}'.format(hostProps[host]['name'], vmkernel_nic))
        task = hostProps[host]['configManager.vsanSystem'].UpdateVsan_Task(configInfo)
        wait_for_task(task)

    # Can make this faster by running tasks concurrently see below scratch code
    #tasks.append(task)
    # Execute the tasks
    #vsanapiutils.WaitForTasks(tasks, si)

    # Build vsanReconfigSpec step by step. It takes effect only after calling the VsanClusterReconfig method
    clusterConfig = vim.VsanClusterConfigInfo(enabled=True)
    vsanReconfigSpec = vim.VimVsanReconfigSpec(
        modify=True, vsanClusterConfig=clusterConfig)

def CreateHostConfigProfile(ntpServer, lockdownMode):
   ntpServers = [ntpServer]
   ntpConfig = vim.HostNtpConfig(server=ntpServers)
   dateTimeConfig = vim.HostDateTimeConfig(ntpConfig=ntpConfig)
   hostConfigProfile = \
       vim.ClusterComputeResource.\
       HostConfigurationProfile(dateTimeConfig=dateTimeConfig,
                                lockdownMode=lockdownMode)
   return hostConfigProfile

def CreateDefaultVSanSpec(vSanCfgInfo):
    dedupConfig = vim.vsan.DataEfficiencyConfig(compressionEnabled=False,dedupEnabled=False)
    encryptionConfig = vim.vsan.DataEncryptionConfig(encryptionEnabled=False)
    vSanSpec = vim.vsan.ReconfigSpec(
        vsanClusterConfig=vSanCfgInfo,
        dataEfficiencyConfig=dedupConfig,
        dataEncryptionConfig=encryptionConfig,
        modify=True,
        allowReducedRedundancy=True
    )
    return vSanSpec

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
        cluster = get_obj(content, [vim.ClusterComputeResource], inputs['cluster'])
        print("Cluster Name is ",cluster.name)

        # Configure vmkernel adapter on all hosts for vSAN
        vmkernel_nic = "vmk0"
        enable_vsan_vmknic(si, vmkernel_nic, cluster)



        ## From https://github.com/storage-code/vsanDeploy/blob/master/vsanDeploy.py
        context = None
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        vcMos = vsanapiutils.GetVsanVcMos(si._stub, context=context)

        vsanClusterSystem = vcMos['vsan-cluster-config-system']
        vsanVcDiskManagementSystem = vcMos['vsan-disk-management-system']

        # Build vsanReconfigSpec step by step, it only take effect after method VsanClusterReconfig is called
        vsanReconfigSpec = vim.VimVsanReconfigSpec(
            modify=True,
            vsanClusterConfig=vim.VsanClusterConfigInfo(
                enabled=True,
                defaultConfig=vim.VsanClusterConfigInfoHostDefaultInfo(
                    autoClaimStorage=True
                )
            )
        )

        print('Disable deduplication and compression for VSAN')
        vsanReconfigSpec.dataEfficiencyConfig = vim.VsanDataEfficiencyConfig(
            compressionEnabled=False,
            dedupEnabled=False)

        task = vsanClusterSystem.VsanClusterReconfig(cluster, vsanReconfigSpec)
        wait_for_task(task)

        '''
        print("Configuring HCI for cluster %s ..." % cluster.name)
        hciCfgs = []
        for mo in cluster.host:
            hciCfg = vim.ClusterComputeResource.HostConfigurationInput()
            hciCfg.host = mo
            hciCfgs.append(hciCfg)

        lockdownMode = vim.host.HostAccessManager.LockdownMode.lockdownDisabled
        NTP_SERVER = "time-c-b.nist.gov"
        hostConfigProfile = CreateHostConfigProfile(NTP_SERVER, lockdownMode)
        vSanCfgInfo = vim.vsan.cluster.ConfigInfo(
            enabled=True,
            defaultConfig=vim.vsan.cluster.ConfigInfo.HostDefaultInfo(
                autoClaimStorage=False))
        print("vSanCfgInfo Set successfully ", vSanCfgInfo)
        vSanSpec = CreateDefaultVSanSpec(vSanCfgInfo)
        print("CreateDefaultVSanSpec successfully ", vSanSpec)

        #vcProf = GetVcProf()
        #dvsProfiles = GetDvsProfiles(cluster.host)
        clusterHciSpec = vim.ClusterComputeResource.HCIConfigSpec(
            hostConfigProfile=hostConfigProfile,
            vSanConfigSpec=vSanSpec)

        task = cluster.ConfigureHCI_Task(clusterSpec=clusterHciSpec, \
                                         hostInputs=hciCfgs)
        wait_for_task(task)
        print("Successfully configured HCI cluster %s" % clusterName)
        '''

    except vmodl.MethodFault as e:
        print("Caught vmodl fault: %s" % e.msg)
        return 1
    except Exception as e:
        print("Caught exception: %s" % str(e))
        return 1


# Start program if run standalone
if __name__ == '__main__':
    main()
