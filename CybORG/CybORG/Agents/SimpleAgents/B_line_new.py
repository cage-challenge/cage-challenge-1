from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Shared import Results
from CybORG.Shared.Actions import PrivilegeEscalate, ExploitRemoteService, DiscoverRemoteSystems, Impact, \
    DiscoverNetworkServices, Sleep


class B_lineAgent(BaseAgent):
    def __init__(self, target='Op_Server0'):
        self.action = 0
        self.target_ip_address = None
        self.last_subnet = None
        self.last_ip_address = None

    def train(self, results: Results):
        """allows an agent to learn a policy"""
        pass

    def get_action(self, observation, action_space):
        # print(self.action)
        """gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space"""
        session = list(action_space['session'].keys())[0]
        loop = False
        while True:
            # Discover Remote Systems
            if self.action == 0:
                self.action = 1
                if 'User0' in observation:
                    if 'Interface' in observation['User0']:
                        if 'Subnet' in observation['User0']['Interface'][0]:
                            self.last_subnet = observation['User0']['Interface'][0]['Subnet']
                return DiscoverRemoteSystems(session=session, agent='Red', subnet=self.last_subnet)
            # Discover Network Services- new IP address found
            if self.action == 1:
                self.action = 2
                self.last_ip_address = [value for key, value in observation.items() if key != 'success'][1]['Interface'][0]['IP Address']
                return DiscoverNetworkServices(session=session, agent='Red', ip_address=self.last_ip_address)
            # Exploit User1
            if self.action == 2:
                 self.action = 3
                 return ExploitRemoteService(session=session, agent='Red', ip_address=self.last_ip_address)
            # Privilege escalation on User1
            elif self.action == 3:
                if observation['success'] == True:
                    self.action = 4
                    hostname = [value for key, value in observation.items() if key != 'success' and 'System info' in value][0]['System info']['Hostname']
                    return PrivilegeEscalate(agent='Red', hostname=hostname, session=session)
                else:
                    self.action = 2
                    loop = True
                    continue
            # Discover Network Services- new IP address found
            if self.action == 4:
                if observation['success'] == True:
                    self.action = 5
                    if 'Enterprise1' in observation:
                        if 'Interface' in observation['Enterprise1']:
                            if 'IP Address' in observation['Enterprise1']['Interface'][0]:
                                self.last_ip_address = observation['Enterprise1']['Interface'][0]['IP Address']
                    return DiscoverNetworkServices(session=session, agent='Red', ip_address=self.last_ip_address)
                else:
                    self.action = 2
            # Exploit- Enterprise1
            elif self.action == 5:
                if observation['success'] == True:
                    self.target_ip_address = [value for key, value in observation.items() if key != 'success'][0]['Interface'][0]['IP Address']
                else:
                    self.action = 2
                    loop = True
                    continue
                self.action = 6
                return ExploitRemoteService(session=session, agent='Red', ip_address=self.last_ip_address)
            # Privilege escalation on Enterprise1
            elif self.action == 6:
                if observation['success'] == True:
                    self.action = 7
                    hostname = [value for key, value in observation.items() if key != 'success' and 'System info' in value][0]['System info']['Hostname']
                    return PrivilegeEscalate(agent='Red', hostname=hostname, session=session)
                else:
                    self.action = 5
                    loop = True
                    continue
            # Scanning the new subnet found.
            elif self.action == 7:
                if observation['success'] == True:
                    self.action = 8
                    if 'Enterprise1' in observation:
                        if 'Interface' in observation['Enterprise1']:
                            if 'Subnet' in observation['Enterprise1']['Interface'][0]:
                                self.last_subnet = observation['Enterprise1']['Interface'][0]['Subnet']
                    return DiscoverRemoteSystems(subnet=self.last_subnet, agent='Red', session=session)
                else:
                    self.action = 5
                    loop = True
                    continue

            # Discover Network Services- Enterprise2
            if self.action == 8:
                self.action = 9
                self.target_ip_address = [value for key, value in observation.items() if key != 'success'][2]['Interface'][0]['IP Address']
                if 'Enterprise2' in observation:
                    if 'Interface' in observation['Enterprise2']:
                        if 'IP Address' in observation['Enterprise2']['Interface'][0]:
                            self.last_ip_address = observation['Enterprise2']['Interface'][0]['IP Address']
                return DiscoverNetworkServices(session=session, agent='Red', ip_address=self.target_ip_address)
            # Exploit- Enterprise2
            elif self.action == 9:
                if observation['success'] == True:
                    self.target_ip_address = [value for key, value in observation.items() if key != 'success'][0]['Interface'][0]['IP Address']
                else:
                    self.action = 7
                    loop = True
                    continue
                self.action = 10
                return ExploitRemoteService(session=session, agent='Red', ip_address=self.target_ip_address)
                # self.action = 8
                # return ExploitRemoteService(session=session, agent='Red', ip_address=[value for key, value in observation.items() if key != 'success'][0]['Interface'][0]['IP Address'])
                # loop = True
                # continue
                # #[value for key, value in observation.items() if key != 'success'][0]['Interface'][0]['IP Address'])

            #Privilege escalation on enterprise2
            elif self.action == 10:
                if observation['success'] == True:
                    self.action = 11
                    hostname = [value for key, value in observation.items() if key != 'success' and 'System info' in value][0]['System info']['Hostname']
                    return PrivilegeEscalate(agent='Red', hostname=hostname, session=session)
                else:
                    self.action = 9
                    loop = True
                    continue
            # Discover Network Services- Op_Server0
            if self.action == 11:
                if observation['success'] == True:
                    self.action = 12
                    return DiscoverNetworkServices(session=session, agent='Red', ip_address=observation['Op_Server0']['Interface'][0]['IP Address'])
                else:
                    self.action = 10
                    loop = True
                    continue
            # Exploit- Op_Server0
            elif self.action == 12:
                self.action = 13
                return ExploitRemoteService(agent='Red', session=session, ip_address=[value for key, value in observation.items() if key != 'success'][0]['Interface'][0]['IP Address'])
            # Privilege escalation on Op_Server0
            elif self.action == 13:
                self.action = 14
                return PrivilegeEscalate(agent='Red', hostname='Op_Server0', session=session)
            # Impact on Op_server0
            elif self.action == 14:
                return Impact(agent='Red', session=session, hostname='Op_Server0')


    def end_episode(self):
        self.action = 0
        self.target_ip_address = None
        self.last_subnet = None
        self.last_ip_address = None

    def set_initial_values(self, action_space, observation):
        pass
