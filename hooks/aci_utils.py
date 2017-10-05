#!/usr/bin/env python

from collections import OrderedDict
from copy import deepcopy
import subprocess
import sys
from itertools import chain
import pdb

ACI_PACKAGES = [
   'python-apicapi',
   'group-based-policy',
   'python-group-based-policy-client',
   'neutron-opflex-agent',
   'aci-integration-module',
   'acitoolkit',
]

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

from charmhelpers.contrib.openstack import context, templating
import aim_context

from charmhelpers.contrib.openstack.utils import (
    pause_unit,
    resume_unit,
    make_assess_status_func,
    is_unit_paused_set,
    os_release,
)

from charmhelpers import fetch

AIM_CONFIG = '/etc/aim/aim.conf'
AIM_CTL_CONFIG = '/etc/aim/aimctl.conf'
AIM_SERVICES = ['aim-aid','aim-event-service-rpc', 'aim-event-service-polling']
NEUTRON_CONF_DIR = "/etc/neutron"
NEUTRON_CONF = '%s/neutron.conf' % NEUTRON_CONF_DIR
TEMPLATES = 'templates/'

BASE_RESOURCE_MAP = OrderedDict([
    (AIM_CONFIG, {
        'services': AIM_SERVICES,
        'contexts': [aim_context.AciAimConfigContext(),
                     context.SharedDBContext(
                         user=config('database-user'),
                         database=config('database'),
                         ssl_dir=NEUTRON_CONF_DIR),
                     context.AMQPContext(ssl_dir=NEUTRON_CONF_DIR),],
    }),
    (AIM_CTL_CONFIG, {
        'services': [],
        'contexts': [aim_context.AciAimCtlConfigContext()],
    }),
])

REQUIRED_INTERFACES = {
   'messaging': ['amqp'],
   'database': ['shared-db'],
}

def register_configs(release=None):
    release = release or os_release('neutron-common')
    configs = templating.OSConfigRenderer(templates_dir=TEMPLATES,
                                          openstack_release=release)
    for cfg, rscs in resource_map().iteritems():
        configs.register(cfg, rscs['contexts'])
    return configs

def resource_map(release=None):
    '''
    Dynamically generate a map of resources that will be managed for a single
    hook execution.
    '''
    resource_map = deepcopy(BASE_RESOURCE_MAP)

    return resource_map

def restart_map():
    '''
    Constructs a restart map based on charm config settings and relation
    state.
    '''
    return {k: v['services'] for k, v in resource_map().iteritems()}

def services():
    """Returns a list of (unique) services associate with this charm
    @returns [strings] - list of service names suitable for (re)start_service()
    """
    s_set = set(chain(*restart_map().values()))
    return list(s_set)


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

def aim_create_infra():
    cmd = ['/usr/bin/aimctl', 'infra', 'create']
    subprocess.check_output(cmd)

def _aim_db_migrate():
    log("Migrating ACI AIM database")
    cmd = ['/usr/bin/aimctl', 'db-migration',
           'upgrade', 'head']
    subprocess.check_output(cmd)

    cmd = ['/usr/bin/aimctl', 'config', 'update']
    subprocess.check_output(cmd)

    try:
        aim_create_infra()
    except:
        pass

    cmd = ['/usr/bin/aimctl','manager', 'load-domains',
           '--enforce']
    subprocess.check_output(cmd)

CONFIGS = register_configs()

def aci_db_setup():
    if (('amqp' in CONFIGS.complete_contexts()) and ('shared-db' in CONFIGS.complete_contexts())):
        if is_leader():
            #_neutron_apic_ml2_db_manage()
            _aim_db_migrate()
            _neutron_gbp_db_manage()

def _build_settings():
    cnf = config()
    settings = {}

    for k, v in cnf.iteritems():
        if k.startswith('aci'):
            settings[k.replace('-', '_')] = v
    
    settings['neutron_plugin'] = 'aci'
    settings['type_drivers'] = 'opflex,local,vlan,vxlan,flat,gre'
    settings['tenant_network_types'] = 'opflex'
    settings['mechanism_drivers'] = 'apic_aim'
    settings['ml2_extension_drivers'] = 'apic_aim,port_security'
    settings['service_plugins'] = 'group_policy,ncp,apic_aim_l3'
    settings['apic_aim_auth_plugin'] = 'v3password'
    settings['group_policy_policy_drivers'] = 'aim_mapping'
    settings['group_policy_extension_drivers'] = 'aim_extension,proxy_group,apic_allowed_vm_name,apic_segmentation_label'

    return settings

def aci_config(rid=None):
    log("Configuring ACI")

    relation_set(relation_settings=_build_settings(), relation_id=rid)

def assess_status(configs):
    """Assess status of current unit
    Decides what the state of the unit should be based on the current
    configuration.
    SIDE EFFECT: calls set_os_workload_status(...) which sets the workload
    status of the unit.
    Also calls status_set(...) directly if paused state isn't complete.
    @param configs: a templating.OSConfigRenderer() object
    @returns None - this function is executed for its side-effect
    """
    assess_status_func(configs)()


def assess_status_func(configs):
    """Helper function to create the function that will assess_status() for
    the unit.
    Uses charmhelpers.contrib.openstack.utils.make_assess_status_func() to
    create the appropriate status function and then returns it.
    Used directly by assess_status() and also for pausing and resuming
    the unit.
    Note that required_interfaces is augmented with neutron-plugin-api if the
    nova_metadata is enabled.
    NOTE(ajkavanagh) ports are not checked due to race hazards with services
    that don't behave sychronously w.r.t their service scripts.  e.g.
    apache2.
    @param configs: a templating.OSConfigRenderer() object
    @return f() -> None : a function that assesses the unit's workload status
    """
    required_interfaces = REQUIRED_INTERFACES.copy()
    return make_assess_status_func(
        configs, required_interfaces,
        services=services(), ports=None)


def pause_unit_helper(configs):
    """Helper function to pause a unit, and then call assess_status(...) in
    effect, so that the status is correctly updated.
    Uses charmhelpers.contrib.openstack.utils.pause_unit() to do the work.
    @param configs: a templating.OSConfigRenderer() object
    @returns None - this function is executed for its side-effect
    """
    _pause_resume_helper(pause_unit, configs)


def resume_unit_helper(configs):
    """Helper function to resume a unit, and then call assess_status(...) in
    effect, so that the status is correctly updated.
    Uses charmhelpers.contrib.openstack.utils.resume_unit() to do the work.
    @param configs: a templating.OSConfigRenderer() object
    @returns None - this function is executed for its side-effect
    """
    _pause_resume_helper(resume_unit, configs)


def _pause_resume_helper(f, configs):
    """Helper function that uses the make_assess_status_func(...) from
    charmhelpers.contrib.openstack.utils to create an assess_status(...)
    function that can be used with the pause/resume of the unit
    @param f: the function to be used with the assess_status(...) function
    @returns None - this function is executed for its side-effect
    """
    # TODO(ajkavanagh) - ports= has been left off because of the race hazard
    # that exists due to service_start()
    f(assess_status_func(configs),
      services=services(),
      ports=None)
