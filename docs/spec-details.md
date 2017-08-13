
# Specification

A detailed specification of each feature.

---

## Controlling the Probe

- The probe is controlled using sequences of 8-bit operations recieved over the
  UART TX line.
- Each sequence is one or more commands in length. Usually starting with a
  single operation specifier and followed by zero or more data operands.

## General Purpose Inputs

### Functionality:

- The module supports 32 individual general purpose inputs (GPIs).
- Each of the 32 GPIs can be addressed per byte.
    - Byte 0 - GPIs `7:0`
    - Byte 1 - GPIs `15:8`
    - Byte 2 - GPIs `23:16`
    - Byte 3 - GPIs `31:24`
- There are four commands associated with the general purpose inputs, one for
  reading each byte:
    - `RDGPI0`, `RDGPI1`, `RDGPI2`, `RDGPI3`
    - Upon recieving any of these commands, the probe will return the current
      value of the relevant GPI byte via the RX line of the UART modem.
- The GPIs are not registered, and are sampled only when they must be read.
  This saves on area and power.
    - It is not recommended that the GPIs be used for communicating with
      parts of the system which require time-critical control. The speed of
      the UART interface to the probe is not suited to this.

### Clock Domains:

- It is assumed that general purpose input signals belong to the same clock
  domain as the rest of the probe module.
- External synchronisation will be needed if this is not the case.

## General Purpose Outputs

### Functionality:

- The module supports 32 individual general purpose outputs (GPOs).
- GPOs are addressed per byte, in the same way as the GPIs.
    - Byte 0 - GPOs `7:0`
    - Byte 1 - GPOs `15:8`
    - Byte 2 - GPOs `23:16`
    - Byte 3 - GPOs `31:24`
- There are eight commands associated with the GPOs, two per byte, one for
  reading and one for writing:
    - `RDGPO0`, `RDGPO1`, `RDGPO2`, `RDGPO3`
    - `WRGPO0`, `WRGPO1`, `WRGPO2`, `WRGPO3`
    - Read commands behave identically to the equivilent `RDGPIx` commands,
      where the value of the GPO is subsequently returned via the TX port of
      the UART.
    - Write commands consist of two RX operations. The first specifies which
      byte is to be written, the second specifies the value to be written. The
      written value is not echoed back to the probe controller.

### Clock Domains:

- GPOs are registered in the same clock domain as the rest of the probe module.
- External synchronisation between clock domains can be added as needed.


## AXI4 Master Bus

### Functionality:

- The module supports a single AXI4 bus master interface.
    - The interface uses byte-level addressing.
    - The interface has a 32-bit address space.
    - Bursts are not supported, since the UART interface is too slow to make
      them sensible to implement.
- The AXI bus is controlled using three different classes of operation:
  control, address and data.
    - Control operations are used to configure certain aspects of the bus
      functionality. This includes address auto-incrementing and detecting
      the status of past transactions.
    - Address operations are used to configure the address of the byte we will
      access using the bus.
    - Data operations are used to either read or write the currently addressed
      byte.
- Control Instructions:
    - `AXRDCS` reads the control status register for the AXI4 interface and
      returns it to the probe controller via the TX line of the UART.
    - `AXWRCS` writes the control status register for the AXI4 interface.
- Address Instructions:
    - `RDAXA0`, `RDAXA1`, `RDAXA2`, `RDAXA3` - Read n'th byte of the AXI4
      address register.
    - `WRAXA0`, `WRAXA1`, `WRAXA2`, `WRAXA3` - Write n'th byte of the AXI4
      address register. Uses two operations, one byte to set which register
      to write, and a second to set the data.
- Data instructions:
    - `RDAXD` - Read the current value of the AXI data register.
    - `WRAXD` - Write the value of the AXI data register. Uses two operations,
      one byte to indicate  which register to write, and a second to set the
      data.

### Registers
   
#### Control Status Register

**Fields:**

Bits | Name |   Purpose                                    | R/W | Reset Value
-----|------|----------------------------------------------|-----|-------------
7:6  | rr   | AXI4 Read response for previous transaction. | R   | Undefined
6:5  | wr   | AXI4 Write response for previous transaction.| R   | Undefined
4    | rv   | Read response valid - has the read finished? | R   | 0
3    | wv   | Write response valid - has the read finished?| R   | 0
2    | ae   | Address auto increment enable.               | R/W | 1         
1    |      | Reserved                                     | R   | Undefined 
0    |      | Reserved                                     | R   | Undefined 

Fields of the AXI4 control status register are written and read using the
`AXRDCS` and `AXWRCS` operations.


#### Address Register

**Fields:**

Bits | Name |   Purpose                                    | R/W | Reset Value
-----|------|----------------------------------------------|-----|-------------
31:24| a0   | Byte 3                                       | R/W | Undefined
23:16| a1   | Byte 2                                       | R/W | Undefined
15:8 | a2   | Byte 1                                       | R/W | Undefined
7:0  | a3   | Byte 0                                       | R/W | Undefined

Fields of the AXI4 address register are written and read using the `RDAXAn`
and `WRAXAn` operations.


#### Data Register

**Fields:**

Bits | Name |   Purpose                                    | R/W | Reset Value
-----|------|----------------------------------------------|-----|-------------
7:0  | d0   | Byte for read / write data                   | R/W | Undefined


Fields of the AXI4 data register are written and read using the `RDAXD`
and `WRAXD` operations.

When a read transaction completes successfully, the returned data is placed
into this register.

When this register is written to, the written value is not stored in it, but
forwarded straight onto the AXI4 bus.

### Clock Domains:

- The AXI4 bus is synchronised to the same clock domain as the rest of the
  probe module.
- External synchronisation between clock domains can be added as needed to
  interface with other faster or slower devices.
