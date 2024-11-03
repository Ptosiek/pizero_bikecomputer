import struct
from datetime import datetime

from modules.constants import ANTDevice
from modules.settings import settings
from .ant_code import AntDeviceType
from .ant_device import ANT_Device
from .ant_device_ctrl import ANT_Device_CTRL


SUPPORTED_TYPES = {
    ANTDevice.CADENCE: (
        AntDeviceType.SPEED_AND_CADENCE,
        ANTDevice.CADENCE,
        ANTDevice.POWER,
    ),
    ANTDevice.CONTROL: (AntDeviceType.CONTROL,),
    ANTDevice.HEART_RATE: (AntDeviceType.HEART_RATE,),
    ANTDevice.LIGHT: (AntDeviceType.LIGHT,),
    ANTDevice.POWER: (AntDeviceType.POWER,),
    ANTDevice.SPEED: (AntDeviceType.SPEED_AND_CADENCE, AntDeviceType.SPEED),
    ANTDevice.TEMPERATURE: (AntDeviceType.TEMPERATURE,),
}


class ANT_Device_Search(ANT_Device):
    name = "SEARCH"
    ant_config = {
        "interval": (),  # Not use
        "type": 0,  # ANY
        "channel_type": 0x00,  # Channel.Type.BIDIRECTIONAL_RECEIVE,
    }
    isUse = False
    search_list = None
    search_state = False

    def __init__(self, node, config, values=None):
        self.node = node
        self.config = config

        if settings.ANT_STATUS:
            # special use of make_channel(c_type, search=False)
            self.make_channel(self.ant_config["channel_type"], ext_assign=0x01)

    def on_data(self, data):
        if not self.search_state:
            return

        if len(data) == 13:
            (device_id, device_type) = self.structPattern["ID"].unpack(data[9:12])
            if device_type in SUPPORTED_TYPES[self.ant_name]:
                # new ANT+ sensor
                self.search_list[device_id] = (device_type, False)

    def on_data_ctrl(self, data):
        if not self.search_state:
            return

        if len(data) == 8:
            (device_id,) = struct.Struct("<H").unpack(data[1:3])
            device_type = 0x10
            if device_type in SUPPORTED_TYPES[self.ant_name]:
                # new ANT+ sensor
                self.search_list[device_id] = (device_type, False)

    def search(self, ant_name):
        self.search_list = {}

        for k in ANTDevice.keys():
            if k == ant_name:
                continue

            status = settings.is_ant_device_enabled(k)
            device_id, device_type = settings.get_ant_device(k)

            if status and device_type in SUPPORTED_TYPES[ant_name]:
                # already connected
                self.search_list[device_id] = (device_type, True)

        if settings.ANT_STATUS and not self.search_state:
            self.ant_name = ant_name

            if self.ant_name not in [ANTDevice.CONTROL]:
                self.set_wait_quick_mode()
                self.channel.set_search_timeout(0)
                self.channel.set_rf_freq(57)
                self.channel.set_id(0, 0, 0)

                self.channel.enable_extended_messages(1)
                self.channel.set_low_priority_search_timeout(0xFF)
                self.node.set_lib_config(0x80)

                self.connect(isCheck=False, isChange=False)  # USE: False -> True

            elif self.ant_name == ANTDevice.CONTROL:
                self.ctrl_searcher = ANT_Device_CTRL(
                    self.node, self.config, {}, ant_name
                )
                self.ctrl_searcher.channel.on_acknowledge_data = self.on_data_ctrl
                self.ctrl_searcher.send_data = True
                self.ctrl_searcher.connect(isCheck=False, isChange=False)

            self.search_state = True

    def stop_search(self, resetWait=True):
        if settings.ANT_STATUS and self.search_state:
            if self.ant_name not in [ANTDevice.CONTROL]:
                self.disconnect(isCheck=False, isChange=False)  # USE: True -> False

                # for background scan
                self.channel.enable_extended_messages(0)
                self.node.set_lib_config(0x00)
                self.channel.set_low_priority_search_timeout(0x00)

                if resetWait:
                    self.set_wait_normal_mode()

            elif self.ant_name == ANTDevice.CONTROL:
                self.ctrl_searcher.disconnect(isCheck=False, isChange=False)
                self.ctrl_searcher.delete()
                del self.ctrl_searcher

            self.search_state = False

    def get_search_list(self):
        if settings.ANT_STATUS:
            return self.search_list
        else:
            # dummy
            timestamp = datetime.now()
            if 0 < timestamp.second % 30 < 15:
                return {
                    12345: (AntDeviceType.SPEED_AND_CADENCE, False),
                    23456: (AntDeviceType.CADENCE, False),
                    6789: (AntDeviceType.SPEED, False),
                }
            elif 15 < timestamp.second % 30 < 30:
                return {
                    12345: (AntDeviceType.SPEED_AND_CADENCE, False),
                    23456: (AntDeviceType.CADENCE, False),
                    34567: (AntDeviceType.SPEED, False),
                    45678: (AntDeviceType.POWER, False),
                    45679: (AntDeviceType.POWER, True),
                    56789: (AntDeviceType.HEART_RATE, False),
                    6789: (AntDeviceType.HEART_RATE, False),
                }
            else:
                return {}
