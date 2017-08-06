
//
// module: uartprobe_uartwrapper
//
//  A wrapper module which allows different UART modem implementations to be
//  dropped into the system. It exposes only the minimal required interface
//  for the uartprobe functionality.
//
module uartprobe_uartwrapper (

    input           clk,
    input           aresetn,

    input           uart_rx,
    input           uart_tx,

    output          rx_valid,
    output [7:0]    rx_data,
    input           rx_ready,

    input           tx_valid,
    input  [7:0]    tx_data,
    output          tx_ready

);


endmodule
