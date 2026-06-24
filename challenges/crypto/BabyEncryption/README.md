# BabyEncryption

We're given the encryption script with some unknown secret & its encrypted text.

```py
import string
from secret import MSG

def encryption(msg):
    ct = []
    for char in msg:
        ct.append((123 * char + 18) % 256)
    return bytes(ct)

ct = encryption(MSG)
f = open('./msg.enc','w')
f.write(ct.hex())
f.close()
```

As the modulo operation results in information loss, it cannot be inversed (AFAIK), so my solution is to brute-force the plain text.

```py
#!/usr/bin/python3

import string

MAP = { ((123 * ord(c) + 18) % 256) : c for c in string.printable }

with open('./msg.enc','r') as f:
    encrypted = bytes.fromhex(f.read())
    result = ''.join([MAP[b] for b in encrypted])

print(result)
```

Result:

```
Th3 nucl34r w1ll 4rr1v3 0n fr1d4y.
HTB{l00k_47_y0u_r3v3rs1ng_3qu4710n5_c0ngr475}
```
