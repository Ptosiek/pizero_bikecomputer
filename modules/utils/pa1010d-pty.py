import os
import time

import pynmea2
import smbus

PA1010D_ADDR = 0x10

# create pseudo terminal device
master, slave = os.openpty()
pty = os.ttyname(slave)

# set permissions for gpsd
os.chmod(pty, 0o444)

print(pty)


class PA1010D:
    __slots__ = (
        "timestamp",
        "datetimestamp",
        "latitude",
        "longitude",
        "altitude",
        "lat_dir",
        "lon_dir",
        "geo_sep",
        "num_sats",
        "gps_qual",
        "speed_over_ground",
        "mode_fix_type",
        "pdop",
        "hdop",
        "vdop",
        "_i2c_addr",
        "_i2c",
        "_debug",
    )

    def __init__(self, i2c_addr=PA1010D_ADDR, debug=False):
        self._i2c_addr = i2c_addr
        self._i2c = smbus.SMBus(1)

        self._debug = debug

        self.timestamp = None
        self.datetimestamp = None
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.num_sats = None
        self.gps_qual = None

        self.lat_dir = None
        self.lon_dir = None
        self.geo_sep = None

        self.pdop = None
        self.hdop = None
        self.vdop = None

        self.speed_over_ground = None
        self.mode_fix_type = None

    @property
    def data(self):
        return dict((slot, getattr(self, slot)) for slot in self.__slots__)

    def _write_sentence(self, bytestring):
        """Write a sentence to the PA1010D device over i2c.

        We could- in theory- do this in one burst, but since smbus is limited to 32bytes,
        we would have to chunk the message and this is already one byte chunks anyway!

        """
        for char_index in bytestring:
            self._i2c.write_byte(self._i2c_addr, char_index)

    def send_command(self, command, add_checksum=True):
        """Send a command string to the PA1010D.

        If add_checksum is True (the default) a NMEA checksum will automatically be computed and added.

        """
        if type(command) is not bytes:
            command = command.encode("ascii")

        # TODO replace with pynmea2 functionality
        if command[0] == b"$":
            command = command[1:]
        if command[-1] == b"*":
            command = command[:-1]

        buf = bytearray()
        buf += b"$"
        buf += command
        if add_checksum:
            checksum = 0
            # bytes() is a real thing in Python 3
            # so `for char in commaud` iterates through char ordinals
            for char in command:
                checksum ^= char
            buf += b"*"  # Delimits checksum value
            buf += "{checksum:02X}".format(checksum=checksum).encode("ascii")
        buf += b"\r\n"
        self._write_sentence(buf)

    def read_sentence(self, timeout=5):
        """Attempt to read an NMEA sentence from the PA1010D."""
        buf = []
        timeout += time.time()

        while time.time() < timeout:
            char = self._i2c.read_byte_data(self._i2c_addr, 0x00)

            if len(buf) == 0 and char != ord("$"):
                continue

            buf += [char]

            # Check for end of line
            # Should be a full \r\n since the GPS emits spurious newlines
            if buf[-2:] == [ord("\r"), ord("\n")]:
                # Remove line ending and spurious newlines from the sentence
                return bytearray(buf).decode("ascii").strip().replace("\n", "")

        raise TimeoutError("Timeout waiting for readline")

    def update(self, wait_for="GGA", timeout=5):
        """Attempt to update from PA1010D.

        Returns true if a sentence has been successfully parsed.

        Returns false if an error has occured.

        Will wait 5 seconds for a GGA message by default.

        :param wait_for: Message type to wait for.
        :param timeout: Wait timeout in seconds

        """
        try:
            sentence = self.read_sentence()
            pynmea2.parse(sentence)
            os.write(master, sentence.encode())
        except TimeoutError:
            pass
        except pynmea2.nmea.ParseError:
            if self._debug:
                print(f"Parse error: {sentence}")


if __name__ == "__main__":
    gps = PA1010D()

    while True:
        gps.update()
        time.sleep(0.01)
