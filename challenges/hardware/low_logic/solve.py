#!/usr/bin/env python3

from bitarray import bitarray


def readline(s: str) -> tuple[bool, bool, bool, bool]:
    return (s[0] == "1", s[2] == "1", s[4] == "1", s[6] == "1")


def circuit(a: bool, b: bool, c: bool, d: bool) -> bool:
    ab = a & b
    cd = c & d
    return ab | cd


with open("./input.csv") as f:
    lines = f.readlines()[1:]
    inp = [readline(line) for line in lines]

out = ""
for line in inp:
    a, b, c, d = line
    out += str(int(circuit(a, b, c, d)))

flag = bitarray(out).tobytes().decode("ascii")
print(flag)
