`timescale 1ns / 1ps

//
// module: uart_to_probe
//
//  Bridge module which interfaces between the probe module and the 
//  Xilinx AXI UART Lite v2.0 IP core.
//
//  This is an example of how the simple rx/tx interface of the probe can be
//  attatched to a pre-supplied peice of IP.
//
module uart_to_probe(
input             clk,
input             m_aresetn,

input             rx_valid,
input      [ 7:0] rx_data,
output            rx_ready,
             
output            tx_valid,
output     [ 7:0] tx_data,
input             tx_ready,

output     [31:0] m_axi_araddr,
input             m_axi_arready,
output     [ 2:0] m_axi_arsize,
output            m_axi_arvalid,
            
output     [31:0] m_axi_awaddr,
input             m_axi_awready,
output     [ 2:0] m_axi_awsize,
output            m_axi_awvalid,
            
output            m_axi_bready,
input      [ 1:0] m_axi_bresp,
input             m_axi_bvalid,
            
input      [31:0] m_axi_rdata,
output            m_axi_rready,
input      [ 1:0] m_axi_rresp,
input             m_axi_rvalid,
            
output     [31:0] m_axi_wdata,
input             m_axi_wready,
output     [ 3:0] m_axi_wstrb,
output            m_axi_wvalid
);

localparam [7:0]  UART_CTRL_CFG = 8'b0001_0000;

localparam [31:0] UART_REG_RX   = 32'h4060_0000;
localparam [31:0] UART_REG_TX   = 32'h4060_0004;
localparam [31:0] UART_REG_STAT = 32'h4060_0008;
localparam [31:0] UART_REG_CTRL = 32'h4060_000C;

//
// FSM state encodings and registers.
//

reg a_ready;
reg d_ready;

// Write channel FSM.
reg [1:0] fsm_w;
reg [1:0] n_fsm_w;

// Read channel FSM.
reg [1:0] fsm_r;
reg [1:0] n_fsm_r;

localparam [1:0] FSM_RESET   = 2'd0;
localparam [1:0] FSM_SETUP   = 2'd1;
localparam [1:0] FSM_IDLE    = 2'd2;
localparam [1:0] FSM_RX      = 2'd3;

//
// UART write channel handling.
//
assign m_axi_awaddr = fsm_w == FSM_SETUP ? UART_REG_CTRL : UART_REG_TX;
assign m_axi_awsize = 3'b0;
assign m_axi_awvalid= fsm_w == FSM_SETUP ? !a_ready   : (rx_valid && !a_ready);

assign m_axi_wdata  = {24'b0, fsm_w==FSM_SETUP ? UART_CTRL_CFG : rx_data};
assign m_axi_wvalid = fsm_w == FSM_SETUP ? !d_ready   : (rx_valid && !d_ready);
assign m_axi_wstrb  = 4'b1111;

assign m_axi_bready = 1'b1;
assign rx_ready     = m_axi_bvalid;

//
// UART read channel handling.
//

assign tx_data      = m_axi_rdata;
assign tx_valid     = m_axi_rvalid && fsm_r == FSM_RX;
assign m_axi_rready = tx_ready     || fsm_r == FSM_IDLE;

assign m_axi_araddr = fsm_r == FSM_IDLE ? UART_REG_STAT : UART_REG_RX;
assign m_axi_arvalid= !m_axi_awvalid && !m_axi_arready && fsm_w == FSM_IDLE;
assign m_axi_arsize = 3'b0;


//
// FSM Next state selection logic. (AXI WRITES)
//
always @(*) begin : p_fsm_w_n
    case(fsm_w)
        FSM_RESET: n_fsm_w = FSM_SETUP;
        FSM_SETUP: n_fsm_w = a_ready && d_ready ? FSM_IDLE : FSM_SETUP;
        FSM_IDLE : n_fsm_w = FSM_IDLE;
        default  : n_fsm_w = FSM_IDLE;
    endcase
end

//
// FSM Next state selection logic. (AXI READS)
//
always @(*) begin : p_fsm_r_n
    case(fsm_r)
        FSM_RESET: n_fsm_r = FSM_IDLE;
        FSM_IDLE : n_fsm_r = (m_axi_rvalid && m_axi_rdata[0]) ? FSM_RX  :
                                                                FSM_IDLE;
        FSM_RX   : n_fsm_r = tx_ready ? FSM_IDLE : FSM_RX;
        default  : n_fsm_r = FSM_IDLE;
    endcase
end


//
// AW and W ready register handling.
//
always @(posedge clk, negedge m_aresetn) begin
    if(!m_aresetn) begin
        a_ready <= 1'b0;
        d_ready <= 1'b0;
    end else begin
        a_ready <= (a_ready || m_axi_awready) && m_axi_awvalid;
        d_ready <= (d_ready || m_axi_wready ) && m_axi_wvalid;
    end
end


//
// Responsible for progressing the state of the FSM
//
always @(posedge clk, negedge m_aresetn) begin : p_fsm_w
    if(!m_aresetn) begin
        fsm_w    <= FSM_RESET;
        fsm_r    <= FSM_RESET;
    end else begin
        fsm_w    <= n_fsm_w;
        fsm_r    <= n_fsm_r;
    end
end



endmodule
