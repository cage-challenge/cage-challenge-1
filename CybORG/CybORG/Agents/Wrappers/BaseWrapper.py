from typing import Union, Any

from CybORG import CybORG
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Shared import Results


class BaseWrapper:
    """Base class for other wrappers.
    Has the abstract methods to be implemented in the inherited classes.
    """
    def __init__(self, env: CybORG = None, agent: BaseAgent = None):
        """Initialize wrapper object

        Parameters
        ----------
        env : CybORG, optional
            The environment being used, by default None
        agent : BaseAgent, optional
            The agent that needs to use the wrapper, by default None
        """
        # wrapper allows changes to be made to the interface between external agents via specification of the env
        self.env = env
        # wrapper allows changes to be made to the interface between internal agents via specification of the agent
        self.agent = agent

    def step(self, agent: str = None, action=None) -> Results:
        """
        Make the agent perform the given action and update observation and
        action_space.

        Parameters
        ----------
        agent : str, optional
            The agent that needs to use the wrapper, by default None
        action : Action, optional
            A specific cyber tool that can be executed by an agent, by default None

        Returns
        -------
        result : Results
            Has action_space and observation dictionaries.
        """
        result = self.env.step(agent, action)
        result.observation = self.observation_change(result.observation)
        result.action_space = self.action_space_change(result.action_space)
        return result

    def reset(self, agent: str = None):
        """Reset environment to be used for a different agent or set up

        Parameters
        ----------
        agent : str, optional
            The agent that needs to use the wrapper, by default None

        Returns
        -------
        result : Results
            Contains fresh action_space and observation dictionaries
        """
        result = self.env.reset(agent)
        result.action_space = self.action_space_change(result.action_space)
        result.observation = self.observation_change(result.observation)
        return result

    def get_action(self, observation: dict, action_space: dict):
        """Gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space.

        Parameters
        ----------
        observation : dict
            Has two keys - 'success' and 'User0'. 
            success tells us if the previous action ran without errors or not.
            User0 is a dict that contains information about the host. 
            Refer to ../../Shared/Observation.py for more info.
        action_space : dict
            Has the actions and parameters that are updated at each step.
            Actions are the tools used to attack/defend.
            Parameters are the inputs to the tools.

        Returns
        -------
        Action
        """
        return self.agent.get_action(self.observation_change(observation), self.action_space_change(action_space))

    def train(self, result: Results):
        """Trains an agent with the new tuple from the environment

        Parameters
        ----------
        result : Results
            Has action_space and observation dictionaries.
        """
        result.action_space = self.action_space_change(result.action_space)
        result.observation = self.observation_change(result.observation)
        self.agent.train(result)

    def set_initial_values(self, observation: dict, action_space: dict):
        """Set the initial values for the current agent.

        Parameters
        ----------
        observation : dict
            Has two keys - 'success' and 'User0'.
            success tells us if the previous action ran without errors or not.
            User0 is a dict that contains information about the host. 
            Refer to ../../Shared/Observation.py for more info.
        action_space : dict
            Has the actions and parameters that are updated at each step.
            Actions are the tools used to attack/defend.
            Parameters are the inputs to the tools.
        """
        self.agent.set_initial_values(action_space, observation)

    def observation_change(self, observation: dict) -> dict:
        """Change value of observation

        Parameters
        ----------
        observation : dict
            Has two keys - 'success' and 'User0'.
            success tells us if the previous action ran without errors or not.
            User0 is a dict that contains information about the host. 
            Refer to ../../Shared/Observation.py for more info.

        Returns
        -------
        observation : dict
            Modified observation
        """
        return observation

    def action_space_change(self, action_space: dict) -> dict:
        """Make a change to the action_space based on wrapper requirements

        Parameters
        ----------
        action_space : dict
            Has the actions and parameters that are updated at each step.
            Actions are the tools used to attack/defend.
            Parameters are the inputs to the tools.

        Returns
        -------
        action_space : dict
            Modified action_space
        """
        return action_space

    def end_episode(self):
        """Allows the agent to update its internal state.
        """
        self.agent.end_episode()

    def get_action_space(self, agent: str) -> dict:
        """Gets the action space for a chosen agent

        Parameters
        ----------
        agent : str
            Given agent

        Returns
        -------
        dict
            action_space for given agent
        """
        return self.action_space_change(self.env.get_action_space(agent))

    def get_observation(self, agent: str):
        """Get observation for chosen agent

        Parameters
        ----------
        agent : str
            Given agent

        Returns
        -------
        dict
            observation for given agent
        """
        return self.observation_change(self.env.get_observation(agent))

    def get_last_action(self, agent: str):
        """Get last action performed by given agent

        Parameters
        ----------
        agent : str
            Given agent

        Returns
        -------
        Action
            last action of given agent
        """
        return self.env.get_last_action(agent=agent)

    def set_seed(self, seed: int):
        """Set seed value for environment

        Parameters
        ----------
        seed : int
            use this integer for initializing a random number generator
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
