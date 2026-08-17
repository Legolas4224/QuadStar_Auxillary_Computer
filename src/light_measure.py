import pyvisa
from ThorlabsPM100 import ThorlabsPM100
import math


def calculate_irradience(power_watts: int) -> float:

    SENSOR_DIAMETER_CM: float = 9.5 / 10  # mm to cm
    AREA_CM2 = math.pi * ((SENSOR_DIAMETER_CM / 2.0) ** 2)  # approx 0.7088cm^2
    # print(f"area:{AREA_CM2}")

    irradiance_w_cm2 = power_watts / AREA_CM2
    return irradiance_w_cm2


def print_adapter():
    import pyvisa

    rm = pyvisa.ResourceManager()
    print(rm.list_resources())


ADAPTER: str = "USB0::4883::32882::1905328::0::INSTR"
CORRECTION_WAVELENGTH: int = 635


class LightMeasure:
    """
    Need to allow write permissions for device:
    $ sudo tee /etc/udev/rules.d/99-thorlabs-pm100.rules > /dev/null <<'EOF'
        SUBSYSTEM=="usb", ATTR{idVendor}=="1313", ATTR{idProduct}=="8072", MODE="0666"
        EOF
    $ sudo udevadm control --reload-rules
    $ sudo udevadm trigger

    Then check with:
    $ ls -l /dev/bus/usb/001/005   # adjust bus/device numbers to match `lsusb

    Also maybe:
    $ echo "blacklist usbtmc" | sudo tee /etc/modprobe.d/usbtmc-blacklist.conf
    """

    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(ADAPTER)
        self.inst.timeout = 5000

        self.power_meter = ThorlabsPM100(inst=self.inst)
        self.power_meter.sense.correction.wavelength = CORRECTION_WAVELENGTH

    def read_irradiance(self) -> float:
        watts = self.power_meter.read
        return calculate_irradience(watts)


def main():
    import time

    meas = LightMeasure()
    print()

    while True:
        print(
            f"\033[2K\r{meas.read_irradience()}W/cm^2", end="", flush=True
        )  ## clears line
        time.sleep(0.5)


if __name__ == "__main__":
    main()
    # print_adapter()
