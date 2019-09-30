import sys
# Add the ptdraft folder path to the sys.path list
#sys.path.append('../')

from ssbm_gym import SSBMEnv
import time
import argparse

parser = argparse.ArgumentParser()
SSBMEnv.update_parser(parser)

args = parser.parse_args()

args.iso = "/home/gurvan/ISOs/Super Smash Bros. Melee (USA) (En,Ja) (v1.02).iso"
args.exe = "dolphin-emu-nogui"
args.zmq = 1
args.gfx = 'OGL'
args.audio = 'No audio backend'
args.speed = 1
args.speedhack = True
args.player1 = 'ai'
args.player2 = 'cpu'
args.cpu2 = 7
args.stage = 'battlefield'


env = SSBMEnv(**args.__dict__)


obs = env.reset()

for i in range(1000):
    obs = env.step([env.action_space.sample()])
    print("Player 1 action state: ", obs.players[0].action_state, "\t\tPlayer 2 actions_state:", obs.players[1].action_state)

env.close()

