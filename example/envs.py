from ssbm_gym.ssbm_env import BaseEnv, isDying
from copy import deepcopy


class GoHighEnv(BaseEnv):
    def __init__(self, **kwargs):
        BaseEnv.__init__(self, **kwargs)
        self._embed_obs = MinimalEmbedGame()

    @property
    def action_space(self):
        if self._action_space is not None:
            return self._action_space
        else:
            from ssbm_gym.spaces import MinimalActionSpace
            self._action_space = MinimalActionSpace()
            return self._action_space

    @property
    def observation_space(self):
        if self._observation_space is not None:
            return self._observation_space
        else:
            self._observation_space = self._embed_obs
            return self._embed_obs

    def embed_obs(self, obs):
        return self._embed_obs(obs)

    def compute_reward(self):
        r = 0.0
        r += self.obs.players[0].y / 50 / 60  # The higher the character, the highest the reward!
        
        if self.prev_obs is not None:
            # This is necesarry because the character might be dying during multiple frames
            if not isDying(self.prev_obs.players[self.pid]) and \
               isDying(self.obs.players[self.pid]):
                r -= 1.0  # We still don't want it to die though.

        return r



class MinimalEmbedPlayer():
    def __init__(self):
        self.n = 3

    def __call__(self, player_state):
        x = player_state.x/10.0
        y = player_state.y/10.0
        in_air = 1.0 if player_state.in_air else 0.0

        return [
                x, y,
                in_air
            ]


class MinimalEmbedGame():
    def __init__(self):
        self.embed_player = MinimalEmbedPlayer()
        self.n = self.embed_player.n

    def __call__(self, game_state):
        player0 = self.embed_player(game_state.players[0])
        return player0

