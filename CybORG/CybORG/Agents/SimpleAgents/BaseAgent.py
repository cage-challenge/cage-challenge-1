from CybORG.Shared import Results

class BaseAgent:
    """Base class for all the other agents.
    Has the abstract methods to be implemented in the inherited classes.
    """    
    def train(self, results: Results):
        """Allows an agent to learn a policy

        Parameters
        ----------
        results : Results
            Has action_space and observation dictionaries.

        Raises
        ------
        NotImplementedError
            Raised if method is not defined in inherited class.
        """
        raise NotImplementedError

    def get_action(self, observation, action_space):
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

        Raises
        ------
        NotImplementedError
            Raised if method is not defined in inherited class.
        """
        
        raise NotImplementedError

    def end_episode(self):
        """Allows an agent to update its internal state.

        Raises
        ------
        NotImplementedError
            Raised if method is not defined in inherited class.
        """        
        
        raise NotImplementedError

    def set_initial_values(self, action_space, observation):
        """Set initial values.

        Parameters
        ----------
        action_space : dict
            Has the actions and parameters that are updated at each step.
            Actions are the tools used to attack/defend.
            Parameters are the inputs to the tools.
        observation : dict
            Has two keys - 'success' and 'User0'. 
            success tells us if the previous action ran without errors or not.
            User0 is a dict that contains information about the host. 
            Refer to ../../Shared/Observation.py for more info.

        Raises
        ------
        NotImplementedError
            Raised if method is not defined in inherited class.
        """        
        raise NotImplementedError
