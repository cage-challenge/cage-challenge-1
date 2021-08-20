import copy
import math

from prettytable import PrettyTable 
from ipaddress import IPv4Address, IPv4Network

from torch import Tensor
import networkx as nx
import matplotlib.pyplot as plt

from CybORG.Agents.Wrappers.BaseWrapper import BaseWrapper

class GlobalObsWrapper(BaseWrapper):
    '''This wrapper glues together raw observations across multiple steps
    to give a high level overview of the network from Red Agent's perspective.
    However it is irreversible. ie. if Red loses access to a host, it will not update.
    Currently it does not support Blue Actions.
    This wrapper should only be used around the CybORG class'''

    def __init__(self,env=None,agent=None,output_mode='table',num_hosts=13):
        super().__init__(env,agent)
        self.tracker = ObservationTracker()
        self.output_mode = output_mode
        self.num_hosts = num_hosts

    def reset(self, agent=None):
        self.tracker.reset()
        result = self.env.reset(agent)
        result.action_space = self.action_space_change(result.action_space)
        result.observation = self.observation_change(result.observation)
        return result

    def observation_change(self,observation):
        obs = observation
        self.tracker.append(obs)

        if self.output_mode == 'table':
            return self.tracker.get_table()
        elif self.output_mode == 'graph':
            return self.tracker.get_graph()
        elif self.output_mode == 'vector':
            return self.tracker.get_vector(num_hosts=self.num_hosts)
        elif self.output_mode == 'raw':
            obs = observation
            obs['success'] = self.tracker.success
            return observation
        else:
            raise ValueError('GlobalStateWrapper recieved invalid output_mode parameter in init.')

    def reset(self, agent=None):    
        self.tracker.reset()
        result = self.env.reset(agent)    
        result.observation = self.observation_change(result.observation)    
        return result   

class ObservationTracker():
    def __init__(self):
        self.reset()

    def reset(self):
        self.history = []
        self.G = Graph()
        self.id_tracker = 0
        self.success = None

    def reset(self):
        self.history = []
        self.G = Graph()
        self.id_tracker = 0
        self.success = None

    def append(self,obs:dict):
        obs = copy.deepcopy(obs)
        self.history.append(obs)
        self.success = obs['success']
        del obs['success']

        self._process_obs(obs)

    def _process_obs(self, obs):
        for hostid in obs:
            host = obs[hostid]
            if 'Interface' in host:
                for interface in host['Interface']:
                    interface['hostid'] = hostid
                    self.G.add_interface(interface)

            if 'Sessions' in host:
                for session in host['Sessions']:
                    session['hostid'] = hostid
                    self.G.add_session(session)

            if 'Processes' in host:
                process_list = host['Processes']
                for process in process_list:
                    if 'Connections' in process and len(process.keys())==1:
                        connection_list = process['Connections']
                        for connection in connection_list:
                            connection['hostid'] = hostid
                            self.G.add_connection(connection)
                
            if 'System info' in host:
                info = host['System info']
                info['hostid'] = hostid
                self.G.add_system_info(info)

        return self.G

    def render(self,table=True):
        self.G.render(table)

    def get_table(self):
        table = self.G.get_table()
        table.success = self.success
        return table

    def get_graph(self):
        graph = self.G.get_graph()
        graph.success = self.success
        return graph

    def get_vector(self,num_hosts=13):
        vector = self.G.get_vector(num_hosts=num_hosts)
        vector.success = self.success
        return vector

class Graph():
    # Graph consists of Host, Interface and Subnet nodes.
    # Interfaces are synonomous with ips in this implementation
    def __init__(self):
        self.G = nx.DiGraph()
        self.G.add_node('NETWORK',datatype='Network')
        self.id_tracker = 0

    def add_subnet(self,subnet:str,unknown=False,**kwargs):
        if not unknown:
            try:
                IPv4Network(subnet)
            except:
                raise ValueError('Tried to add invalid subnet')
        
        subnet = str(subnet)
        self.G.add_node(subnet, datatype='subnet',**kwargs)
        self.G.add_edge(subnet,'NETWORK',datatype='in_network')

    def add_host(self,host:dict):
        host['datatype'] = 'Host'
        if 'Hostname' in host:
            name = host.pop('Hostname')
        else:
            name = self._generate_id('HOST')

        if 'User Access' not in host:
            host['User Access'] = False

        if 'Privileged Access' not in host:
            host['Privileged Access'] = False
        
        self.G.add_node(name,**host)
            
    def add_interface(self,interface:dict):
        # Interfaces are used to work out IP addresses and subnets
        try:
            ip = str(interface['IP Address'])
        except:
            ValueError('Tried to add interface without providing an IP Address')

        try:
            IPv4Address(ip)
        except:
            ValueError('Tried to add interface with invalid IP Address')

        if 'Interface Name' in interface:
            name = interface['Interface Name']
        else:
            name = self._generate_id('INTERFACE_NAME')

        if ip not in self.G.nodes:
            self.G.add_node(ip,name=name,Scanned=False,datatype='Interface')
        ip_data = self.G.nodes[ip]

        # Interface may come with subnet.
        # We want to link every ip to a subnet or a placeholder if it is unknown.
        if 'Subnet' in interface:
            subnet = str(interface['Subnet'])
            self.add_subnet(subnet)
        else:
            subnet = None

        self._link_subnet(ip,subnet)

        # Interface may be linked to a host.
        # We want every interface to be linked to a host or a placeholder.
        if 'Hostname' in interface:
            host = interface['Hostname']
        elif 'Hostname' in ip_data:
            host = ip_data['Hostname']
        elif self._classify(interface['hostid']) == 'Hostname':
            host = interface['hostid']
        else:
            host = self._generate_id('HOST')

        if host not in self.G:
            self.add_host({'Hostname':host})

        self._link_host(ip,host)
        
    def add_system_info(self, info):
        # System info is only used to work out hostnames
        # But could be used for operating systems later on
        try:
            new_name = info['Hostname']
        except:
            raise NotImplementedError('All System Info needs Hostname')

        hostid = info['hostid']
        if self._classify(hostid) == 'IP Address':
            old_name = self.G.nodes[hostid]['Hostname']
            self.G = nx.relabel_nodes(self.G,{old_name:new_name})
            self.G.nodes[hostid]['Hostname'] = new_name

    def add_session(self, session):
        # Sessions are used to detect if Red has access to a machine
        # and at which privilege level
        try:
            host = self._process_hostid(session['hostid'])
            agent = session['Agent']

        except:
            raise ValueError('Session must have hostid and agent.')

        if 'Username' in session: 
            user = session['Username']
        else:
            user = None

        if agent == 'Red':
            session_privileges = 'User Access'
            if user == 'root' or user == 'SYSTEM':
                session_privileges = 'Privileged Access'

            self.G.nodes[host][session_privileges] = True
            
    def add_connection(self, connection):
        # Connections currently only used to detect if host has been scanned
        ip = connection['hostid']
        if self._classify(ip) == 'IP Address':
            self.G.nodes[ip]['Scanned'] = True
        else:
            raise NotImplementedError('Added Connection with Hostid not IP Address')

    def _process_hostid(self,hostid):
        # Converts an ip hostid into the hostname of the linked host.
        if self._classify(hostid) == 'IP Address':
            hostid = self.G.nodes[hostid]['Hostname']
        return hostid

    def _classify(self,hostid):
        # Allows us to work out if a hostid is an ip address or hostname.
        try:
            IPv4Address(hostid)
            return 'IP Address'
        except:
            pass
        
        return 'Hostname'

    def _generate_id(self, datatype:str):
        # Unknown objects can be uniquely identified by their integer id_tracker
        # The rest of the string is for human readability.
        unique_id = 'UNKNOWN_' + datatype + ': ' + str(self.id_tracker)  
        self.id_tracker += 1
        return unique_id

    def _link_subnet(self,ip,subnet):
        ip_data = self.G.nodes[ip]

        # If we get an ip address by itself, look for its subnet
        if subnet is None:
            for node in self.G:
                node_data = self.G.nodes[node]
                if node_data['datatype'] == 'subnet':
                    # Check if Unknown Subnets are linked with IP
                    if 'UNKNOWN' in node:
                        if ip == node_data['ip']:
                            subnet = node
                            break
                    # Check if known subnets are linked with IP

                    try:
                        if IPv4Address(ip) in IPv4Network(node):
                            subnet = node
                            break
                    except:
                        pass
            else:
                # Having failed to find a subnet we create
                # a placeholder unknown subnet
                subnet = self._generate_id('SUBNET')
                self.add_subnet(subnet,unknown=True,ip=ip)

        # If we get an ip + subnet pair, check if we are replacing 
        # an unknown subnet with a known one
        elif 'Subnet' in ip_data:
            old_subnet = ip_data['Subnet']
            if old_subnet != subnet:
                self.G = nx.relabel_nodes(self.G,{old_subnet:subnet})

        self.G.nodes[ip]['Subnet'] = subnet
        self.G.add_edge(ip,subnet,datatype='in_subnet')

    def _link_host(self,ip,host):
        # Connect an interface to a host
        self.G.add_edge(host,ip,datatype='has_ip')
        self.G.nodes[ip]['Hostname'] = host

    def get_table(self):
        # The table data is all stored inside the ip nodes
        # which form the rows of the table
        table = PrettyTable([
            'Subnet',
            'IP Address',
            'Hostname',
            'Scanned',
            'Access',
            ])
        for node in self.G:
            ip_data = self.G.nodes[node]
            if ip_data['datatype'] == 'Interface':
                host = ip_data['Hostname']
                host_data = self.G.nodes[host]

                access_level = 'None'
                if host_data['Privileged Access']:
                    access_level = 'Privileged'
                elif host_data['User Access']:
                    access_level = 'User'

                table.add_row([
                    ip_data['Subnet'],
                    node,
                    host,
                    ip_data['Scanned'],
                    access_level,
                    ])
        table.sortby = 'IP Address'
        return table

    def get_graph(self):
        return self.G

    def get_vector(self,num_hosts=13):
        table = self.get_table()._rows

        # Compute required length of vector based on number of hosts
        padding = num_hosts-len(table)
        id_length = math.ceil(math.log2(num_hosts))

        proto_vector = []
        for row in table:
            # Scanned
            proto_vector.append(int(row[3]))

            # Access
            access = row[4]
            if access == 'None':
                value = [0,0]
            elif access == 'User':
                value = [1,0]
            elif access == 'Privileged':
                value = [0,1]
            else:
                raise ValueError('Table had invalid Access Level')
            proto_vector.extend(value)

        proto_vector.extend(padding * 3 * [-1])

        return Tensor(proto_vector)


    def render(self,table=True):
        # Keyboard agent wants table = True
        # The table = False option displays the backend graph
        # and is currently just for debugging purposes
        if table:
            print(self.get_table())
        else:
            nx.draw_kamada_kawai(self.G,with_labels=True)
            plt.show()
