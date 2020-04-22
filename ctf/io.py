"""I/O module"""

import pkg_resources


def resource_path(filename):
    """Returns the path to a resource.

    Args:
        filename (str): Filename to get path to, must be in resources/.

    Returns:
        path (str): Path to resources/<filename>.

    """
    path = pkg_resources.resource_filename(
        __name__,
        f'resources/{filename}'
    )
    return path
