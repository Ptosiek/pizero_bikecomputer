from modules._pyqt import (
    QT_COMPOSITION_MODE_DARKEN,
    QT_FORMAT_ARGB32_PREMULTIPLIED,
    QtCore,
    QtGui,
    pg,
)

import numpy as np


def load_tile(
    img_path: str, z_level: int, crop: list[int] = None, overlay: bool = False
):
    # instantiating the image with path directly will fail,
    # we use loadFromData anyway to be able to set the zoom level fo .mvt file
    # https://github.com/tumic0/QtPBFImagePlugin
    img = QtGui.QImage()

    with open(img_path, "rb") as f:
        data = f.read()

    img.loadFromData(data, str(z_level))
    img = img.convertToFormat(QT_FORMAT_ARGB32_PREMULTIPLIED)

    if crop:
        img = img.copy(QtCore.QRect(*crop))

    img_array = pg.imageToArray(img, copy=True, transpose=False)
    # Rearrange channels from BGRA to RGBA
    img_array = img_array[..., [2, 1, 0, 3]]
    img_array = np.rot90(img_array, -1)

    img_item = pg.ImageItem(img_array, levels=(0, 255))

    if overlay:
        img_item.setCompositionMode(QT_COMPOSITION_MODE_DARKEN)

    return img_item
