#!/usr/bin/env python3

from charmhelpers.core.hookenv import config
from charmhelpers.contrib.openstack import context, templating
import yaml
import pdb

class AciAimConfigContext(context.OSContextGenerator):
    def __call__(self):
        ctxt = {}

        ctxt['debug'] = 'True'
        ctxt['apic_hosts'] = config('aci-apic-hosts')
        ctxt['apic_username'] = config('aci-apic-username')
        ctxt['apic_password'] = config('aci-apic-password')

        return ctxt

class AciAimCtlConfigContext(context.OSContextGenerator):
    def __call__(self):
        ctxt = {}
        cnf = config()

        ctxt['aci_apic_system_id'] = cnf['aci-apic-system-id']
        ctxt['aci_encap'] = cnf['aci-encap']
        ctxt['aci_vlan_ranges'] = cnf['aci-vlan-ranges']
        ctxt['aci_vpc_pairs'] = cnf['aci-vpc-pairs']
        #ctxt['aci_apic_vmm_domain_name'] = cnf['aci-apic-vmm-domain-name']
        ctxt['aci_apic_entity_profile'] = cnf['aci-apic-entity-profile']
        ctxt['aci_disable_vmdom'] = cnf['aci-disable-vmdom']
        ctxt['aci_vlan_ranges'] = cnf['aci-vlan-ranges']

        if 'aci-connection-json' in cnf.keys():
           ctxt['aci_connection_json'] = cnf['aci-connection-json']

        if 'aci-physnet-host-mapping' in cnf.keys() and cnf['aci-physnet-host-mapping']:
           #sample input '{"physnet0": "host1:e1:e2,host2:e3", "physnet1":"host1:e4:e5:e6"}'
           aphm = yaml.load(cnf['aci-physnet-host-mapping'])

           ctxt['aci_physnet_host_mapping_dict'] = {}
           for pnet in aphm.keys():
              ctxt['aci_physnet_host_mapping_dict'][pnet] = ",".join([x.split(':')[0] for x in aphm[pnet].split(',')])

        if 'aci-physdom-id' in cnf.keys():
           ctxt['aci_physdom_id'] = cnf['aci-physdom-id']

        return ctxt

