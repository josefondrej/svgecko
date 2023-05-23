from typing import Callable, Tuple


def transform_path_command_string(path_command_string: str,
                                  transformation: Callable[[Tuple[float, float]], Tuple[float, float]]) -> str:
    """
    Transforms a path command string by applying a transformation to every point.
    :param path_command_string: SVG path command string
    :param transformation: Transformation that maps points from R2 to R2
    :return: Transformed path command string
    """
    raise NotImplemented('TODO: Implement this function')
