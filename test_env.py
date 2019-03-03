import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('../')

from ssbm_env import SSBMEnv
import time
import argparse

parser = argparse.ArgumentParser()
SSBMEnv.update_parser(parser)

args = parser.parse_args()

env = SSBMEnv(**args.__dict__)
#cpu1=9, cpu2=9

while 1:
    env.step(None)

#env.close()

