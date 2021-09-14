
![Banner](/images/bannernologo.PNG)

Recent advances in artificial intelligence \(AI\) technologies show promise for autonomous cyber operations \(ACO\), offering the potential for distributed, adaptive defensive measures at machine speed and scale\. The cyber domain is a particularly challenging domain for autonomous AI\. We nominate a challenge in this space which we believe requires further research in order to enable ACO to become an operational capability\. To facilitate this AI research, we are releasing CybORG, an experimental platform using the OpenAI Gym interface together with a cyber security scenario and a challenge to which we invite researchers to respond\. 

Our aim is to support the development of AI tactics, techniques and procedures with CybORG and a series of CAGE scenarios with associated challenge problems in order to support practical demonstrations of ACO\. We wish to engage the AI and cyber security research communities, especially to leverage domain experts outside of the cyber field, and by encapsulating the cyber elements in environments such as CybORG along with the CAGE scenarios and challenge problems, we hope that the cyber problem set becomes accessible to a wider audience\. The first CAGE scenario and associated challenge problem were released at the IJCAI\-21 1st International Workshop on Adaptive Cyber Defense \(ACD 2021\)\.

Our focus, which is rare in this area, is on the development of defensive cyber agents\. Rather than focusing on the detection of an attacker based on data, CybORG aims to develop the higher\-level strategies required to effectively respond to an attacker across an entire network\. Therefore, the defensive agents in CybORG select from a set of high\-level actions including the analysis of hosts, removal of malicious code and restoring of systems from backup\. In an extension to be released within the next two months, the defensive agents will also be able to employ deception on hosts, through the creation of decoy services\. Each action has costs, in terms of effort and system downtime, that must be balanced against the need to protect systems of differing importance from an attack\. For the purposes of the challenge, some red agents are provided for the defensive agents to train and be tested against\. 

# Scenario narrative

“There is an ongoing rivalry between neighbouring nations Guilder and Florin\. During a period of increasing tension between the two nations, Florin is receiving a significant increase of phishing attacks\. These attacks seem to be specifically targeted at factories manufacturing equipment for the Florin military\.

Cyber Threat Intelligence analysts have studied the attacks and believe that the attackers, potentially at the direction of Guilder, are attempting to disrupt the manufacture of a new weapon under development by Florin\. When the phishing attacks are successful, the attackers then use lateral movement to explore the network\. The ultimate goal of these attackers appears to be to compromise key operational systems that control aspects of the weapon system’s manufacturing\. This would cause delays in the delivery of the new weapon to the Florin military\.

Your firm has been contracted by Florin to trial your new autonomous defence agents\. Florin have given your agent authority to defend the computer network at one of their manufacturing plants\. The network, shown in Figure 1, contains a user network for staff, an enterprise network, and an operational network which contains the key manufacturing and logistics servers\. The defence agent receives an alert feed from Florin’s existing monitoring systems\. It can run detailed analyses on hosts, then remove malicious software if found\. If an attacker is too well established on a host to be removed, the host can be restored from a clean backup\. 

The network owner has undertaken an evaluation of the factory systems and contracted your firm to defend these systems according to the following criteria:

1. Maintain the critical operational server, so as to ensure information about the new weapon system is not revealed to Guilder and the production and delivery of the new weapon system remains on schedule\. 
2. Where possible, maintain enterprise servers so as to ensure day\-to\-day operations of the manufacturing plant are not disrupted or revealed\.”

# Challenge problem details

This challenge is designed for teams to create a blue agent to defend a network against a red agent, with a green agent representing the effect of network users\. The network is illustrated below\. It is divided into three subnets\. Subnet 1 consists of user hosts that are not critical\. Subnet 2 consists of enterprise servers designed to support the user activities on Subnet 1\. Subnet 3 contains the critical operational server and three user hosts\.

![Figure1](/images/figure1.png)

Each scenario run is a fixed number of steps representing a fixed period of time\. An episode will terminate only once the time expires\. At each step, the red and blue agents each choose one action from a set of high\-level actions that are described in Appendix A\. CybORG will take the chosen action and select a context\-appropriate low\-level action, such as modelling the behaviour of an operating system\-specific exploit in response to a high\-level exploit action by the red agent\. This is designed to reduce the action space and make a wider range of learning approaches tractable\.

The red agent starts each scenario run with an initial foothold: access to one of the user machines in Subnet 1\. The red agent can then choose actions to perform reconnaissance on hosts in the enterprise network \(Subnet 2\) and then exploit these hosts and perform privilege escalation\. Once they have exploited the server in the enterprise network that has the Operational Server IP address on it, they can access the operational network \(Subnet 3\)\. The Operational Server maintains a service that is key to the system owners’ operations; the goal of the red agent is to disrupt this service for as long as possible through the Impact action\.

In order to create a more robust blue agent, two red agents have been implemented, each with its own unique strategy\. The first has prior knowledge of the network layout and beelines straight to the Operational Server\. Another explores the network one subnet at a time, seeking to gain privileged access on all hosts in a subnet before moving on to the next one, eventually arriving at the Operational Server\.

The blue agent is assumed to start each scenario run with monitoring tools installed on all the user and server hosts\. It automatically receives data on new events that occur on these hosts\. It can use actions to perform more detailed analysis of hosts, giving it improved knowledge as to whether particular activity on a system is due to malicious activities of the red agent or benign activities of a green agent\. It can remove red access to hosts, or restore a system back to a standard configuration\. Removing red access only works if the red agent has not escalated their privilege on the system, as at this point it is assumed the red agent has sufficient access and persistence to recover from deleted processes or files\. Restoring a system is guaranteed to remove red agent activity, but restoring a system from a previously\-generated image is assumed to disrupt user activities on that system\. The red agent cannot be removed from the initial foothold system, even by the restore action – this assumption is made both as a means of ensuring the game lasts for the entire period, and to reflect the difficulty of eliminating a threat that has successfully phished credentials\. 

The effect of each action on the state of a targeted host is summarised in Figure 1\. 

![Figure2](/images/figure2.png)

Figure 1 Effect of actions on host state \(initial version\)

The green agent only performs the discovery action, and does not exploit hosts\. It should prevent the blue agent from assuming all network activity is due to the red agent\.

Every time the blue agent takes a step, the green agent will firstly choose and enact an action, followed by the red agent, before the blue agent’s action is finally enacted\. The blue agent then receives an observation and reward based on the events which occurred during this entire process\. 

The blue agent receives a negative reward any time the red agent gets administrator access to a system\. They continue to receive negative rewards as long as the red agent maintains administrator access\. The amount of each reward is dependent on the relative importance of that host to the confidentiality or availability of the entire system: -0\.1 and -1\.0 for low and high importance systems respectively\. They also receive a negative reward if the red agent successfully uses the Impact action on the operational server \(\-10\) or the blue agent uses the restore action \(\-1\)\. The final score for a blue agent is the cumulative reward received by the agent over the course of the scenario run\.

![Table](/images/table1.PNG)

# Challenge Extension

As an extension of the first challenge, we will later release an additional action for blue agents: Misinform\. This action will allow the blue agent to set up decoy services, intended to raise an alarm when the red agent accesses them\. The effect of each action on the state in the second release is summarised in Figure 2\. 

![Figure3](/images/figure3.png)

Figure 2 Effect of actions on host state \(extended version\)

# Instructions for obtaining environment

The CAGE challenge environment, CybORG, and first challenge are available here: [https://github\.com/cage\-challenge/cage\-challenge\-1/tree/main/CybORG](https://github.com/cage-challenge/cage-challenge-1/tree/main/CybORG)

The CAGE challenge is written in Python\. Dependencies can be installed using pip\. Further instructions are included on the GitHub page\. The challenge includes red agents to test against, and an example blue agent\. Submissions should implement the same methods of the example blue agent\.

# Instructions for submitting responses

Successful blue agents and any queries re the challenge can be submitted via email to: cage\.aco\.challenge@gmail\.com

When submitting a blue agent, teams should include:

- A team name and contact details\.
- The code implementing the agent, with a list of dependencies\.
- A description of your approach in developing a blue agent\.
- The files and terminal output of the evaluation function\.

 

We intend to publish the final results at the AAAI\-22 Workshop on Artificial Intelligence for Cyber Security \(AICS\)\. 

We also invite teams to submit full papers on their work on this CAGE challenge or using the CybORG environment to AAAI\-22, IJCAI\-22, or any other venue of their choice\. Please cite the challenge announcement as follows to reference the challenge:

```
@PROCEEDINGS{cage_challenge_announcement,
  author = {CAGE},
  Title = {CAGE Challenge 1},
  booktitle = {IJCAI-21 1st International Workshop on Adaptive Cyber Defense.} 
  Publisher = {arXiv},
  Year = {2021}
}
```

In addition, authors may reference the following paper that describes CybORG:

```
@PROCEEDINGS{cyborg_acd_2021,
  author = {Maxwell Standen, Martin Lucas, David Bowman, Toby J\. Richer, Junae Kim and Damian Marriott},
  Title = {CybORG: A Gym for the Development of Autonomous Cyber Agents},
  booktitle = {IJCAI-21 1st International Workshop on Adaptive Cyber Defense.} 
  Publisher = {arXiv},
  Year = {2021}
}
```

The challenge software can be referenced as:

```
@misc{cage_challenge_1,
  Title = {Cyber Autonomy Gym for Experimentation Challenge 1},
  Note = {Created by Maxwell Standen, David Bowman, Son Hoang, Toby Richer, Martin Lucas},
  Publisher = {GitHub},
  Howpublished = {\url{https://github.com/cage-challenge/cage-challenge-1}},
  Year = {2021},
}
```

## Evaluation of submissions

A leader board for submissions will be maintained until February 2022\. Final results will be announced at the close of the challenge via the GitHub site\.

## Important dates

20 August 2021: Challenge announced at ACD 2021 and open for submissions\.

September/October 2021: Release of an additional version of the Challenge problem with a Misinform action available to the blue agent\.

1 February 2022: Challenge closed\.

4 February 2022: Final results announced\.

# Future challenges

We will continue to develop this platform and plan to announce a new challenge problem after the close of this challenge\. Future topics may include expanded action sets, the introduction of multiple agents, and more complex and realistic scenarios\. 

![Appendix1](/images/appendix1.PNG)

![Appendix2](/images/appendix2.PNG)

[1] Open Command and Control (OpenC2): <a>https://openc2.org/</a>

[2] MITRE ATT&CK: <a>https://attack.mitre.org/</a>



