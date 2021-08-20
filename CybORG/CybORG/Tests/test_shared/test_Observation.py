# Copyright DST Group. Licensed under the MIT license.

from CybORG.Shared import Observation

IPS = [
    "127.0.0.1",
    "192.0.0.10",
    "168.0.0.10",
    "148.0.10.0"
]

CIDRS = [
    "192.0.0.0/16",
    "168.0.0.0/16",
    "148.0.0.0/16"
]

OBS_MAP = {
    "proc0_0": lambda o: o.add_process(
        hostid="0",
        pid=111,
        process_name="proc0_0",
        local_address=IPS[0],
        remote_address=IPS[1],
    ),
    "proc0_1": lambda o: o.add_process(
        hostid="0",
        pid=333,
        process_name="proc0_1",
        local_address=IPS[0],
        remote_address=IPS[2],
    ),
    "proc0_2": lambda o: o.add_process(
        hostid="0",
        pid=555,
        process_name="proc0_2",
        local_address=IPS[0],
        remote_address=IPS[3],
    ),
    "proc1_0": lambda o: o.add_process(
        hostid="1",
        pid=222,
        process_name="proc1_0",
        local_address=IPS[0],
        remote_address=IPS[1],
    ),
    "proc1_1": lambda o: o.add_process(
        hostid="1",
        pid=444,
        process_name="proc1_1",
        local_address=IPS[0],
        remote_address=IPS[2],
    ),
    "proc1_2": lambda o: o.add_process(
        hostid="1",
        pid=666,
        process_name="proc1_2",
        local_address=IPS[0],
        remote_address=IPS[3],
    ),
    "interface0_0": lambda o: o.add_interface_info(
        hostid="0",
        ip_address=IPS[0],
    ),
    "interface0_1": lambda o: o.add_interface_info(
        hostid="0",
        interface_name="interface0_1",
        ip_address=IPS[1],
        subnet=CIDRS[0]
    ),
    "interface1_0": lambda o: o.add_interface_info(
        hostid="1",
        ip_address=IPS[0],
    ),
    "interface1_1": lambda o: o.add_interface_info(
        hostid="1",
        interface_name="interface1_1",
        ip_address=IPS[2],
        subnet=CIDRS[1]
    ),
    "interface2_1": lambda o: o.add_interface_info(
        hostid="2",
        interface_name="interface2_1",
        ip_address=IPS[3],
        subnet=CIDRS[2]
    )
}


def gen_obs(success: bool, excludes: list) -> Observation:
    obs = Observation()
    obs.set_success(success)
    for k, fn in OBS_MAP.items():
        if k not in excludes:
            fn(obs)
    return obs


def test_obs_filter():
    actual_obs = gen_obs(True, [])
    actual_obs.filter_addresses(
        ips=[IPS[1], IPS[2]],
        cidrs=[CIDRS[0], CIDRS[1]],
        include_localhost=True
    )

    expected_obs = gen_obs(
        True,
        [
            "proc0_2",
            "proc1_2",
            "interface2_1"
        ]
    )

    print(actual_obs)
    print(expected_obs)

    assert actual_obs == expected_obs


def test_obs_combine():

    obs_one = gen_obs(
        True,
        [
            "proc1_0",
            "proc1_1",
            "proc1_2"
        ])
    obs_two = gen_obs(
        True,
        [
            "proc0_0",
            "proc0_1",
            "proc0_2"
        ])
    obs_final = gen_obs(
        True,
        [])

    obs_one.combine_obs(obs_two)
    print(obs_one)
    print(obs_final)
    assert str(obs_one) == str(obs_final)
