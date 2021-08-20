import inspect

from CybORG import CybORG
import pytest

from CybORG.Tests.utils import compare_fundamental_observations


@pytest.mark.parametrize(['info'], [(None,), ({'Attacker': {'System info': 'All'}},)])
def test_compare_get_true_state(info):
    path = str(inspect.getfile(CybORG))
    path = path[:-10] + '/Shared/Scenarios/Scenario1.yaml'
    cyborg_simulation = CybORG(path, 'sim')
    sim = cyborg_simulation.get_true_state(info).data
    cyborg_emulation = CybORG(path, 'aws', env_config={
        "config": AWSConfig.load_and_setup_logger(test=True),
        "create_tunnel": False
    })
    try:
        em = cyborg_emulation.get_true_state(info).data
        print(sim)
        print(em)
        assert compare_fundamental_observations(sim, em, {})
    finally:
        cyborg_emulation.shutdown(teardown=True)
