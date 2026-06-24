#!/usr/bin/python3
encrypted = bytes.fromhex(
    "134af6e1297bc4a96f6a87fe046684e8047084ee046d84c5282dd7ef292dc9"
)
known_plain_text = "HTB{"

# 4 unknown bytes from os.urandom(4),
# but it can be recovered with a known plain text
key = [encrypted[i] ^ ord(known_plain_text[i]) for i in range(4)]

# since the same 4 bytes are looped & xor'd against the whole string,
# we can to the same in to get back the original text
flag = "".join([chr(encrypted[i] ^ key[i % 4]) for i in range(len(encrypted))])

print(flag)
