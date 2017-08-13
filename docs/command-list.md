
# Command List

- `RDGPIx`
- `RDGPOx`
- `WRGPOx`

## RDGPI [A]

### Description

Read the `x'th` byte of the general purpose inputs and write them over the
UART interface.

### Sequence

Byte | RX Value   | Notes
-----|------------|-----------------------------------------------------------
0    | `000000AA` | `AA` is 2-bit encoding of byte index to read.
1    | `XXXXXXXX` | Data from inputs returned.

---

## RDGPO [A]

### Description

Read the `x'th` byte of the general purpose outputs and write them over the
UART interface.

### Sequence

Byte | RX Value   | Notes
-----|------------|-----------------------------------------------------------
0    | `000010AA` | `AA` is 2-bit encoding of byte index to read.
1    | `XXXXXXXX` | Data currently on output byte is returned.

---

## WRGPO [A]

### Description

Write the `x'th` byte of the general purpose outputs with a given value.

### Sequence

Byte | RX Value   | Notes
-----|------------|-----------------------------------------------------------
0    | `000011AA` | `AA` is 2-bit encoding of byte index to write.
1    | `XXXXXXXX` | Data to be written to output byte is recieved.

