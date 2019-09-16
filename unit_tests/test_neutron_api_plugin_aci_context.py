
import io

from contextlib import contextmanager

from mock import (
    MagicMock,
    patch
)
import aim_context

from test_utils import (
    CharmTestCase
)

TO_PATCH = [
    'config',
]


@contextmanager
def patch_open():
    '''Patch open() to allow mocking both open() itself and the file that is
    yielded.

    Yields the mock for "open" and "file", respectively.'''
    mock_open = MagicMock(spec=open)
    mock_file = MagicMock(spec=io.FileIO)

    @contextmanager
    def stub_open(*args, **kwargs):
        mock_open(*args, **kwargs)
        yield mock_file

    with patch('builtins.open', stub_open):
        yield mock_open, mock_file


class TestAciAimCtlConfigContext(CharmTestCase):
    def setUp(self):
        super(TestAciAimCtlConfigContext, self).setUp(aim_context, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def test_apicsystemid(self):
        self.test_config.set('aci-apic-system-id', 'JuJu101')
        self.assertEqual(aim_context.AciAimCtlConfigContext()(),
                       {'aci_apic_system_id': 'JuJu101',
                        'aci_encap': 'vxlan',
                        'aci_vlan_ranges': '1000:1010',
                        'aci_vpc_pairs': '',
                        'aci_apic_entity_profile': 'openstack',
                        'aci_disable_vmdom': False,
                        'aci_connection_dict': {}})

    def test_aci_encap(self):
        self.test_config.set('aci-encap', 'vlan')
        self.assertEqual(aim_context.AciAimCtlConfigContext()(),
                       {'aci_apic_system_id': 'openstack',
                        'aci_encap': 'vlan',
                        'aci_vlan_ranges': '1000:1010',
                        'aci_vpc_pairs': '',
                        'aci_apic_entity_profile': 'openstack',
                        'aci_disable_vmdom': False,
                        'aci_connection_dict': {}})

    def test_aci_vlan_ranges(self):
        self.test_config.set('aci-vlan-ranges', '2121:2233')
        self.assertEqual(aim_context.AciAimCtlConfigContext()(),
                       {'aci_apic_system_id': 'openstack',
                        'aci_encap': 'vxlan',
                        'aci_vlan_ranges': '2121:2233',
                        'aci_vpc_pairs': '',
                        'aci_apic_entity_profile': 'openstack',
                        'aci_disable_vmdom': False,
                        'aci_connection_dict': {}})

    def test_aci_vpc_pairs(self):
        self.test_config.set('aci-vpc-pairs', '101:102')
        self.assertEqual(aim_context.AciAimCtlConfigContext()(),
                       {'aci_apic_system_id': 'openstack',
                        'aci_encap': 'vxlan',
                        'aci_vlan_ranges': '1000:1010',
                        'aci_vpc_pairs': '101:102',
                        'aci_apic_entity_profile': 'openstack',
                        'aci_disable_vmdom': False,
                        'aci_connection_dict': {}})

    def test_aci_apic_entity_profile(self):
        self.test_config.set('aci-apic-entity-profile', 'OstackAep')
        self.assertEqual(aim_context.AciAimCtlConfigContext()(),
                       {'aci_apic_system_id': 'openstack',
                        'aci_encap': 'vxlan',
                        'aci_vlan_ranges': '1000:1010',
                        'aci_vpc_pairs': '',
                        'aci_apic_entity_profile': 'OstackAep',
                        'aci_disable_vmdom': False,
                        'aci_connection_dict': {}})

    def test_aci_disable_vmdom(self):
        self.test_config.set('aci-disable-vmdom', True)
        self.assertEqual(aim_context.AciAimCtlConfigContext()(),
                       {'aci_apic_system_id': 'openstack',
                        'aci_encap': 'vxlan',
                        'aci_vlan_ranges': '1000:1010',
                        'aci_vpc_pairs': '',
                        'aci_apic_entity_profile': 'openstack',
                        'aci_disable_vmdom': True,
                        'aci_connection_dict': {}})

    def test_aci_connection_json(self):
        self.test_config.set('aci-connection-json', '{"101": ["srv1:vpc-1-25/101-102-1-25", "srv2:vpc-1-26/101-102-1-26"],"102": ["srv1:vpc-1-25/101-102-1-25", "srv2:vpc-1-26/101-102-1-26"]}')
        self.assertEqual(aim_context.AciAimCtlConfigContext()(),
                       {'aci_apic_system_id': 'openstack',
                        'aci_encap': 'vxlan',
                        'aci_vlan_ranges': '1000:1010',
                        'aci_vpc_pairs': '',
                        'aci_apic_entity_profile': 'openstack',
                        'aci_disable_vmdom': False,
                        'aci_connection_dict': {'101':["srv1:vpc-1-25/101-102-1-25", "srv2:vpc-1-26/101-102-1-26"],
                                                '102':["srv1:vpc-1-25/101-102-1-25", "srv2:vpc-1-26/101-102-1-26"]} })

    def test_aci_physnet_host_mapping(self):
        self.test_config.set('aci-physnet-host-mapping', '{"p0":"host1:e1:e2,host2:e1", "p1":"host3:es1:es2:es3"}')
        self.assertEqual(aim_context.AciAimCtlConfigContext()(),
                       {'aci_apic_system_id': 'openstack',
                        'aci_encap': 'vxlan',
                        'aci_vlan_ranges': '1000:1010',
                        'aci_vpc_pairs': '',
                        'aci_apic_entity_profile': 'openstack',
                        'aci_disable_vmdom': False,
                        'aci_physnet_host_mapping_dict': {'p0': 'host1,host2', 'p1': 'host3'},
                        'aci_connection_dict': {}})

    def test_aci_physdom_id(self):
        self.test_config.set('aci-physdom-id', 'PhysDom')
        self.assertEqual(aim_context.AciAimCtlConfigContext()(),
                       {'aci_apic_system_id': 'openstack',
                        'aci_encap': 'vxlan',
                        'aci_vlan_ranges': '1000:1010',
                        'aci_vpc_pairs': '',
                        'aci_apic_entity_profile': 'openstack',
                        'aci_disable_vmdom': False,
                        'aci_physdom_id': 'PhysDom',
                        'aci_connection_dict': {}})


class TestAciAimConfigContext(CharmTestCase):

    def setUp(self):
        super(TestAciAimConfigContext, self).setUp(aim_context, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def test_aim_config(self):
        self.test_config.set('aci-apic-hosts', '1.1.1.2,2.2.2.1,3.3.3.3')
        self.test_config.set('aci-apic-username', 'test_user')
        self.test_config.set('aci-apic-password', 'changeme')
        self.assertEqual(aim_context.AciAimConfigContext()(),
                         {'debug': 'True',
                          'apic_hosts': '1.1.1.2,2.2.2.1,3.3.3.3',
                          'apic_username': 'test_user',
                          'apic_password': 'changeme'})
