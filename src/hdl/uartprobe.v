
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

// Next value of the general purpose outputs.
reg  [7:0]  n_gpo_0;
reg  [7:0]  n_gpo_1;
reg  [7:0]  n_gpo_2;
reg  [7:0]  n_gpo_3;

//
// Registers which store AXI bus related values.
//
reg  [1:0]  axi_status_bresp;
reg  [1:0]  axi_status_rresp;


//
// UART Commands
//
localparam CMD_GPI_R = 6'b00_0000;
localparam CMD_GPO_R = 6'b00_0100;
localparam CMD_GPO_W = 6'b00_1000;


//
// FSM State encodings and state registers
//

reg [1:0] byte_a;
reg [1:0] n_byte_a;

reg [3:0] fsm;      // Current FSM state
reg [3:0] n_fsm;    // Next FSM state

localparam FSM_RESET    = 4'd0;
localparam FSM_IDLE     = 4'd1;
localparam FSM_DECODE   = 4'd2;
localparam FSM_GPI_R    = 4'd3;
localparam FSM_GPO_R    = 4'd4;
localparam FSM_GPO_W0   = 4'd5;
localparam FSM_GPO_W1   = 4'd6;

// 
// ---------------------- Control FSM -----------------------------------------
//

//
// Responsible for choosing the next state of the FSM.
//
always @(*) begin : p_n_fsm
    
    n_byte_a = byte_a;
    n_fsm    = FSM_IDLE;
    rx_ready = 1'b0;
    tx_valid = 1'b0;
    tx_data  = 8'b0;
    n_gpo_0  = gpo[ 7: 0];
    n_gpo_1  = gpo[15: 8];
    n_gpo_2  = gpo[23:16];
    n_gpo_3  = gpo[31:24];

    case(fsm)
        FSM_RESET   :
            n_fsm = FSM_IDLE;
        
        FSM_IDLE    :
            n_fsm = rx_valid ? FSM_DECODE : FSM_IDLE;
        
        FSM_DECODE  : begin
            n_byte_a = rx_data[1:0];

            if(rx_data[7:2] == CMD_GPI_R) n_fsm = FSM_GPI_R;
            if(rx_data[7:2] == CMD_GPO_R) n_fsm = FSM_GPO_R;
            if(rx_data[7:2] == CMD_GPO_W) n_fsm = FSM_GPO_W0;
        end
        
        FSM_GPI_R   : begin
            // Read the indicated GPI byte and send it out on the TX
            rx_ready = 1'b1;
            tx_valid = 1'b1;
            tx_data  = gpi[ 7: 0] & {8{byte_a == 2'b00}} |
                       gpi[15: 8] & {8{byte_a == 2'b01}} |
                       gpi[23:16] & {8{byte_a == 2'b10}} |
                       gpi[31:24] & {8{byte_a == 2'b11}} ;
            n_fsm    = tx_ready ? FSM_IDLE : FSM_GPI_R;
        end
        
        FSM_GPO_R   : begin
            // Read the indicated GPO byte and send it out on the TX
            rx_ready = 1'b1;
            tx_valid = 1'b1;
            tx_data  = gpo[ 7: 0] & {8{byte_a == 2'b00}} |
                       gpo[15: 8] & {8{byte_a == 2'b01}} |
                       gpo[23:16] & {8{byte_a == 2'b10}} |
                       gpo[31:24] & {8{byte_a == 2'b11}} ;
            n_fsm    = tx_ready ? FSM_IDLE : FSM_GPO_R;
        end
        
        FSM_GPO_W0  : begin
            // Wait for rx valid to fall after asserting rx ready.
            n_fsm    = rx_valid ? FSM_GPO_W0    : FSM_GPO_W1;
            rx_ready = rx_valid;
        end
        
        FSM_GPO_W1  : begin
            // If RX data is valid, write it to the appropriate byte and return
            // to the idle state. Otherwise keep waiting.
            n_fsm    = rx_valid ? FSM_IDLE      : FSM_GPO_W1;
            rx_ready = rx_valid;
            n_gpo_0  = byte_a == 2'b00 ? rx_data : gpo[ 7: 0];
            n_gpo_1  = byte_a == 2'b01 ? rx_data : gpo[15: 8];
            n_gpo_2  = byte_a == 2'b10 ? rx_data : gpo[23:16];
            n_gpo_3  = byte_a == 2'b11 ? rx_data : gpo[31:24];
        end

        default     : n_fsm = FSM_IDLE;
    endcase
end


// 
// ---------------------- Registers -------------------------------------------
//


//
// Updates the internal status register which records the outcomes of
// AXI Write transactions.
//
always @(posedge clk, negedge aresetn) begin : p_axi_status_bresp
    if(!resetn) begin
        axi_status_bresp  <= 2'b0;
    end else if(m_axi_bvalid) begin
        axi_status_bresp  <= m_axi_bresp;
    end
end


//
// Updates the internal status register which records the outcomes of
// AXI Read transactions.
//
always @(posedge clk, negedge aresetn) begin : p_axi_status_rresp
    if(!resetn) begin
        axi_status_rresp  <= 2'b0;
    end else if(m_axi_rvalid) begin
        axi_status_rresp  <= m_axi_rresp;
    end
end


//
// Responsible for progressing the state of the general purpose outputs.
//
always @(posedge clk, negedge aresetn) begin : p_gpo
    if(!resetn) begin
        gpo <= GPO_POST_RESET;
    end else begin
        gpo [ 7: 0] <= n_gpo_0;
        gpo [15: 8] <= n_gpo_1;
        gpo [23:16] <= n_gpo_2;
        gpo [31:24] <= n_gpo_3;
    end
end


//
// Responsible for progressing the state of the FSM
//
always @(posedge clk, negedge aresetn) begin : p_fsm
    if(!resetn) begin
        fsm    <= FSM_RESET;
        byte_a <= 2'b00;
    end else begin
        fsm    <= n_fsm;
        byte_a <= n_byte_a;
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
