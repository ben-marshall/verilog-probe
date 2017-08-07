
//
// module: uartprobe_gpio
//
//
module uartprobe_gpio (
    
input              clk,
input              aresetn,

output reg  [31:0] gpo,
input       [31:0] gpi,

// Recieved data.
input              rx_valid,
input       [7:0]  rx_data,
output             rx_ready,

// Data to be sent.
output             tx_valid,
output      [7:0]  tx_data,
input              tx_ready

);

//
// Registered general purpose outputs.
wire [7:0] n_gpo [1:0];  // Next value

//
// Synchronous general purpose inputs.
reg  [7:0] r_gpi [1:0];  // Current value

//
// Are we accessing a particular register?
reg  do_gpi_read;
reg  do_gpo_read;
reg  do_gpo_write;

//
// Byte address for the register being accessed.
reg [1:0] byte_addr;


//
// Assign next values of the general purpose outputs.
wire   gpo_wr       = rx_valid && do_gpo_write;
assign n_gpo[ 7: 0] = (gpo_wr && byte_addr == 2'b00) ? rx_data : gpo[ 7: 0];
assign n_gpo[15: 8] = (gpo_wr && byte_addr == 2'b01) ? rx_data : gpo[15: 8];
assign n_gpo[23:16] = (gpo_wr && byte_addr == 2'b10) ? rx_data : gpo[23:16];
assign n_gpo[31:24] = (gpo_wr && byte_addr == 2'b11) ? rx_data : gpo[31:24];


//
// register: responsible for updating the general purpose outputs
//
always @(posedge clk, negedge resetn) begin : register_gpi
    if(!resetn) begin
        gpo[ 7: 0] <= 8'h00;
        gpo[15: 8] <= 8'h00;
        gpo[23:16] <= 8'h00;
        gpo[31:24] <= 8'h00;
    end else begin
        gpo[ 7: 0] <= n_gpo[ 7: 0];
        gpo[15: 8] <= n_gpo[15: 8];
        gpo[23:16] <= n_gpo[23:16];
        gpo[31:24] <= n_gpo[31:24];
    end
end



//
// register: responsible for catching the value of GP inputs.
//
always @(posedge clk) begin : register_gpi
    r_gpi[0] <= gpi[ 7: 0];
    r_gpi[1] <= gpi[15: 8];
    r_gpi[2] <= gpi[23:16];
    r_gpi[3] <= gpi[31:24];
end


endmodule

