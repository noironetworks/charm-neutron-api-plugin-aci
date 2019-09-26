#!/usr/bin/env python3

from collections import OrderedDict
from copy import deepcopy
import subprocess
import sys
import pdb

from aci_utils import (
    ACI_PACKAGES,
    aci_config,
    aci_db_setup,
    aim_create_infra,
    assess_status,
    register_configs,
    restart_map,
)

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
    unit_get,
    network_get_primary_address,
)

from charmhelpers.core.host import (
    restart_on_change,
    service_restart
)

from charmhelpers.contrib.openstack import context, templating
import aim_context

from charmhelpers.contrib.openstack.utils import (
    os_release,
)

from charmhelpers import fetch

hooks = Hooks()
CONFIGS = register_configs()

@hooks.hook()
@hooks.hook('install')
def aci_install(relation_id=None):
    log("Installing ACI packages")

    opt = ['--option=Dpkg::Options::=--force-confdef' ,'--option=Dpkg::Options::=--force-confold']

    conf = config()

    if config('aci-repo-key'):
        fetch.add_source(config('aci-repo'), key=config('aci-repo-key'))
    else:
        with open('/etc/apt/apt.conf.d/90insecure', 'w') as ou:
           ou.write('Acquire::AllowInsecureRepositories "true";')
        fetch.add_source(config('aci-repo'))
        opt.append('--allow-unauthenticated')

    fetch.apt_update(fatal=True)
    fetch.apt_upgrade(fatal=True, options=opt)

    fetch.apt_install(ACI_PACKAGES, options=opt, fatal=True)

@hooks.hook('update-status')
def update_status():
    log("Updating status")

@hooks.hook("neutron-plugin-api-subordinate-relation-changed")
@hooks.hook('config-changed')
@restart_on_change(restart_map())
def config_changed():
    aci_install()

    CONFIGS.write_all()
    for r_id in relation_ids('neutron-plugin-api-subordinate'):
        neutron_plugin_api_subordinate_joined(rid=r_id)

    aci_db_setup()

@hooks.hook("neutron-plugin-api-subordinate-relation-joined")
@hooks.hook("neutron-plugin-api-subordinate-relation-changed")
def neutron_plugin_api_subordinate_joined(rid=None):
    aci_config(rid=rid)

@hooks.hook('amqp-relation-joined')
def amqp_joined(relation_id=None):
    relation_set(relation_id=relation_id,
                 username=config('rabbit-user'),
                 vhost=config('rabbit-vhost'))


@hooks.hook('amqp-relation-changed')
@hooks.hook('amqp-relation-departed')
@restart_on_change(restart_map())
def amqp_changed():
    if 'amqp' not in CONFIGS.complete_contexts():
        log('amqp relation incomplete. Peer not ready?')
        return
    CONFIGS.write_all()
    aci_db_setup()
    service_restart('aim-event-service-polling')
    service_restart('aim-aid')
    service_restart('aim-event-service-rpc')

@hooks.hook('shared-db-relation-joined')
def shared_db_joined(relation_id=None):
    host = None
    try:
       # NOTE: try to use network spaces
       host = network_get_primary_address('shared-db')
    except NotImplementedError:
       # NOTE: fallback to private-address
       host = unit_get('private-address')

    relation_set(database=config('database'),
                 username=config('database-user'),
                 hostname=host)

@hooks.hook('shared-db-relation-changed')
@hooks.hook('shared-db-relation-departed')
@restart_on_change(restart_map())
def shared_db_changed():
    if 'shared-db' not in CONFIGS.complete_contexts():
        log('shared-db relation incomplete. Peer not ready?')
        return
    CONFIGS.write_all()
    aci_db_setup()
    service_restart('aim-event-service-polling')
    service_restart('aim-aid')
    service_restart('aim-event-service-rpc')

#@hooks.hook("leader-elected")
#def leader_elected():
#    if is_leader():
#        log("This unit is the leader. Will migrate the database")
#        #aci_db_setup()

@hooks.hook('upgrade-charm')    
def upgrade_charm():
    aci_install()
    config_changed()

def main():
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))
    assess_status(CONFIGS)

if __name__ == '__main__':
    main()
