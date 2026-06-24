#!/usr/bin/env python3

import time
from pwn import *

rounds = 100

# io = remote("IP", PORT)
io = process("./misc_lucky_dice/challenge.py")
io.recvuntil(b'The humans are about to start the game! Are you ready?')
io.recvuntil(b'>')
io.sendline(b'1')
io.recvuntil(b'Go!')
io.recvline()

def parse_line(s: str) -> list:
    # print(f"DEBUG: {s}")
    return [int(x) for x in s.split(" ")[2:]]

def solve_loop(players):
    start = time.time()
    sums = [sum(parse_line(line)) for line in players]
    # print(f"SUMS: {sums}")

    sums.reverse() # get last max instead of 1st max
    answer = (len(sums) - sums.index(max(sums)))
    print(f"TIME: {time.time() - start}")
    return answer

for _ in range(rounds):
    print(io.recvline().decode())
    io.recvline()
    players = []
    while True:
        # do many recvline's instead of just 1 recvuntil
        # to take the IO read delay out of the time check
        # that would otherwise fail
        line = io.recvline().decode()
        print(line)
        if line.startswith("Player"):
            players.append(line)
        elif 'Who wins this round?' in line:
            break
    print(io.recvuntil(b'>').decode(), end="")
    answer = solve_loop(players)
    print(f" {answer}")
    io.sendline(f"{answer}".encode())
    n = io.recvline().decode()
    print(n)

print(io.recvall().decode())
