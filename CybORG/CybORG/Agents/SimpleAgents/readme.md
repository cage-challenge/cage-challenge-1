# SimpleAgents

- [SimpleAgents](#simpleagents)
  - [How to implement an agent?](#how-to-implement-an-agent)
  - [B_line](#b_line)
  - [BaseAgent](#baseagent)
  - [BlueLoadAgent](#blueloadagent)
  - [BlueMonitorAgent](#bluemonitoragent)
  - [BlueReactAgent](#bluereactagent)
  - [CounterKillchainAgent](#counterkillchainagent)
  - [DebuggingAgent](#debuggingagent)
  - [GreenAgent](#greenagent)
  - [HeuristicRed](#heuristicred)
  - [KeyboardAgent](#keyboardagent)
  - [KillchainAgent](#killchainagent)
  - [Meander](#meander)
  - [SleepAgent](#sleepagent)
  - [TestAgent](#testagent)

## How to implement an agent?

The methods that have to be part of any Agent class are mentioned in the `BaseAgent` class.
Some of the parameters we can include in an agent are previous actions, target IP address, steps to be taken (Killchain), etc.
To create a new type of agent, we make sure to inherit from BaseAgent class and ensure no `NotImplementedError` is raised.
Depending on the function of the agent, we define the methods and parameters.

To use any agent, we need a scenario and a CybORG environment.

To initialize an agent named SleepAgent: `agent = SleepAgent()`

## B_line

This represents an actor who has inside information, so is able to beeline straight towards the OpServer.
This agent runs along a predetermined path to the OpServer, but is smart enough able to recover its position if interrupted.
We can see below after Blue Team restores some hosts, the agent works out where the error in and re-exploits its way to the OpServer.

## BaseAgent

This is the base class with abstract methods for all the inherited Agent classes.
This agent is commented thoroughly to make implementing new agents easy.

## BlueLoadAgent

Agent that loads a `StableBaselines3` PPO model file.
PPO is a reinforcement learning algorithm default for OpenAI.

## BlueMonitorAgent

Blue agent that monitors the changes in the environment.

## BlueReactAgent

Has two classes.

`BlueReactRemoveAgent` can monitor or remove suspicious files and processes.
It will wait until it sees suspicious activity, before using remove on all the hosts it has flagged.
However, due to the 5% change that Red's exploit is missed, Red will always eventually get to the OpServer.

`BlueReactRestoreAgent` is the same as the React agent above, but uses the Restore action.

## CounterKillchainAgent

Agent that can counter a Killchain attack.
[Info on KillChain](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)

## DebuggingAgent

Agent that can be used to debug.

## GreenAgent

An important part of CybORG `Scenario1b` is the Green agent, which represents the users on the network. The Green Agent is very simple, it only performs a scanning action on random hosts some of the time. This is only visible by Blue Agent.

## HeuristicRed

Red agent that works based on Heuristics and not the best case scenarios.

## KeyboardAgent

Agent that can be controlled with the keyboard.

## KillchainAgent

Agent that uses KillChain method.
[Info on KillChain](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)

## Meander

A red agent that follows Scenario1B.
This performs a breadth first search on all known hosts, scanning each one in turn, before attempting a mix of exploit and privilege escalate on the rest. This is an extremely slow agent in contrast to the laser-focussed `B_lineAgent`.

## SleepAgent

Agent that can only perform one function - sleep.

## TestAgent

Agent that can be used to test. It performs random actions.
