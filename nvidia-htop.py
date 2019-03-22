#!/usr/bin/env python3

#######
# USAGE
#
# nvidia-smi | nvidia-htop.py [-l [length]]
#   print GPU utilization with usernames and CPU stats for each GPU-utilizing process
#
#   -l|--command-length [length]     Print longer part of the commandline. If `length'
#                                    is provided, use it as the commandline length,
#                                    otherwise print first 100 characters.
#   -c|--color                       Colorize the output (green - free GPU, yellow - 
#                                    moderately used GPU, red - fully used GPU)
######

import sys
import os
import re
import subprocess
import argparse
from termcolor import colored

MEMORY_FREE_RATIO = 0.05
MEMORY_MODERATE_RATIO = 0.9
GPU_FREE_RATIO = 0.05
GPU_MODERATE_RATIO = 0.75

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--command-length', default=20, const=100, type=int, nargs='?')
parser.add_argument('-c', '--color', action='store_true')

args = parser.parse_args()

# parse the command length argument
command_length = args.command_length
color = args.color

# for testing, the stdin can be provided in a file
fake_stdin_path = os.getenv("FAKE_STDIN_PATH", None)
if fake_stdin_path is not None:
    with open(fake_stdin_path, 'rt') as f:
        lines = f.readlines()
else:
    lines = sys.stdin.readlines()


def colorize(_lines):
    for i in range(len(_lines)):
        line = _lines[i]
        m = re.match(r"\| ..%\s+[0-9]{2,3}C.*\s([0-9]+)MiB\s+\/\s+([0-9]+)MiB.*\s([0-9]+)%", line)
        if m is not None:
            used_mem = int(m.group(1))
            total_mem = int(m.group(2))
            gpu_util = int(m.group(3)) / 100.0
            mem_util = used_mem / float(total_mem)

            is_low = is_moderate = is_high = False
            is_high = gpu_util >= GPU_MODERATE_RATIO or mem_util >= MEMORY_MODERATE_RATIO
            if not is_high:
                is_moderate = gpu_util >= GPU_FREE_RATIO or mem_util >= MEMORY_FREE_RATIO

            if not is_high and not is_moderate:
                is_free = True

            c = 'red' if is_high else ('yellow' if is_moderate else 'green')
            _lines[i] = colored(_lines[i], c)
            _lines[i-1] = colored(_lines[i-1], c)

    return _lines



lines_to_print = []
# Copy the utilization upper part verbatim
for i in range(len(lines)):
    if not lines[i].startswith("| Processes:"):
        lines_to_print.append(lines[i].rstrip())
    else:
        i += 3
        break

if color:
    lines_to_print = colorize(lines_to_print)

for line in lines_to_print:
    print(line)

# Parse the PIDs from the lower part
gpu_num = []
pid = []
gpu_mem = []
user = []
cpu = []
mem = []
time = []
command = []

while not lines[i].startswith("+--"):
    if "Not Supported" in lines[i]:
        i+=1
        continue
    line = lines[i]
    line = re.split(r'\s+', line)
    gpu_num.append(line[1])
    pid.append(line[2])
    gpu_mem.append(line[-3])
    user.append("")
    cpu.append("")
    mem.append("")
    time.append("")
    command.append("")
    i+=1

# Query the PIDs using ps
ps_format = "pid,user,%cpu,%mem,etime,command"
processes = subprocess.run(["ps", "-o", ps_format, "-p", ",".join(pid)], stdout=subprocess.PIPE)

# Parse ps output
for line in processes.stdout.decode().split("\n"):
    if line.strip().startswith("PID") or len(line) == 0:
        continue
    parts = re.split(r'\s+', line.strip(), 5)
    idx = pid.index(parts[0])
    user[idx] = parts[1]
    cpu[idx] = parts[2]
    mem[idx] = parts[3]
    time[idx] = parts[4] if not "-" in parts[4] else parts[4].split("-")[0] + " days"
    command[idx] = parts[5][0:100]

format = ("|  %3s %5s %8s   %8s %5s %5s %9s  %-" + str(command_length) + "." + str(command_length) + "s  |")

print(format % (
    "GPU", "PID", "USER", "GPU MEM", "%CPU", "%MEM", "TIME", "COMMAND"
))

for i in range(len(pid)):
    print(format % (
        gpu_num[i],
        pid[i],
        user[i],
        gpu_mem[i],
        cpu[i],
        mem[i],
        time[i],
        command[i]
    ))

print(lines[-1])
