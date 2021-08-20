from CybORG.Shared import Observation
from CybORG.Shared.Actions import Action


class Misinform(Action):
    def __init__(self, session: int, agent: str):
        super().__init__()
        self.agent = agent
        self.session = session

    def sim_execute(self, state) -> Observation:
        raise NotImplementedError