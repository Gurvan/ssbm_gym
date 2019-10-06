"""
This is an example of environment definition and execution of the program.
Look inide envs.py to see how to create your own environment.
You can find how to create an action space inside ssbm_gym/spaces.py (MinimalActionSpace).
In this code player2 is set as "human", so you can play with the bot if you have a gamecube adapter and a controller in port 2.
"""
from envs import GoHighEnv
import atexit
import platform
import random
import time

options = dict(
    render=True,
    player1='ai',
    player2='human',
    char1='peach',
    char2='falcon',
    stage='battlefield',
)
if platform.system() == 'Windows':
    options['windows'] = True


env = GoHighEnv(frame_limit=3600, options=options)
obs = env.reset()
atexit.register(env.close)

r = 0
while True:
    action = random.randint(0, env.action_space.n - 1)
    obs, reward, done, infos = env.step(action)
    r += reward
    if env.obs.frame % 60:
        print("Reward per second:", round(r, 4))
        r = 0
    if done:
        break
    