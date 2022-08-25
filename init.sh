#!/bin/sh
# sysctl vm.overcommit_memory=1
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
