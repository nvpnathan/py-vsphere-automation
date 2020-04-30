#!/usr/bin/env python
"""
Written by Michael Rice
Github: https://github.com/michaelrice
Website: https://michaelrice.github.io/
Blog: http://www.errr-online.com/
This code has been released under the terms of the Apache 2.0 license
http://opensource.org/licenses/Apache-2.0
"""
import atexit
import os

from pyvim.connect import SmartConnect, Disconnect

# from tools import cluster
# from tools import datacenter
# from tools import cli

from pyVmomi import vim, vmodl
from pyvim import connect
from pyvim.connect import Disconnect

inputs = {'vcenter_ip': os.environ.get('VCENTER_IP'),
          'vcenter_password': os.environ.get('VCENTER_PW'),
          'vcenter_user': os.environ.get('VCENTER_USER'),
          'datacenter': 'python-tmp-dc',
          'cluster': 'python-tmp-cluster'
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
        cluster_spec = vim.cluster.ConfigSpecEx()

    host_folder = datacenter.hostFolder

    print("Host Folder is ", host_folder)
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
            #si_old = connect.Connect(inputs['vcenter_ip'], 443, inputs['vcenter_user'], inputs['vcenter_password'])
            si = connect.SmartConnectNoSSL('https', inputs['vcenter_ip'], 443, inputs['vcenter_user'], inputs['vcenter_password'])
            #test = connect.SmartConnectNoSSL()
        except IOError as e:
            pass
            atexit.register(Disconnect, si)

        print("Connected to VCENTER SERVER !")
        dc = create_datacenter(dcname=inputs['datacenter'], service_instance=si)
        create_cluster(datacenter=dc, name=inputs['cluster'])

    except vmodl.MethodFault as e:
        print("Caught vmodl fault: %s" % e.msg)
        return 1
    except Exception as e:
        print("Caught exception: %s" % str(e))
        return 1

# Start program
if __name__ == '__main__':
    main()
