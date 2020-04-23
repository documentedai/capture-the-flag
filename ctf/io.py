"""I/O module."""

import pkg_resources


def resource_path(filename):
    """Returns the path to a resource.

    Args:
        filename (:obj:`str`): Filename to get path to, must be in
            resources directory.

    Returns:
        :obj:`str`: Path to <filename>, relative to resources directory.

    """
    path = pkg_resources.resource_filename(
        __name__,
        f'resources/{filename}'
    )
    return path
