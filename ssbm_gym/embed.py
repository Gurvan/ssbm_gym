maxAction = 0x017E
numActions = 1 + maxAction

numCharacters = 32
numStages = 32
maxJumps = 8

def oneHot(x, n):
    y = n * [0.0]
    y[x] = 1.0
    return y


class EmbedPlayer():
    def __init__(self, flat=True):
        self.flat = flat

    def __repr__(self):
        s = ''
        s += 'character:\tOneHot(' + str(numCharacters) + ')\n'
        s += 'action_state:\tOneHot(' + str(numActions) + ')\n'
        s += 'state:\tList\n'
        s += '\tpercent:\tFloat\n'
        s += '\tfacing:\tFloat\n'
        s += '\tx:\tFloat\n'
        s += '\ty:\tFloat\n'
        s += '\taction_frame:\tFloat\n'
        s += '\tinvulnerable:\tBool\n'
        s += '\thitlag_frames_left:\tFloat\n'
        s += '\thitstun_frames_left:\tFloat\n'
        s += '\tshield_size:\tFloat\n'
        s += '\tin_air:\tBool\n'

        return s

    def __call__(self, player_state):
        percent = player_state.percent/100.0
        facing = player_state.facing
        x = player_state.x/10.0
        y = player_state.y/10.0
        action_state = oneHot(player_state.action_state, numActions)
        action_frame = player_state.action_frame/50.0
        character = oneHot(player_state.character, numCharacters)
        invulnerable = 1.0 if player_state.invulnerable else 0
        hitlag_frames_left = player_state.hitlag_frames_left/10.0
        hitstun_frames_left = player_state.hitstun_frames_left/10.0
        #jumps_used = float(player_state.jumps_used)
        #charging_smash = 1.0 if player_state.charging_smash else 0.0
        shield_size = player_state.shield_size/100.0
        in_air = 1.0 if player_state.in_air else 0.0

        data = {
            'character': character,
            'action_state': action_state,
            'state': [
                percent,
                facing,
                x, y,
                action_frame,
                invulnerable,
                hitlag_frames_left,
                hitstun_frames_left,
                shield_size,
                in_air
            ]
        }

        if self.flat:
            return list(data.values())
        else:
            return data


class EmbedGame():
    def __init__(self, flat=True):
        self.flat = flat
        self.embed_player = EmbedPlayer(self.flat)

    def __repr__(self):
        s = ''
        s += 'player0/player1:\tEmbedPlayer\n'
        s += str(self.embed_player).replace('\n', '\n\t')
        s += 'stage:\tOneHot(' + str(numStages) + ')\n'

        return s

    def __call__(self, game_state):
        player0 = self.embed_player(game_state.players[0])
        player1 = self.embed_player(game_state.players[1])
        stage = oneHot(game_state.stage, numStages)

        data = {
            'player0': player0,
            'player1': player1,
            'stage': stage,
        }

        if self.flat:
            return list(data.values())
        else:
            return data


"""
def embedPlayer(player_state, flat=True):
    percent = player_state.percent/100.0
    facing = player_state.facing
    x = player_state.x/10.0
    y = player_state.y/10.0
    action_state = oneHot(player_state.action_state, numActions)
    action_frame = player_state.action_frame/50.0
    character = oneHot(player_state.character, numCharacters)
    invulnerable = 1.0 if player_state.invulnerable else 0
    hitlag_frames_left = player_state.hitlag_frames_left/10.0
    hitstun_frames_left = player_state.hitstun_frames_left/10.0
    #jumps_used = float(player_state.jumps_used)
    #charging_smash = 1.0 if player_state.charging_smash else 0.0
    shield_size = player_state.shield_size/100.0
    in_air = 1.0 if player_state.in_air else 0.0

    data = {
        'character': character,
        'action_state': action_state,
        'state': [
            percent,
            facing,
            x, y,
            action_frame,
            invulnerable,
            hitlag_frames_left,
            hitstun_frames_left,
            shield_size,
            in_air
        ]
    }

    if flat:
        return list(data.values())
    else:
        return data


def embedGame(game_state, flat=True):
    player0 = embedPlayer(game_state.players[0], flat)
    player1 = embedPlayer(game_state.players[1], flat)
    stage = oneHot(game_state.stage, numStages)

    data = {
        'player0': player0,
        'player1': player1,
        'stage': stage,
    }

    if flat:
        return list(data.values())
    else:
        return data
"""