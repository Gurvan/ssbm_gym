from .dolphin_api import DolphinAPI
from copy import deepcopy

class BaseEnv():
    def __init__(self, frame_limit = 100000, pid = 0, options = {}):
        self.api = DolphinAPI(**options)
        self.frame_limit = frame_limit
        self.pid = pid  # player id
        self.obs = None
        self.prev_obs = None
        self._action_space = None
        self._observation_space = None

    @property
    def action_space(self):
        if self._action_space is not None:
            return self._action_space
        else:
            raise NotImplementedError()

    @property
    def observation_space(self):
        if self._observation_space is not None:
            return self._observation_space
        else:
            raise NotImplementedError()

    def embed_obs(self, obs):
        raise NotImplementedError()

    def compute_reward(self):
        raise NotImplementedError()

    def is_terminal(self):
        return self.obs.frame >= self.frame_limit

    def reset(self):
        return self.embed_obs(self.api.reset())

    def step(self, action):
        if self.obs is not None:
            self.prev_obs = deepcopy(self.obs)
        
        obs = self.api.step([action])
        self.obs = obs
        reward = self.compute_reward()
        done = self.is_terminal()
        infos = dict({'frame': self.obs.frame})

        return self.embed_obs(self.obs), reward, done, infos

    def close(self):
        self.api.close()


class SSBMEnv(BaseEnv):
    def __init__(self, **kwargs):
        BaseEnv.__init__(self, **kwargs)
        from .embed import EmbedGame
        self._embed_obs = EmbedGame(flat=True)

    @property
    def action_space(self):
        if self._action_space is not None:
            return self._action_space
        else:
            from .spaces import DiagonalActionSpace
            self._action_space = DiagonalActionSpace()
            return self._action_space

    @property
    def observation_space(self):
        if self._observation_space is not None:
            return self._observation_space
        else:
            self._observation_space = str(self.embed_obs)
            return self._embed_obs

    def embed_obs(self, obs):
        return self._embed_obs(obs)

    def compute_reward(self):
        r = 0.0
        if self.prev_obs is not None:
            # This is necesarry because the character might be dying during multiple frames
            if not isDying(self.prev_obs.players[self.pid]) and \
               isDying(self.obs.players[self.pid]):
                r -= 1.0
            
            # We give a reward of -0.01 for every percent taken. The max() ensures that not reward is given when a character dies
            r -= 0.01 * max(0, self.obs.players[self.pid].percent - self.prev_obs.players[self.pid].percent)

            # Here we reverse the pid list to access the opponent state
            if not isDying(self.prev_obs.players[1-self.pid]) and \
                isDying(self.obs.players[1-self.pid]):
                r += 1.0

            r += 0.01 * max(0, self.obs.players[self.pid].percent - self.prev_obs.players[self.pid].percent) 

        return r


def isDying(player):
    # see https://docs.google.com/spreadsheets/d/1JX2w-r2fuvWuNgGb6D3Cs4wHQKLFegZe2jhbBuIhCG8/edit#gid=13
    return player.action_state <= 0xA


# Custom reward
#r += self.obs.players[self.pid].y / 100.0 / 60.0