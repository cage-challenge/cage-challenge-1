from CybORG.Shared import Observation
from CybORG.Tests.utils import compare_fundamental_observations

# Things we expect to change between fundamental observations: IP Addresses, Ephemeral Ports, PIDs, subnets

def test_compare_fundamental_observations_success_pass():
    translation ={'10.0.1.1': '10.0.0.1'}
    obs1 = Observation()
    obs1.set_success(True)
    obs2 = Observation()
    obs2.set_success(True)
    assert compare_fundamental_observations(obs1.data, obs2.data, translation)


def test_compare_fundamental_observations_success_fail():
    translation ={'10.0.1.1': '10.0.0.1'}

    obs1 = Observation()
    obs1.set_success(True)
    obs2 = Observation()
    obs2.set_success(False)
    good = False
    try:
        compare_fundamental_observations(obs1.data, obs2.data, translation)
    except AssertionError:
        good = True
    assert good


def test_compare_fundamental_observations_ip_address_same_host_id():
    translation ={'10.0.1.1': '10.0.0.1'}
    obs1 = Observation()
    obs1.add_interface_info(hostid='hostid', ip_address='10.0.0.1')
    obs2 = Observation()
    obs2.add_interface_info(hostid='hostid', ip_address='10.0.1.1')

    assert compare_fundamental_observations(obs1.data, obs2.data, translation)


def test_compare_fundamental_observations_ip_address_diff_host_id():
    translation ={'10.0.1.1': '10.0.0.1'}

    obs1 = Observation()
    obs1.add_interface_info(hostid='10.0.0.1', ip_address='10.0.0.1')
    obs2 = Observation()
    obs2.add_interface_info(hostid='10.0.1.1', ip_address='10.0.1.1')

    assert compare_fundamental_observations(obs1.data, obs2.data, translation)


def test_compare_fundamental_observations_ip_address_diff_host_id_fail():
    translation ={'10.0.1.1': '10.0.0.1',
                  '10.0.1.2': '10.0.0.2'}

    obs1 = Observation()
    obs1.add_interface_info(hostid='10.0.0.1', ip_address='10.0.0.1')
    obs2 = Observation()
    obs2.add_interface_info(hostid='10.0.1.2', ip_address='10.0.1.2')
    good = False
    try:
        compare_fundamental_observations(obs1.data, obs2.data, translation)
    except AssertionError:
        good = True
    assert good

def test_compare_fundamental_observations_ip_address_wrong_number_fail():
    translation ={'10.0.1.1': '10.0.0.1',
                  '10.0.1.2': '10.0.0.2'}

    obs1 = Observation()
    obs1.add_interface_info(hostid='10.0.0.1', ip_address='10.0.0.1')
    obs2 = Observation()
    obs2.add_interface_info(hostid='10.0.1.1', ip_address='10.0.1.1')
    obs2.add_interface_info(hostid='10.0.1.2', ip_address='10.0.1.2')
    good = False
    try:
        compare_fundamental_observations(obs1.data, obs2.data, translation)
    except AssertionError:
        good = True
    assert good


def test_compare_fundamental_observations_ip_address_right_number():
    translation = {'10.0.1.1': '10.0.0.1',
                   '10.0.1.2': '10.0.0.2'}
    obs1 = Observation()
    obs1.add_interface_info(hostid='10.0.0.1', ip_address='10.0.0.1')
    obs1.add_interface_info(hostid='10.0.0.2', ip_address='10.0.0.2')

    obs2 = Observation()
    obs2.add_interface_info(hostid='10.0.1.1', ip_address='10.0.1.1')
    obs2.add_interface_info(hostid='10.0.1.2', ip_address='10.0.1.2')

    assert compare_fundamental_observations(obs1.data, obs2.data, translation)


def test_compare_fundamental_observations_subnets():
    translation ={'10.0.1.1': '10.0.0.1'}

    obs1 = Observation()
    obs1.add_interface_info(hostid='10.0.0.1', subnet='10.0.0.0/28')
    obs2 = Observation()
    obs2.add_interface_info(hostid='10.0.1.1', subnet='10.0.1.0/28')

    assert compare_fundamental_observations(obs1.data, obs2.data, translation)


def test_compare_fundamental_observations_ports():
    translation ={'10.0.1.1': '10.0.0.1'}

    obs1 = Observation()
    obs1.add_process(hostid='10.0.0.1', local_address='10.0.0.1', local_port=22)
    obs2 = Observation()
    obs2.add_process(hostid='10.0.1.1', local_address='10.0.1.1', local_port=22)

    assert compare_fundamental_observations(obs1.data, obs2.data, translation)


def test_compare_fundamental_observations_procs():
    translation ={'10.0.1.1': '10.0.0.1'}

    obs1 = Observation()
    obs1.add_process(hostid='10.0.0.1', pid=1)
    obs2 = Observation()
    obs2.add_process(hostid='10.0.1.1', pid=1)

    assert compare_fundamental_observations(obs1.data, obs2.data, translation)


def test_compare_fundamental_observations_connections():
    translation ={'10.0.1.1': '10.0.0.1',
                  '10.2.3.1': '10.1.2.3'}

    obs1 = Observation()
    obs1.add_process(hostid='10.0.0.1', local_address='10.0.0.1', local_port=22, remote_port=5325, remote_address='10.1.2.3')
    obs2 = Observation()
    obs2.add_process(hostid='10.0.1.1', local_address='10.0.1.1', local_port=22, remote_port=5432, remote_address='10.2.3.1')

    assert compare_fundamental_observations(obs1.data, obs2.data, translation)