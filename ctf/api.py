"""`Ctf` state machine and game logic"""

import numpy as np

from ctf.pieces import Unit, Flag
from ctf import error


class Ctf(object):
    """`Ctf` class, handles a game of CTF.

    Typical utilization:

    >>> import ctf
    >>> game = ctf.Ctf()
    >>> game.new_game()
    >>> while game.winner is None:
    >>>     for unit in game.need_to_move:
    >>>         game.render() # If you'd like to view the game
    >>>         obs = game.observation
    >>>         action = # Decide this however you'd like
    >>>         game.move(unit, action)

    """
    def __init__(self,
                 dimensions=(16, 9),
                 num_units=3,
                 max_score=1,
                 jail_timer=5):
        """Initialization of `Ctf` object.

        Args:
            dimensions (tuple, optional): Tuple of integers
                representing board dimensions. Defaults to `(16, 9)`.
            num_units (int, optional): Number of units each
                player controls. Defaults to `3`.
            max_score (int, optional): Score the game is played to.
                Defaults to `1`.
            jail_timer (int, optional): How many turns a unit spends in
                jail. Defaults to `5`.

        """
        self._dimensions = dimensions
        self._num_units = num_units
        self._max_score = max_score
        self._jail_timer = jail_timer
        self._jail = {}
        self._renderer = None

    @property
    def board(self):
        """Board property.

        Returns a copy of the board state.

        Returns:
            board (:obj:`np.array`): Copy of board state.

        """
        return np.copy(self._board)

    @property
    def key(self):
        """Key property.

        Returns a dictionary representation of the objects and their
        respective idxs. The key is formatted as such:
            0 -> 'EMPTY'
            1 -> :obj:~`ctf.pieces.Flag` for Team 1
            2 -> :obj:~`ctf.pieces.Flag` for Team 2
            3+ -> :obj:~`ctf.pieces.Unit` Units

        Returns:
            key (dict): Dictionary representation of key.

        """
        key = {k: vars(v) for k, v in self._key.items() if v != 'EMPTY'}
        key[0] = 'EMPTY'
        return key

    @property
    def log(self):
        """Log property.

        Returns a copy of submitted actions. Logs are in the format of
        a list with dictionaries as elements. The dictionaries have
        only two key value pairs:
            {
                'unit': <Idx of unit that moved>,
                'Direction': <direction of movement>
            }

        Returns:
            log (list): Copy of submitted actions.

        """
        return list(self._game_log)

    @property
    def moved_units(self):
        """Moved Units property.

        Returns a copy of the moved units dictionary. The keys are ints
        representing units idxs, and the values are booleans
        representing whether or not the unit has moved yet.

        Returns:
            moved_units (dict): Copy moved units dictionary.

        """
        return dict(self._moved_units)

    @property
    def need_to_move(self):
        """Need To Move property.

        Returns a list of units who have yet to move this turn.

        Returns:
            need_to_move (list): List of units who have yet to move this
                turn.

        """
        return [unit for unit, moved in self._moved_units.items() if not moved]

    @property
    def observation(self):
        """Observation property.

        Returns a combination of the other properties. Observation
        contains:
            {
                'board': Board property,
                'key': Key property,
                'log': Log property,
                'moved_units': Moved Units property,
                'turn': Turn property,
                'winner': Winner property
            }

        Returns:
            observation (dict): Dictionary containing each of the other
                properties.

        """
        observation = {
            'board': self.board,
            'key': self.key,
            'log': self.log,
            'moved_units': self.moved_units,
            'turn': self.turn,
            'winner': self.winner
        }
        return observation

    @property
    def score(self):
        return dict(self._score)

    @property
    def turn(self):
        """Turn property.

        Returns an integer representing whose turn it is:
            1 -> Player 1
            2 -> Player 2

        Returns:
            turn (int): Whose turn it is.

        """
        return self._turn

    @property
    def winner(self):
        """Winner property.

        Returns a integer or `None` depending on if game is finished:
            1 -> Player 1 wins
            2 -> Player 2 wins
            `None` -> No one has won yet

        Returns:
            winner (int | `None`): Integer corresponding to player if a
                player has one, or `None` if no player has won yet.

        """
        if max(self._score.values()) >= self._max_score:
            return max(self._score, key=self._score.get)
        else:
            return False

    def _apply_movement(self, unit, direction):
        instance = self._key[unit]

        self._board[instance.position] = 0
        y, x = instance.position

        if direction == 'N':
            y -= 1
        elif direction == 'E':
            x += 1
        elif direction == 'S':
            y += 1
        elif direction == 'W':
            x -= 1

        other = self._key[self._board[(y, x)]]

        if other == 'EMPTY':
            self._move(instance, x, y)

        elif isinstance(other, Unit):
            if other.has_flag:
                self._capture(instance, other)
                self._move(instance, x, y)
            else:
                if (instance.team == 1) & (y < self._board.shape[0] // 2):
                    self._capture(instance, other)
                    self._move(instance, x, y)

                elif (instance.team == 1) & (y >= self._board.shape[0] // 2):
                    self._capture(other, instance)

                elif (instance.team == 2) & (y >= self._board.shape[0] // 2):
                    self._capture(instance, other)
                    self._move(instance, x, y)

                elif (instance.team == 2) & (y < self._board.shape[0] // 2):
                    self._capture(other, instance)

        unit_pos = np.array(instance.position)
        if instance.team == 1:
            home_flag = self._key[1]
            away_flag = self._key[2]
        elif instance.team == 2:
            home_flag = self._key[2]
            away_flag = self._key[1]

        away_flag_pos = np.array(away_flag.position)
        home_flag_pos = np.array(home_flag.position)

        if (np.linalg.norm(unit_pos - away_flag_pos) == 1) & \
           away_flag.grounded:
            instance.has_flag = True
            away_flag.grounded = False
            self._board[away_flag.position] = 0
            away_flag.position = instance.position

        if (np.linalg.norm(unit_pos - home_flag_pos) == 1) & \
           home_flag.grounded & \
           instance.has_flag:
            instance.has_flag = False
            self._place_flag(away_flag.team)
            self._score[instance.team] += 1

    def _capture(self, capturer, capturee):
        self._send_to_jail(capturee.idx)
        if capturee.has_flag:
            capturee.has_flag = False
            self._place_flag(capturer.team)

    def _legal_moves(self, unit):
        instance = self._key[unit]

        if instance.in_jail:
            return ['PASS']

        legal_moves = ['N', 'E', 'S', 'W']
        y, x = instance.position

        if (y - 1) < 0:
            legal_moves.remove('N')

        if (x + 1) >= self._board.shape[1]:
            legal_moves.remove('E')

        if (y + 1) >= self._board.shape[0]:
            legal_moves.remove('S')

        if (x - 1) < 0:
            legal_moves.remove('W')

        movement_dict = {}
        for move in legal_moves:
            if move == 'N':
                movement_dict[move] = (y - 1, x)
            elif move == 'E':
                movement_dict[move] = (y, x + 1)
            elif move == 'S':
                movement_dict[move] = (y + 1, x)
            elif move == 'W':
                movement_dict[move] = (y, x - 1)

        for direction, pos in movement_dict.items():
            if self._board[pos] != 0:
                if self._board[pos] in [1, 2]:
                    try:
                        legal_moves.remove(direction)
                    except ValueError:
                        pass
                elif isinstance(self._key[self._board[pos]], Unit):
                    other = self._key[self._board[pos]]
                    if other.team == instance.team:
                        try:
                            legal_moves.remove(direction)
                        except ValueError:
                            pass

        if len(legal_moves) > 0:
            return legal_moves
        else:
            return ['PASS']

    def _move(self, instance, x, y):
        instance.position = (y, x)
        self._board[instance.position] = instance.idx
        if instance.has_flag:
            if instance.team == 1:
                flag = self._key[2]
            elif instance.team == 2:
                flag = self._key[1]
            flag.position = instance.position

    def _place_flag(self, team):
        y, x = self._dimensions
        middle = x // 2

        if team == 1:
            self._board[1, middle] = team
            self._key[team].position = (1, middle)
        elif team == 2:
            self._board[y - 2, middle] = team
            self._key[team].position = (y - 2, middle)

        self._key[team].grounded = True

    def _send_to_jail(self, unit):
        instance = self._key[unit]

        if instance.team == 1:
            y = 0
            for x in range(self._board.shape[1]):
                if self._board[(y, x)] == 0:
                    break
        else:
            y = self._board.shape[0] - 1
            for x in reversed(range(self._board.shape[1])):
                if self._board[(y, x)] == 0:
                    break

        self._board[instance.position] = 0
        self._board[(y, x)] = unit
        instance.position = (y, x)
        instance.in_jail = True
        self._jail[unit] = self._jail_timer

    def legal_moves(self):
        """Method to get all legal moves.

        Returns a dictionary of all legal moves for all units. The keys
        are integers corresponding the the units idxs, and the values
        are lists of legal moves. This method does not filter the
        output by only units who may move this turn.

        >>> game.legal_moves()
        {3: ['N', 'E', 'S', 'W'], 4: ['PASS']} # 4 is in jail or trapped

        Returns:
            legal_moves (dict): Dictionary representing the legal moves
                for each unit given the current state.

        Raises:
            GameNotFoundError: Raised if this method is called prior to
                `new_game`.

        """
        # TODO: make a decorator to handle this check.
        if not hasattr(self, '_key'):
            raise error.GameNotFoundError(
                'Call .new_game() prior to this method.'
            )

        moves = {}
        for k, v in self._key.items():
            if isinstance(v, Unit):
                moves[k] = self._legal_moves(k)
        return moves

    def move(self, unit, direction):
        """Method for moving units.

        This method applies the movement logic for a given unit in a
        given direction. This method handles all capturing, jailing,
        logging, and flag picking up / dropping logic.

        For a unit's movement to be eligible, the movement must be in
        the list of `legal_moves` for the unit's idx, and the unit must
        be present in the `need_to_move` property.

        >>> import ctf
        >>> game = ctf.Ctf()
        >>> game.new_game()
        >>> game.legal_moves()
        {3: ['N', 'E'], 4: ['PASS']} # 4 is in jail or trapped
        >>> game.need_to_move
        [3]
        >>> game.move(unit=3, direction='S') # Raises IllegalMoveError
        >>> game.move(unit=4, direction='N') # Raises OutOfTurnError
        >>> game.move(unit=3, direction='N') # legal

        Args:
            unit (int): A unit's idx.
            direction (str): Direction for unit to move.

        Raises:
            GameNotFoundError: Raised if this method is called prior to
                `new_game`.
            OutOfTurnError: Raised if unit isn't within `need_to_move`.
            IllegalMoveError: Raised if unit's direction isn't within
                `legal_moves`.

        """
        if not hasattr(self, '_key'):
            raise error.GameNotFoundError(
                'Call .new_game() prior to this method.'
            )

        if unit not in self.need_to_move:
            raise error.OutOfTurnError(
                """Unit {} is not allowed to move, only one of {} are allowed
                to move.
                """.format(unit, self.need_to_move)
            )

        direction = direction.upper()
        if direction not in self.legal_moves()[unit]:
            raise error.IllegalMoveError(
                """Direction {} is illegal for unit {}, unit {}'s legal moves
                are {}.
                """.format(direction, unit, unit, self.legal_moves()[unit])
            )

        self._apply_movement(unit, direction)
        self._game_log.append({'unit': unit, 'direction': direction})
        self._moved_units[unit] = True

        if len(self.need_to_move) == 0:
            if self._turn == 1:
                self._turn = 2
            elif self._turn == 2:
                self._turn = 1

            self._moved_units = {}
            for k, v in self._key.items():
                if isinstance(v, Unit):
                    if v.team == self._turn:
                        self._moved_units[k] = False

            freedom = []
            for unit in self._jail:
                self._jail[unit] -= 1
                if self._jail[unit] == 0:
                    freedom.append(unit)

            for f in freedom:
                del self._jail[f]
                self._key[f].in_jail = False

    def new_game(self):
        """Method for starting a new game.

        This method creates a new game, the previous game's data, and
        corresponding state, are erased.

        Calling a game's methods prior to calling new_game will result
        in a GameNotFoundError.

        >>> import ctf
        >>> game = ctf.Ctf()
        >>> game.move(unit=1, direction='N') # Raises GameNotFoundError
        >>> game.new_game()

        """
        self._game_log = []
        self._key = {
            0: 'EMPTY',
            1: Flag(idx=1, team=1, position=None),
            2: Flag(idx=2, team=2, position=None)
        }

        self._score = {1: 0, 2: 0}

        y, x = self._dimensions

        self._board = np.zeros(self._dimensions)
        for team in range(1, 3):
            self._place_flag(team)
            for unit in range(self._num_units):
                available = False
                while not available:
                    if team == 1:
                        pos = (
                            np.random.randint(0, y / 2),
                            np.random.randint(0, x)
                        )
                    elif team == 2:
                        pos = (
                            np.random.randint(y / 2, y),
                            np.random.randint(0, x)
                        )

                    if self._board[pos] == 0:
                        available = True

                idx = max(self._key) + 1
                self._key[idx] = Unit(idx=idx, team=team, position=pos)
                self._board[pos] = idx

        self._turn = np.random.randint(1, 3)
        self._moved_units = {}
        for k, v in self._key.items():
            if isinstance(v, Unit):
                if v.team == self._turn:
                    self._moved_units[k] = False

    def render(self):
        """Method for rendering a frame.

        If this method is called and the `Ctf` instance currently has no
        renderer, the `ctf.rendering.Renderer` is imported and
        intialized which requires OpenGL.

        Once the renderer is initialized and stored on the `Ctf` object
        it will create a window displaying the state of the game. All
        subsequent calls will utilize the intialized renderer stored on
        the `Ctf` object.

        >>> import ctf
        >>> game = ctf.Ctf()
        >>> game.new_game()
        >>> game.render()

        Raises:
            GameNotFoundError: Raised if this method is called prior to
                `new_game`.

        """
        if not hasattr(self, '_key'):
            raise error.GameNotFoundError(
                'Call .new_game() prior to this method.'
            )

        if self._renderer is None:
            from ctf.rendering import Renderer
            self._renderer = Renderer(
                width=800,
                height=600,
                x_pad=60.0,
                y_pad=20.0,
                box=(600 - 20.0 * 2) / self._dimensions[0],
                unit_pad=((600 - 20.0 * 2) / self._dimensions[0]) // 5
            )

        self._renderer.init_window()
        self._renderer.draw_scoreboard_logs(
            dims=self._dimensions,
            score=self._score,
            logs=self._game_log[-12:],
            key=self._key
        )
        self._renderer.draw_grid(self._dimensions)
        self._renderer.draw_pieces(self._dimensions, self._key)
        self._renderer.show()
