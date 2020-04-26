import random

import numpy as np
import pytest

import ctf
from ctf import io


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


def test_score():
    game = ctf.Ctf()
    game.new_game()

    score = game.score

    assert score[1] == 0
    assert score[2] == 0

    game._score[1] = 1

    assert game.winner == 1


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


def test_all_directions():
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


def test_trapped():
    game = ctf.Ctf(num_units=3)
    game.new_game()

    unit_pos = {i:game._key[i].position for i in range(3, 9)}
    for k, v in unit_pos.items():
        game._board[v] = 0

        new_pos = None
        if k == 6:
            new_pos = (0, 0)
        elif k == 7:
            new_pos = (1, 0)
        elif k == 8:
            new_pos = (0, 1)

        if new_pos:
            game._board[new_pos] = k
            game._key[k].position = new_pos
            unit_pos[k] = new_pos

    assert game._legal_moves(unit=6) == ['PASS']

    for k, v in unit_pos.items():
        game._board[v] = 0

        new_pos = None
        if k == 6:
            new_pos = (game._board.shape[0] - 1, game._board.shape[1] - 1)
        elif k == 7:
            new_pos = (game._board.shape[0] - 2, game._board.shape[1] - 1)
        elif k == 8:
            new_pos = (game._board.shape[0] - 1, game._board.shape[1] - 2)

        if new_pos:
            game._board[new_pos] = k
            game._key[k].position = new_pos
            unit_pos[k] = new_pos

    assert game._legal_moves(unit=6) == ['PASS']

    unit_6_pos = game._key[6].position

    game._board[unit_6_pos] = 0

    flag_1_pos = game._key[1].position
    flag_2_pos = game._key[2].position

    for flag_pos in [flag_1_pos, flag_2_pos]:
        game._board[flag_pos[0] + 1, flag_pos[1]] = 6
        game._key[6].position = (flag_pos[0] + 1, flag_pos[1])

        assert 'N' not in game._legal_moves(unit=6)


@pytest.mark.parametrize(
    'anchor, unit, direction, jailed',
    [
        ((1,1), 3, 'S', 4),
        ((1,1), 4, 'N', 4),
        ((14,1), 3, 'S', 3),
        ((14,1), 4, 'N', 3)
    ]
)
def test_apply_movement(anchor, unit, direction, jailed):
    game = ctf.Ctf(num_units=1)
    game.new_game()

    unit_3_pos = game._key[3].position
    unit_4_pos = game._key[4].position

    game._board[unit_3_pos] = 0
    game._board[unit_4_pos] = 0

    game._board[anchor] = 3
    game._key[3].position = anchor

    game._board[anchor[0] + 1, anchor[1]] = 4
    game._key[4].position = (anchor[0] + 1, anchor[1])

    game._apply_movement(unit=unit, direction=direction)

    assert game._key[jailed].in_jail


def test_flag_movement():
    game = ctf.Ctf(num_units=1)
    game.new_game()

    unit_3_pos = game._key[3].position
    unit_4_pos = game._key[4].position

    game._board[unit_3_pos] = 0
    game._board[unit_4_pos] = 0

    flag_2_pos = game._key[2].position

    game._board[flag_2_pos[0] + 1, flag_2_pos[1] + 1] = 3
    game._key[3].position = (flag_2_pos[0] + 1, flag_2_pos[1] + 1)

    game._apply_movement(unit=3, direction='N')

    assert game._key[3].has_flag
    assert not game._key[2].grounded
    assert game._key[3].position == game._key[2].position

    unit_3_pos = game._key[3].position

    game._board[unit_3_pos[0] + 1, unit_3_pos[1]] = 4
    game._key[4].position = (unit_3_pos[0] + 1, unit_3_pos[1])

    game._apply_movement(unit=3, direction='N')

    game._apply_movement(unit=4, direction='N')
    game._apply_movement(unit=4, direction='N')

    assert not game._key[3].has_flag
    assert game._key[2].grounded
    assert game._key[3].position != game._key[2].position


def test_scoring():
    game = ctf.Ctf(num_units=1)
    game.new_game()

    unit_3_pos = game._key[3].position
    unit_4_pos = game._key[4].position

    game._board[unit_3_pos] = 0
    game._board[unit_4_pos] = 0

    flag_1_pos = game._key[1].position
    flag_2_pos = game._key[2].position

    game._board[flag_2_pos[0] + 1, flag_2_pos[1] + 1] = 3
    game._key[3].position = (flag_2_pos[0] + 1, flag_2_pos[1] + 1)

    game._apply_movement(unit=3, direction='N')

    assert game._key[3].has_flag
    assert not game._key[2].grounded
    assert game._key[3].position == game._key[2].position

    game._board[flag_1_pos[0] + 1, flag_1_pos[1] + 1] = 3
    game._key[3].position = (flag_1_pos[0] + 1, flag_1_pos[1] + 1)
    game._key[2].position = (flag_1_pos[0] + 1, flag_1_pos[1] + 1)

    game._apply_movement(unit=3, direction='N')

    assert not game._key[3].has_flag
    assert game._key[2].grounded
    assert game._key[3].position != game._key[2].position
    assert game.score[1] == 1

    game._board[flag_1_pos[0] + 1, flag_1_pos[1] - 1] = 4
    game._key[4].position = (flag_1_pos[0] + 1, flag_1_pos[1] - 1)

    game._apply_movement(unit=4, direction='N')

    assert game._key[4].has_flag
    assert not game._key[1].grounded
    assert game._key[4].position == game._key[1].position

    game._board[flag_2_pos[0] + 1, flag_2_pos[1] - 1] = 4
    game._key[4].position = (flag_2_pos[0] + 1, flag_2_pos[1] - 1)
    game._key[1].position = (flag_2_pos[0] + 1, flag_2_pos[1] - 1)

    game._apply_movement(unit=4, direction='N')

    assert not game._key[4].has_flag
    assert game._key[1].grounded
    assert game._key[4].position != game._key[1].position
    assert game.score[2] == 1


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


def test_io():
    io.resource_path('PressStart2P-Regular.ttf')
