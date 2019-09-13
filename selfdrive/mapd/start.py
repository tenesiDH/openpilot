#!/usr/bin/env python3
import os

assert os.system("make") == 0

os.execv("python3 mapd.py", ["mapd"])
