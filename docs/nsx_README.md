###  Note
- For now we are relying on the following REPO (https://github.com/madhukark/nsx-install-wrapper) which provides a Python wrapper around Ansible Playbooks.  This is configured as a submodule in our Repo and configuration inputs are separate from yaml configuration file used for other automation pieces.

###  Requirements

- You need the NSX-T 3.0 Datacenter Unified Appliance OVA downloaded
- You need ansible installed
- You need ovftool installed locally
- Optional:  You need a product key for NSX-T 3.0



### Install Requirements

Coming soon.

``` 

```
### Fill in the nsx-config.txt file with your environment information

``` 
vi github/py-vsphere-automation/nsx-install-wrapper/nsx-config.txt
```

### Run the NSX Install script.
Once you have exported the 3 ENV VARS you can execute the wrapper script to Install NSX Cluster, Edge Nodes, T0 Router etc.

```shell
python3 nsx-install.py --start
```
