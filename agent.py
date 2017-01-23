import argparse
import logging
import sys
import json
import io
import numpy as np

import gym
from gym import wrappers

import gym_ple

class State():
    def __init__(self, i, j):
        self.qValueFall = 0.0
        self.qValueJump = 0.0
        self.i = i+500
        self.j = j
    def getQValueFall():
        return self.qValueFall

    def getQValueJump():
        return self.qValueJump

    def setQValueFall(val):
        self.qValueFall = val

    def setQValueJump(val):
        self.qValueJump = val

    def dump(self):
        return {

            'vDiff': self.i,
            'hDiff': self.j,
            'qFall': self.qValueFall,
            'qJump': self.qValueJump

                               }


# The world's simplest agent!
class RandomAgent(object):
    def __init__(self, action_space):
        self.action_space = action_space
        self.lastAction = 0
        self.lastState = State(0,0)
        self.moves = []
        self.qValues = None
        self.r = {0: 200, 1: -1000, 2: 1} # Reward
        self.lr = 0.7 # learning rate
        self.discount = 1.0
        self.playerY = 0

    def act(self, observation, reward, done, isLearning):

       # Player y at index 7
       playerY = observation['player_y']
       self.playerY = playerY

       #if reward > 0 or reward == -5:
       self.updateQValues(reward)

       if reward > 0:
        print "SUCCESS b"

       # Next pipe bottom y
       nextPipeBottomY = observation['next_pipe_bottom_y']

       # vertical difference between player and bottom pipe
       vDiff = int(round(int(playerY - nextPipeBottomY),-1)+500)/10

       # horizontal distance from next pipe
       hDiff = int(round(int(observation['next_pipe_dist_to_player']),-1))/10

       # Get current state
       state = self.qValues[vDiff][hDiff]

       # Store last action/state and current state
       self.moves.append([self.lastAction, self.lastState, state])
       self.lastState = state

       if (state.qValueJump > state.qValueFall):
        self.lastAction = 0
        print "JUMP"
        return 0
       elif (state.qValueJump < state.qValueFall):
        self.lastAction = 1
        print "FALL"
        return 1
       else:
        randAct = self.action_space.sample()
        self.lastAction = randAct
        return randAct

    def updateQValues(self, rewardValue):
        #Update Q Values from stored history
        previousMoves = list(reversed(self.moves))


        # q learning
        t = 1
        for move in previousMoves:
            action = move[0]
            prevState = move[1]
            state = move[2]


            #Flag if the bird died in the top pipe
            high_death_flag = True if self.playerY < 0 else False
            #if high_death_flag:
                # print "HIGH DEATH"


            if (action == 0):
                self.qValues[prevState.i][prevState.j].qValueJump = (self.qValues[prevState.i][prevState.j].qValueJump) + ((self.lr) * ( rewardValue + (self.discount) * max(self.qValues[state.i][state.j].qValueFall,self.qValues[state.i][state.j].qValueJump) - self.qValues[prevState.i][prevState.j].qValueJump))
            else:
                self.qValues[prevState.i][prevState.j].qValueFall = (self.qValues[prevState.i][prevState.j].qValueFall) + ((self.lr) * ( rewardValue + (self.discount) * max(self.qValues[state.i][state.j].qValueFall,self.qValues[state.i][state.j].qValueJump) - self.qValues[prevState.i][prevState.j].qValueFall))


        #for row in self.qValues:
         #   for cell in row:
          #      if(cell.qValueFall != 0.0 or cell.qValueJump != 0.0):
                    #print str(cell.i) + ",,,,," + str(cell.j)
                    #print "[ Fall: "+str(cell.qValueFall)+", Jump: "+str(cell.qValueJump)+"]"       




if __name__ == '__main__':
    # You can set the level to logging.DEBUG or logging.WARN if you
    # want to change the amount of output.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


    
    env = gym.make('FlappyBird-v0' if len(sys.argv)<2 else sys.arinit_arrygv[1])

    with open('data.json') as data_file:    
        data = json.load(data_file)

    print data[15]


    # You provide the directory to write to (can be an existing
    # directory, including one with existing data -- all monitor files
    # will be namespaced). You can also dump to a tempdir if you'd
    # like: tempfile.mkdtemp().
    outdir = '/tmp/random-agent-results'
    env = wrappers.Monitor(env, directory=outdir, force=True)
    env.seed(0)
    agent = RandomAgent(env.action_space)
    #agent.qValues = [[State() for j in range(500)] for i in range(500)]
    agent.qValues = [[State(int(round(i))/10,int(round(j))/10) for j in range(500)] for i in range(1000)]

    # learning_iterations_count = 100
    episode_count = 10000
    max_steps = 200
    reward = 0
    done = False

    for i in range(episode_count):
        successCount = 0
        if(i%250==0):
            print i
        ob = env.reset()
        # print(ob)
        for j in range(max_steps):
            if i == episode_count-1:
                env.render()
            action = agent.act(ob, reward, done, False)
            if(reward > 0):
                #env.render()
                successCount = successCount+1
                #print "success #" + str(successCount)
            ob, reward, done, _ = env.step(action)
            # print(env.action_space.__repr__())
            if done:
                break
            # Note there's no env.render() here. But the environment still can open window and
            # render if asked by env.monitor: it calls env.render('rgb_array') to record video.
            # Video is not recorded every episode, see capped_cubic_video_schedule for details.

    # Close the env and write monitor result info to disk
    env.close()



    #ob = State(0,0)
    #json_string=""
    #for row in agent.qValues:
     # for cell in row:
      #  if cell.vDiff%10==0 && cell.hDiff%10==0
           # json_string += str(cell.dump()) + ","


    #with open('data.json', 'w') as outfile:
    #    json.dump(json_string, outfile)

    # Upload to the scoreboard. We could also do this from another
    # process if we wanted.
    logger.info("Successfully ran RandomAgent. Now trying to upload results to the scoreboard. If it breaks, you can always just try re-uploading the same results.")
    gym.scoreboard.api_key = "sk_3qlTNVYeSq5H6cCDbF6Q"
    gym.upload(outdir)
