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
PROBE_CMD_RDAXD  = bytes("\x16", "ascii")
PROBE_CMD_WRAXD  = bytes("\x17", "ascii")
PROBE_CMD_AXRDCS = bytes("\x18", "ascii")
PROBE_CMD_AXWRCS = bytes("\x19", "ascii")

CMD_PRINT_REGISTERS = "print-registers"
CMD_TRY_CONNECT     = "test"
CMD_GPI             = "gpi"
CMD_GPO             = "gpo"
CMD_AXI             = "axi"

# AXI control / status register field indexes.
AXCS_AE             = 1
AXCS_WV             = 3
AXCS_RV             = 2

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
