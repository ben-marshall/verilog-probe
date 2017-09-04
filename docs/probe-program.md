
# Probe Program

This page shows how to use the probe software running on a PC to communicate
with the hardware implementation of the probe.

---

It is assumed that having implemented the probe, it can communicate with
your compute via a serial port, and that you know which serial port to
connect to. The process is the same as talking to an Arduino via a
serial port, but instead of using the Arduino IDE, we use a different program.

---

## Usage

### General

```
usage: ProbeProgram.py [-h] [--baud BAUD] [--verbose]
                       port {test,demo,print-registers,gpi,gpo,axi} ...

Software to communicate with a simple UART Probe Module.

positional arguments:
  port                  The name of the TTY/COM port to connect to the probe
                        over.
  {test,demo,print-registers,gpi,gpo,axi}

optional arguments:
  -h, --help            show this help message and exit
  --baud BAUD, -b BAUD  Baud rate of the serial port.
  --verbose, -v
```
