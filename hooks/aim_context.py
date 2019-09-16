#!/usr/bin/env python3

from charmhelpers.core.hookenv import config
from charmhelpers.contrib.openstack import context, templating
import json, yaml

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

        ctxt['aci_apic_system_id'] = config('aci-apic-system-id')
        ctxt['aci_encap'] = config('aci-encap')
        ctxt['aci_vlan_ranges'] = config('aci-vlan-ranges')
        ctxt['aci_vpc_pairs'] = config('aci-vpc-pairs')
        ctxt['aci_apic_entity_profile'] = config('aci-apic-entity-profile')
        ctxt['aci_disable_vmdom'] = config('aci-disable-vmdom')

        if config('aci-connection-json'):
           ctxt['aci_connection_dict'] = json.loads(config('aci-connection-json'))
        else:
           ctxt['aci_connection_dict'] = {}

        if config('aci-physnet-host-mapping'): 
           #sample input '{"physnet0": "host1:e1:e2,host2:e3", "physnet1":"host1:e4:e5:e6"}'
           aphm = yaml.load(config('aci-physnet-host-mapping'))

           ctxt['aci_physnet_host_mapping_dict'] = {}
           for pnet in aphm.keys():
              ctxt['aci_physnet_host_mapping_dict'][pnet] = ",".join([x.split(':')[0] for x in aphm[pnet].split(',')])

        if config('aci-physdom-id'):
           ctxt['aci_physdom_id'] = config('aci-physdom-id')

        return ctxt

