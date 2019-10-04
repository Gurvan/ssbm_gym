from ssbm_gym import SSBMEnv

options = dict(
    # iso="/home/gurvan/ISOs/Super Smash Bros. Melee (USA) (En,Ja) (v1.02).iso",
    # exe="dolphin-emu-nogui",
    # zmq=1,
    gfx='OGL',  # gfx='Null' to start Dolphin headless
    # speed=1,
    # speedhack=True # Enable this for major speedup in emulation
    player1='ai',
    player2='cpu',
    char1='fox',
    char2='falco',
    cpu2=7,
    stage='battlefield',
)

env = SSBMEnv(options=options)

obs = env.reset()
for i in range(1000):
    action = env.action_space.sample()
    obs, reward, done, infos = env.step(action)
    print("Player 1 action state: ", env.obs.players[0].action_state, "\t\tPlayer 2 actions_state:", env.obs.players[1].action_state)

env.close()

