#!/usr/bin/env python

from charmhelpers.core.hookenv import config
from charmhelpers.contrib.openstack import context, templating

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
        #ctxt['aci_apic_vmm_domain_name'] = config('aci-apic-vmm-domain-name')
        ctxt['aci_apic_entity_profile'] = config('aci-apic-entity-profile')
        ctxt['aci_connection_json'] = config('aci-connection-json')

        return ctxt

