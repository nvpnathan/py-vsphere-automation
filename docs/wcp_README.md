###  Note
- For now we are relying on the following REPO (https://github.com/vThinkBeyondVM/vThinkBVM-scripts) which provides a Python script that makes REST calls to the vSphere REST API.  This is configured as a submodule in our Repo and configuration inputs are separate from yaml configuration file and placed on the Command Line as Arguments.

###  Requirements

- You need NSX-T 3.0 Datacenter installed in the cluster you are preparing for Kubernetes
- 
- 


### Install Requirements

Coming soon.

``` 

```
### Get script parameters and environmental information

``` 
-s = 
-u
-cl
-mnw 
-sip
-sm
-gw
-dns
-ntp
-sp
-ingress
-egress
-prefix
-
```

### Run the configure_supervisor_cluster.py Install script.
Once you have exported the 3 ENV VARS you can execute the wrapper script to Install NSX Cluster, Edge Nodes, T0 Router etc.

```shell
python3 configure_supervisor_cluster.py -s "10.193.245.14" -u "administrator@vsphere.local" \
-cl "Workload-Cluster" -mnw "DVPG-Management Network" -sip "10.193.245.45" -sm "255.255.255.0" \
-gw "10.193.245.1" -dns "10.192.2.10" -ntp "10.192.2.5 " -sp "pacific-gold-storage-policy" \
-ingress "10.193.254.128" -egress "10.193.245.64" -prefix 26
    Enter VC password:
    Session creation is successful
    cluster-id::domain-c8
    storage policy id:e08fac3e-eaa6-44ff-a7bc-e988c7b79606
    ee76eac5-e47c-4965-8d24-eaa769b487a4
    d8c340e5-e487-4ff9-ab30-2eac01e69052
    network id::dvportgroup-18
    Enable API invoked, checkout your H5
```
