import inspect
from ipaddress import IPv4Address, IPv4Network

from prettytable import PrettyTable

from CybORG import CybORG
from CybORG.Shared.Enums import TrinaryEnum
from CybORG.Agents.Wrappers.GlobalObsWrapper import GlobalObsWrapper
from CybORG.Shared.Actions.AbstractActions import DiscoverRemoteSystems, DiscoverNetworkServices, ExploitRemoteService, PrivilegeEscalate, Impact

def get_table(rows):    
    table = PrettyTable([    
        'Subnet',    
        'IP Address',    
        'Hostname',    
        'Scanned',    
        'Access',    
        ])    
    for r in rows:
        table.add_row(r)

    table.sortby = 'IP Address'
    return table    

def test_GlobalObsWrapper():
    path = str(inspect.getfile(CybORG))    
    path = path[:-10] + '/Shared/Scenarios/Scenario1b.yaml'    
    
    cyborg = GlobalObsWrapper(env=CybORG(path, 'sim'), output_mode='table')    
    agent_name = 'Red'

    def get_ip(host):
        ip_map = cyborg.env.environment_controller.state.ip_addresses
        for ip in ip_map:
            if ip_map[ip] == host:
                return str(ip)
        raise ValueError('Searched for host with no ip address. Probably invalid hostname.')

    def get_subnet(subnet):
        cidr_map = cyborg.env.environment_controller.state.subnet_name_to_cidr
        return str(cidr_map[subnet])

    # Test Initial Observation
    results = cyborg.reset(agent=agent_name)    
    observation = results.observation

    # Success tested separately. See comments in get_table function.
    expected_success = TrinaryEnum(2) # UNKNOWN
    assert observation.success == expected_success 

    expected_rows = [[get_subnet('User'),get_ip('User0'),'User0',False,'Privileged']]
    expected_table = get_table(expected_rows)

    # We compare strings instead of tables. See comments in get_table function.
    assert observation.get_string() == expected_table.get_string()

    # Test New Host Discovery
    subnet = IPv4Network(get_subnet('User'))
    action = DiscoverRemoteSystems(subnet=subnet, agent=agent_name,session=0)
    results = cyborg.step(action=action,agent=agent_name)
    observation = results.observation

    expected_success = TrinaryEnum(1) # TRUE
    assert observation.success == expected_success

    expected_rows = [[get_subnet('User'),get_ip('User0'),'User0',False,'Privileged']]
    for i in range(1,5):
        host = 'User' + str(i)
        host_table = 'UNKNOWN_HOST: '+str(2*i)
        expected_rows.append([get_subnet('User'),get_ip(host),host_table,False,'None'])

    expected_table = get_table(expected_rows)
    assert observation.get_string() == expected_table.get_string()

    # Test Port Scan
    ip_address = IPv4Address(get_ip('User1'))
    action = DiscoverNetworkServices(ip_address=ip_address, agent=agent_name,session=0)
    results = cyborg.step(action=action,agent=agent_name)
    observation = results.observation

    expected_success = TrinaryEnum(1) # TRUE
    assert observation.success == expected_success

    expected_rows = [
            [get_subnet('User'),get_ip('User0'),'User0',False,'Privileged'],
            [get_subnet('User'),get_ip('User1'),'UNKNOWN_HOST: 2',True,'None']
            ]
    for i in range(2,5):
        host = 'User' + str(i)
        host_table = 'UNKNOWN_HOST: '+str(2*i)
        expected_rows.append([get_subnet('User'),get_ip(host),host_table,False,'None'])

    expected_table = get_table(expected_rows)
    assert observation.get_string() == expected_table.get_string()

    # Test Remote Exploit
    ip_address = IPv4Address(get_ip('User1'))
    action = ExploitRemoteService(ip_address=ip_address, agent=agent_name,session=0)
    results = cyborg.step(action=action,agent=agent_name)
    observation = results.observation

    expected_success = TrinaryEnum(1) # TRUE
    assert observation.success == expected_success

    expected_rows = [
            [get_subnet('User'),get_ip('User0'),'User0',False,'Privileged'],
            [get_subnet('User'),get_ip('User1'),'User1',True,'User']
            ]
    for i in range(2,5):
        host = 'User' + str(i)
        host_table = 'UNKNOWN_HOST: '+str(2*i)
        expected_rows.append([get_subnet('User'),get_ip(host),host_table,False,'None'])

    expected_table = get_table(expected_rows)
    assert observation.get_string() == expected_table.get_string()

    # Test Privilege Escalate
    action = PrivilegeEscalate(hostname='User1', agent=agent_name,session=0)
    results = cyborg.step(action=action,agent=agent_name)
    observation = results.observation

    expected_success = TrinaryEnum(1) # TRUE
    assert observation.success == expected_success

    expected_rows = [
            [get_subnet('User'),get_ip('User0'),'User0',False,'Privileged'],
            [get_subnet('User'),get_ip('User1'),'User1',True,'Privileged']
            ]
    for i in range(2,5):
        host = 'User' + str(i)
        host_table = 'UNKNOWN_HOST: '+str(2*i)
        expected_rows.append([get_subnet('User'),get_ip(host),host_table,False,'None'])

    expected_rows.append(['UNKNOWN_SUBNET: 13',get_ip('Enterprise1'),'Enterprise1',
        False,'None'])

    expected_table = get_table(expected_rows)
    assert observation.get_string() == expected_table.get_string()

    # Test Failed Action
    action = Impact(hostname='User0',agent=agent_name,session=0)
    results = cyborg.step(action=action,agent=agent_name)
    observation = results.observation

    expected_success = TrinaryEnum(3) # FALSE
    assert observation.success == expected_success 

    # Expected table same as previous
    assert observation.get_string() == expected_table.get_string()

