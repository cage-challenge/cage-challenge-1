from ipaddress import IPv4Address

from CybORG.Shared import Observation
from CybORG.Shared.Actions.ConcreteActions.ConcreteAction import ConcreteAction
from CybORG.Shared.Actions.MSFActionsFolder.MSFAction import lo
from CybORG.Shared.Enums import ProcessType, OperatingSystemType
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Session import Session
from CybORG.Simulator.State import State


class EscalateAction(ConcreteAction):
    def __init__(self, session: int, agent: str, target_session: int):
        super().__init__(session, agent)
        self.target_session = target_session

    def sim_escalate(self, state: State, user: str) -> Observation:
        self.state = state
        obs = Observation()
        if self.session not in state.sessions[self.agent] or self.target_session not in state.sessions[self.agent]:
            obs.set_success(False)
            return obs
        target_host = state.hosts[state.sessions[self.agent][self.target_session].host]
        session = state.sessions[self.agent][self.session]
        target_session = state.sessions[self.agent][self.target_session]

        if not session.active or not target_session.active:
            obs.set_success(False)
            return obs

        if self.test_exploit_works(target_host):
            obs = self.upgrade_session(state, user, target_host, target_session)
        else:
            obs.set_success(False)
        return obs

    def test_exploit_works(self, target_host: Host):
        # check if OS and process information is correct for exploit to work
        raise NotImplementedError

    def upgrade_session(self, state: State, username: str, target_host: Host, session: Session):
        if target_host.os_type == OperatingSystemType.WINDOWS:
            ext = 'exe'
            path = 'C:\\temp\\'
        elif target_host.os_type == OperatingSystemType.LINUX:
            ext = 'sh'
            path = '/tmp/'
        else:
            return Observation(False)
        obs = Observation()
        # upgrade session to new username
        session.username = username
        target_host.get_process(session.pid).user = username
        file = target_host.add_file(f'escalate.{ext}', path, username, 7, density=0.9, signed=False)
        # add in new session info to observation
        obs.add_session_info(hostid=str(target_host.hostname),
                             session_id=session.ident,
                             session_type=session.session_type,
                             username=username,
                             agent=self.agent)
        obs.set_success(True)
        return obs


class ExploreHost(ConcreteAction):
    def __init__(self, session: int, agent: str, target_session: int):
        super().__init__(session, agent)
        self.target_session = target_session

    def sim_execute(self, state: State) -> Observation:
        if self.session not in state.sessions[self.agent] or self.target_session not in state.sessions[self.agent]:
            return Observation(success=False)
        target_host = state.hosts[state.sessions[self.agent][self.target_session].host]
        obs = state.get_true_state(target_host.info)
        obs.set_success(True)
        return obs
