#!/usr/bin/env python3

#######
# USAGE
#
# [nvidia-smi | ] nvidia-htop.py [-l [length]]
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
import select
import argparse
from termcolor import colored

MEMORY_FREE_RATIO = 0.05
MEMORY_MODERATE_RATIO = 0.9
GPU_FREE_RATIO = 0.05
GPU_MODERATE_RATIO = 0.75

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--command-length', default=20, const=100, type=int, nargs='?')
parser.add_argument('-c', '--color', action='store_true')
# only for testing
parser.add_argument('-p', '--fake-ps', help="The list of processes to use instead of real output of `ps`")

args = parser.parse_args()

# parse the command length argument
command_length = args.command_length
color = args.color
fake_ps = args.fake_ps

# for testing, the stdin can be provided in a file
fake_stdin_path = os.getenv("FAKE_STDIN_PATH", None)
stdin_lines = []
if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    stdin_lines = sys.stdin.readlines()

if fake_stdin_path is not None:
    with open(fake_stdin_path, 'rt') as f:
        lines = f.readlines()
elif stdin_lines:
    lines = stdin_lines
else:
    ps_call = subprocess.run('nvidia-smi', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ps_call.returncode != 0:
        print('nvidia-smi exited with error code {}:'.format(ps_call.returncode))
        print(ps_call.stdout.decode() + ps_call.stderr.decode())
        sys.exit()
    lines_proc = ps_call.stdout.decode().split("\n")
    lines = [line + '\n' for line in lines_proc[:-1]]
    lines += lines_proc[-1]


def colorize(_lines):
    for j in range(len(_lines)):
        line = _lines[j]
        m = re.match(r"\| (?:N/A|..%)\s+[0-9]{2,3}C.*\s([0-9]+)MiB\s+/\s+([0-9]+)MiB.*\s([0-9]+)%", line)
        if m is not None:
            used_mem = int(m.group(1))
            total_mem = int(m.group(2))
            gpu_util = int(m.group(3)) / 100.0
            mem_util = used_mem / float(total_mem)

            is_moderate = False
            is_high = gpu_util >= GPU_MODERATE_RATIO or mem_util >= MEMORY_MODERATE_RATIO
            if not is_high:
                is_moderate = gpu_util >= GPU_FREE_RATIO or mem_util >= MEMORY_FREE_RATIO

            c = 'red' if is_high else ('yellow' if is_moderate else 'green')
            _lines[j] = colored(_lines[j], c)
            _lines[j-1] = colored(_lines[j-1], c)

    return _lines


lines_to_print = []
is_new_format = False
# Copy the utilization upper part verbatim
for i in range(len(lines)):
    if not lines[i].startswith("| Processes:"):
        lines_to_print.append(lines[i].rstrip())
    else:
        while not lines[i].startswith("|===="):
            m = re.search(r'GPU\s*GI\s*CI', lines[i])
            if m is not None:
                is_new_format = True
            i += 1
        i += 1
        break

if color:
    lines_to_print = colorize(lines_to_print)

for line in lines_to_print:
    print(line)

no_running_process = "No running processes found"
if no_running_process in lines[i] or lines[i].startswith("+--"):
    print("| " + no_running_process + " " * (73 - len(no_running_process)) + "   |")
    # Issue #9, running inside docker and seeing no processes
    if lines[i].startswith("+--"):
        print("| If you're running in a container, you'll only see processes running inside. |")
    print(lines[-1])
    sys.exit()

# Parse the PIDs from the lower part
gpu_num = []
pid = []
gpu_mem = []
user = []
cpu = []
mem = []
time = []
command = []

gpu_num_idx = 1
pid_idx = 2 if not is_new_format else 4
gpu_mem_idx = -3

while not lines[i].startswith("+--"):
    if "Not Supported" in lines[i]:
        i += 1
        continue
    line = lines[i]
    line = re.split(r'\s+', line)
    gpu_num.append(line[gpu_num_idx])
    pid.append(line[pid_idx])
    gpu_mem.append(line[gpu_mem_idx])
    user.append("")
    cpu.append("")
    mem.append("")
    time.append("")
    command.append("")
    i += 1

if fake_ps is None:
    # Query the PIDs using ps
    ps_format = "pid,user,%cpu,%mem,etime,command"
    ps_call = subprocess.run(["ps", "-o", ps_format, "-p", ",".join(pid)], stdout=subprocess.PIPE)
    processes = ps_call.stdout.decode().split("\n")
else:
    with open(fake_ps, 'r') as f:
        processes = f.readlines()

# Parse ps output
for line in processes:
    if line.strip().startswith("PID") or len(line) == 0:
        continue
    parts = re.split(r'\s+', line.strip(), 5)
    # idx = pid.index(parts[0])
    for idx in filter(lambda p: pid[p] == parts[0], range(len(pid))):
        user[idx] = parts[1]
        cpu[idx] = parts[2]
        mem[idx] = parts[3]
        time[idx] = parts[4] if "-" not in parts[4] else parts[4].split("-")[0] + " days"
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
