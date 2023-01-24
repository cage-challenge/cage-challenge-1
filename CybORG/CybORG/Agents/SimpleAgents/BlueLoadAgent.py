'''
This is a modified version of the CybORG BlueLoadAgent that was developed to enhance the capability of the original and improve on it

Developed:  Sky TianYi Zhang
            Mitchell Knyn
            Jayden Fowler
            
Last Modified: 18 January 2023
'''


import inspect
from stable_baselines3 import PPO
from CybORG import CybORG
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Agents.Wrappers.EnumActionWrapper import EnumActionWrapper
from CybORG.Agents.Wrappers.FixedFlatWrapper import FixedFlatWrapper
from CybORG.Agents.Wrappers.OpenAIGymWrapper import OpenAIGymWrapper
from CybORG.Agents.Wrappers.ReduceActionSpaceWrapper import ReduceActionSpaceWrapper
from CybORG.Agents.Wrappers import *
import numpy as np
import os

path = str(inspect.getfile(CybORG))
path = path[:-10] + '/Shared/Scenarios/Scenario1b.yaml'
env = CybORG(path, 'sim')

#Sets the global environment to ensure that it can be used by all modules in the class
path = str(inspect.getfile(CybORG))
path = path[:-10] + '/Shared/Scenarios/Scenario1b.yaml'
cyborg = OpenAIGymWrapper('Blue', EnumActionWrapper(FixedFlatWrapper(ReduceActionSpaceWrapper(CybORG(path, 'sim')))))
ppo_path = str(inspect.getfile(CybORG))
ppo_path = ppo_path[:-10] + "/Evaluation/ppo_training.zip"

#Defines the vector for each host
observationHostnameVector = {
    "Impact on OpServer": np.float32(-1),
    "Enterprise0": np.float32(0.2),
    "Enterprise1": np.float32(0.4),
    "Enterprise2": np.float32(0.6),
    "User1": np.float32(0.8),
    "OpServer0": np.float32(1),
    "User3": np.float32(1.4),
    "User0": np.float32(1.6)
}

#Defines the vector for each action
actionVector = {
    "Remove Enterprise0": 16,
    "Remove Enterprise1": 17,
    "Remove Enterprsie2": 18,
    "Remove OpServer0": 22,
    "Remove User1": 24,
    "Remove User3": 26,
    "Restore OpServer0": 48
}

class BlueLoadAgent(BaseAgent):
    # agent that loads a StableBaselines3 PPO model file
    def train(self):
        if os.path.exists(ppo_path):
            self.model = PPO.load("ppo_training")
            print("\nModel file found, loaded\n")
        else:
            self.model = PPO('MlpPolicy', cyborg)
            self.model.learn(total_timesteps=int(10000), progress_bar=True)
            self.model.save("ppo_training")
            self.model.reset()
            self.model.load("ppo_training")
            print("\nNo Model file, trained new one\n")
        pass

    def end_episode(self):
        pass

    def set_initial_values(self, action_space, observation):
        pass
    
    def wrap(env):
        return OpenAIGymWrapper("Blue", EnumActionWrapper(FixedFlatWrapper(ReduceActionSpaceWrapper(env))))

    def evaluate(self,num_steps):
        episode_rewards = [0.0]
        obs = env.reset()
        for i in range(num_steps):
            action, _states = self.model.predict(obs)
            obs, reward, done, info = env.step(action)
            episode_rewards[-1] += reward
            if done:
                obs = env.reset()
        episode_rewards.append(0.0)
        mean_100ep_reward = round(np.mean(episode_rewards[-100:]), 1)
        print("Mean reward:", mean_100ep_reward, "Num episode:", len(episode_rewards))

        return mean_100ep_reward

    def __init__(self):
        self.scanned_subnets = []
        self.scanned_ips = []
        self.exploited_ips = []
        self.escalated_hosts = []
        self.host_ip_map = {}
        self.last_host = None
        self.last_ip = None
        self.task = 0
        self.train()

    def get_action(self, observation, action_space):
        """gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space"""
        
        if observation[1] == observationHostnameVector["OpServer0"] or self.task == 2:
            action = actionVector["Restore OpServer0"]
            if self.task == 2:
                action = 48
                self.task = 0
            else:
                self.task = self.task + 2

        elif observation[1] == observationHostnameVector["Enterprise2"] or self.task == 3:
            action = actionVector["Remove Enterprsie2"]
            if self.task == 3:
                self.task = 0
            else:
                self.task = self.task + 3
                
        elif observation[1] == observationHostnameVector["Enterprise1"] or self.task == 1:
            action = actionVector["Remove Enterprise1"]
            if self.task == 1:
                self.task = 0
            else:
                self.task = self.task + 1

        elif observation[1] == observationHostnameVector["User1"] or self.task == 4:
            action = actionVector["Remove User1"]
            if self.task == 4:
                self.task = 0
            else:
                self.task = self.task + 4

        elif observation[1] == observationHostnameVector["Enterprise0"] or self.task == 5:
            action = actionVector["Remove Enterprise0"]
            if self.task == 5:
                self.task = 0
            else:
                self.task = self.task + 5

        elif observation[1] == observationHostnameVector["User3"] or self.task == 6:
            action = actionVector["Remove User3"]
            if self.task == 6:
                self.task = 0
            else:
                self.task = self.task + 6

        else:
            action = actionVector["Remove OpServer0"]
            action, _states = self.model.predict(observation)
            
        return action
        