#!/usr/bin/python3

import sys

#
# Probe Command Encodings
#
#   These represent encoded versions of probe commands, and the actual data
#   we send to the probe to do stuff.
#

PROBE_CMD_RDGPI0 = bytes("\x02", "ascii")
PROBE_CMD_RDGPI1 = bytes("\x03", "ascii")
PROBE_CMD_RDGPI2 = bytes("\x04", "ascii")
PROBE_CMD_RDGPI3 = bytes("\x05", "ascii")
PROBE_CMD_RDGPO0 = bytes("\x06", "ascii")
PROBE_CMD_RDGPO1 = bytes("\x07", "ascii")
PROBE_CMD_RDGPO2 = bytes("\x08", "ascii")
PROBE_CMD_RDGPO3 = bytes("\x09", "ascii")
PROBE_CMD_WRGPO0 = bytes("\x0A", "ascii")
PROBE_CMD_WRGPO1 = bytes("\x0B", "ascii")
PROBE_CMD_WRGPO2 = bytes("\x0C", "ascii")
PROBE_CMD_WRGPO3 = bytes("\x0D", "ascii")
PROBE_CMD_RDAXA0 = bytes("\x0E", "ascii")
PROBE_CMD_RDAXA1 = bytes("\x0F", "ascii")
PROBE_CMD_RDAXA2 = bytes("\x10", "ascii")
PROBE_CMD_RDAXA3 = bytes("\x11", "ascii")
PROBE_CMD_WRAXA0 = bytes("\x12", "ascii")
PROBE_CMD_WRAXA1 = bytes("\x13", "ascii")
PROBE_CMD_WRAXA2 = bytes("\x14", "ascii")
PROBE_CMD_WRAXA3 = bytes("\x15", "ascii")
PROBE_CMD_AXIRB0 = bytes("\x16", "ascii")
PROBE_CMD_AXIRB1 = bytes("\x17", "ascii")
PROBE_CMD_AXIRB2 = bytes("\x18", "ascii")
PROBE_CMD_AXIRB3 = bytes("\x19", "ascii")
PROBE_CMD_AXIWB0 = bytes("\x1A", "ascii")
PROBE_CMD_AXIWB1 = bytes("\x1B", "ascii")
PROBE_CMD_AXIWB2 = bytes("\x1C", "ascii")
PROBE_CMD_AXIWB3 = bytes("\x1D", "ascii")
PROBE_CMD_AXIRDRC= bytes("\x1E", "ascii")
PROBE_CMD_AXIWRRC= bytes("\x1F", "ascii")
PROBE_CMD_AXIRDWC= bytes("\x20", "ascii")
PROBE_CMD_AXIWRWC= bytes("\x21", "ascii")

CMD_PRINT_REGISTERS = "print-registers"
CMD_TRY_CONNECT     = "test"
CMD_GPI             = "gpi"
CMD_GPO             = "gpo"
CMD_AXI             = "axi"
CMD_DEMO            = "demo"

cols={"RED"   : "\033[1;31m",  
      "BLUE"  : "\033[1;34m",
      "CYAN"  : "\033[1;36m",
      "GREEN" : "\033[0;32m",
      "RESET" : "\033[0;0m"}

def color_stdout(col="GREEN"):
    """
    Set the colour of text printed to stdout.
    """
    sys.stdout.write(cols[col])

def nocolor_stdout():
    """
    Set the colour of text printed to stdout.
    """
    color_stdout(col="RESET")
