#!/usr/bin/env python
"""
Author: Tkraus
"""

import vsphere.esx_deploy
import vsphere.create_vds
import vsphere.create_dc_cluster
import vsphere.vcsa_deploy


def main():
    vsphere.esx_deploy.main()
    vsphere.vcsa_deploy.deploy_vcsa()
    vsphere.create_dc_cluster.main()
    vsphere.create_vds.main()

# Start program
if __name__ == '__main__':
    main()


