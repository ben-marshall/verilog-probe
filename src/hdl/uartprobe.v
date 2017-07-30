
//
// module: uartprobe
//
//  A simple probe which can be interfaced with over UART and used to
//  control an AXI bus master and a set of general purpose inputs and outputs.
//
module uartprobe (
    
input                   clk,
input                   aresetn,

input                   uart_rx,
output                  uart_tx,

output  [UAP_GPO_W-1:0] gpo,
input   [UAP_GPI_W-1:0] gpi
);

localparam UAP_GPO_W = 32,
localparam UAP_GPI_W = 32 

endmodule
