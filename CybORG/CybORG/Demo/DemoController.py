# Copyright DST Group. Licensed under the MIT license.
import argparse
import os
import signal
import sys

from CybORG.Emulator.TeamServer.TeamClient import TeamClient
import CybORG.Shared.Actions as actions
from CybORG.Shared.Enums import OperatingSystemType as ost
from CybORG.Emulator.SSH import SSHTunnelHandler
from CybORG.Emulator.AWS.Config import AWSConfig
import CybORG.Shared.Enums as CyEnums
from CybORG.Shared.EnvironmentController import EnvironmentController as ec
from CybORG import CybORG


class DemoController:
    """ Set up the environment required for the CybORG EMulator demo

    Parameters
    ----------
        scenario_path : str
            path to the scenario description
        emulator_config : EmulatorConfig, optional
            the emulator configuration object, if None will load and
            use the current config (default=None)

    """

    def __init__(self, scenario_path,
                 emu_path=None, aws_path=None,
                 teardown=False):
        print(f"Starting CybORG with teardown={teardown}....")

        if emu_path is not None:

            self.aws_config = AWSConfig.load_and_setup_logger(
                emu_config_file_path=emu_path,
                aws_config_file_path=aws_path
            )

        else:

            self.aws_config = AWSConfig.load_and_setup_logger(
                aws_config_file_path=aws_path
            )
        self.teardown = teardown
        # print(f"self.aws_config={self.aws_config}")

        signal.signal(signal.SIGINT, self.shutdown)

        self.cyborg = CybORG(
            scenario_path,
            environment="aws",
            env_config={
                "config": self.aws_config,
                "create_tunnel": True
            }
        )

        print(f"Connecting to Team Server...")
        self.ts_client = self.establish_ts_server_connection()

    def shutdown(self):
        print(f"Shutting down with teardown {self.teardown}...")

        self.cyborg.shutdown(teardown=self.teardown)

        print(f"Goodbye....")

    def get_session_id(self, agent, key):

        observation_dict = self.cyborg.get_observation(agent).get_dict()
        print(f"key={key} observation_dict={observation_dict}")
        obs = observation_dict.get(key)

        return observation_dict.get(key)['Sessions'][0]['ID']

    def establish_ts_server_connection(self):
        ts_client = TeamClient(self.aws_config.team_server_address,
                               self.aws_config.team_server_port)
        ts_client.connect()
        return ts_client

    def create_ssh_tunnel(self):
        print(f"Setting up SSH tunnel...")
        print(f"aws_config={self.aws_config}")
        tunnel = SSHTunnelHandler(
            remote_ip=self.aws_config.team_server_address,
            remote_port=self.aws_config.team_server_port,
            proxy_ip=self.aws_config.aws_bastion_address,
            proxy_port=self.aws_config.aws_bastion_ssh_port,
            proxy_username=self.aws_config.aws_bastion_username,
            proxy_key_path=self.aws_config.aws_bastion_ssh_key_path,
            local_ip=self.aws_config.team_server_address,
            local_forward_port=self.aws_config.team_server_port
        )

        tunnel.start()
        return tunnel


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    #    /home/mdl/Autonomous-Cyber-Ops/CybORG/Tests/test_em/Scenarios/Scenario1.yaml

    parser.add_argument('-s', '--scenario_file', type=str,
                        help="The filepath of the YAML scenario to run")

    parser.add_argument('-t', '--teardown', action='store_true',
                        help="Shutdown the VMs when finished (False for pre-deployed network)")

    parser.add_argument('-a', '--aws_config', type=str,
                        help="The path to the aws file.")

    parser.add_argument('-e', '--emu_config', type=str,
                        help="The path to the AWS config file.")

    args = parser.parse_args()

    if args.scenario_file is None:

        parser.print_usage()
        sys.exit(1)

    if not os.path.exists(args.scenario_file):
        print(f"Unable to open {args.scenario_file}: File not found")
        sys.exit(1)

    if args.aws_config and not os.path.exists(args.aws_config):
        print(f"Unable to open {args.aws_config}: File not found")
        sys.exit(1)

    if args.emu_config and not os.path.exists(args.emu_config):
        print(f"Unable to open {args.emu_config}: File not found")

    demo_client = DemoController(scenario_path=args.scenario_file,
                                 emu_path=args.emu_config,
                                 aws_path=args.aws_config,
                                 teardown=args.teardown)

    session_id = demo_client.get_session_id('Blue', 'VelociraptorServer')

    print(f"Blue session ID is {session_id}")

    hostnames_list = []
    clients_list = []

    results = demo_client.cyborg.step(agent='Blue',
                                      action=actions.VelociraptorActionsFolder.GetHostList(agent='Blue',
                                                                                           session=session_id))
    #print(f"results={results}")

    items = results.observation.get_dict().items()

    for key, value in items:
        if key.startswith('C.'):

            if len(value['System info']['Hostname']) == 0:
                print(f"WARNING: Have blank hostname for client {key}, this needs to be investigated, skipping host")
                continue
            else:
                hostnames_list.append(value['System info']['Hostname'])
                clients_list.append(key)

    # for client in clients_list:
    #     print(f"client={client}")

    for hostname in hostnames_list:


        print(f"Have hostname {hostname}")

        if hostname == "Gateway":
            print("Skipping Linux host Gateway")
            continue

        # results = demo_client.cyborg.step(agent='Blue',
        #                                   action=actions.VelociraptorActionsFolder.GetProcessList(session=session_id,
        #                                                                                           agent="Blue",
        #                                                                                           hostname=item))
        #
        # print(f"results={results}")

        if True:
            print(f"Calling GetProcessList with hostname={hostname}")
            results = demo_client.cyborg.step(agent='Blue',
                                              action=actions.VelociraptorActionsFolder.GetProcessList(agent='Blue',
                                                                                                      session=session_id,
                                                                                                      hostname=hostname))
            print(f"results={results}")

        if False:
            print(f"Calling GetUsers with hostname={hostname}")
            results = demo_client.cyborg.step(agent='Blue',
                                              action=actions.VelociraptorActionsFolder.GetUsers(agent='Blue',
                                                                                                session=session_id,
                                                                                                hostname=hostname,
                                                                                                ostype=ost.WINDOWS))
            print(f"results={results.observation.get_dict()}")

        if False:
            pid = input("Enter the PID...")

            if hostname == "Internal":
                results = demo_client.cyborg.step(agent='Blue',
                                                  action=actions.VelociraptorActionsFolder.KillProcessPID(
                                                      session=session_id,
                                                      agent="Blue",
                                                      hostname=hostname,
                                                      process=pid,
                                                      ostype=CyEnums.OperatingSystemType.WINDOWS))
            else:

                results = demo_client.cyborg.step(agent='Blue',
                                                  action=actions.VelociraptorActionsFolder.KillProcessPID(
                                                      session=session_id,
                                                      agent="Blue",
                                                      hostname=hostname,
                                                      process=pid,
                                                      ostype=CyEnums.OperatingSystemType.LINUX))

            print(f"results={results}")

    demo_client.shutdown()
