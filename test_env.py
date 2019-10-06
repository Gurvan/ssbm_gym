from ssbm_gym import SSBMEnv
import atexit
import platform
import random
import time

options = dict(
    render=True,
    player1='ai',
    player2='cpu',
    char1='fox',
    char2='falco',
    cpu2=7,
    stage='battlefield',
)

if platform.system() == 'Windows':
    options['windows'] = True


env = SSBMEnv(options=options)
obs = env.reset()
atexit.register(env.close)

t = time.time()
for i in range(1000):
    action = random.randint(0, env.action_space.n - 1)
    obs, reward, done, infos = env.step(action)
    try:
        print("FPS:", round(1/(time.time() - t)), "\tPlayer 1 action state: ", env.obs.players[0].action_state, "\tPlayer 2 actions_state:", env.obs.players[1].action_state)
    except:
        pass
    t = time.time()
