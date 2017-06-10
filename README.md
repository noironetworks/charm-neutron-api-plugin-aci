Overview
--------

This subordinate charm provides the Neutron API component which configure neutron-server for Group Based Policy (GBP) and cisco ACI configuration.


Usage
-----

Neutron API is a prerequisite service to deploy. 'neutron-api' charm should be deployed with neutron-plugin option set to 'aci'

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

aci-encap

     (string)

     Options are 'vlan' or 'vxlan'. 

     (vlan)

aci-vlan-ranges

     (string)

     Vlan range to be used. Format <starting_vlan>:<ending_vlan>. Ignored if aci-encap is vxlan. Should match vlan-ranges option of neutron-gateway

     (1000:1010)

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

aci-apic-system-id

     (string)

     Id string for this openstack instance

     openstack

aci-apic-entity-profile:
     
     (string)
    
     ACI Attached Entity Profile that is configured on fabric

apic-connection-json

     (string)

     Describes nova-compute connections to ACI leaf in JSON format. Example {'101': ['host1.domain:1/1', 'host2.domain:1/2'], '102':['host3.domain:1/4']}. 101 is the switch id, host1.domain is connected to port 1/1 

apic-vpc-pairs

     (string)
     
     If using VPC to connect the nodes to ACI leaf switches, specify the switch id pairs for vpc. Example, if switch ids 101 and 102 form a vpc pair and switch ids 103, 104 form a vpc pair, then set the value to '101:102,103:104'



Deployment
----------
For this plugin deployment, the dependent charms need to have the following configuration

neutron-api charm

    neutron-plugin value should be 'aci', neutron-security-groups value should be set to 'true'

neutron-gateway
    
    plugin value should be 'aci', data-port needs to be set to port connected to ACI leaf, example 'br-data:eth2'

neutron-openvswitch
   
    data-port should be set to port connected to ACI leaf
Contact Information
-------------------

Author: Ratnakar Kolli (rkolli@noironetworks.com)
Report bugs at: 
Location: 


