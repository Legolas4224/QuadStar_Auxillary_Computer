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
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(ADAPTER)
        self.inst.timeout = 5000

        self.power_meter = ThorlabsPM100(inst=self.inst)
        self.power_meter.sense.correction.wavelength = CORRECTION_WAVELENGTH

    def read_irradience(self) -> float:
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
