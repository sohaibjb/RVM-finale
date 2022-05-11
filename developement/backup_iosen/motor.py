import sys
import time
import RPi.GPIO as GPIO


class motor:

    def __init__(self, in1, in2, in3, in4, delay=.001):

        GPIO.setmode(GPIO.BCM)
        self.control_pins = [in1, in2, in3, in4]  # GPIO ports to use
        self.delay = delay  # delay between each sequence step
        self.currentIndex = 0
        for pin in self.control_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)
        self.pos = [512, 128, 256, 384]
        self.seq = [
            [1, 0, 0, 1],
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1]
        ]

    def move_to(self, index):
        if (index == self.currentIndex): return
        steps = self.get_steps(index)
        nseq = self.seq[::-1] if steps < 0 else self.seq
        for i in range(abs(steps)):
            for step in nseq:
                GPIO.output(self.control_pins, step)
                time.sleep(self.delay)
        GPIO.output(self.control_pins, [0, 0, 0, 0])

    def get_steps(self, i):
        steps = 0
        if 0 == self.currentIndex and i < len(self.pos) / 2:
            steps = self.pos[i]
        else:
            steps = self.pos[i] - self.pos[self.currentIndex]
        self.currentIndex = i
        return steps
