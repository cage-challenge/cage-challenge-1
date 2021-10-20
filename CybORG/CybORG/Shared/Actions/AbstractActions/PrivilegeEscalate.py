from collections.abc import Iterable
from random import choice

from CybORG.Shared import Observation
from CybORG.Shared.Actions import Action
from CybORG.Shared.Actions.ConcreteActions.EscalateAction import ExploreHost
from CybORG.Shared.Actions.ConcreteActions.JuicyPotato import JuicyPotato
from CybORG.Shared.Actions.ConcreteActions.V4L2KernelExploit import V4L2KernelExploit
from CybORG.Shared.Enums import OperatingSystemType
from CybORG.Simulator.State import State


class PrivilegeEscalate(Action):
    def __init__(self, session: int, agent: str, hostname: str):
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname

    def sim_execute(self, state: State) -> Observation:
        # find session on the chosen host
        sessions = [s for s in state.sessions[self.agent].values() if s.host == self.hostname]
        if len(sessions) == 0:
            # no valid session could be found on chosen host
            return Observation(success=False)
        # find if any session are already SYSTEM or root
        min_level = 0
        session = None
        for s in sessions:
            # else find if session is Admin or sudo
            if s.username == 'root' or s.username == 'SYSTEM':
                session = s.ident
                obs = Observation(success=True)
                obs.add_session_info(hostid=self.hostname, **s.get_state())
                break
        # else use random session
        if session is None:
            session = choice(sessions).ident

            # run privilege escalation that corresponds to that operating system
            if state.sessions[self.agent][self.session].operating_system[self.hostname] == OperatingSystemType.WINDOWS:
                sub_action = JuicyPotato(session=self.session, target_session=session, agent=self.agent)
            else:
                sub_action = V4L2KernelExploit(session=self.session, target_session=session, agent=self.agent)
            obs = sub_action.sim_execute(state)
        if obs.data['success'] == True:
            sub_action = ExploreHost(session=self.session, target_session=session, agent=self.agent)
            obs2 = sub_action.sim_execute(state)
            for host in obs2.data.values():
                if isinstance(host, Iterable) and 'Processes' in host:
                    for proc in host['Processes']:
                        if 'Service Name' in proc:
                            if proc['Service Name'] == 'OTService':
                                state.sessions[self.agent][self.session].ot_service = 'OTService'
                                break

            obs.combine_obs(obs2)
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
