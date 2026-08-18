import thorlabs_elliptec
import time
import numpy as np

MIN_OPEN: float = 1.0
MAX_OPEN: float = 11.5  # unused atm
OPEN_RANGE: float = MAX_OPEN - MIN_OPEN  # unused atm

MIN_AREA: float = np.pi * ((MIN_OPEN / 2) ** 2)
MAX_AREA: float = np.pi * ((MAX_OPEN / 2) ** 2)
AREA_RANGE: float = MAX_AREA - MIN_AREA


def diameter_from_area(area: float) -> float:
    diameter = 2 * np.sqrt(area / np.pi)
    return diameter


VID: int = 0x0403
PID: int = 0x6015


class Iris:
    def __init__(self, num_exposures: int):

        # print(thorlabs_elliptec.list_devices())
        self.stage = thorlabs_elliptec.ELLx(vid=VID, pid=PID)
        # print(f"#{stage.model_number}, #{stage.device_id}")

        self.position: float = MIN_OPEN
        self.index: int = 0
        self.step: float = (
            AREA_RANGE / num_exposures
        )  # This needs to be updated to reflect the area change rather than the diameter

        self.area_array = [MIN_AREA + (self.step * i) for i in range(num_exposures + 1)]
        self.pos_array = [diameter_from_area(area) for area in self.area_array]
        # print(self.area_array)
        # print(self.pos_array)

        self.stage.home()

    def set(self, index: int):
        if self.stage is None:
            raise RuntimeError("Iris stage has not been initalized")

        index = max(0, index)
        index = min(len(self.pos_array) - 1, index)
        self.index = index

        self.position = self.pos_array[self.index]
        self.stage.move_absolute(self.position)

    def next(self):
        if self.index < len(self.pos_array):
            self.index += 1

        self.position = self.pos_array[self.index]
        self.stage.move_absolute(self.position)


def main():
    print(thorlabs_elliptec.list_devices())
    iris = Iris(50)

    for i in range(50):
        iris.set(i)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
