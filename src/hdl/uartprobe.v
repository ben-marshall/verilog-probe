
//
// module: uartprobe
//
//  A simple probe which can be interfaced with over UART and used to
//  control an AXI bus master and a set of general purpose inputs and outputs.
//
module uartprobe #(
    parameter [31:0] GPO_ON_RESET      = 32'hDEAD_BEEF,
    parameter [31:0] AXI_ADDR_ON_RESET = 32'b0
)(
    
input             clk,
input             m_aresetn,

input             rx_valid,
input      [ 7:0] rx_data,
output            rx_ready,
             
output            tx_valid,
output     [ 7:0] tx_data,
input             tx_ready,

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
output            m_axi_rready,
input      [ 1:0] m_axi_rresp,
input             m_axi_rvalid,
            
output reg [31:0] m_axi_wdata,
input             m_axi_wready,
output     [ 3:0] m_axi_wstrb,
output            m_axi_wvalid

);

//
// AXI Register declarations
//

`define AXI_CTRL_RR 7:6
`define AXI_CTRL_WR 5:4
`define AXI_CTRL_RV 3:3
`define AXI_CTRL_WV 2:2
`define AXI_CTRL_AE 1:1
`define AXI_CTRL_RD 0:0

// "go" signals to trigger a read or write transaction on the AXI bus.
reg           axi_rd_go;
reg           axi_wr_go;
reg           axi_wa_go;

reg  [31:0]   axi_addr;
reg  [ 7:0]   axi_data;
reg  [ 7:0]   axi_ctrl;

//
// AXI Signal Handling
//

assign        m_axi_arsize = 3'b0;
assign        m_axi_arvalid= axi_rd_go;

assign        m_axi_awsize = 3'b0;
assign        m_axi_awvalid= axi_wa_go;

assign        m_axi_bready = m_axi_bvalid;

assign        m_axi_rready = m_axi_rvalid;

assign        m_axi_wstrb  = 4'b1;
assign        m_axi_wvalid = axi_wr_go;

assign        m_axi_araddr = axi_addr;
assign        m_axi_awaddr = axi_addr;

//
// FSM State encodings and state registers
//

reg [5:0] fsm;      // Current FSM state
reg [5:0] n_fsm;    // Next FSM state

//
// Expected byte values recieved on the RX lines which indicate particular
// commands.
localparam [7:0] CMD_GPI_RD0    = 8'd2;
localparam [7:0] CMD_GPI_RD1    = 8'd3;
localparam [7:0] CMD_GPI_RD2    = 8'd4;
localparam [7:0] CMD_GPI_RD3    = 8'd5;
localparam [7:0] CMD_GPO_RD0    = 8'd6;
localparam [7:0] CMD_GPO_RD1    = 8'd7;
localparam [7:0] CMD_GPO_RD2    = 8'd8;
localparam [7:0] CMD_GPO_RD3    = 8'd9;
localparam [7:0] CMD_GPO_WR0    = 8'd10;
localparam [7:0] CMD_GPO_WR1    = 8'd11;
localparam [7:0] CMD_GPO_WR2    = 8'd12;
localparam [7:0] CMD_GPO_WR3    = 8'd13;
localparam [7:0] CMD_AXI_RD0    = 8'd14;
localparam [7:0] CMD_AXI_RD1    = 8'd15;
localparam [7:0] CMD_AXI_RD2    = 8'd16;
localparam [7:0] CMD_AXI_RD3    = 8'd17;
localparam [7:0] CMD_AXI_WR0    = 8'd18;
localparam [7:0] CMD_AXI_WR1    = 8'd19;
localparam [7:0] CMD_AXI_WR2    = 8'd20;
localparam [7:0] CMD_AXI_WR3    = 8'd21;
localparam [7:0] CMD_AXI_RD     = 8'd22;
localparam [7:0] CMD_AXI_WR     = 8'd23;
localparam [7:0] CMD_AXI_RDC    = 8'd24;
localparam [7:0] CMD_AXI_WRC    = 8'd25;

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
localparam [5:0] FSM_AXI_RD0    = CMD_AXI_RD0;
localparam [5:0] FSM_AXI_RD1    = CMD_AXI_RD1;
localparam [5:0] FSM_AXI_RD2    = CMD_AXI_RD2;
localparam [5:0] FSM_AXI_RD3    = CMD_AXI_RD3;
localparam [5:0] FSM_AXI_WR0    = CMD_AXI_WR0;
localparam [5:0] FSM_AXI_WR1    = CMD_AXI_WR1;
localparam [5:0] FSM_AXI_WR2    = CMD_AXI_WR2;
localparam [5:0] FSM_AXI_WR3    = CMD_AXI_WR3;
localparam [5:0] FSM_AXI_RD     = CMD_AXI_RD ;
localparam [5:0] FSM_AXI_WR     = CMD_AXI_WR ;
localparam [5:0] FSM_AXI_RDC    = CMD_AXI_RDC;
localparam [5:0] FSM_AXI_WRC    = CMD_AXI_WRC;



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

        FSM_GPI_RD0 : n_fsm = tx_ready ? FSM_IDLE : FSM_GPI_RD0;
        FSM_GPI_RD1 : n_fsm = tx_ready ? FSM_IDLE : FSM_GPI_RD1;
        FSM_GPI_RD2 : n_fsm = tx_ready ? FSM_IDLE : FSM_GPI_RD2;
        FSM_GPI_RD3 : n_fsm = tx_ready ? FSM_IDLE : FSM_GPI_RD3;
                                                       
        FSM_GPO_RD0 : n_fsm = tx_ready ? FSM_IDLE : FSM_GPO_RD0;
        FSM_GPO_RD1 : n_fsm = tx_ready ? FSM_IDLE : FSM_GPO_RD1;
        FSM_GPO_RD2 : n_fsm = tx_ready ? FSM_IDLE : FSM_GPO_RD2;
        FSM_GPO_RD3 : n_fsm = tx_ready ? FSM_IDLE : FSM_GPO_RD3;

        FSM_GPO_WR0 : n_fsm = rx_valid ? FSM_IDLE : FSM_GPO_WR0;
        FSM_GPO_WR1 : n_fsm = rx_valid ? FSM_IDLE : FSM_GPO_WR1;
        FSM_GPO_WR2 : n_fsm = rx_valid ? FSM_IDLE : FSM_GPO_WR2;
        FSM_GPO_WR3 : n_fsm = rx_valid ? FSM_IDLE : FSM_GPO_WR3;

        FSM_AXI_RD0 : n_fsm = tx_ready ? FSM_IDLE : FSM_AXI_RD0;
        FSM_AXI_RD1 : n_fsm = tx_ready ? FSM_IDLE : FSM_AXI_RD1;
        FSM_AXI_RD2 : n_fsm = tx_ready ? FSM_IDLE : FSM_AXI_RD2;
        FSM_AXI_RD3 : n_fsm = tx_ready ? FSM_IDLE : FSM_AXI_RD3;

        FSM_AXI_WR0 : n_fsm = rx_valid ? FSM_IDLE : FSM_AXI_WR0;
        FSM_AXI_WR1 : n_fsm = rx_valid ? FSM_IDLE : FSM_AXI_WR1;
        FSM_AXI_WR2 : n_fsm = rx_valid ? FSM_IDLE : FSM_AXI_WR2;
        FSM_AXI_WR3 : n_fsm = rx_valid ? FSM_IDLE : FSM_AXI_WR3;
        
        FSM_AXI_RD  : n_fsm = tx_valid ? FSM_IDLE : FSM_AXI_RD ;
        FSM_AXI_WR  : n_fsm = rx_valid ? FSM_IDLE : FSM_AXI_WR ;
                                                   
        FSM_AXI_RDC : n_fsm = tx_valid ? FSM_IDLE : FSM_AXI_RDC;
        FSM_AXI_WRC : n_fsm = rx_valid ? FSM_IDLE : FSM_AXI_WRC;

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
    ({8{fsm == FSM_AXI_RD }} & axi_data[7:0]  ) | 
    ({8{fsm == FSM_AXI_RDC}} & axi_ctrl       ) | 
    ({8{fsm == FSM_AXI_RD3}} & axi_addr[31:24]) | 
    ({8{fsm == FSM_AXI_RD2}} & axi_addr[23:16]) | 
    ({8{fsm == FSM_AXI_RD1}} & axi_addr[15: 8]) | 
    ({8{fsm == FSM_AXI_RD0}} & axi_addr[ 7: 0]) | 
    ({8{fsm == FSM_GPI_RD3}} &      gpi[31:24]) | 
    ({8{fsm == FSM_GPI_RD2}} &      gpi[23:16]) | 
    ({8{fsm == FSM_GPI_RD1}} &      gpi[15: 8]) | 
    ({8{fsm == FSM_GPI_RD0}} &      gpi[ 7: 0]) | 
    ({8{fsm == FSM_GPO_RD3}} &      gpo[31:24]) | 
    ({8{fsm == FSM_GPO_RD2}} &      gpo[23:16]) | 
    ({8{fsm == FSM_GPO_RD1}} &      gpo[15: 8]) | 
    ({8{fsm == FSM_GPO_RD0}} &      gpo[ 7: 0]) ;


// Signal that a word should be sent.
assign tx_valid = 
    (fsm == FSM_AXI_RD ) || 
    (fsm == FSM_AXI_RDC) || 
    (fsm == FSM_AXI_RD0) || 
    (fsm == FSM_AXI_RD1) || 
    (fsm == FSM_AXI_RD2) || 
    (fsm == FSM_AXI_RD3) || 
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
// Responsible for updating the axi_rd_go signal.
//
always @(posedge clk, negedge m_aresetn) begin : p_axi_rd_go
    if(!m_aresetn) begin
        axi_rd_go <= 1'b0;
    end else if (m_axi_arready) begin
        axi_rd_go <= 1'b0;
    end else if(fsm == FSM_AXI_WRC && rx_valid && rx_data[`AXI_CTRL_RD]) begin
        axi_rd_go <= 1'b1;
    end
end

//
// Responsible for updating the axi_wa_go signal.
//
always @(posedge clk, negedge m_aresetn) begin : p_axi_wa_go
    if(!m_aresetn) begin
        axi_wa_go <= 1'b0;
    end else begin
        if (m_axi_awready) begin
            axi_wa_go <= 1'b0;
        end else if(fsm == FSM_AXI_WR && rx_valid) begin
            axi_wa_go <= 1'b1;
        end
    end
end

//
// Responsible for updating the axi_wr_go signal.
//
always @(posedge clk, negedge m_aresetn) begin : p_axi_wr_go
    if(!m_aresetn) begin
        axi_wr_go <= 1'b0;
    end else begin
        if (m_axi_wready) begin
            axi_wr_go <= 1'b0;
        end else if(fsm == FSM_AXI_WR && rx_valid) begin
            axi_wr_go <= 1'b1;
        end
    end
end

//
// Responsible for updating the AXI control register
//
always @(posedge clk, negedge m_aresetn) begin : p_axi_ctrl
    if(!m_aresetn) begin

        axi_ctrl[`AXI_CTRL_RV] <= 1'b1;
        axi_ctrl[`AXI_CTRL_WV] <= 1'b1;
        axi_ctrl[`AXI_CTRL_AE] <= 1'b1;

    end else begin
        
        if(fsm == FSM_AXI_WRC && rx_valid) begin
            axi_ctrl[`AXI_CTRL_AE] <= rx_data; 
        end

        if(m_axi_rvalid) begin
            axi_ctrl[`AXI_CTRL_RR] <= m_axi_rresp;
            axi_ctrl[`AXI_CTRL_RV] <= 1'b1;
        end else if (fsm == FSM_AXI_RD && tx_ready) begin
            axi_ctrl[`AXI_CTRL_RV] <= 1'b0;
        end
        
        if(m_axi_bvalid) begin
            axi_ctrl[`AXI_CTRL_WR] <= m_axi_bresp;
            axi_ctrl[`AXI_CTRL_WV] <= 1'b1;
        end else if (fsm == FSM_AXI_RD && tx_ready) begin
            axi_ctrl[`AXI_CTRL_WV] <= 1'b0;
        end
    end
end

//
// Responsible for updating the AXI write data register.
//
always @(posedge clk) begin : p_axi_wdata
    m_axi_wdata [31:8] <= 24'b0;
    if(fsm == FSM_AXI_WR && rx_valid) m_axi_wdata[7:0] <= rx_data;
end

//
// Responsible for updating the AXI read data register.
//
always @(posedge clk) begin : p_axi_rdata
    if(m_axi_rvalid) axi_data <= m_axi_rdata[7:0];
end

//
// This process is responsible for updating the AXI address register.
//
always @(posedge clk, negedge m_aresetn) begin : p_axi_addr
    if(!m_aresetn) begin
        axi_addr <= AXI_ADDR_ON_RESET;
    end else if (fsm == FSM_AXI_WR0 && rx_valid) begin
        axi_addr <= {axi_addr[31:8], rx_data};
    end else if (fsm == FSM_AXI_WR1 && rx_valid) begin
        axi_addr <= {axi_addr[31:16], rx_data, axi_addr[7:0]};
    end else if (fsm == FSM_AXI_WR2 && rx_valid) begin
        axi_addr <= {axi_addr[31:24], rx_data, axi_addr[15:0]};
    end else if (fsm == FSM_AXI_WR3 && rx_valid) begin
        axi_addr <= {rx_data, axi_addr[23:0]};
    end
end

//
// These processes are responsible for updating the GPO byte registers.
//
always @(posedge clk, negedge m_aresetn) begin : p_gpo
    if(!m_aresetn) begin
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
always @(posedge clk, negedge m_aresetn) begin : p_fsm
    if(!m_aresetn) begin
        fsm    <= FSM_RESET;
    end else begin
        fsm    <= n_fsm;
    end
end


endmodule
