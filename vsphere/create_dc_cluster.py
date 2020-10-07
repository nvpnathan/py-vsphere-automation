#!/usr/bin/env python
"""
Adapted from: https://github.com/vmware/pyvmomi-community-samples/edit/master/samples/make_dc_and_cluster.py
From vmware/pyvmomi-community-samples
This code has been released under the terms of the Apache 2.0 license
http://opensource.org/licenses/Apache-2.0
"""

import atexit
import yaml
import os
import ssl
import socket
import hashlib

from pyVmomi import vim, vmodl
from pyVim import connect
from pyVim.task import WaitForTask
from pyVim.connect import Disconnect

homedir = os.getenv('HOME')
yaml_file = open(homedir+"/vsphere_config.yaml")
cfg_yaml = yaml.load(yaml_file, Loader=yaml.Loader)

inputs = {'vcenter_ip': cfg_yaml['VC_IP'],
          'vcenter_password': cfg_yaml['VC_SSO_PWD'],
          'vcenter_user': 'administrator@vsphere.local',
          'datacenter': cfg_yaml['VC_DATACENTER'],
          'cluster': cfg_yaml['VC_CLUSTER'],
          'esx_hosts': cfg_yaml['ESX_IPS'],
          'esx_user': cfg_yaml['VC_ESXI_USR'],
           'esx_pwd': cfg_yaml['VC_ESXI_PWD']
          }


def get_obj(content, vimtype, name = None):
    return [item for item in content.viewManager.CreateContainerView(
        content.rootFolder, [vimtype], recursive=True).view]

def create_cluster(**kwargs):
    """
    Method to create a Cluster in vCenter
    :param kwargs:
    :return: Cluster MORef
    """
    cluster_name = kwargs.get("name")
    cluster_spec = kwargs.get("cluster_spec")
    datacenter = kwargs.get("datacenter")
    service_instance = kwargs.get("service_instance")

    if cluster_name is None:
        raise ValueError("Missing value for name.")
    if datacenter is None:
        raise ValueError("Missing value for datacenter.")

    try:
        for cl in get_obj(service_instance.content, vim.ComputeResource):
            if cl.name == cluster_name:
                cluster = cl
                raise ValueError()
    except(ValueError):
        print('Cluster already exists with that name, ', cluster_name)
        return cluster
    else:
        if cluster_spec is None:
            # Create Cluster Spec
            cluster_spec = vim.cluster.ConfigSpecEx()
            # Create HA SubSpec and add to ClusterSpec https://pubs.vmware.com/vi-sdk/visdk250/ReferenceGuide/vim.cluster.DasConfigInfo.html
            ha_spec = vim.cluster.DasConfigInfo()
            ha_spec.enabled = True
            ha_spec.hostMonitoring = vim.cluster.DasConfigInfo.ServiceState.enabled
            ha_spec.failoverLevel = 1
            cluster_spec.dasConfig = ha_spec
            # Create DRS subspec and add to cluster_spec https://pubs.vmware.com/vi-sdk/visdk250/ReferenceGuide/vim.cluster.DrsConfigInfo.html
            drs_spec = vim.cluster.DrsConfigInfo()
            drs_spec.enabled = True
            cluster_spec.drsConfig = drs_spec


    host_folder = datacenter.hostFolder
    try:
        cluster = host_folder.CreateClusterEx(name=cluster_name, spec=cluster_spec)
        raise ValueError()
    except(ValueError):
        print('Could NOT create the cluster !')

    return cluster

def create_datacenter(dcname=None, service_instance=None, folder=None):
    #dcname = kwargs.get("dcname")
    #service_instance = kwargs.get("service_instance")
    print('dcname !', dcname)
    print('service_instance !', service_instance.content.about.name)
    print('folder !', folder)

    if len(dcname) > 79:
        raise ValueError("The name of the datacenter must be under 80 characters.")

    folder = service_instance.content.rootFolder
    print('Obtained the root folder !')
    datacenters = [entity for entity in service_instance.content.rootFolder.childEntity
                           if hasattr(entity, 'vmFolder')]
    try:
        for dc in datacenters:
            if dc.name == dcname:
                dc_moref = dc
                raise ValueError()
    except(ValueError):
        print('Datacenter already exists !')
        return dc_moref
    else:
        if folder is not None and isinstance(folder, vim.Folder):
            dc_moref = folder.CreateDatacenter(name=dcname)
            print('Datacenter created !')
            return dc_moref

def add_hosts_to_vc(dc,cluster,esx_hosts,esx_user,esx_pwd):
    host_objects = []
    folder = dc.hostFolder
    for ip in esx_hosts:
        # Get ESXi SSL thumbprints
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        wrappedSocket = ssl.wrap_socket(sock)
        wrappedSocket.connect((ip, 443))
        der_cert_bin = wrappedSocket.getpeercert(True)
        thumb_sha1 = hashlib.sha1(der_cert_bin).hexdigest()
        thumb = ':'.join(a + b for a, b in zip(thumb_sha1[::2], thumb_sha1[1::2]))
        print("Host thumbprint is ", thumb)

        connect_spec = vim.host.ConnectSpec(hostName=ip,
                                        userName=esx_user,
                                        password=esx_pwd,
                                        sslThumbprint=thumb,
                                        force=False)
        print("Adding Host ({}) to vCenter".format(ip))
        task = folder.AddStandaloneHost(connect_spec,
                                           vim.ComputeResource.ConfigSpec(),
                                           True)
        # Get host from task result
        WaitForTask(task)
        host_mo = task.info.result.host[0]
        #print("Created Host '{}' ({})".format(mo._moId, ip))
        print("Added Host '{}' ({} to vCenter)".format(host_mo._moId, host_mo.name))
        host_objects.append(host_mo)
    return host_objects


def move_hosts_to_cluster(cluster_mo, host_objects):
    for host_mo in host_objects:
        task = cluster_mo.MoveInto([host_mo])
        WaitForTask(task)
        print("Host '{}' ({}) moved into Cluster {} ({})".
              format(host_mo, host_mo.name, cluster_mo, cluster_mo.name))

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
            print("Connected to VCENTER SERVER !", si.content.about.name)
        except IOError as e:
            print("Error connecting to vCenter !", inputs['vcenter_ip'])
            print("Error is: ", e)
            pass
            atexit.register(Disconnect, si)

        print("Connected to VCENTER SERVER !")
        content = si.RetrieveContent()
        # CREATE THE DATACENTER
        print("Creating Datacenter !")
        dc = create_datacenter(dcname=inputs['datacenter'], service_instance=si)

        # CREATE THE CLUSTER
        print("Creating Cluster !")
        cluster = create_cluster(datacenter=dc, service_instance=si, name=inputs['cluster'])

        # ADD THE HOSTS to vCENTER
        print("Adding Hosts !")
        host_objects = add_hosts_to_vc(dc, cluster, inputs['esx_hosts'], inputs['esx_user'], inputs['esx_pwd'])
        for i in host_objects:
            print ("ESX ADDED NAME = ", i.name)

        move_hosts_to_cluster (cluster,host_objects)


    except vmodl.MethodFault as e:
        print("Caught vmodl fault: %s" % e.msg)
        return 1
    except Exception as e:
        print("Caught exception: %s" % str(e))
        return 1

# Start program
if __name__ == '__main__':
    main()
