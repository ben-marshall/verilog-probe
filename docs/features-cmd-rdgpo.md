
## RDGPO [A]

### Description

Read the `x'th` byte of the general purpose outputs and write them over the
UART interface.

### Sequence

Byte | RX Value   | Notes
-----|------------|-----------------------------------------------------------
0    | `000010AA` | `AA` is 2-bit encoding of byte index to read.
1    | `XXXXXXXX` | Data currently on output byte is returned.

