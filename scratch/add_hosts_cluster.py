
#!/usr/bin/env python
#
# Written by Juan Manuel Rey
# Github: https://github.com/jreypo
# Blog: http://blog.jreypo.io/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# vSphere Python SDK script to force the HA reconfiguration in an ESXi host
# Tested with vSphere 6.0 U1
#

import atexit
import yaml
import os

from pyVmomi import vim, vmodl
from pyvim import connect
from pyvim.connect import Disconnect

homedir = os.getenv('HOME')
yaml_file = open(homedir+"/vcsa-params.yaml")
config = yaml.load(yaml_file, Loader=yaml.Loader)


# Method that populates objects of type vimtype
def get_all_objs(content, vimtype):
    obj = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref: managed_object_ref.name})
    return obj


def main():

    try:
        si = None
        try:
            print("Trying to connect to VCENTER SERVER . . .")
            si = connect.SmartConnectNoSSL('https', config['VC_IP'], 443, 'administrator@vsphere.local', config['VC_SSO_PWD'])

        except IOError as e:
            pass
            atexit.register(Disconnect, si)





        print("Connected to VCENTER SERVER !")
        content = si.content

        # Get all Clusters
        clusters = get_all_objs(content, [vim.ClusterComputeResource])

        # For ESXi host
        hosts = get_all_objs(content, [vim.HostSystem])

        # For datacenters
        dcs = get_all_objs(content, [vim.Datacenter])

        # For datastores
        datastores = get_all_objs(content, [vim.Datastore])

        # Iterating each datacenter object and printing its name
        for dc in dcs:
            print("Datacenter found:", dc.name)

        # Iterating each host object and printing its name
        for cluster in clusters:
            print("Cluster found :", cluster.name)
            if cluster.name==config["VC_CLUSTER"]:
                print("Found what we were looking for", config["VC_CLUSTER"])
                return cluster
            else:
                print("Could NOT find what we were looking for", config["VC_CLUSTER"])

        # Iterating each cluster object and printing its name
        for host in hosts:
            print("Host found :", host.name)

        # Iterating each cluster object and printing its name
        for datastore in datastores:
            print("Datastore found:",datastore.name)




        # Get all ESXi hosts from the VC
        object_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                              [vim.HostSystem],
                                                              True)
        host_list = object_view.view
        print(host_list)
        object_view.Destroy()


        for host in host_list:
            #if host.name == args.esx_host:
            esx = host
            print("ESX Name", esx.name)


    except vmodl.MethodFault as e:
        print("Caught vmodl fault: %s" % e.msg)
        return 1
    except Exception as e:
        print("Caught exception: %s" % str(e))
        return 1

# Start program
if __name__ == '__main__':
    main()
