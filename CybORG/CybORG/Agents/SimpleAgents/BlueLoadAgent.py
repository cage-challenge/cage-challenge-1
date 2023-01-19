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
        #print(observation[1])
        if observation[1] == np.float32(1) or self.task == 2:
            action = 48
            if self.task == 2:
                action = 48
                self.task = 0
            else:
                self.task = self.task + 2
        #print("Op_Server", type(observation[1]))
        elif observation[1] == np.float32(0.6) or self.task == 3:
            #print("Enterprise2", type(observation[1]))
            action = 18
            if self.task == 3:
                self.task = 0
            else:
                self.task = self.task + 3
        elif observation[1] == np.float32(0.4) or self.task == 1:
            action = 17
            if self.task == 1:
                self.task = 0
            else:
                self.task = self.task + 1
        #print("Enterprise1", type(observation[1]))
        elif observation[1] == np.float32(0.8) or self.task == 4:
            action = 24
            if self.task == 4:
                self.task = 0
            else:
                self.task = self.task + 4
            #print("User1", type(observation[1]))
        elif observation[1] == np.float32(0.2) or self.task == 5:
            action = 16
            if self.task == 5:
                self.task = 0
            else:
                self.task = self.task + 5
            #print("Enterprise0", type(observation[1]))
        elif observation[1] == np.float32(1.4) or self.task == 6:
            action = 26
            if self.task == 6:
                self.task = 0
            else:
                self.task = self.task + 6
            #print("User3", type(observation[1]))
        else:
            action = 22
            #action, _states = self.model.predict(observation)
        return action
        