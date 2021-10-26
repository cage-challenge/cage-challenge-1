from datetime import datetime

from CybORG.Agents.Wrappers.BaseWrapper import BaseWrapper
from CybORG.Shared import Observation
from CybORG.Shared.Actions import ShellSleep
from CybORG.Shared.Enums import OperatingSystemType, SessionType, ProcessName, Path, ProcessType, ProcessVersion, \
    AppProtocol, FileType, ProcessState, Vulnerability, Vendor, PasswordHashType, BuiltInGroups, \
    OperatingSystemDistribution, OperatingSystemVersion, OperatingSystemKernelVersion, Architecture, \
    OperatingSystemPatch, FileVersion

import inspect, random

class FixedFlatWrapper(BaseWrapper):
    def __init__(self, env: BaseWrapper=None, agent=None):
        super().__init__(env, agent)

        self.MAX_HOSTS = 5
        self.MAX_PROCESSES = 100
        self.MAX_CONNECTIONS = 2
        self.MAX_VULNERABILITIES = 1
        self.MAX_INTERFACES = 4
        self.MAX_FILES = 10
        self.MAX_SESSIONS = 20
        self.MAX_USERS = 10
        self.MAX_GROUPS = 10
        self.MAX_PATCHES = 10

        self.observation_structure = Object(None, 1, [
            Object('System info', 1, [
                String('Hostname', self.MAX_HOSTS),
                Enum('OSType', OperatingSystemType),
                Enum('OSDistribution', OperatingSystemDistribution),
                Enum('OSVersion', OperatingSystemVersion),
                Enum('OSKernelVersion', OperatingSystemKernelVersion),
                Enum('Architecture', Architecture),
                Time('Local Time'),
                EnumArray('os_patches', OperatingSystemPatch, self.MAX_PATCHES)
            ]),
            Object('Processes', self.MAX_PROCESSES, [
                Float('PID', 32768),
                Float('PPID', 32768),
                String('Process Name'),
                String('Username'),
                String('Path'),
                Enum('Known Process', ProcessName),
                Enum('Known Path', Path),
                Enum('Process Type', ProcessType),
                Enum('Process Version', ProcessVersion),
                Object('Connections', self.MAX_CONNECTIONS, [
                    Float('local_port', 65535),
                    Float('remote_port', 65535),
                    Float('local_address', 4294967296),
                    Float('Remote Address', 4294967296),
                    Enum('Application Protocol', AppProtocol),
                    Enum('Status', ProcessState)
                ]),
                EnumArray('Vulnerability', Vulnerability, self.MAX_VULNERABILITIES)
            ]),
            Object('Files', self.MAX_FILES, [
                String('Path'),
                Enum('Known Path', Path),
                String('File Name'),
                Enum('Known File', FileType),
                Enum('Type', FileType),
                Enum('Vendor', Vendor),
                Enum('Version', FileVersion),
                String('Username'),
                String('Group Name'),
                Time('Last Modified Time'),
                Float('User Permissions', 7),
                Float('Group Permissions', 7),
                Float('Default Permissions', 7)
            ]),
            Object('Users', self.MAX_USERS, [
                String('Username'),
                String('Password'),
                String('Password Hash'),
                Enum('Password Hash Type', PasswordHashType),
                Float('UID'),
                Float('Logged In'),
                Object('Groups', self.MAX_GROUPS, [
                    Enum('Builtin Group', BuiltInGroups),
                    String('Group Name'),
                    Float('GID')
                ])
            ]),
            Object('Sessions', self.MAX_SESSIONS, [
                String('Username'),
                Enum('Type', SessionType),
                Float('ID', 20),
                Float('Timeout'),
                Float('PID', 32768)
            ]),
            Object('Interface', self.MAX_INTERFACES, [
                String('Interface Name'),
                Subnet('Subnet'),
                Float('IP Address', 4294967296)
            ])
        ])

        self.cache = {}

    def get_action(self, observation, action_space):

        action = self.agent.get_action(self.observation_change(observation), self.action_space_change(action_space))

        action_class = action['action']
        params = {}
        for p in inspect.signature(action_class).parameters:
            if p in action:
                params[p] = action[p]
            else:
                action_class = ShellSleep
                params = {}
                break
        action = action_class(**params)
        return action

    # def action_space_change(self, action_space: dict) -> dict:
    #     action_space.pop('process')
    #     action_space['session'] = {0: True}
    #     action_space['username'] = {'pi': action_space['username']['pi'],
    #                                 'vagrant': action_space['username']['vagrant']}
    #     action_space['password'] = {'raspberry': action_space['password']['raspberry'],
    #                                 'vagrant': action_space['password']['vagrant']}
    #     action_space['port'] = {22: action_space['port'][22]}
    #     return action_space

    def observation_change(self, obs: dict) -> list:
        numeric_obs = obs
        flat_obs = []
        while len(numeric_obs) < self.MAX_HOSTS:
            hostid = str(random.randint(0, self.MAX_HOSTS+1))
            if hostid not in numeric_obs.keys():
                numeric_obs[hostid] = {}

        while len(numeric_obs) > self.MAX_HOSTS:
            numeric_obs.popitem()
            #raise ValueError("Too many hosts in observation for fixed size")

        for key_name, host in numeric_obs.items():
            if key_name == 'success':
                flat_obs.append(float(host.value)/3)
            else:
                flat_obs += self.observation_structure.flatten(host, self.cache)

        return flat_obs

    def get_attr(self,attribute:str):
        return self.env.get_attr(attribute)

    def get_observation(self, agent: str):
        obs = self.get_attr('get_observation')(agent)
        return self.observation_change(obs)

## BEGIN PRIVATE DATA CLASSES ##

class Data:
    def __init__(self, key):
        self.key = key

    def flatten(self, data, cache):
        try:
            return self._flatten(data, cache)
        except Exception as e:
            raise Exception(f'Exception flattening {self.key}') from e

    def _flatten(self, data, cache):
        raise NotImplementedError

    def fill(self, elements, size, default):
        while len(elements) > size:
            elements.pop()
            #raise ValueError(f"Too many {self.key} elements in observation for fixed size of {size}")

        while len(elements) < size:
            elements.append(default)

        return elements

class Object(Data):
    def __init__(self, key, count, attrs):
        super().__init__(key)
        self.count = count
        self.attrs = attrs

    def _flatten(self, data, cache):
        # Root dictionary has no key
        if self.key:
            if self.key not in data:
                data[self.key] = {} if self.count == 1 else []

            if 1 < self.count:
                data[self.key] = self.fill(data[self.key], self.count, {})

            data = data[self.key]

        # This is to allow for all cases to be handled in the for loop
        if self.count == 1:
            data = [data]

        flat_obj = []
        for item in data:
            for attr in self.attrs:
                flattened = attr.flatten(item, cache)
                if isinstance(flattened, list):
                    flat_obj += flattened
                else:
                    flat_obj.append(flattened)
        return flat_obj

    def _flatten_attrs(self, data, cache, attrs):
        flat_attrs = []

        return flat_attrs

class String(Data):
    def __init__(self, key, divisor = None):
        super().__init__(key)
        self.divisor = 1.0 if divisor is None else divisor

    def _flatten(self, data, cache):
        if self.key not in data:
            return -1.0

        if self.key not in cache:
            cache[self.key] = {}

        _cache = cache[self.key]
        element = data[self.key]

        if element not in _cache:
            _cache[element] = len(_cache)

        value = _cache[element]

        return (float(value) / self.divisor)

class Float(Data):
    def __init__(self, key, divisor = 1.0):
        super().__init__(key)
        self.divisor = divisor

    def _flatten(self, data, cache):
        if self.key not in data:
            return -1.0
        return (float(int(data[self.key])) / self.divisor)

class Enum(Data):
    def __init__(self, key, enum):
        super().__init__(key)
        self.enum = enum
        self.divisor = len(enum.__members__)

    def _flatten(self, data, cache):
        if self.key not in data:
            return -1.0

        element = data[self.key]
        if element != -1:
            element = element.value / self.divisor

        return float(element)

class EnumArray(Enum):
    def __init__(self, key, enum, size):
        super().__init__(key, enum)
        self.size = size

    def _flatten(self, data, cache):
        if self.key not in data:
            return [ -1.0 for _ in range(self.size) ]

        elements = self.fill(data[self.key], self.size, -1.0)

        flat_data = []
        for element in elements:
            if element != -1:
                element = element.value / self.divisor
            flat_data.append(float(element))
        return flat_data

class Time(Data):
    def __init__(self, key, reference_datetime = None):
        super().__init__(key)

        if reference_datetime is None:
            self.reference = datetime(2020, 1, 1)
        else:
            self.reference = reference_datetime

    def _flatten(self, data, cache):
        if self.key not in data:
            return -1.0
        return float((data[self.key] - self.reference).total_seconds())

class Subnet(Data):
    def __init__(self, key):
        super().__init__(key)

    def _flatten(self, data, cache):
        if self.key not in data:
            return [ -1.0, -1.0 ]
        subnet = data[self.key]
        return [ float(int(subnet.network_address))/4294967296,
                 float(int(subnet.prefixlen))/4294967296 ]
