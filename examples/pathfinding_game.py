import random
import time

import numpy as np

import ctf


game = ctf.Ctf()
game.new_game()

fps = 30

while not game.winner:
    for unit in game.need_to_move:
        started = time.time()

        game.render()

        observation = game.observation
        key = observation['key']

        has_flag = key[unit]['has_flag']
        unit_position = np.array(key[unit]['position'])
        team = key[unit]['team']

        if has_flag:
            flag_position = np.array(key[team]['position'])
        else:
            if team == 1:
                flag_position = np.array(key[2]['position'])
            elif team == 2:
                flag_position = np.array(key[1]['position'])

        dist = unit_position - flag_position

        if abs(dist[0]) >= abs(dist[1]):
            if dist[0] >= 0:
                move = 'N'
            else:
                move = 'S'
        else:
            if dist[1] >= 0:
                move = 'W'
            else:
                move = 'E'

        legal_moves = game.legal_moves()
        if move in legal_moves[unit]:
            game.move(unit=unit, direction=move)
        else:
            game.move(unit=unit, direction=random.choice(legal_moves[unit]))

        finished = time.time()
        sleeptime = 1.0/fps - (finished - started)
        if sleeptime > 0:
            time.sleep(sleeptime)

    print(game.board)

print(game.score)
print(game.winner)
