import thorlabs_elliptec
import time

MIN_OPEN: float = 1.0
MAX_OPEN: float = 11.5
OPEN_RANGE: float = MAX_OPEN - MIN_OPEN
VID: int = 0x0403
PID: int = 0x6015


class Iris:
    def __init__(self, num_exposures: int):

        # print(thorlabs_elliptec.list_devices())
        self.stage = thorlabs_elliptec.ELLx(vid=VID, pid=PID)
        # print(f"#{stage.model_number}, #{stage.device_id}")

        self.position: float = MIN_OPEN
        self.index: int = 0
        self.step: float = OPEN_RANGE / num_exposures # This needs to be updated to reflect the area change rather than the diameter
        self.pos_array = [MIN_OPEN + (self.step * i) for i in range(num_exposures)]
        print(self.pos_array)
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
    iris = Iris(50)

    for i in range(50):
        iris.set(i)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
