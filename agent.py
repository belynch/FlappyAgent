import argparse
import logging
import sys
import numpy as np

import gym
from gym import wrappers

import gym_ple

class State():
    def __init__(self, i, j):
        self.qValueFall = 0.0
        self.qValueJump = 0.0
        self.i = i
        self.j = j
    def getQValueFall():
        return self.qValueFall

    def getQValueJump():
        return self.qValueJump

    def setQValueFall(val):
        self.qValueFall = val

    def setQValueJump(val):
        self.qValueJump = val


# The world's simplest agent!
class RandomAgent(object):
    def __init__(self, action_space):
        self.action_space = action_space
        self.lastAction = 0
        self.lastState = None
        self.moves = []
        self.qValues = None
        self.r = {0: 1, 1: -1000} # Reward
        self.lr = 0.7
        self.discount = 1.0

    def act(self, observation, reward, done):
       # Player y at index 7
       playerY = observation['player_y']

       # Next pipe bottom y
       nextPipeBottomY = observation['next_pipe_bottom_y']

       # vertical difference between player and bottom pipe
       vDiff = int(abs(playerY - nextPipeBottomY))

       # horizontal distance from next pipe
       hDiff = int(observation['next_pipe_dist_to_player'])

       # Get current state
       state = self.qValues[vDiff][hDiff]

       # Store last action/state and current state
       self.moves.append([self.lastAction, self.lastState, state])
       self.lastState = state

       if (state.qValueJump > state.qValueFall):
        self.lastAction = 0
        return 0
       else:
        self.lastAction = 1
        return 1

    def updateQValues(self):
        #Update Q Values from stored history
        previousMoves = list(reversed(self.moves))


        # q learning
        t = 1
        for move in previousMoves:
            action = move[0]
            prevState = move[1]
            state = move[2]

        # TODO:
        if t==1 or t==2:
            if (action == 0):
                qvalues[prevState.i][prevState.j].qValueJump
            else:
                qvalues[prevState.i][prevState.j].qValueFall

            self.qvalues[prevState.i][prevState.j] = (1- self.lr) * (self.qvalues[prevState.i][prevState.j]) + (self.lr) * ( self.r[1] + (self.discount)*max(self.qvalues[state]) )



if __name__ == '__main__':
    # You can set the level to logging.DEBUG or logging.WARN if you
    # want to change the amount of output.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    
    env = gym.make('FlappyBird-v0' if len(sys.argv)<2 else sys.arinit_arrygv[1])

    # You provide the directory to write to (can be an existing
    # directory, including one with existing data -- all monitor files
    # will be namespaced). You can also dump to a tempdir if you'd
    # like: tempfile.mkdtemp().
    outdir = '/tmp/random-agent-results'
    env = wrappers.Monitor(env, directory=outdir, force=True)
    env.seed(0)
    agent = RandomAgent(env.action_space)
    #agent.qValues = [[State() for j in range(500)] for i in range(500)]
    agent.qValues = [[State(i,j) for j in range(500)] for i in range(500)]

    episode_count = 100
    max_steps = 200
    reward = 0
    done = False

    for i in range(episode_count):
        ob = env.reset()
        # print(ob)
        for j in range(max_steps):
            env.render()
            action = agent.act(ob, reward, done)
            ob, reward, done, _ = env.step(action)
            # print(env.action_space.__repr__())
            if done:
                break
            # Note there's no env.render() here. But the environment still can open window and
            # render if asked by env.monitor: it calls env.render('rgb_array') to record video.
            # Video is not recorded every episode, see capped_cubic_video_schedule for details.

    # Close the env and write monitor result info to disk
    env.close()

    # Upload to the scoreboard. We could also do this from another
    # process if we wanted.
    logger.info("Successfully ran RandomAgent. Now trying to upload results to the scoreboard. If it breaks, you can always just try re-uploading the same results.")
    #gym.scoreboard.api_key = "sk_3qlTNVYeSq5H6cCDbF6Q"
    #gym.upload(outdir)
