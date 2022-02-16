# Wrappers

- [Wrappers](#wrappers)
  - [What are wrappers?](#what-are-wrappers)
  - [BaseWrapper](#basewrapper)
  - [BlueTableWrapper](#bluetablewrapper)
  - [ChallengeWrapper](#challengewrapper)
  - [EnumActionWrapper](#enumactionwrapper)
  - [FixedFlatWrapper](#fixedflatwrapper)
  - [IntListToAction](#intlisttoaction)
  - [OpenAIGymWrapper](#openaigymwrapper)
  - [RedTableWrapper](#redtablewrapper)
  - [ReduceActionSpaceWrapper](#reduceactionspacewrapper)
  - [RewardShape](#rewardshape)
  - [TrueTableWrapper](#truetablewrapper)

## What are wrappers?

Wrappers allow us to use non-CybORG native functions to assist our AI applications.

## BaseWrapper

Base class for other wrappers.
Has the abstract methods to be implemented in the inherited classes.
Commented thoroughly for easier implementation.

## BlueTableWrapper

Allows us to look at the observations in a table format for the blue agents.

## ChallengeWrapper

The challenge wrapper is three wrappers nested together: BlueTableWrapper, EnumActionWrapper and OpenAIGymWrapper.

## EnumActionWrapper

EnumActionWrapper calculates all the possible actions and returns the action space as the number of such actions.

## FixedFlatWrapper

The FlatFixedWrapper parses the internal state of CybORG and turns it into a list of floats, which can easily be converted into a vector.

## IntListToAction

Converts list to action object.

## OpenAIGymWrapper

The OpenAIGymWrapper converts the output of FlatFixedWrapper to a numpy array as well as conforming to other parts of the OpenAI Gym API. It requires FlatFixedWrapper and EnumActionWrapper in order to function and should always be the outermost of the provided wrappers. You must also specify an agent parameter and explitly specify the environment parameter.

## RedTableWrapper

Same as BlueTableWrapper but for red agent.

## ReduceActionSpaceWrapper

Remove some actions based on whether they are found in action signature or not.

## RewardShape

Adjust reward according to action and observation buffers.

## TrueTableWrapper

TrueTableWrapper modifies the get_agent_state method to return the true state in the form of the table.