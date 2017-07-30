
# Features

Overview of the features of the module.

- Interface with probe software via a UART interface. Supports 112500 baud.
- Control upto 32 general purpose inputs and 32 general purpose outputs.
- Commands for controlling an AXI4 Bus Master interface.

## Command List

### RDGPI [x]

Read the `x'th` byte of the general purpose inputs and write them over the
UART interface.

### RDGPO [x]

Read the `x'th` byte of the general purpose outputs and write them over the
UART interface.

### WRGPO [x]

Write the `x'th` byte of the general purpose outputs with a given value.


