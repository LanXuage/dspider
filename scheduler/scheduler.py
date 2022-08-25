#!/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from multiprocessing import Process
from task_processor import TaskProcessor
from task_receiver import TaskReceiver

class Scheduler:
    def __init__(self, 
                num_task_processor=1, 
                num_task_receiver=1, 
                num_task_processor_async=1,
                num_task_receiver_async=1):
        self.num_task_processor_async = num_task_processor_async
        self.num_task_receiver_async = num_task_receiver_async
        self.task_processors = [Process(target=self.start_task_processor) for _ in range(num_task_processor)]
        self.task_receivers = [Process(target=self.start_task_receiver) for _ in range(num_task_receiver)]
    
    def start_task_processor(self):
        task_processor = TaskProcessor(self.num_task_processor_async)
        asyncio.run(task_processor.run())
        
    def start_task_receiver(self):
        task_receiver = TaskReceiver(self.num_task_receiver_async)
        asyncio.run(task_receiver.run())
    
    def start(self):
        for task_processor in self.task_processors:
            task_processor.start()
        for task_receiver in self.task_receivers:
            task_receiver.start()
        for task_processor in self.task_processors:
            task_processor.join()
        for task_receiver in self.task_receivers:
            task_receiver.join()
        

if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.start()

