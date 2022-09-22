#!/bin/env python3
import asyncio

from multiprocessing import Process
from task_processor import TaskProcessor
from task_receiver import TaskReceiver
from config import logging

log = logging.getLogger(__name__)


class Scheduler:
    def __init__(self,
                 num_processor=1,
                 num_receiver=1,
                 num_processor_unit=1,
                 num_receiver_unit=1):
        self.num_processor_unit = num_processor_unit
        self.num_receiver_unit = num_receiver_unit
        self.tasks = [
            Process(target=self.start_task_processor) for _ in range(num_processor)]
        self.tasks.extend([
            Process(target=self.start_task_receiver) for _ in range(num_receiver)])

    def start_task_processor(self):
        task_processor = TaskProcessor(self.num_processor_unit)
        log.info('Task Processor starting. ')
        asyncio.run(task_processor.run())

    def start_task_receiver(self):
        task_receiver = TaskReceiver(self.num_receiver_unit)
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
