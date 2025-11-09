from pizero_bikecomputer.modules._pyqt import qasync
from pizero_bikecomputer.modules.constants import MenuLabel

from ..components import icons
from .base import MenuItem, MenuType, MenuWidget


class UploadActivityMenuWidget(MenuWidget):
    def get_menu_items(self):
        return [
            MenuItem(
                type=MenuType.UPLOAD,
                name=MenuLabel.RIDE_WITH_GPS,
                action=self.rwgps_upload,
                icon=icons.RideWithGPSIcon(),
            )
        ]

    @qasync.asyncSlot()
    async def rwgps_upload(self):
        await self.menu_items[MenuLabel.RIDE_WITH_GPS].run(self.config.api.rwgps.upload)
