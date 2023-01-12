'''
This is a modified version of the CybORG BlueLoadAgent that was developed to enhance the capability of the original and improve on it

Developed:  Sky Tainyi Zhang
            Mitchell Knyn
            Jayden Fowler
            
Date: 12 January 2023
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
    def train(self, results):
        pass

    def end_episode(self):
        pass

    def set_initial_values(self, action_space, observation):
        pass
        

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

    def __init__(self, model_file: str = "ppo_training"):
        if os.path.exists(ppo_path):
            self.model = PPO.load(model_file)
            print("\nsuccessfully loaded the ppo file\n")
        else:
            self.model = PPO('MlpPolicy', cyborg)
            self.model.learn(total_timesteps=int(200), log_interval=10)
            self.model.save("ppo_training")
            print("\nNo Model file, trained new one\n")

    def get_action(self, observation, action_space):
        """gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space"""
        action, _states = self.model.predict(observation)
        return action
        