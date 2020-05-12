## VDS Creation with single uplink and 3 Portgroups with VLAN Tags

### Requirements

The VCSA Appliance needs to be deployed already

### Configure Parameters.

To create the VDS and Port Groups you need to set the following parameters:

``` 
export VCENTER_IP ='192.168.44.86'                                  # IP for VCSA Appliance
export VCENTER_PW = 'passforvc'
export VCENTER_USER ='administrator@vsphere.local'

```

### Configure Variables in the Script 

To create the VDS and Port Groups you need to update the inputs in the create_vds.py script:

``` 
inputs = {'vcenter_ip': os.environ.get('VCENTER_IP'),
          'vcenter_password': os.environ.get('VCENTER_PW'),
          'vcenter_user': os.environ.get('VCENTER_USER'),
          'datacenter': 'Datacenter',
          'cluster': 'Nested-PKS',
          'dvs_name': 'PythonDVS1',
          'dvs_pg1_name': 'management-vm',
          'dvs_pg1_vlan': 100,
          'dvs_pg2_name': 'tep-edge',
          'dvs_pg2_vlan': 102,
          'dvs_pg3_name': 'ext-uplink-edge',
          'dvs_pg3_vlan': 103,
          }
```

### Run the VDS creation script.
Once you have exported the 3 ENV VARS and updated inputs in the script you can run with the following:

```shell
python3 ./vds/ create_vds.py
```
