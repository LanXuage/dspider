#!/bin/env python3
import asyncio

from multiprocessing import Process
from workshop import Workshop

class Factoty:
    def __init__(self, num_workshops=1):
        self.workshops = [Process(target=self.start_workshop) for i in range(num_workshops)]

    def start_workshop(self):
        workshop = Workshop()
        asyncio.run(workshop.run())

    def run(self):
        for workshop in self.workshops:
            workshop.start()
        for workshop in self.workshops:
            workshop.join()

if __name__ == '__main__':
    factory = Factoty(2)
    factory.run()

