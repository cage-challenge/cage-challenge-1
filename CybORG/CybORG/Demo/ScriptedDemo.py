import argparse
import inspect
from datetime import datetime
from ipaddress import IPv4Address, IPv4Network
from pprint import pprint
from time import sleep

from CybORG import CybORG
from CybORG.Emulator.AWS import AWSConfig
from CybORG.Shared.Actions import MS17_010_PSExec, SSHLoginExploit, UpgradeToMeterpreter, MSFAutoroute, MSFPingsweep, \
    MSFPortscan, MeterpreterIPConfig, GetProcessList, GetHostList
from CybORG.Shared.Actions.VelociraptorActionsFolder import KillProcessPID
from CybORG.Shared.Enums import OperatingSystemType

from termcolor import colored

colour = {'Red': '',  # '\033[91m',
          'Blue': ''}  # '\033[94m'}
ENDSTR = ''  # '\x1b[0m'


def execute_action(cyborg, agent, action, await_user_input, verbose, print_cyborg_obs):
    if await_user_input:
        input(colored(f'Execute {agent} Action: {str(action)}', agent.lower()))
        print('...\n')
    else:
        print(colored(f'Execute {agent} Action: {str(action)}', agent.lower()))

    results = cyborg.step(agent, action)
    if verbose:
        print("Raw Observation:")
        if results.observation.raw is not None:
            if '[' in results.observation.raw:
                print(results.observation.raw[results.observation.data['raw'].find('['):])
            else:
                if type(results.observation.data['raw']) is str:
                    print(results.observation.raw)
                else:
                    pprint(results.observation.raw)
    if print_cyborg_obs:
        print("CybORG Observation:")
        pprint(results.observation.data)
    return results


def run_demo(verbose, await_user_input, print_cyborg_obs, aws_config, scenario_path):
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + '/Shared/Scenarios/'
    if not scenario_path:
        path += 'Scenario1.yaml'

    else:
        path += scenario_path+'.yaml'

    print(f"Using scenario {path}")
    cyborg = CybORG(path, 'aws',
                    env_config={
                        "config": aws_config,
                        "create_tunnel": False
                    })

    try:
        red_agent = 'Red'
        blue_agent = 'Blue'
        print('\nBlue\'s initial observation')
        initial_result_blue = cyborg.get_observation(blue_agent)
        pprint(initial_result_blue.data)
        if 'VelociraptorServer' in initial_result_blue.data:
            blue_session = initial_result_blue.data['VelociraptorServer']['Sessions'][0]['ID']
        elif 'Velociraptor_Server' in initial_result_blue.data:
            blue_session = initial_result_blue.data['Velociraptor_Server']['Sessions'][0]['ID']
        else:
            raise ValueError("Velociraptor Server not in initial blue observation")

        print('\nRed\'s initial observation')
        initial_result_red = cyborg.get_observation(red_agent)
        pprint(initial_result_red.data)

        action = GetHostList(session=blue_session, agent=blue_agent)
        results = execute_action(cyborg, blue_agent, action, await_user_input, verbose, print_cyborg_obs)

        action = GetProcessList(session=blue_session, agent=blue_agent, hostname='Gateway')
        results = execute_action(cyborg, blue_agent, action, await_user_input, verbose, print_cyborg_obs)

        # create ssh session on pretend pi host
        msf_session = initial_result_red.data['Attacker']['Sessions'][0]['ID']
        k_ip_address = initial_result_red.data['Attacker']['Interface'][0]['IP Address']
        pp_ip_address = initial_result_red.data['Gateway']['Interface'][0]['IP Address']
        action = MSFPortscan(session=msf_session, agent=red_agent, ip_address=pp_ip_address)

        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)

        action = SSHLoginExploit(session=msf_session, agent=red_agent, ip_address=pp_ip_address, port=22)

        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)

        target_session = results.observation.data[str(pp_ip_address)]['Sessions'][0]['ID']
        action = UpgradeToMeterpreter(session=msf_session, agent=red_agent, target_session=target_session)

        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)
        target_session = results.observation.data[str(target_session)]['Sessions'][-1]['ID']

        action = GetProcessList(session=blue_session, agent=blue_agent, hostname='Gateway')
        results = execute_action(cyborg, blue_agent, action, await_user_input, verbose, print_cyborg_obs)

        action = MeterpreterIPConfig(session=msf_session, agent=red_agent, target_session=target_session)

        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)

        subnet = results.observation.data[str(target_session)]['Interface'][0]['Subnet']

        action = MSFPingsweep(subnet=subnet, session=msf_session, agent=red_agent, target_session=target_session)

        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)

        hpc_ip_address = None

        for key, value in results.observation.data.items():
            if key != 'success' and key != 'raw' and key != str(pp_ip_address):
                if 'Interface' not in value:
                    continue  # ignoring the *.*.*.1 ip address that is found by scanning the private subnet
                assert len(value['Interface']) == 1
                if 'IP Address' in value['Interface'][0]:
                    address = value['Interface'][0]['IP Address']
                    hpc_ip_address = address
        assert hpc_ip_address is not None

        action = MSFPortscan(agent=red_agent, ip_address=hpc_ip_address, session=msf_session)

        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)

        action = MSFAutoroute(session=msf_session, agent=red_agent, target_session=target_session)

        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)

        action = MSFPortscan(agent=red_agent, ip_address=hpc_ip_address, session=msf_session)

        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)

        # action = GetProcessList(session=blue_session, agent=blue_agent, hostname='Internal')
        # results = execute_action(cyborg, blue_agent, action, await_user_input, verbose, print_cyborg_obs)
        # results.observation.data.pop('success')
        # plist = list(results.observation.data.values())[0]['Processes']
        # pslist = [item for item in plist if item['Process Name'] == 'powershell.exe']

        action = SSHLoginExploit(session=msf_session, agent=red_agent, ip_address=hpc_ip_address, port=22)

        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)
        # if results.observation.data['success'] != True:
        #     results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)
        # assert results.observation.data['success'] == True, 'SSH Login Bruteforce failed'

        action = MS17_010_PSExec(session=msf_session, agent=red_agent, ip_address=hpc_ip_address, username='vagrant',
                                 password='vagrant')
        attempts = 0
        MAX_ATTEMPTS = 5
        while attempts < MAX_ATTEMPTS:

            results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)
            if results.observation.data['success'] == True:
                break
            attempts += 1

        hpc_met_session = results.observation.data[str(hpc_ip_address)]['Sessions'][0]['ID']
        action = MeterpreterIPConfig(session=msf_session, agent=red_agent, target_session=hpc_met_session)
        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)

        # action = MeterpreterIPConfig(session=msf_session, agent=red_agent, target_session=hpc_met_session)
        # results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)

        action = GetProcessList(session=blue_session, agent=blue_agent, hostname='Internal')
        results = execute_action(cyborg, blue_agent, action, await_user_input, verbose, print_cyborg_obs)
        results.observation.data.pop('success')
        plist2 = list(results.observation.data.values())[0]['Processes']
        pslist2 = [item for item in plist2 if item['Process Name'] == 'powershell.exe']
        # print(pslist)
        # print(pslist2)
        pid = pslist2[0]['PID']
        # if pid1 == pslist2[1]['PPID']:
        #     # pid = pid1
        #     pid = pslist2[1]['PID']
        # else:
        #     # pid = pslist2[1]['PID']
        #     pid = pid1
        action = KillProcessPID(session=blue_session, agent="Blue", hostname='Internal', process=pid,
                                ostype=OperatingSystemType.WINDOWS)
        results = execute_action(cyborg, blue_agent, action, await_user_input, verbose, print_cyborg_obs)

        action = MeterpreterIPConfig(session=msf_session, agent=red_agent, target_session=hpc_met_session)
        results = execute_action(cyborg, red_agent, action, await_user_input, verbose, print_cyborg_obs)
        print("\nDemo Complete!\n")
    finally:
        cyborg.shutdown(teardown=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--aws_path", type=str, help="The path to the AWS config file.")
    parser.add_argument("-s", "--scenario", type=str, help="The scenario to use (don't include the .yaml extension).", default="Scenario1_predeployed")
    parser.add_argument("-t", "--use_test", type=str, help="Use the test configuration.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Use the test configuration.")

    args = parser.parse_args()

    if args.aws_path:
        print(f"Using AWS config file {args.aws_path}")
        aws_config = AWSConfig.load_and_setup_logger(
            aws_config_file_path=args.aws_path,
            test=args.use_test
        )
    else:
        print(f"Using the default AWS config file.")
        aws_config = AWSConfig.load_and_setup_logger(test=args.use_test)

    for i in range(1):
        run_demo(verbose=False, await_user_input=True, print_cyborg_obs=True, aws_config=aws_config, scenario_path=args.scenario)
