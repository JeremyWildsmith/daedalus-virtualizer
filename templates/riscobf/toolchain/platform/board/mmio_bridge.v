`timescale 1ns/1ps

module femto_mmio_bridge (
    input  wire        clk,
    input  wire        resetn,

    // CPU Memory Bus
    input  wire [31:0] cpu_mem_addr,
    input  wire [31:0] cpu_mem_wdata,
    input  wire [ 3:0] cpu_mem_wmask,
    output wire [31:0] cpu_mem_rdata,
    input  wire        cpu_mem_rstrb,
    output wire        cpu_mem_rbusy,
    output wire        cpu_mem_wbusy,

    // RAM Bus
    output wire [31:0] mem_addr,
    output wire [31:0] mem_wdata,
    output wire [ 3:0] mem_wmask,
    input  wire [31:0] mem_rdata,

    // Simulation Input & Output
    output reg         output_data_ready,
    output reg  [7:0]  output_data,

    output wire        input_ready,
    input  wire        input_valid,
    input  wire [7:0]  input_data
);

    localparam [31:0] CONSOLE_ADDR   = 32'h1000_0000;
    localparam [31:0] CONSOLE_RXDATA = 32'h1000_0004;
    localparam [31:0] CONSOLE_RXSTAT = 32'h1000_0008;

    reg       rx_full;
    reg [7:0] rx_byte;

    wire addr_is_mmio =
        (cpu_mem_addr == CONSOLE_ADDR)   ||
        (cpu_mem_addr == CONSOLE_RXDATA) ||
        (cpu_mem_addr == CONSOLE_RXSTAT);

    // The RAM module we use for Daedalus is always ready
    // so this simplifies a lot of the handshaking
    assign cpu_mem_rbusy = 1'b0;
    assign cpu_mem_wbusy = 1'b0;

    assign mem_addr  = cpu_mem_addr;
    assign mem_wdata = cpu_mem_wdata;
    assign mem_wmask = addr_is_mmio ? 4'b0000 : cpu_mem_wmask;

    // Read mux
    assign cpu_mem_rdata =
        (cpu_mem_addr == CONSOLE_RXSTAT) ? {31'b0, rx_full} :
        (cpu_mem_addr == CONSOLE_RXDATA) ? {24'b0, rx_byte} :
                                           mem_rdata;

    assign input_ready = !rx_full;

    always @(posedge clk) begin
        if (!resetn) begin
            rx_full           <= 1'b0;
            rx_byte           <= 8'h00;
            output_data_ready <= 1'b0;
            output_data       <= 8'h00;
        end else begin
            output_data_ready <= 1'b0;

            if (!rx_full && input_valid) begin
                rx_full <= 1'b1;
                rx_byte <= input_data;
            end

            if (cpu_mem_rstrb && cpu_mem_addr == CONSOLE_RXDATA) begin
                rx_full <= 1'b0;
            end

            if ((|cpu_mem_wmask) && cpu_mem_addr == CONSOLE_ADDR) begin
                output_data       <= cpu_mem_wdata[7:0];
                output_data_ready <= 1'b1;
            end
        end
    end
endmodule