# NSX Install Wrapper

## Overview
This repository contains code that simplifies NSX Install by providing a wrapper script. The information needed to install NSX is read from 2 files.

* Defaults: This contains certain display names. Users can change this but is not required to.

* Uer Config: This contains all the information that is needed from the user (like network details, passwords etc)

The provided nsx-install.py script merges these files to generate a JSON file which is used by the Ansible modules to install NSX.

### What the wrapper does:
* Deploys a NSX Manager cluster (or a single NSX node)
* Configures NSX Manager with vCenters
* Deploys 2 Edges and creates a cluster
* Creates a Host Switch Profile and Transport Node Profile
* Preps one or more vCenter Clusters (to create Host Transport Nodes)
* Adds a License file to NSX Manager and Accepts the EULA

## System Dependencies
There are dependency on the following tools:
* Python > 3.6.x
* Ansible > 2.9.x
* PyVmomi
* OVFTool

## Version Check
An easy way to verify if Python and Ansible are in the right versions:
```
$> ansible-playbook --version
ansible-playbook 2.9.6
  config file = /etc/ansible/ansible.cfg
  configured module search path = ['/home/vmware/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/local/lib/python3.6/dist-packages/ansible
  executable location = /usr/local/bin/ansible-playbook
  python version = 3.6.9 (default, Nov  7 2019, 10:44:02) [GCC 8.3.0]
```

## Getting Started
* Read the FAQ below
* Clone this repo to a linux based system (Ubuntu/CentOS)
* Make sure the dependencies are met (Install Python/Ansible/PyVmomi)
* Download the NSX unified appliance installer OVA on the local file system
* Edit nsx-config.txt file and update ALL the fields. Make sure you also have a NSX License!
* Run python nsx-install.py --start

## Optional (Advanced) functionality
* Run python nsx-install.py --reset-defaults
  This creates the nsx-defaults.txt file. Edit the file if needed. Editing it is purely optional
  Note: Running python nsx-install.py --reset-defaults will overwrite the existing file
* Run python nsx-install.py --reset-config
  This creates the nsx-config.txt file. Edit the file and provide all the information
  Save the nsx-config.txt in case you want to refer to it later
  Note: Running python nsx-install.py --reset-config will overwrite the existing file

## Logging
All logs are generated in nsx-install.log

## Frequently Asked Questions (FAQ)

  - [Can I deploy just 1 NSX manager](#can-i-deploy-just-1-nsx-manager)
  - [Can I run in an nested environment](#can-i-run-in-a-nested-environment)
  - [I only have 1 vCenter](#i-only-have-1-vcenter-what-can-i-do)
  - [Dont want to run the whole install but run playbooks manually](#i-dont-want-to-run-the-whole-install-but-want-to-run-the-playbooks-manually-can-i)
  - [I just have 1 cluster where I want to deploy NSX Manager, Edges and Host Transport Nodes](#i-just-have-1-cluster-where-i-want-to-deploy-nsx-manager-edges-and-have-host-transport-nodes-can-i-use-this-script)
  - [Can I prep my Hosts Induvidually and not as a Cluster](#can-i-prep-my-host-induvidually-and-not-at-a-cluster-level)
  - [Can I change the number of Edges that are deployed](#can-i-change-the-number-of-edges-that-are-deployed)
  - [Can I customize the workflow](#can-i-customize-the-workflow)

### Can I deploy just 1 NSX manager?

  Yes.

  - Edit nsx-config.txt and change the 'nsx_manager_cluster' to 'No'
  - Run 'python nsx-install.py --start'
  
### Can I run in a nested environment?

  Yes.

  As long as there are enough resources (CPU, Memory, Disk) and there is IP connectivity between 
  vCenter, NSX and the system on which the script is run.

### I only have 1 vCenter. What can I do?

  Just put the same information (fqdn, username, password) in both places in nsx-cofig.txt:
```
    nsx_vcenter_fqdn = ""
    nsx_vcenter_username = ""
    nsx_vcenter_password = ""
```

```
    vcenter_fqdn = ""
    vcenter_username = ""
    vcenter_password = ""
```
  NOTE: There has to be at least 2 Clusters in your datacenter. One cluster will be used
        to deploy NSX Manager(s) and Edges and the second cluster will be used for Host Transport Nodes.
        

### I dont want to run the whole install but want to run the playbooks manually. Can I?

  Yes.

  Run 'python nsx-install.py --manual'. This will first merge the nsx-defaults.txt and nsx-config.txt and generate the nsx_pacific_vars.yml.
  You can then run: 'ansible-playbook 01_deploy_first_node.yml'  or any other playbook.

### I just have 1 cluster where I want to deploy NSX Manager, Edges and have Host Transport Nodes. Can I use this script?

  No.

  The install wrapper expects at least 2 different clusters. One cluster will be to install NSX Manager(s) and Edges. THe other cluster will be prepped for NSX. So ALL hosts in that cluster will be Host Transport Nodes.


### Can I prep my Host induvidually and not at a cluster level?

  Not through this script. The underlying Ansible playbooks support this. Please look at example here:
  ["Prep Single Hosts as Transport Nodes](https://github.com/vmware/ansible-for-nsxt/tree/dev/examples/setup_infra "Example")

### Can I change the number of Edges that are deployed?

  No. Customization can be done by using the underlying Ansible modules directly. Please check ["NSX-T Ansible modules"](https://github.com/vmware/ansible-for-nsxt/tree/dev "NSX-T Ansible Modules")
  
### Can I customize the workflow?

  No. The script is ment to deploy a specific topology quickly. Customization can be done by using the underlying Ansible modules directly. Please check ["NSX-T Ansible modules"](https://github.com/vmware/ansible-for-nsxt/tree/dev "NSX-T Ansible Modules")

## Issues?

  Please file an issue on GitHub with the following info:
  - The complete log file (nsx-install.log)
  - nsx-defaults.txt and nsx-config.txt (feel free to sanitize the password)
  - The output of 'ansible-playbook --version'

## Resources
For general information about Ansible, visit the [GitHub project page][an-github].

[an-github]: https://github.com/ansible/ansible

Documentation on the NSX platform can be found at the [NSX-T Documentation page](https://docs.vmware.com/en/VMware-NSX-T/index.html)

