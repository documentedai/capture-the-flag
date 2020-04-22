class IllegalMoveError(Exception):
    """Raised when a user attempts to move a unit in an illegal
    direction.

    """
    pass


class OutOfTurnError(Exception):
    """Raised when a user attempts to move a unit out of turn."""
    pass


class GameNotFoundError(Exception):
    """Raised when a user attempts to move a piece or render a frame
    before invoking `new_game`.

    """
    pass
