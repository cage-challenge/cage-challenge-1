from typing import Union, Any

from CybORG import CybORG
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Shared import Results


class BaseWrapper:
    """Base class for other wrappers.
    Has the abstract methods to be implemented in the inherited classes.
    """
    def __init__(self, env: CybORG = None, agent: BaseAgent = None):
        # wrapper allows changes to be made to the interface between external agents via specification of the env
        self.env = env
        # wrapper allows changes to be made to the interface between internal agents via specification of the agent
        self.agent = agent

    def step(self, agent=None, action=None) -> Results:
        """[summary]

        Parameters
        ----------
        agent : [type], optional
            [description], by default None
        action : [type], optional
            [description], by default None

        Returns
        -------
        Results
            [description]
        """
        result = self.env.step(agent, action)
        result.observation = self.observation_change(result.observation)
        result.action_space = self.action_space_change(result.action_space)
        return result

    def reset(self, agent=None):
        """[summary]

        Parameters
        ----------
        agent : [type], optional
            [description], by default None

        Returns
        -------
        [type]
            [description]
        """
        result = self.env.reset(agent)
        result.action_space = self.action_space_change(result.action_space)
        result.observation = self.observation_change(result.observation)
        return result

    def get_action(self, observation: dict, action_space: dict):
        """[summary]

        Parameters
        ----------
        observation : dict
            [description]
        action_space : dict
            [description]

        Returns
        -------
        [type]
            [description]
        """
        return self.agent.get_action(self.observation_change(observation), self.action_space_change(action_space))

    def train(self, result: Results):
        """[summary]

        Parameters
        ----------
        result : Results
            [description]
        """        
        """Trains an agent with the new tuple from the environment"""
        result.action_space = self.action_space_change(result.action_space)
        result.observation = self.observation_change(result.observation)
        self.agent.train(result)

    def set_initial_values(self, observation: dict, action_space: dict):
        """[summary]

        Parameters
        ----------
        observation : dict
            [description]
        action_space : dict
            [description]
        """
        self.agent.set_initial_values(action_space, observation)

    def observation_change(self, observation: dict) -> dict:
        """[summary]

        Parameters
        ----------
        observation : dict
            [description]

        Returns
        -------
        dict
            [description]
        """
        return observation

    def action_space_change(self, action_space: dict) -> dict:
        """[summary]

        Parameters
        ----------
        action_space : dict
            [description]

        Returns
        -------
        dict
            [description]
        """
        return action_space

    def end_episode(self):
        """[summary]
        """
        self.agent.end_episode()

    def get_action_space(self, agent: str) -> dict:
        """[summary]

        Parameters
        ----------
        agent : str
            [description]

        Returns
        -------
        dict
            [description]
        """
        return self.action_space_change(self.env.get_action_space(agent))

    def get_observation(self, agent: str):
        """[summary]

        Parameters
        ----------
        agent : str
            [description]

        Returns
        -------
        [type]
            [description]
        """
        return self.observation_change(self.env.get_observation(agent))

    def get_last_action(self, agent: str):
        """[summary]

        Parameters
        ----------
        agent : str
            [description]

        Returns
        -------
        [type]
            [description]
        """
        return self.env.get_last_action(agent=agent)

    def set_seed(self, seed: int):
        """[summary]

        Parameters
        ----------
        seed : int
            [description]
        """
        self.env.set_seed(seed)

    def shutdown(self, **kwargs) -> bool:
        """Shutdown CybORG

        Parameters
        ----------
        **kwargs : dict, optional
            keyword arguments to pass to environment controller shutdown
            function. See the shutdown function of the specific environment
            controller used for details.

        Returns
        -------
        bool
            True if cyborg was shutdown without issue
        """
        return self.env.shutdown(**kwargs)

    def get_attr(self, attribute: str) -> Any:
        """Gets a specified attribute from this wrapper if present of requests it from the wrapped environment

        Parameters
        ----------
        attribute : str
            name of the requested attribute

        Returns
        -------
        Any
            the requested attribute
        """
        if hasattr(self, attribute):
            return self.__getattribute__(attribute)
        else:
            return self.env.get_attr(attribute)
