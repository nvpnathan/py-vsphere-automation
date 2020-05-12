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
yaml_file = open(homedir+"/vcsa-params.yaml")
config = yaml.load(yaml_file, Loader=yaml.Loader)

inputs = {'vcenter_ip': config['VC_IP'],
          'vcenter_password': config['VC_SSO_PWD'],
          'vcenter_user': 'administrator@vsphere.local',
          'datacenter': config['VC_DATACENTER'],
          'cluster': config['VC_CLUSTER'],
          'esx_hosts': config['ESX_IPS'],
          'esx_user': config['VC_ESXI_USR'],
           'esx_pwd': config['VC_ESXI_PWD']
          }

def create_cluster(**kwargs):
    """
    Method to create a Cluster in vCenter
    :param kwargs:
    :return: Cluster MORef
    """
    cluster_name = kwargs.get("name")
    cluster_spec = kwargs.get("cluster_spec")
    datacenter = kwargs.get("datacenter")

    if cluster_name is None:
        raise ValueError("Missing value for name.")
    if datacenter is None:
        raise ValueError("Missing value for datacenter.")
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
    cluster = host_folder.CreateClusterEx(name=cluster_name, spec=cluster_spec)

    return cluster

def create_datacenter(dcname=None, service_instance=None, folder=None):
    """
    Creates a new datacenter with the given name.
    Any % (percent) character used in this name parameter must be escaped,
    unless it is used to start an escape sequence. Clients may also escape
    any other characters in this name parameter.
    An entity name must be a non-empty string of
    less than 80 characters. The slash (/), backslash (\) and percent (%)
    will be escaped using the URL syntax. For example, %2F
    This can raise the following exceptions:
    vim.fault.DuplicateName
    vim.fault.InvalidName
    vmodl.fault.NotSupported
    vmodl.fault.RuntimeFault
    ValueError raised if the name len is > 79
    https://github.com/vmware/pyvmomi/blob/master/docs/vim/Folder.rst
    Required Privileges
    Datacenter.Create
    :param folder: Folder object to create DC in. If None it will default to
                   rootFolder
    :param dcname: Name for the new datacenter.
    :param service_instance: ServiceInstance connection to a given vCenter
    :return:
    """
    if len(dcname) > 79:
        raise ValueError("The name of the datacenter must be under "
                         "80 characters.")
    if folder is None:
        folder = service_instance.content.rootFolder

    if folder is not None and isinstance(folder, vim.Folder):
        dc_moref = folder.CreateDatacenter(name=dcname)
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

        except IOError as e:
            pass
            atexit.register(Disconnect, si)

        print("Connected to VCENTER SERVER !")

        # CREATE THE DATACENTER
        print("Creating Datacenter !")
        dc = create_datacenter(dcname=inputs['datacenter'], service_instance=si)

        # CREATE THE CLUSTER
        print("Creating Cluster !")
        cluster = create_cluster(datacenter=dc, name=inputs['cluster'])

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
