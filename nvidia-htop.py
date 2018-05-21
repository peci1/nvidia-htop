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
######

import sys
import os
import re
import subprocess

# parse the command length argument
command_length = 20
if len(sys.argv) > 1 and (sys.argv[1] == "-l" or sys.argv[1] == "--command-length"):
    command_length = 100
if len(sys.argv) > 2:
    try:
        command_length = int(sys.argv[2])
    except ValueError:
        print("Invalid command length, provide an integer")

# for testing, the stdin can be provided in a file
fake_stdin_path = os.getenv("FAKE_STDIN_PATH", None)
if fake_stdin_path is not None:
    with open(fake_stdin_path, 'rt') as f:
        lines = f.readlines()
else:
    lines = sys.stdin.readlines()


# Copy the utilization upper part verbatim
for i in range(len(lines)):
    if not lines[i].startswith("| Processes:"):
        print(lines[i].rstrip())
    else:
        i += 3
        break

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
    "GPU", "PID", "USER", "GPU MEM", "%MEM", "%CPU", "TIME", "COMMAND"
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