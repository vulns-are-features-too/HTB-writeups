# xorxorxor

We're given the following code:

```py
#!/usr/bin/python3
import os
flag = open('flag.txt', 'r').read().strip().encode()

class XOR:
    def __init__(self):
        self.key = os.urandom(4)
    def encrypt(self, data: bytes) -> bytes:
        xored = b''
        for i in range(len(data)):
            xored += bytes([data[i] ^ self.key[i % len(self.key)]])
        return xored
    def decrypt(self, data: bytes) -> bytes:
        return self.encrypt(data)

def main():
    global flag
    crypto = XOR()
    print ('Flag:', crypto.encrypt(flag).hex())

if __name__ == '__main__':
    main()
```

Its output is:

```
Flag: 134af6e1297bc4a96f6a87fe046684e8047084ee046d84c5282dd7ef292dc9
```

It's simply XOR-ing the same 4-byte key over [blocks](https://en.wikipedia.org/wiki/Block_cipher) of the plaintext to get the encrypted text.
This can easily be reversed by XOR-ing the key with the encrypted text to get back the original plaintext.

Since we know the flag format is `HTB{...}`, we can use a [known plaintext attack](https://en.wikipedia.org/wiki/Known-plaintext_attack) to get the key and decrypt the flag.

```py
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
```

FLAG: `HTB{rep34t3d_x0r_n0t_s0_s3cur3}`
