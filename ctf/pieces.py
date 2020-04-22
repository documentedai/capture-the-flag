"""Pieces used in `Ctf` game"""

class Piece(object):
    """The base class for other pieces"""
    def __init__(self, idx, team, position):
        """Initializtion of `Piece` object.

        This class initializes the storage of standard attributes,
        shared amongst the other pieces.

        Args:
            idx (int): Index of Unit.
            team (int): The team this piece belongs to.
            position (tuple): Location of the piece on the board.

        """
        self.idx = idx
        self.team = team
        self.position = position


class Unit(Piece):
    """`Unit` class, represents a moveable unit in a `Ctf` game."""
    def __init__(self, idx, team, position, has_flag=False, in_jail=False):
        """Initialization of `Unit` object.

        This class inherits from `Piece`.

        Args:
            has_flag (bool, optional): Whether or not the unit has the
                flag. Defaults to `False`.
            in_jail (bool, optional): Whether or not the unit is in
                jail. Defaults to `False`.

        """
        super().__init__(idx, team, position)
        self.has_flag = has_flag
        self.in_jail = in_jail


class Flag(Piece):
    def __init__(self, idx, team, position, grounded=True):
        """Initialization of `Flag` object.

        This class inherits from `Piece`.

        Args:
            grounded (bool, optional): Whether or not this flag is on
                the ground. `True` meaning this flag is on the ground,
                `False` meaning a unit is currently carrying this flag.
                Defaults to `True`.

        """
        super().__init__(idx, team, position)
        self.grounded = grounded
