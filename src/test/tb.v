
`timescale 1ns/1ps

//
// module: tb_uartprobe
//
//      Self-contained testbench for the uartprobe module.
//
module tb_uartprobe ();

//
// DUT I/O signals
//

reg               clk;
reg               m_aresetn;

reg               uart_rx;
wire              uart_tx;

wire       [31:0] gpo;
reg        [31:0] gpi;

wire       [31:0] m_axi_araddr;
reg               m_axi_arready;
wire       [ 2:0] m_axi_arsize;
wire              m_axi_arvalid;
            
wire       [31:0] m_axi_awaddr;
reg               m_axi_awready;
wire       [ 2:0] m_axi_awsize;
wire              m_axi_awvalid;
            
wire              m_axi_bready;
reg        [ 1:0] m_axi_bresp;
reg               m_axi_bvalid;
            
reg        [ 7:0] m_axi_rdata;
wire              m_axi_rready;
reg        [ 1:0] m_axi_rresp;
reg               m_axi_rvalid;
            
wire       [ 7:0] m_axi_wdata;
reg               m_axi_wready;
wire       [ 0:0] m_axi_wstrb;
wire              m_axi_wvalid;

//
// Testbench variables.
//
integer clock_counter;
    
//
// Simple testbench control
//

always #5 clk = !clk;

//
// Wave dumping and reset.
//
initial begin

    $dumpfile("work/waves.vcd");
    $dumpvars(0, tb_uartprobe);

    m_aresetn = 1'b0;
    clk     = 0;
    clock_counter = 0;
#20 m_aresetn = 1'b1;

end

//
// Watchdog timer so sims don't spin forever
//
always @(posedge clk) begin
    clock_counter = clock_counter + 1;
    if(clock_counter > 10000) begin
        $finish;
    end
end
    

//
// Returns random data to the AXI master whenever it makes a read request.
//
task handle_reads;
    forever begin
        
        wait(m_axi_arvalid);
        
        @(posedge clk) begin
            m_axi_arready = 1'b1;
        end
        #13
        @(posedge clk) begin
            m_axi_arready = 1'b0;
            m_axi_rdata = $random;
            m_axi_rvalid = 1'b1;
        end

        wait(m_axi_rready)
        
        @(posedge clk) begin
            m_axi_rvalid = 1'b0;
        end
    end
endtask

//
// Start all the different channel handlers off on separate threads.
//
initial begin
    m_axi_arready=0;
    m_axi_awready=0;
    m_axi_bresp=0;
    m_axi_bvalid=0;
    m_axi_rdata=0;
    m_axi_rresp=0;
    m_axi_rvalid=0;
    m_axi_wready=0;
    fork
        handle_reads();
    join
end


//
// instance: the UART probe module which is being tested.
//
uartprobe i_dut (   
    .clk            (clk           ), 
    .m_aresetn        (m_aresetn       ), 
    .uart_rx        (uart_rx       ), 
    .uart_tx        (uart_tx       ), 
    .gpo            (gpo           ), 
    .gpi            (gpi           ), 
    .m_axi_araddr   (m_axi_araddr  ), 
    .m_axi_arready  (m_axi_arready ), 
    .m_axi_arsize   (m_axi_arsize  ), 
    .m_axi_arvalid  (m_axi_arvalid ), 
    .m_axi_awaddr   (m_axi_awaddr  ), 
    .m_axi_awready  (m_axi_awready ), 
    .m_axi_awsize   (m_axi_awsize  ), 
    .m_axi_awvalid  (m_axi_awvalid ), 
    .m_axi_bready   (m_axi_bready  ), 
    .m_axi_bresp    (m_axi_bresp   ), 
    .m_axi_bvalid   (m_axi_bvalid  ), 
    .m_axi_rdata    (m_axi_rdata   ), 
    .m_axi_rready   (m_axi_rready  ), 
    .m_axi_rresp    (m_axi_rresp   ), 
    .m_axi_rvalid   (m_axi_rvalid  ), 
    .m_axi_wdata    (m_axi_wdata   ), 
    .m_axi_wready   (m_axi_wready  ), 
    .m_axi_wstrb    (m_axi_wstrb   ), 
    .m_axi_wvalid   (m_axi_wvalid  )  
);


endmodule

