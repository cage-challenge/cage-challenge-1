import inspect

from CybORG import CybORG
from CybORG.Agents import SleepAgent
from CybORG.Agents.SimpleAgents.B_line import B_lineAgent
from CybORG.Agents.SimpleAgents.BlueReactAgent import BlueReactRemoveAgent, BlueReactRestoreAgent
from CybORG.Shared.Enums import TrinaryEnum
from CybORG.Shared.Actions import Impact, Remove, Monitor

import pytest


def test_blineagent_step():
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + f'/Shared/Scenarios/Scenario1b.yaml'
    cyborg = CybORG(path, 'sim', agents={'Red': B_lineAgent})
    action_space = cyborg.get_action_space(agent='Red')
    session = list(action_space['session'].keys())[0]
    reward = 0
    for i in range(20):
        result = cyborg.step(agent='Red')
        assert result.observation['success'] == True, f'Step: {i}, Action: {result.action}'
        if i >= 14:
            assert type(result.action) == Impact
            assert result.action.agent == 'Red'
            assert result.action.session == session
            assert result.action.hostname == 'Op_Server0'
            if i == 14:
                reward += 10.0
        elif i in [2]:
            reward += 0.1
        elif i in [6, 13]:
            reward += 1.0
        elif i in [10]:
            reward += 1
        assert result.reward == round(reward, 1), f'error for step {1} action {result.action}'

    cyborg.reset()

    reward = 0
    for i in range(20):
        result = cyborg.step(agent='Red')
        assert result.observation['success'] == True, f'Step: {i}, Action: {result.action}'
        if i >= 14:
            assert type(result.action) == Impact
            assert result.action.agent == 'Red'
            assert result.action.session == session
            assert result.action.hostname == 'Op_Server0'
            if i ==14:
                reward += 10.0
        elif i in [2]:
            reward += 0.1
        elif i in [6, 13]:
            reward += 1.0
        elif i in [10]:
            reward += 1
        assert result.reward == round(reward, 1), f'error for step {1} action {result.action}'


def test_bline_agent_blue_interruptions():
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + f'/Shared/Scenarios/Scenario1b.yaml'
    cyborg = CybORG(path, 'sim')
    cyborg.set_seed(12)  # todo; Parametrised with different seeds
    agent = B_lineAgent()

    results = cyborg.reset(agent='Red')
    observation = results.observation
    action_space = results.action_space
    session = list(action_space['session'].keys())[0]
    for i in range(20):
        action = agent.get_action(observation, action_space)
        result = cyborg.step(action=action, agent='Red')
        action_space = result.action_space
        observation = result.observation
        # session = 0

        if i == 4:
            action = Monitor(session=session, agent='Blue')
            blue_result = cyborg.step(agent='Blue', action=action)
            # print(blue_result.observation)
            action = Remove(session=session, agent='Blue', hostname='Enterprise1')
            blue_result = cyborg.step(agent='Blue', action=action)
            assert blue_result.observation['success'] == True, f'Step: {i}, Action: {blue_result.action}'
        if i in []:
            assert result.observation['success'] == False, f'Step: {i}, Action: {result.action}'
            # action = Sleep
        else:
            blue_result = cyborg.step(agent='Blue')
            assert blue_result.observation['success'] == TrinaryEnum.TRUE, f'Step: {i}, Action: {blue_result.action}'


@pytest.mark.parametrize('blue_agent', [BlueReactRemoveAgent, BlueReactRestoreAgent, SleepAgent])
def test_bline_vs_blue_agent_start(blue_agent):
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + f'/Shared/Scenarios/Scenario1b.yaml'
    cyborg = CybORG(path, 'sim', agents={'Red': B_lineAgent, 'Blue': blue_agent})
    cyborg.start(100)
    cyborg.reset()
    cyborg.start(100)


def test_blineagent_vs_react_remove_agent_step():
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + f'/Shared/Scenarios/Scenario1b.yaml'
    cyborg = CybORG(path, 'sim', agents={'Red': B_lineAgent, 'Blue': BlueReactRemoveAgent})
    action_space = cyborg.get_action_space(agent='Red')
    session = list(action_space['session'].keys())[0]
    for i in range(50):
        result = cyborg.step(agent='Red')
        if i in []:
            assert result.observation['success'] == False, f'Successful action {result.action} for step {i}'
        else:
            assert result.observation['success'] == True, f'Unsuccessful action {result.action} for step {i}'
        if i > 35:
            assert result.reward > 10.


def test_blineagent_vs_react_restore_agent_step():
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + f'/Shared/Scenarios/Scenario1b.yaml'
    cyborg = CybORG(path, 'sim', agents={'Red': B_lineAgent, 'Blue': BlueReactRestoreAgent})
    action_space = cyborg.get_action_space(agent='Red')
    session = list(action_space['session'].keys())[0]
    for i in range(50):
        result = cyborg.step(agent='Red')
        if not result.observation['success']:
            print(i)
            breakpoint()
        if i in list(range(5, 50)):
            assert result.observation['success'] == False, f'Successful action {result.action} for step {i}'
        else:
            assert result.observation['success'] == True, f'Unsuccessful action {result.action} for step {i}'

#
