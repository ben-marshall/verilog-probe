
`timescale 1ns/1ps

//
// module: tb_uartprobe
//
//      Self-contained testbench for the uartprobe module.
//
module tb_uartprobe ();

//
// Commands for the probe.
//

localparam [7:0] CMD_GPI_RD0    = 8'd2;
localparam [7:0] CMD_GPI_RD1    = 8'd3;
localparam [7:0] CMD_GPI_RD2    = 8'd4;
localparam [7:0] CMD_GPI_RD3    = 8'd5;
localparam [7:0] CMD_GPO_RD0    = 8'd6;
localparam [7:0] CMD_GPO_RD1    = 8'd7;
localparam [6:0] CMD_GPO_RD2    = 8'd8;
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
// DUT I/O signals
//

reg               clk;
reg               m_aresetn;

reg               rx_valid;
reg        [ 7:0] rx_data;
wire              rx_ready;
             
wire              tx_valid;
wire       [ 7:0] tx_data;
reg               tx_ready;

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
            
reg        [31:0] m_axi_rdata;
wire              m_axi_rready;
reg        [ 1:0] m_axi_rresp;
reg               m_axi_rvalid;
            
wire       [31:0] m_axi_wdata;
reg               m_axi_wready;
wire       [ 3:0] m_axi_wstrb;
wire              m_axi_wvalid;

//
// Testbench variables.
//
integer clock_counter;
    
//
// Simple testbench control
//

localparam CLOCK_PERIOD = 5;
always #(CLOCK_PERIOD) clk = !clk;

initial rx_valid = 1'b0;
initial tx_ready = 1'b0;
initial begin
    gpi      = $random;
    model_gpi = gpi;
end

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

// ---------------- DUT Model ------------------------------------------

reg [ 1:0] model_axi_bresp;
reg [ 1:0] model_axi_rresp;
reg [31:0] model_axi_rdata;
reg [31:0] model_axi_wdata;

reg [31:0] model_axi_addr;
reg [31:0] model_gpo     ;
reg [31:0] model_gpi     ;


// ---------------- AXI Handling ---------------------------------------
    

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
            model_axi_rdata = m_axi_rdata;
            m_axi_rvalid = 1'b1;
            m_axi_rresp  = $random;
            model_axi_rresp = m_axi_rresp;
        end

        wait(m_axi_rready)
        
        @(posedge clk) begin
            m_axi_rvalid = 1'b0;
        end
    end
endtask


//
// Checks all AXI write transactions against expected values.
//
task handle_writes;
    reg [31:0] wdata;
    reg [31:0] addr;
    forever begin
        
        fork
            begin // Address channel
                wait(m_axi_awvalid);
                addr = m_axi_awaddr;
                @(posedge clk) begin
                    m_axi_awready = 1'b1;
                end
                @(posedge clk) begin
                    m_axi_awready = 1'b0;
                end
            end
            begin // Data channel
                wait(m_axi_wvalid);
                wdata = m_axi_wdata;
                @(posedge clk) begin
                    m_axi_wready = 1'b1;
                end

                @(posedge clk) begin
                    m_axi_wready = 1'b0;
                end
            end
        join
                
        if(wdata== model_axi_wdata &&
           addr == model_axi_addr  ) begin
            $display("AXI> Wrote %h to %h", wdata,addr);
        end else begin
            $display("Write of %h to %h expected but got %h to %h",
                model_axi_wdata, model_axi_addr,
                m_axi_wdata, m_axi_awaddr);
            $finish(1);
        end

        @(posedge clk);
        m_axi_bresp     = $random;
        model_axi_bresp = $random;
        m_axi_bvalid    = 1'b1;
        wait(m_axi_bready == 1'b1);
        @(posedge clk);
        m_axi_bvalid    = 1'b0;;        
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
        handle_writes();
    join
end

// ---------------- Command IO -----------------------------------------

//  
//  task: send_byte
//
//      Sends a single byte down the UART RX line to the DUT.
//
task send_byte;
    input [7:0] to_send;
    integer i;
    begin
        $display("UART TX> Sending byte: %h,\t %d,\t %b at time %d",
            to_send,to_send,to_send, $time);

        rx_data = to_send;
        rx_valid = 1'b1;
        @(posedge clk);
        wait(rx_ready);
        @(posedge clk);
        rx_valid = 1'b0;
        @(posedge clk);

    end
endtask

//  
//  task: recieve_byte
//
//      Recieve a single byte from the UART TX line from the DUT.
//
task recieve_byte;
    output [7:0] recieved;
    integer i;
    begin
        wait(tx_valid);
        @(posedge clk);
        
        recieved = tx_data;
        tx_ready = 1'b1;
        
        wait(!tx_valid);
        @(posedge clk);
        
        tx_ready = 1'b0;
        $display("UART RX> Recieved byte: %h,\t %d,\t %b at time %d",
            recieved,recieved,recieved, $time);
    end
endtask

//
//  task: expect_byte
//
//      Wrapper around the recieve_byte task which checks if the expected
//      byte value was recieved.
//
task expect_byte;
    input [7:0] expected_value;
    reg   [7:0] recieved_value;
    begin
        wait(tx_valid);
        @(posedge clk);

        recieved_value = tx_data;

        if(expected_value == recieved_value) begin
            $display("Expected to recieve %h, got %h",
                expected_value, recieved_value);
        end else begin
            $display("[ERROR] Expected to recieve %h, got %h",
                expected_value, recieved_value);
            $finish(1);
        end
    end
endtask


//
//  task: read_gpi
//
//      Read the supplied GPI byte and have it returned via the UART TX line.
//  
task read_gpi;
    input [1:0] gpi;
    begin
        case(gpi)
            3   : begin 
                send_byte(CMD_GPI_RD3); expect_byte(model_gpi[31:24]);
            end
            2   : begin
                send_byte(CMD_GPI_RD2); expect_byte(model_gpi[23:16]);
            end
            1   : begin
                send_byte(CMD_GPI_RD1); expect_byte(model_gpi[15: 8]);
            end
            0   : begin
                send_byte(CMD_GPI_RD0); expect_byte(model_gpi[ 7: 0]);
            end
        endcase
    end
endtask


//
//  task: read_gpo
//
//      Read the supplied GPO byte and have it returned via the UART TX line.
//  
task read_gpo;
    input [1:0] gpo;
    begin
        case(gpo)
            0   : begin
                send_byte(CMD_GPO_RD0);
                expect_byte(model_gpo[ 7: 0]);
            end
            1   : begin
                send_byte(CMD_GPO_RD1);
                expect_byte(model_gpo[15: 8]);
            end
            2   : begin
                send_byte(CMD_GPO_RD2);
                expect_byte(model_gpo[23:16]);
            end
            3   : begin
                send_byte(CMD_GPO_RD3);
                expect_byte(model_gpo[31:24]);
            end
        endcase
    end
endtask


//
//  task: write_gpo
//
//      Write the supplied GPO byte with a given value.
//  
task write_gpo;
    input [1:0] gpo;
    input [7:0] val;
    begin
        case(gpo)
            0   : begin
                send_byte(CMD_GPO_WR0);
                model_gpo[7:0] = val;
            end
            1   : begin
                send_byte(CMD_GPO_WR1);
                model_gpo[15:8] = val;
            end
            2   : begin 
                send_byte(CMD_GPO_WR2);
                model_gpo[23:16] = val;
            end
            3   : begin
                send_byte(CMD_GPO_WR3);
                model_gpo[31:24] = val;
            end
        endcase
        send_byte(val);
    end
endtask


//
//  task: read_axi_addr
//
//      Read a byte of the AXI interface address.
//  
task read_axi_addr;
    input [1:0] byte;
    begin
       case(byte)
            0   : begin
                send_byte(CMD_AXI_RD0);
                expect_byte(model_axi_addr[ 7: 0]);
            end
            1   : begin
                send_byte(CMD_AXI_RD1);
                expect_byte(model_axi_addr[15: 8]);
            end
            2   : begin
                send_byte(CMD_AXI_RD2);
                expect_byte(model_axi_addr[23:16]);
            end
            3   : begin
                send_byte(CMD_AXI_RD3);
                expect_byte(model_axi_addr[31:24]);
            end
        endcase
    end
endtask


//
//  task: write_axi_addr
//
//      Write a byte of the AXI interface address.
//  
task write_axi_addr;
    input [1:0] byte;
    input [7:0] val;
    begin
        case(byte)
            0   : begin
                send_byte(CMD_AXI_WR0);
                model_axi_addr[7:0] = val;
            end
            1   : begin
                send_byte(CMD_AXI_WR1);
                model_axi_addr[15:8] = val;
            end
            2   : begin 
                send_byte(CMD_AXI_WR2);
                model_axi_addr[23:16] = val;
            end
            3   : begin
                send_byte(CMD_AXI_WR3);
                model_axi_addr[31:24] = val;
            end
        endcase
        send_byte(val);
    end
endtask

//
//  task: read_axi_ctrl
//
//      Read the AXI control register.
//  
task read_axi_ctrl;
    send_byte(CMD_AXI_RDC);
endtask

//
//  task: write_axi_ctrl 
//
//      Write a value to the AXI control register.
//  
task write_axi_ctrl;
    input [7:0] value;
    begin
        if(value[1]) begin
            model_axi_addr = model_axi_addr + 1;
        end
        send_byte(CMD_AXI_WRC);
        send_byte(value);
    end
endtask


//
//  task: read_axi_data
//
//      Read the last returned value in the AXI data register.
//  
task read_axi_data;
    send_byte(CMD_AXI_RD);
endtask


//
//  task: write_axi_data
//
//      Perform an AXI interface write to the current address in the AXI
//      address register of the supplied value.
//  
task write_axi_data;
    input [7:0] value;
    begin
        model_axi_wdata = value;
        send_byte(CMD_AXI_WR);
        send_byte(value);
    end
endtask

// ---------------- Test Sequences -------------------------------------

//
// The main simple test sequence
//
initial begin : main_test_sequence
    integer i;

    #(CLOCK_PERIOD*40);

    write_axi_ctrl(8'b0);

    //
    // General Purpose Input test
    //
    repeat (40) begin : random_read_write_gpi
        reg [1:0] tgt;

        tgt     = $random;

        $display("GPI> Read GPI %d", tgt);
        read_gpi(tgt);

        // Don't change anything again until the probe is IDLE.
        wait(tx_valid ~& tx_ready);
    end


    //
    // General Purpose Output test
    //
    repeat (40) begin : random_read_write_gpo
        reg [1:0] tgt;
        reg [7:0] value;

        tgt     = $random;
        value   = $random;

        $display("GPO> Write %h to GPO %d", value, tgt);

        write_gpo(tgt,value);
        read_gpo(tgt);
    end


    //
    // AXI Address Test
    //
    repeat (40) begin : random_read_write_axi_addr
        reg [1:0] tgt;
        reg [7:0] value;

        tgt     = $random;
        value   = $random;

        $display("AXI> Write %h to Addr %d", value, tgt);

        write_axi_addr(tgt,value);
        read_axi_addr(tgt);

    end


    //
    // AXI Write Test
    //
    repeat (40) begin : random_write_axi_data
        reg [7:0] value;

        value   = $random;

        $display("AXI> Write %h to memory", value);

        write_axi_data(value);

    end
    
    //
    // AXI Read Test
    //
    repeat (40) begin : random_read_axi_data
        
        $display("AXI> Read from memory");

        write_axi_ctrl(8'b0000_0001); // Do a read.
        read_axi_data();              // Return the read data.
        expect_byte(model_axi_rdata);

    end
    
    #(CLOCK_PERIOD*4);
    
    $finish;

end


//
// Monitor sequence for the UART TX line.
//
initial begin : uart_tx_monitor
    forever begin : uart_tx_monitor_loop
        reg [7:0] recieved;
        recieve_byte(recieved);
    end
end


//
// instance: the UART probe module which is being tested.
//
uartprobe i_dut (   
    .clk            (clk           ), 
    .m_aresetn      (m_aresetn     ), 
    .rx_valid       (rx_valid      ), 
    .rx_data        (rx_data       ), 
    .rx_ready       (rx_ready      ), 
    .tx_valid       (tx_valid      ), 
    .tx_data        (tx_data       ), 
    .tx_ready       (tx_ready      ), 
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

