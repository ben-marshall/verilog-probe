
//
// module: uartprobe
//
//  A simple probe which can be interfaced with over UART and used to
//  control an AXI bus master and a set of general purpose inputs and outputs.
//
module uartprobe (
    
input             clk,
input             aresetn,

input             uart_rx,
output            uart_tx,

output reg [31:0] gpo,
input      [31:0] gpi,

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
input             m_axi_rlast,
output            m_axi_rready,
input      [ 1:0] m_axi_rresp,
input             m_axi_rvalid,
            
output     [31:0] m_axi_wdata,
output            m_axi_wlast,
input             m_axi_wready,
output     [ 3:0] m_axi_wstrb,
output            m_axi_wvalid

);

// Interface to recieve new data via the UART.
wire          rx_valid;
wire [7:0]    rx_data ;
reg           rx_ready;


// Interface to send new data via the UART.
reg           tx_valid;
reg  [7:0]    tx_data ;
wire          tx_ready;


// Post-reset value of the general purpose outputs.
parameter     GPO_POST_RESET = 32'b0;


//
// UART Commands
//
localparam CMD_GPI_R = 6'b00_0000;
localparam CMD_GPO_R = 6'b00_0100;
localparam CMD_GPO_W = 6'b00_1000;


//
// FSM State encodings and state registers
//

reg [3:0] fsm;      // Current FSM state
reg [3:0] n_fsm;    // Next FSM state


// 
// ---------------------- Control FSM -----------------------------------------
//

//
// Responsible for choosing the next state of the FSM.
//
always @(*) begin : p_n_fsm
    
    n_fsm    = FSM_IDLE;

    case(fsm)

        FSM_RESET   : begin
            n_fsm = FSM_IDLE;
        end
        
        FSM_IDLE    : begin
            n_fsm = rx_valid ? FSM_DECODE : FSM_IDLE;
        end
        
        default     : begin
            n_fsm = FSM_IDLE;
        end

    endcase

end


// 
// ---------------------- Registers -------------------------------------------
//


//
// Responsible for progressing the state of the FSM
//
always @(posedge clk, negedge aresetn) begin : p_fsm
    if(!resetn) begin
        fsm    <= FSM_RESET;
    end else begin
        fsm    <= n_fsm;
    end
end


//
// instance: i_uartwrapper
//
//  Generic interface into the UART modem implementation.
//
uartprobe_uartwrapper i_uartwrapper (
    .clk        (clk     ),
    .aresetn    (aresetn ),
    .uart_rx    (uart_rx ),
    .uart_tx    (uart_tx ),
    .rx_valid   (rx_valid),
    .rx_data    (rx_data ),
    .rx_ready   (rx_ready),
    .tx_valid   (tx_valid),
    .tx_data    (tx_data ),
    .tx_ready   (tx_ready)
);


endmodule
