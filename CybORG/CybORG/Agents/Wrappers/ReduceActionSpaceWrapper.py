import inspect
from typing import Union

from CybORG import CybORG
from CybORG.Agents.Wrappers.BaseWrapper import BaseWrapper
from CybORG.Shared import Results


class ReduceActionSpaceWrapper(BaseWrapper):
    def __init__(self, env: Union[BaseWrapper, CybORG]=None, agent=None):
        super().__init__(env, agent)
        self.action_signature = {}
        self.known_params = {}

    def action_space_change(self, action_space: dict) -> dict:
        assert type(action_space) is dict, f"Wrapper required a dictionary action space. " \
                                           f"Please check that the wrappers below the ReduceActionSpaceWrapper return the action space as a dict"
        params = ['action']
        for action in action_space['action']:
            if action not in self.action_signature:
                self.action_signature[action] = inspect.signature(action).parameters
            for p in self.action_signature[action]:
                if p not in params:
                    params.append(p)
        to_remove = []
        for key, value in action_space.items():
            if key not in params:
                to_remove.append(key)

        for p in to_remove:
            action_space.pop(p)

        return action_space

    def get_attr(self,attribute:str):
        return self.env.get_attr(attribute)
