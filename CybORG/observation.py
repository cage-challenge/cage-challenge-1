from CybORG.Agents import B_lineAgent
import inspect
import random
from CybORG.Shared.Actions import Analyse
from CybORG.Shared.Actions import Sleep
from pprint import pprint
from CybORG import CybORG

STEPS = 10

#Environment Initialization
path = str(inspect.getfile(CybORG))
path = path[:-10] + '/Shared/Scenarios/Scenario1b.yaml'
env = CybORG(path, 'sim')

#Red Agent Initialization
results = env.reset(agent='Red')
obs = results.observation

action_space = results.action_space
red_obs = results.observation
agent = B_lineAgent()

def step_red(obs):
    action = agent.get_action(obs,action_space)
    print('Red Action:',action)
    print(76*'-')

    results = env.step(action=action,agent='Red')
    obs = results.observation
    #pprint(obs)

    return results

#Blue Agent Detecting Red Agent Network Service Scans
susHosts = []
for i in range(STEPS):
    results = step_red(red_obs)
    red_obs = results.observation
    
    blue_obs = env.get_observation("Blue")
    pprint(list(blue_obs.keys()))
    if len(list(blue_obs.keys())) > 1:
        if list(blue_obs.keys())[1] not in susHosts:
            susHosts.append(list(blue_obs.keys())[1])


print("\n*** Malicious Hosts ***")
print(susHosts)

# -- Analysing Malicous Hosts -- #

#Blue Agent Re-Initialization for action space
env = CybORG(path, 'sim',agents={'Red':B_lineAgent})
results = env.reset('Blue')
actions = results.action_space['action']

action = Sleep()

for i in range(STEPS):
    results = env.step(action=action, agent="Blue")
    obs = results.observation
        
for i in range(len(susHosts)):
    action = Analyse(hostname=susHosts[i], session=0, agent="Blue")
    results = env.step(action=action, agent="Blue")
    obs = results.observation
    print("\n *** Analysis of Malicious Host: "+ susHosts[i] + " ***")
    pprint(obs)