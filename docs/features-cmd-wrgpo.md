
## WRGPO [A]

### Description

Write the `x'th` byte of the general purpose outputs with a given value.

### Sequence

Byte | RX Value   | Notes
-----|------------|-----------------------------------------------------------
0    | `000011AA` | `AA` is 2-bit encoding of byte index to write.
1    | `XXXXXXXX` | Data to be written to output byte is recieved.

