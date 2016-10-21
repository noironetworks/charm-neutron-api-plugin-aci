#!/usr/bin/env python


import subprocess
import sys

from charmhelpers.core.hookenv import (
    Hooks,
    UnregisteredHookError,
    config,
    log,
    relation_set,
    relation_get,
    relation_ids,
    is_relation_made,
    is_leader,
)

from charmhelpers.core.host import (
    restart_on_change,
    service_restart
)

from charmhelpers import fetch

NEUTRON_CONF_DIR = "/etc/neutron"

NEUTRON_CONF = '%s/neutron.conf' % NEUTRON_CONF_DIR

hooks = Hooks()

def _neutron_apic_ml2_db_manage():
    log("Migrating the neutron database for ACI")
    cmd = ['apic-ml2-db-manage',
           '--config-file', NEUTRON_CONF,
           'upgrade',
           'head']
    subprocess.check_output(cmd)

def _neutron_gbp_db_manage():
    log("Migrating the neutron database for GBP")
    cmd = ['gbp-db-manage',
           '--config-file', NEUTRON_CONF,
           'upgrade',
           'head']
    subprocess.check_output(cmd)

def _build_settings():
    cnf = config()
    settings = {}
    
    settings['neutron_plugin'] = 'aci'
    settings['use_gbp'] = cnf['use-gbp']
    if settings['use_gbp']:
        settings['service_plugins'] = 'apic_gbp_l3,group_policy,servicechain'
        if cnf['use-opflex']:
            settings['mechanism_drivers'] = 'apic_gbp'
        else:
            if cnf['enable-sriov']:
                settings['mechanism_drivers'] = 'openvswitch,sriovnicswitch,apic_gbp'
            else:
                settings['mechanism_drivers'] = 'openvswitch,apic_gbp'
    else:
        settings['service_plugins'] = 'cisco_apic_l3'
        settings['mechanism_drivers'] = 'cisco_apic_ml2'

    settings['apic_system_id'] = cnf['apic-domain-name']

    if cnf['use-opflex']:
        settings['type_drivers'] = 'opflex,local,flat,vlan,gre,vxlan'
        settings['tenant_network_types'] = 'opflex'
        settings['aci_encap'] = cnf['aci-encap']
    else:
        settings['type_drivers'] = 'local,flat,vlan,gre,vxlan'
        #if not opflex, encap can be only vlan, ignore config
        settings['aci_encap'] = 'vlan'
        settings['tenant_network_types'] = 'vlan'

    settings['apic_hosts'] = cnf['apic-hosts'] 
    settings['apic_username'] = cnf['apic-username']
    settings['apic_password'] = cnf['apic-password']
 
    settings['use_vmm'] = cnf['use-vmm']
    settings['apic_domain_name'] = cnf['apic-domain-name']
 
    settings['apic_provision_infra'] = "False"
    settings['apic_provision_hostlinks'] = "False"
 
    #settings['apic_connection_json'] = yaml.safe_load(cnf['apic-connection-json'].replace("'", "\""))
    settings['apic_connection_json'] = cnf['apic-connection-json']
    settings['apic_vpc_pairs'] = cnf['apic-vpc-pairs']
    settings['apic_l3out'] = cnf['apic-l3out']
    settings['apic_create_auto_ptg'] = cnf['apic-auto-ptg']

    return settings

def _aci_install(relation_id=None):
    log("Installing ACI packages")

    pkgs = ['python-apicapi', 'neutron-ml2-driver-apic', 'group-based-policy',
            'python-group-based-policy-client', 'neutron-opflex-agent']
    gbp_pkgs = ['group-based-policy', 'python-group-based-policy-client']
    opt = ['--option=Dpkg::Options::=--force-confdef' ,'--option=Dpkg::Options::=--force-confold']

    conf = config()

    if 'aci-repo-key' in conf.keys():
        fetch.add_source(conf['aci-repo'], key=conf['aci-repo-key'])
    else:
        fetch.add_source(conf['aci-repo'])
        opt.append('--allow-unauthenticated')

    fetch.apt_update(fatal=True)
    fetch.apt_upgrade(fatal=True)

    for pkg in pkgs:
       fetch.apt_install(pkg, options=opt, fatal=True)

    if conf['use-gbp']:
        for pkg in gbp_pkgs:
            fetch.apt_install(pkg, options=opt, fatal=True)
    
def _aci_config(rid=None):
    log("Configuring ACI")

    cnf = config()
    relation_set(relation_settings=_build_settings(), relation_id=rid)

@hooks.hook('update-status')
def update_status():
    log("Updating status")

@hooks.hook('config-changed')
def config_changed():
    for r_id in relation_ids('neutron-plugin-api-subordinate'):
        neutron_plugin_api_subordinate_joined(rid=r_id)

@hooks.hook("neutron-plugin-api-subordinate-relation-joined")
@hooks.hook("neutron-plugin-api-subordinate-relation-changed")
def neutron_plugin_api_subordinate_joined(rid=None):
    _aci_config(rid=rid)

@hooks.hook("leader-elected")
def leader_elected():
    if is_leader():
        log("This unit is the leader. Will migrate the database")
        _neutron_apic_ml2_db_manage()
        cnf = config()
        if cnf['use-gbp']:
            _neutron_gbp_db_manage()

@hooks.hook('upgrade-charm')    
def upgrade_charm():
    _aci_install()
    config_changed()

@hooks.hook()
@hooks.hook('install')
def aci_install(relation_id=None):
    _aci_install()

def main():
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))

if __name__ == '__main__':
    main()
