Overview
--------

This subordinate charm provides the Neutron API component which configure neutron-server for Group Based Policy (GBP) and cisco ACI configuration.


Usage
-----

Neutron API is a prerequisite service to deploy.

    juju deploy neutron-api-plugin-aci
    juju add-relation neutron-api-plugin-aci neutron-api

Configuration
-------------
aci-repo

     (string)

     Repository url for ACI plugin packages

aci-repo-key

     (string)

     GPG key for aci-repo. If not specified, packages will be installed with out authentication

use-gbp

     (boolean)

     If true, configures aci plugin to use Group Based Policy, else configures plugin for ML2

     True

use-opflex

     (boolean)

     If true, sets up the environment to use Opflex, the aci encap can be Vlan or Vxlan. When not using Opflex, aci encap value is ignored and set to Vlan

     False

aci-encap

     (string)

     Options are 'vlan' or 'vxlan'. When 'use-opflex' is set to False, this value is ignored and encap is forced to vlan.

     (vlan)

apic-hosts

     (string)

     Comma separated list of ACI controller host names or ip addresses

apic-username

     (string)

     username for ACI controller
 
     admin

apic-password

     (string)

     password for ACI user

use-vmm

     (string)

     If true, api creates a openstack vmm domain, if false it uses domain specified by apic-domain-name

     True

apic-domain-name

     (string)

     Name of aci domain for this openstack instance

apic-connection-json

     (string)

     Describes nova-compute connections to ACI leaf in JSON format. Example {'101': ['host1.domain:1/1', 'host2.domain:1/2'], '102':['host3.domain:1/4']}. 101 is the switch id, host1.domain is connected to port 1/1 

apic-l3out

     (string)

     comma separated string representing external network name and associated epg. Example 'ext1:ext1epg, ext2:ext2epg'

Contact Information
-------------------

Author: Ratnakar Kolli (rkolli@noironetworks.com)
Report bugs at: 
Location: 


