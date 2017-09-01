
# Probe Program

This page shows how to use the probe software running on a PC to communicate
with the hardware implementation of the probe.

---

It is assumed that having implemented the probe, it can communicate with
your compute via a serial port, and that you know which serial port to
connect to. The process is the same as talking to an Arduino via a
serial port, but instead of using the Arduino IDE, we use a different program.

---

## Commands Supported

### test

Tests that we can actually open a connection on the specified port.

### print-registers

Prints the values of all registers accessible on the probe.

### gpi

Allows for access to the general purpose inputs.

- Can read all inputs, or an individual input.

### gpo

Allows for access to the general purpose outputs.

- Can read or write all outputs, or an individual output.
