import random
import time

import ctf


game = ctf.Ctf()
game.new_game()

fps = 30

while not game.winner:
    for unit in game.need_to_move:
        started = time.time()

        game.render()

        legal_moves = game.legal_moves()
        game.move(unit=unit, direction=random.choice(legal_moves[unit]))

        finished = time.time()
        sleeptime = 1.0/fps - (finished - started)
        if sleeptime > 0:
            time.sleep(sleeptime)

    print(game.board)

print(game.score)
print(game.winner)
