
//
// module: uartprobe
//
//  A simple probe which can be interfaced with over UART and used to
//  control an AXI bus master and a set of general purpose inputs and outputs.
//
module uartprobe #(
    parameter [31:0] GPO_ON_RESET = 32'b0;
)(
    
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
wire          rx_ready;


// Interface to send new data via the UART.
wire          tx_valid;
wire [7:0]    tx_data ;
wire          tx_ready;

//
// FSM State encodings and state registers
//

reg [5:0] fsm;      // Current FSM state
reg [5:0] n_fsm;    // Next FSM state

//
// Expected byte values recieved on the RX lines which indicate particular
// commands.
localparam [7:0] CMD_GPI_RD0    = 'd2;
localparam [7:0] CMD_GPI_RD1    = 'd3;
localparam [7:0] CMD_GPI_RD2    = 'd4;
localparam [7:0] CMD_GPI_RD3    = 'd5;
localparam [7:0] CMD_GPO_RD0    = 'd6;
localparam [7:0] CMD_GPO_RD1    = 'd7;
localparam [7:0] CMD_GPO_RD2    = 'd8;
localparam [7:0] CMD_GPO_RD3    = 'd9;
localparam [7:0] CMD_GPO_WR0    = 'd10;
localparam [7:0] CMD_GPO_WR1    = 'd11;
localparam [7:0] CMD_GPO_WR2    = 'd12;
localparam [7:0] CMD_GPO_WR3    = 'd13;

//
// FSM State encodings
localparam [5:0] FSM_RESET      = 'd0;
localparam [5:0] FSM_IDLE       = 'd1;
localparam [5:0] FSM_GPI_RD0    = CMD_GPI_RD0;
localparam [5:0] FSM_GPI_RD1    = CMD_GPI_RD1;
localparam [5:0] FSM_GPI_RD2    = CMD_GPI_RD2;
localparam [5:0] FSM_GPI_RD3    = CMD_GPI_RD3;
localparam [5:0] FSM_GPO_RD0    = CMD_GPO_RD0;
localparam [5:0] FSM_GPO_RD1    = CMD_GPO_RD1;
localparam [5:0] FSM_GPO_RD2    = CMD_GPO_RD2;
localparam [5:0] FSM_GPO_RD3    = CMD_GPO_RD3;
localparam [5:0] FSM_GPO_WR0    = CMD_GPO_WR0;
localparam [5:0] FSM_GPO_WR1    = CMD_GPO_WR1;
localparam [5:0] FSM_GPO_WR2    = CMD_GPO_WR2;
localparam [5:0] FSM_GPO_WR3    = CMD_GPO_WR3;

// 
// ---------------------- Control FSM -----------------------------------------
//

//
// Responsible for choosing the next state of the FSM.
//
always @(*) begin : p_n_fsm
    
    n_fsm    = FSM_IDLE;

    case(fsm)

        FSM_RESET   : n_fsm = FSM_IDLE;
        
        FSM_IDLE    : begin
            if(rx_valid) begin
                n_fsm = rx_data[5:0];
            end else begin
                n_fsm = FSM_IDLE;
            end
        end

        FSM_GPI_RD0 : n_fsm = tx_ready ? FSM_GPI_RD0 : FSM_IDLE;
        FSM_GPI_RD1 : n_fsm = tx_ready ? FSM_GPI_RD1 : FSM_IDLE;
        FSM_GPI_RD2 : n_fsm = tx_ready ? FSM_GPI_RD2 : FSM_IDLE;
        FSM_GPI_RD3 : n_fsm = tx_ready ? FSM_GPI_RD3 : FSM_IDLE;
                                                     
        FSM_GPO_RD0 : n_fsm = tx_ready ? FSM_GPO_RD0 : FSM_IDLE;
        FSM_GPO_RD1 : n_fsm = tx_ready ? FSM_GPO_RD1 : FSM_IDLE;
        FSM_GPO_RD2 : n_fsm = tx_ready ? FSM_GPO_RD2 : FSM_IDLE;
        FSM_GPO_RD3 : n_fsm = tx_ready ? FSM_GPO_RD3 : FSM_IDLE;
                                         
        FSM_GPO_WR0 : n_fsm = rx_valid ? FSM_GPO_WR0 : FSM_IDLE;
        FSM_GPO_WR1 : n_fsm = rx_valid ? FSM_GPO_WR1 : FSM_IDLE;
        FSM_GPO_WR2 : n_fsm = rx_valid ? FSM_GPO_WR2 : FSM_IDLE;
        FSM_GPO_WR3 : n_fsm = rx_valid ? FSM_GPO_WR3 : FSM_IDLE;

        default     : n_fsm = FSM_IDLE;

    endcase

end

// 
// ---------------------- UART RX Channel -------------------------------------
//

// Signal we have read the recieved RX data and that we are ready for the
// next one. Everything is caught and dealt with in one cycle.
assign rx_ready = rx_valid;

// 
// ---------------------- UART TX Channel -------------------------------------
//

// Select a register to be read.
assign tx_data = 
    ((fsm == FSM_GPI_RD0) & gpi[31:24]) || 
    ((fsm == FSM_GPI_RD1) & gpi[23:16]) || 
    ((fsm == FSM_GPI_RD2) & gpi[15: 8]) || 
    ((fsm == FSM_GPI_RD3) & gpi[ 7: 0]) || 
    ((fsm == FSM_GPO_RD0) & gpo[31:24]) || 
    ((fsm == FSM_GPO_RD1) & gpo[23:16]) || 
    ((fsm == FSM_GPO_RD2) & gpo[15: 8]) || 
    ((fsm == FSM_GPO_RD3) & gpo[ 7: 0])  ;


// Signal that a word should be sent.
assign tx_valid = 
    (fsm == FSM_GPI_RD0) || 
    (fsm == FSM_GPI_RD1) || 
    (fsm == FSM_GPI_RD2) || 
    (fsm == FSM_GPI_RD3) || 
    (fsm == FSM_GPO_RD0) || 
    (fsm == FSM_GPO_RD1) || 
    (fsm == FSM_GPO_RD2) || 
    (fsm == FSM_GPO_RD3)  ;

// 
// ---------------------- Registers -------------------------------------------
//

//
// These processes are responsible for updating the GPO byte registers.
//
always @(posedge clk, negedge aresetn) begin : p_gpo
    if(!aresetn) begin
        gpo <= GPO_ON_RESET;
    end else if (fsm == FSM_GPO_WR0 && rx_valid) begin
        gpo <= {gpo[31:8], rx_data};
    end else if (fsm == FSM_GPO_WR1 && rx_valid) begin
        gpo <= {gpo[31:16], rx_data, gpo[7:0]};
    end else if (fsm == FSM_GPO_WR2 && rx_valid) begin
        gpo <= {gpo[31:24], rx_data, gpo[15:0]};
    end else if (fsm == FSM_GPO_WR3 && rx_valid) begin
        gpo <= {rx_data, gpo[23:0]};
    end
end


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
