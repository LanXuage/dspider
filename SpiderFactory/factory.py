#!/bin/env python3
import asyncio

from multiprocessing import Process
from workshop import Workshop


class Factoty:
    def __init__(self, num_workshop=1, num_spider=2):
        self.num_spider = num_spider
        self.workshops = [Process(target=self.start_workshop)
                          for _ in range(num_workshop)]

    def start_workshop(self):
        workshop = Workshop(self.num_spider)
        asyncio.run(workshop.run())

    def run(self):
        for workshop in self.workshops:
            workshop.start()
        for workshop in self.workshops:
            workshop.join()


if __name__ == '__main__':
    factory = Factoty()
    factory.run()
