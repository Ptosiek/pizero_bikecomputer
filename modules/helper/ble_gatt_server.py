import asyncio
import base64
import json
import re
from datetime import datetime, timedelta

try:
    from bluez_peripheral.gatt.service import Service
    from bluez_peripheral.gatt.characteristic import (
        characteristic,
        CharacteristicFlags as CharFlags,
    )
    from bluez_peripheral.util import *
    from bluez_peripheral.advert import Advertisement
    from bluez_peripheral.agent import NoIoAgent
except ImportError:
    raise ImportError("Missing bluez requirements")

from logger import app_logger

# Message first and last byte markers
F_BYTE_MARKER = 0x10
L_BYTE_MARKER = 0x0A  # ord("\n")


class GadgetbridgeService(Service):
    service_uuid = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
    rx_characteristic_uuid = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
    tx_characteristic_uuid = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

    config = None
    bus = None

    status = False
    gps_status = False
    value = bytearray()
    value_extend = False

    # TODO this has become useless. AFAIU it's preventing to handle more than once the setTime message during the \
    #  lifetime of the service, with current changes it time would be set each time the message is received
    timestamp_done = False

    message = None

    # TODO,
    #  if we want to be precise we should account the time of sending/receiving message for the setTime command
    #  it is sent through 8 messages (should still be less than 1s)
    time_correction = 0  # seconds

    def __init__(self, product, sensor):
        self.product = product
        self.sensor = sensor
        super().__init__(self.service_uuid, True)

    async def quit(self):
        if not self.status and self.bus is not None:
            self.bus.disconnect()

    # direct access from central
    @characteristic(tx_characteristic_uuid, CharFlags.NOTIFY | CharFlags.READ)
    def tx_characteristic(self, options):
        return bytes(self.product, "utf-8")

    # notice to central
    def send_message(self, value):
        self.tx_characteristic.changed(bytes(value + "\\n\n", "utf-8"))

    # receive from central
    @characteristic(rx_characteristic_uuid, CharFlags.WRITE).setter
    def rx_characteristic(self, value, options):
        # GB messages handler/decoder
        # messages are sent as \x10<content>\n (https://www.espruino.com/Gadgetbridge)
        # They are mostly \x10GB<>content\n but the setTime message which does not have the GB prefix
        if value[0] == F_BYTE_MARKER:
            if self.message:
                app_logger.warning(
                    f"Previous message was not received fully and got discarded: {self.message}"
                )
            self.message = bytearray(value)
        else:
            self.message.extend(bytearray(value))

        if self.message[-1] == L_BYTE_MARKER:
            # full message received, we can decode it
            message_str = self.message.decode()
            app_logger.debug(f"Received message: {message_str}")
            self.decode_message(message_str)
            self.message = None

    async def on_off_uart_service(self):
        if self.status:
            self.bus.disconnect()
        else:
            self.bus = await get_message_bus()
            await self.register(self.bus)
            agent = NoIoAgent()
            await agent.register(self.bus)
            adapter = await Adapter.get_first(self.bus)
            advert = Advertisement(self.product, [self.service_uuid], 0, 60)
            await advert.register(self.bus, adapter)

        self.status = not self.status

    def on_off_gadgetbridge_gps(self):
        if not self.gps_status:
            self.send_message('{t:"gps_power", status:true}')
        else:
            self.send_message('{t:"gps_power", status:false}')
        self.gps_status = not self.gps_status

    @staticmethod
    def decode_b64(match_object):
        return f'"{base64.b64decode(match_object.group(1)).decode()}"'

    def decode_message(self, message: str):
        message = message.lstrip(chr(F_BYTE_MARKER)).rstrip(chr(L_BYTE_MARKER))

        if message.startswith("setTime"):
            res = re.match(r"^setTime\((\d+)\);E.setTimeZone\((\S+)\);", message)

            if res is not None:
                time_diff = timedelta(hours=float(res.group(2)))
                utctime = (
                    datetime.fromtimestamp(int(res.group(1)))
                    - time_diff
                    + timedelta(seconds=self.time_correction)
                )

                self.sensor.set_gb_timediff_from_utc(time_diff)
                self.sensor.get_utc_time(utctime)

        elif message.startswith("GB("):
            message = message.lstrip("GB(").rstrip(")")
            # GadgetBridge uses a json-ish message format ('{t:"is_gps_active"}'), so we need to add "" to keys
            # It can also encode value in base64 using {key: atob("...")}

            message = re.sub(r'(\w+):("?\w*"?)', '"\\1":\\2', message)
            message = re.sub(r"atob\(\"(\S+)\"\)", self.decode_b64, message)

            try:
                message = json.loads(message, strict=False)

                m_type = message.get("t")
                if m_type == "notify" and "title" in message and "body" in message:
                    self.config.gui.show_message(
                        message["title"], message["body"], limit_length=True
                    )
                    app_logger.info(f"success: {message}")
                elif m_type.startswith("find") and message.get("n", False):
                    self.config.gui.show_dialog_ok_only(fn=None, title="Gadgetbridge")
                elif m_type == "gps":
                    asyncio.create_task(self.sensor.update_manual(message))

            except json.JSONDecodeError:
                app_logger.exception(f"Failed to load message as json {message}")

        else:
            app_logger.warning(f"{message} unknown message received")
