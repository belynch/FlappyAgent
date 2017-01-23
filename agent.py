import argparse
import logging
import sys
import math
import numpy as np
import matplotlib
matplotlib.use("TkAgg")

from matplotlib import pyplot as plt

import gym
from gym import wrappers

import gym_ple

class FlappyAgent(object):

    def __init__(self, action_space):

    	#action space is {0,1} - flap / fall
        self.action_space = action_space
        #keep track of the current and past state information
        self.lastState = '0_0'
        self.lastAction = 0
        self.currentState = '0_0'
        #dictionary of q values
        self.qValues = {self.lastState:[0.0,0.0]} #initalise with last state
        #q learning variables
        self.lr = 0.7 # learning rate
        self.discount = 1.0
        self.currentPoints = 0

    def roundup(self,x):
    	return int(math.ceil(x / 10.0)) * 10

    def act(self, observation, reward, done):
		#reward space is {-5,0,1} - death / alive / travel through pipe
		if(reward == 1):
			self.currentPoints += 1

		playerY = observation['player_y']
		nextPipeBottomY = observation['next_pipe_bottom_y']
		#both of the below values are rounded to the nearest 10 to reduce the state space
		# vertical difference between player and bottom pipe
		vDiff = self.roundup(playerY - nextPipeBottomY)
		# horizontal distance from next pipe
		hDiff = self.roundup(observation['next_pipe_dist_to_player'])
		# Get current state
		self.lastState = self.currentState
		# Store last action/state and current state
		self.currentState = str(hDiff) + '_' + str(vDiff)

		#update the q values of the last state-action
		self.updateQValues(reward)

		#if the q value for a given state and a fly action is greater than the q value of the same
		#state and a down action, select the fly action
		if (self.qValues[self.currentState][0] > self.qValues[self.currentState][1]):
			self.lastAction = 0
			return 0
		#opposite if the above condition
		elif (self.qValues[self.currentState][0] < self.qValues[self.currentState][1]):
			self.lastAction = 1
			return 1
		#if there's is a tie, take a random action
		else:
			randAct = self.action_space.sample()
			self.lastAction = randAct
			return randAct

    def updateQValues(self, rewardValue):
        #Update Q Values for the last state-action pair
        # q learning 
       
        lastAction = self.lastAction
        prevState = self.lastState
        currentState = self.currentState

        #print ('last state: ' + prevState + ' current state: ' + currentState)
        #Q(S,A) = Q(S,A) + lr * ( R + dis + max(Q(S',A)) - Q(S,A) )
        self.qValues[prevState][lastAction] = self.qValues[prevState][lastAction] + (self.lr * ( rewardValue + self.discount * max(self.qValues[currentState]) - self.qValues[prevState][lastAction]) )

    #intialise q-values to 0
    def initialiseQValues(self):
    	#the horizontal distance (x) is bounded from 0 to 300
    	#the vertical distance (y) is bounded from -500 to 500
    	#in order to reduce the state space, the distances are rounded tp the nearest
    	#ten (i.e a horizontal distance of 116 gets rounded to 120)
    	for x in range(0,300,10):
	    	for y in range(-500,500,10):
	        	self.qValues[str(x)+'_'+str(y)] = [0,0]


if __name__ == '__main__':
	#variables for plotting
	score = []
	# You can set the level to logging.DEBUG or logging.WARN if you
	# want to change the amount of output.
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	env = gym.make('FlappyBird-v0' if len(sys.argv)<2 else sys.arinit_arrygv[1])

	outdir = '/tmp/random-agent-results'
	#uncomment below to upload to openAI gym
	#env = wrappers.Monitor(env, directory=outdir, force=True)
	env.seed(0)
	agent = FlappyAgent(env.action_space)

	agent.initialiseQValues()

	episode_count = 5000
	max_steps = 400
	reward = 0
	done = False

	for i in range(episode_count):

		#let us know when 250 episodes have completed
		if i%250 == 0:
			print str(i)
		ob = env.reset()

		for j in range(max_steps):
			if i == episode_count-1:
			    env.render()
			action = agent.act(ob, reward, done)
			ob, reward, done, _ = env.step(action)
			if done:
			    break

		score.append(agent.currentPoints)
		#reset the score for the next episode
		agent.currentPoints = 0

	# Close the env and write monitor result info to disk
	env.close()

	logger.info("Successfully ran RandomAgent. Now trying to upload results to the scoreboard. If it breaks, you can always just try re-uploading the same results.")

	# uncomment to upload openAi Gym
	# gym.scoreboard.api_key = "sk_3qlTNVYeSq5H6cCDbF6Q"
	# gym.upload(outdir)

	#plot the score vs episode
	plt.plot(score, 'ro')
	plt.axis([0, episode_count, 0, 5])
	plt.xlabel('Episode Number')
	plt.ylabel('Score')
	plt.show()
