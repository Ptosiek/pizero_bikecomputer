import asyncio

from logger import app_logger

from dbus_next import BusType, DBusError
from dbus_next.service import ServiceInterface, method, signal, dbus_property  # noqa
from dbus_next.aio.message_bus import MessageBus
from dbus_next import Variant  # noqa


class BTPan:
    bus = None
    devices = None

    obj_bluez = "org.bluez"
    obj_object_manager = "org.freedesktop.DBus.ObjectManager"
    obj_properties = "org.freedesktop.DBus.Properties"
    obj_device = "org.bluez.Device1"
    obj_service = "org.bluez.Network1"
    path_bluez = "/org/bluez"

    service_uuid = "nap"
    remote_addr = ""
    interface = None

    async def bluetooth_tethering(self, remote_addr, disconnect=False):
        if disconnect:
            res = await self.disconnect_tethering(remote_addr)
        else:
            res = await self.connect_tethering(remote_addr)
        return bool(res)

    async def check_dbus(self):
        try:
            self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
            await self.bus.introspect(self.obj_bluez, self.path_bluez)
            return True
        except Exception as e:  # noqa
            app_logger.warning(f"Check dbus failed {e}")
        return False

    async def find_bt_pan_devices(self):
        self.devices = {}

        proxy_object = self.bus.get_proxy_object(
            self.obj_bluez, "/", await self.bus.introspect(self.obj_bluez, "/")
        )
        manager = proxy_object.get_interface(self.obj_object_manager)
        objs = await manager.call_get_managed_objects()
        for path, ifaces in objs.items():
            if self.obj_service in ifaces.keys():
                proxy_object = self.bus.get_proxy_object(
                    self.obj_bluez,
                    path,
                    await self.bus.introspect(self.obj_bluez, path),
                )
                device = proxy_object.get_interface(self.obj_device)
                self.devices[await device.get_address()] = {
                    "name": await device.get_name(),
                    "path": path,
                }

    async def initialize_device(self, remote_addr):
        try:
            if self.remote_addr != remote_addr:
                path = self.devices[remote_addr]["path"]
                proxy_object = self.bus.get_proxy_object(
                    self.obj_bluez,
                    path,
                    await self.bus.introspect(self.obj_bluez, path),
                )
                self.interface = proxy_object.get_interface(self.obj_service)
                self.remote_addr = remote_addr
        except Exception:  # noqa
            app_logger.exception("[BT] failed to initialize_device")
            return False
        return True

    async def connect_tethering(self, remote_addr):
        if not await self.initialize_device(remote_addr):
            return False

        for n in range(2):
            try:
                await self.interface.call_connect(self.service_uuid)
            except DBusError as e:
                app_logger.error(f"[BT] {e}")
                await asyncio.sleep(1)
            else:
                break

        # Wait to check if the connection really succeeded or got rejected, checking before nap profile is asked
        # would result in connected=True but to be closed later on
        await asyncio.sleep(1)

        connected = await self.interface.get_connected()
        return connected

    async def disconnect_tethering(self, remote_addr):
        if not await self.initialize_device(remote_addr):
            return True

        try:
            await self.interface.call_disconnect()
        except DBusError as e:
            app_logger.error(f"[BT] {e}")

        await asyncio.sleep(1)

        connected = await self.interface.get_connected()
        return not connected
