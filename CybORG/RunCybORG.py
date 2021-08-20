# Copyright DST Group. Licensed under the MIT license.
"""A script for running a CybORG Scenario

Usage
-----

Using default step limit and games:

 $ python RunCybORG --environment env path/to/scenario.yaml

 or

 $ python RunCybORG -e env path/to/scenario.yaml


Using custom step limit and games:

 $ python RunCybORG -e env --steps 100 --games 10 path/scenario.yaml

 or

 $ python RunCybORG -e env -s 100 -g 10 path/scenario.yaml


where:

 - 'env' is name of supported environment (e.g. 'sim', 'aws')

"""

from CybORG import CybORG
from CybORG.Emulator.AWS import AWSConfig


def run_cyborg(scenario_file: str,
               environment: str,
               aws_path: str = None,
               steps: int = 100,
               games: int = 1):
    """Run CybORG

    Parameters
    ----------
    scenario_file : str
        path for scenario YAML file
    environment : str, optional
        the environment to use
    steps : int, optional
        step limit for a single game (default=100)
    games : int, optional
        number of games to play (default=1)
    """

    print(f"Running CybORG with scenario file {scenario_file} for environment {environment}")

    if aws_path:

        aws_config = AWSConfig.load_and_setup_logger(
            aws_config_file_path=aws_path
        )
        #cyborg = CybORG(scenario_file, environment)
        cyborg = CybORG(
            scenario_file,
            environment=environment,
            env_config={
                "config": aws_config,
                "create_tunnel": True
            }
        )
    else:
        aws_config = AWSConfig.load_and_setup_logger()
        cyborg = CybORG(scenario_file,
                        environment=environment,
                        env_config={
                            "config": aws_config,
                            "create_tunnel": True})

    line_break = "="*60
    for g in range(games):
        print(f"{line_break}\nStarting game {g+1}\n{line_break}")
        cyborg.reset()
        done = cyborg.start(steps)
        print(f"{line_break}\nGame {g+1} finished")
        print(f"Goal reached = {done}")
    print(f"{line_break}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario_file", type=str,
                        help="The filepath of the YAML scenario to run")
    parser.add_argument("-e", "--environment", type=str,
                        help="Environment to use (e.g. 'sim', 'aws')")
    parser.add_argument('-a', '--aws_path', type=str,
                        help="The path to the aws file.")
    parser.add_argument("-s", "--steps", type=int, default=100,
                        help="Step limit for single game (default=100)")
    parser.add_argument("-g", "--games", type=int, default=1,
                        help="Number of games to play (default=1)")
    args = parser.parse_args()

    run_cyborg(**vars(args))
