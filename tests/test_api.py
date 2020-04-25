import random

import numpy as np
import pytest

import ctf


def test_init():
    game = ctf.Ctf()


def test_board_immutability():
    game = ctf.Ctf()
    game.new_game()
    b = game.board
    b[(0, 0)] = 16

    assert game.board[(0, 0)] != 16


def test_errors():
    game = ctf.Ctf()

    with pytest.raises(ctf.error.GameNotFoundError):
        game.legal_moves()
    with pytest.raises(ctf.error.GameNotFoundError):
        game.move(unit=3, direction='N')
    with pytest.raises(ctf.error.GameNotFoundError):
        game.render()

    game.new_game()

    if 3 in game.need_to_move:
        active = 3
        inactive = 6
    else:
        active = 6
        inactive = 3

    with pytest.raises(ctf.error.OutOfTurnError):
        game.move(inactive, 'N')

    game._capture(game._key[inactive], game._key[active])

    with pytest.raises(ctf.error.IllegalMoveError):
        game.move(active, 'N')


def test_game_log():
    game = ctf.Ctf()
    game.new_game()

    unit = game.need_to_move[0]
    direction = random.choice(game.legal_moves()[unit])

    game.move(unit=unit, direction=direction)

    logs = game.log

    assert logs[0]['unit'] == unit
    assert logs[0]['direction'] == direction


def test_moved_units():
    game = ctf.Ctf()
    game.new_game()

    unit = game.need_to_move[0]
    direction = random.choice(game.legal_moves()[unit])

    assert not game.moved_units[unit]

    game.move(unit=unit, direction=direction)

    assert game.moved_units[unit]


def test_key_board_sync():
    game = ctf.Ctf()
    game.new_game()

    for _ in range(10):
        for unit in game.need_to_move:
            legal_moves = game.legal_moves()
            game.move(unit=unit, direction=random.choice(legal_moves[unit]))

            pos = game.key[unit]['position']

            assert game.board[pos] == unit


def test_all_moves():
    game = ctf.Ctf()
    game.new_game()

    moves_left = ['N', 'E', 'S', 'W']

    while len(moves_left) > 0:
        for unit in game.need_to_move:
            legal_moves = game.legal_moves()
            if len(moves_left) > 0:
                if moves_left[0] in legal_moves[unit]:
                    game.move(unit, moves_left[0])
                    moves_left.remove(moves_left[0])
                else:
                    game.move(unit, random.choice(legal_moves[unit]))
            else:
                game.move(unit, random.choice(legal_moves[unit]))


def test_jail():
    game = ctf.Ctf(max_score=10)
    game.new_game()

    special_unit = game.need_to_move[0]
    if special_unit <= 5:
        capturer = 6
    else:
        capturer = 5

    game._capture(game._key[capturer], game._key[special_unit])

    obs = game.observation

    assert game.key[special_unit]['in_jail']

    legal_moves = game.legal_moves()

    assert legal_moves[special_unit] == ['PASS']

    game.move(special_unit, 'PASS')

    for _ in range(5):
        for unit in game.need_to_move:
            legal_moves = game.legal_moves()
            game.move(unit=unit, direction=random.choice(legal_moves[unit]))

    assert not game.key[special_unit]['in_jail']


def test_observation():
    game = ctf.Ctf()
    game.new_game()

    obs = game.observation

    assert np.array_equal(obs['board'], game.board)
    assert obs['key'] == game.key
    assert obs['log'] == game.log
    assert obs['moved_units'] == game.moved_units
    assert obs['turn'] == game.turn
    assert obs['winner'] == game.winner
