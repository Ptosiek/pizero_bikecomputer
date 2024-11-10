from typing import Any

import numpy as np


def shift_insert(arr: np.ndarray, value: Any) -> None:
    """
    Shit left insert value into array.
    This mutates the original array not to mae a copy of it
    """
    if arr.ndim == 1:
        arr[:-1] = arr[1:]
        arr[-1] = value
    elif arr.ndim == 2:
        arr[:, :-1] = arr[:, 1:]
        arr[:, -1] = value
    else:
        raise TypeError(f"{arr.ndmin}D arrays are not supported")
