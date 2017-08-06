
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
input   [UAP_GPI_W-1:0] gpi,

output  [         31:0] m_axi_araddr,
input                   m_axi_arready,
output  [          2:0] m_axi_arsize,
output                  m_axi_arvalid,
                  
output  [         31:0] m_axi_awaddr,
input                   m_axi_awready,
output  [          2:0] m_axi_awsize,
output                  m_axi_awvalid,
                  
output                  m_axi_bready,
input   [          1:0] m_axi_bresp,
input                   m_axi_bvalid,
                  
input   [         31:0] m_axi_rdata,
input                   m_axi_rlast,
output                  m_axi_rready,
input   [          1:0] m_axi_rresp,
input                   m_axi_rvalid,
                  
output  [         31:0] m_axi_wdata,
output                  m_axi_wlast,
input                   m_axi_wready,
output  [          3:0] m_axi_wstrb,
output                  m_axi_wvalid

);

localparam UAP_GPO_W = 32,
localparam UAP_GPI_W = 32 

endmodule
