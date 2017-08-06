
## RDGPI [A]

### Description

Read the `x'th` byte of the general purpose inputs and write them over the
UART interface.

### Sequence

Byte | RX Value   | Notes
-----|------------|-----------------------------------------------------------
0    | `000000AA` | `AA` is 2-bit encoding of byte index to read.
1    | `XXXXXXXX` | Data from inputs returned.
