from ssbm_gym import SSBMEnv, EnvVec
import atexit
import platform
import random
import time

options = dict(
    render=False,
    player1='ai',
    player2='cpu',
    char1='fox',
    char2='falco',
    cpu2=7,
    stage='battlefield',
)

# Vectorized envs not supported on Windows
# if platform.system() == 'Windows':
#     options['windows'] = True

num_workers = 4


# Required for vectorized envs
if __name__ == "__main__":
    print("Creating envs")
    env = EnvVec(SSBMEnv, num_workers, options=options)
    print("Envs created")
    print("Resetting envs")
    obs = env.reset()
    print("Envs resetted")
    atexit.register(env.close)

    t = time.time()
    for i in range(1000):
        action = [random.randint(0, env.action_space.n - 1) for _ in range(num_workers)]
        print("Sending actions", action)
        obs, reward, done, infos = env.step(action)
        try:
            print("FPS:", round(1/(time.time() - t)), "ActionState", [o[0][1].index(1.0) for o in obs])
        except Exception as e:
            print(e)
            pass
        t = time.time()
