import networkx as nx
import matplotlib.pyplot as plt

class KnowledgeGraph():
    def __init__(self):
        self.G = nx.Graph()
        self.G.add_node('NETWORK',datatype='Network')
        self.id_tracker = 0
        self.step = -1
        self.history = []

    def update(self,obs):
        self.step += 1
        self.history.append(obs)

    def render(self):
        nx.draw_kamada_kawai(self.G,with_labels=True)
        plt.show()

    def get_graph(self):
        return self.G

    def get_table(self):
        raise NotImplementedError

    def get_vector(self,num_hosts=13):
        raise NotImplementedError

    def _generate_id(self, datatype:str):
        # Unknown objects can be uniquely identified by their integer id_tracker
        # The rest of the string is for human readability.
        unique_id = 'UNKNOWN_' + datatype + ': ' + str(self.id_tracker)  
        self.id_tracker += 1
        return unique_id

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

