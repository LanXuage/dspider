#!/bin/env python3
import asyncio

from multiprocessing import Process
from task_processor import TaskProcessor
from task_receiver import TaskReceiver
from config import logging

log = logging.getLogger(__name__)


class Scheduler:
    def __init__(self,
                 nprocessor=1,
                 nreceiver=1,
                 npasync=1,
                 nrasync=1):
        self.npasync = npasync
        self.nrasync = nrasync
        self.tasks = [
            Process(target=self.start_task_processor) for _ in range(nprocessor)]
        #self.tasks.extend([
        #    Process(target=self.start_task_receiver) for _ in range(nreceiver)])

    def start_task_processor(self):
        task_processor = TaskProcessor(self.npasync)
        log.info('Task Processor starting. ')
        asyncio.run(task_processor.run())

    def start_task_receiver(self):
        task_receiver = TaskReceiver(self.nrasync)
        log.info('Task Receiver starting. ')
        asyncio.run(task_receiver.run())

    def start(self):
        log.info('Scheduler start. ')
        for task_processor in self.tasks:
            task_processor.start()
        for task_processor in self.tasks:
            task_processor.join()


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.start()
