# CybORG: A Guide for Me
**Purpose**: A written (informal) guide for anyone who has minimial to no experience in Python/Cyber/Machine learning. Anyone like me. 

Please skip the sections that may be irrelevant to you (e.g. setting up Virtual Environments).

## Prerequisites
* Python 3.7.5

Python 3.7.5 is required for the CybORG environment to run on. If your system already has a newer version of python installed, then an option to help manage older python versions is `pyenv`. 

Please refer to the `pyenv` [documentation](https://github.com/pyenv/pyenv#choosing-the-python-version) for further guidance. 

**TODO**: Write up quick 'how to setup' pyenv
<details>
<summary>
<b> 
Setting up pyenv for older versions of python
</b>
</summary>
<p>
</p>

**TODO**: Run through the steps on a system that does not have python 3.7.5 

</details>

## Installing CybORG
For anyone reading this on other platforms you can find the link to the GitLab repository here (granted Toby Richer has given you to access it)
```
https://gitlab.com/cyborg-owners/Autonomous-Cyber-Ops
```
<details>
<summary> <b> Setting up a python virtual environment</b> </summary>
<p>
</p>
I hear that setting up virtual environments is good practice. My example, is like with Skyrim mods. If there are too many mods installed, then the Skyrim game crashes. Therefore, like python libraries (mods), our python program can crash and we want to have different environments for each project.  

<p>
</p>
To setup a virtual environment on your Linux system. 
<p>
</p>

```
pip install venv
python -m venv myenv
``` 

Locate the file directory of your newly created virtual environment and activate it.
```
source myenv/bin/activate
```
This virtual environment is where CybORG will be installed and any other python libraries relevant for this project.
</details>

<details>
<summary> <b> Git cloning the repository </b> </summary>
<p>
</p>
To download or clone the CybORG files onto your local computer you can run the following git command. Make sure you run the command in the chosen location you want the files downloaded to. 
<p>
</p>

```
git clone https://gitlab.com/cyborg-owners/Autonomous-Cyber-Ops.git
```
</details>


Locate to `Autonomous-Cyber-Ops` folder to install CybORG locally using `pip`.
```
# from the root Autonomous-Cyber-Ops directory
pip install -e .
```
<sub> **Pro tip:** Don't be like me. Don't forget the 'space' and 'period' after the '-e' in the command </sub>

You may need to install additional libraries to get CybORG running. When prompted with an error of a missing library, please use `pip` to install the necessary library instructed. If prompted to install `grpc`, please use `pip install grpcio` instead to fix the error.


## Running the Keyboard Agent
As someone who is relatively new to Cyber Security, the Keyboard Agent was a great tool to learn what an agent wanted to achieve in this CybORG environment. The Keyboard Agent will give a better idea of what actions are available for a reinforcement agent during a game. 

Locate the `TestKeyboard.py` file to run the Keyboard Agent. 
```
Autonomous-Cyber-Ops/CybORG/Agents/SimpleAgents/TestKeyboard.py
```

Before running the script, lets run through what the scenario is and what the agent(you) is expected to achieve. The network diagram of the scenario is as below:

<img src="https://gitlab.com/cyborg-owners/Autonomous-Cyber-Ops/-/raw/BlueSimDev/CybORG/FAQ/Images/scenario_network_diagram.png" alt="drawing" width="625"/>

The agent will already have access to a host in the public subnet at the beginning of an episode and will have to perform tactics, techniques and procedures under the MITRE ATT&CK framework to exploit and gain user access to a host on the private subnet. From there, the agent will have to repeat the process, in addition to pivoting, to finally exploit the host on the secure subnet and capturing the flag.

Run `TestKeyboard.py`. In the terminal you should recieve the initial observation of the scenario and a list of available actions. 

<sub> **Note:** TestKeyboard.py action list is designed for the red agent. To observe how the blue actions with a Keyboard Agent please run `TestKeyboardBlue.py` instead.

<img src='https://gitlab.com/cyborg-owners/Autonomous-Cyber-Ops/-/raw/BlueSimDev/CybORG/FAQ/Images/initial_obs.png' alt='drawing' width='625'/>

You will also notice that the KeyboardAgent is waiting for a user input, where the input is tied with the corresponding integer for said actions. Type the action you would like to execute and press 'Enter' to see the results. A successful action will be met with a 'Success' message and consequently new information displayed on the observation table.

<img src='https://gitlab.com/cyborg-owners/Autonomous-Cyber-Ops/-/raw/BlueSimDev/CybORG/FAQ/Images/successful_action.png' alt='drawing' width='625'/>



Play through the game to exploit the secure host and capture the flag by executing the correct kill chain.

<sub> **Note:** The current version of Keyboard Agent is missing it's celebration message when the flag is captured but just ask Max and he will celebrate for you. </sub>

## Running CybORG
Below is the bare minimum of getting CybORG to run with a `Red` agent and a `Scenario1b.yaml` file. Please change the relevant fields for your specific needs. 
```python
from CybORG import CybORG
import inspect
path = str(inspect.getfile(CybORG))
path = path[:-10] + '/Shared/Scenarios/Scenario1b.yaml'
env = CybORG(path, 'sim')
env.reset(agent='Red')

steps = 1000
for eps in range(1):
    print(f'Game: {eps}')
    env.start(steps)
    env.reset() 
```

### Wrappers
Running CybORG can also be done under the use of our wrappers. These wrappers puts an overlay over the CybORG code to retrofit it to conform to other design requirements. Here is an example of using the various wrappers to get CybORG to function in an OpenAI Gym environment.

```python
import inspect
from CybORG import CybORG
from CybORG.Agents.Wrappers.GlobalObsWrapper import GlobalObsWrapper
from CybORG.Agents.Wrappers.OpenAIGymWrapper import OpenAIGymWrapper
from CybORG.Agents.Wrappers.FixedFlatWrapper import FixedFlatWrapper
from CybORG.Agents.Wrappers.EnumActionWrapper import EnumActionWrapper
from CybORG.Agents.Wrappers.ReduceActionSpaceWrapper import ReduceActionSpaceWrapper

agent_name = 'Red'
path = str(inspect.getfile(CybORG))
path = path[:-10] + '/Shared/Scenarios/Scenario1b.yaml'
cyborg = OpenAIGymWrapper(agent_name, GlobalObsWrapper(EnumActionWrapper(ReduceActionSpaceWrapper(CybORG(path, 'sim'))),
                                                       output_mode='vector')
cyborg.reset()

for i in range(10):
    action = cyborg.action_space.sample()
obs, rew, done, info = cyborg.step(action)

# To view observation in table format.
# cyborg.env.tracker.render()
```
Here is a brief run through of what each wrapper implements. 

**OpenAIGymWrapper**
- A wrapper to set the CybORG game to conform to the OpenAI Gym environment requirements. 

**GlobalObsWrapper**
- Wrapper was designed to reduce the size of the observation into a smaller table of the relevant observation. CybORG gives the agent the unfiltered access to the observable state of the game and can prolong training times. The GlobalObsWrapper packages the observation state into only the relevant observation for that given time step in the game, where the agent will only receive information on what machines/hosts it currently has access to. 

**EnumActionWrapper**
- This wrapper enumerates the list of possible reduced actions that the red agent can perform in CybORG and outputs a discrete integer value. This allows the environment to conform to OpenAI gym discrete space properties and enables the OpenAIWrapper.

**ReduceActionSpaceWrapper**
- The action space in CybORG has 8 elements and consists of the subnet, IP addresses, usernames, passwords, processes, ports and session ID. The possible combination of these parameters can often inflate exponentially and this wrapper has limited the parameters to each individual action. For example, to perform the action ‘Privilege Escalate’, the necessary parameters are the session ID, agent name and the hostname. This limits the number of possible actions the agent has to perform.

**FlatFixedWrapper**
- This wrapper is used over the GlobalObsWrapper as it does not minimise the observation of each state of the game and allows the agent to have the full state observation at all times. CybORG's observation is set as a dictionary format and the FlatFixedWrapper converts this information format into a list of integars or a vector to give the observation inputs meaning to the agent learning.



## CybORG Observation Design
The observation space in CybORG is set up as a complex diciontary data structure that also features methods to add information to this data structure. 

The dictionary always contains a trinary value for a `success` entry to represent successful, unsuccessful or unknown and indicates the result of the action.

The other keys within the observation are host IDS and are string values that are used to collect information that is believed to originate from a single host. Examples of host IDS are IP addresses or hostnames. These host ID is not guaranteed to repesent any information and for the agents to infer information from the environment. 

Each host ID also has a dictionary structure within that has information collected about the host. These entries have keys:
* Sessions
* Files
* Interfaces
* Proccesses
* Users
* System Info

An example of the observation data structure are show here:
```python
{
    "Success": TrinaryEnum,
    "<hostid0>" : {
        "Processes":[
            {"PID": int
            "PPID": int
            "Process name": str
            "Known Process": ProcessNameEnum
            "Program name": FileNameEnum
            "Username": str
            "Path": str
            "Known Path": PathEnum
            "Connections": {
                "local_port": int
                "local_address": IPv4Address
                "Remote port": int
                "Remote Address": IPv4Address
                "Application Protocol": ApplicationProtocolEnum,
                "Transport Protocol": TransportProtocolEnum
            }  
            "status": ProcessStateEnum
            "type": ProcessTypeEnum
            "version": ProcessVersionEnum
            "vulnerabilities": [VulnerabilityEnum]},
            ...
        ],
        "System info":{
                "Hostname": str,
                "OSType": OperatingSystemTypeEnum,
                "OSDistribution": OperatingSystemDistributionEnum,
                "OSVersion": OperatingSystemVersionEnum,
                "OSKernelVersion": OperatingSystemKernelVersionEnum,
                "Patches": [OperatingSystemPatchEnum],
                "Architecture": ArchitectureEnum
        },
        "Interfaces":[
            {"Interface": str,
            "IP Address" : IPv4Address,
            "Subnet": IPv4Subnet
            },
            ...
        ],
        "User Info":[
                {"Username" : str,
                "UID" : int,
                "Password" : str,
                "Password Hash" : str,
                "Password Hash Type" : PasswordHashType,
                "Groups" : [
                    {"Group Name" : str,
                     "Builtin Group" : BuiltInGroupsEnum,
                     "GID" : int},
                    ...
                ]
            },
            ...
        ],
        "Files":[
            {"Name" : str,
            "Known File" : FileNameEnum,
            "Group" : str,
            "GroupPermission" : int,
            "User" : str,
            "UserPermission" : int,
            "DefaultPermission" : int
            "Path": str,
            "Known Path": PathEnum,
            "Vendor": VendorEnum,
            "Version": str
            },
            ...
        ],
        "Sessions": [
            {"ID": int,
            "Username": str,
            "Timeout": int,
            "PID": int,
            "Type": SessionTypeEnum,
            "Agent": str}
        ]      
    }
...
}
```

While, an example of how an action will utilise the necessary keys within this data structure format can be shown below. This example shows a successful port scan and revealing an open port.

```python
{"success": True,
str(scanned_ip_address): {
	'Interface': [{'IP Address': scanned_ip_address}],
	'Processes': [{
		'Connections': [{
			'local_address': scanned_ip_address,
			'local_port': 22}]}]},
}
```
