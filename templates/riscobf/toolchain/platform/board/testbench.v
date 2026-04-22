`timescale 1ns/1ps

module tb_femto_sdram (
  input  wire clk,
  input  wire resetn,

  output wire        output_data_ready,
  output wire [7:0]  output_data,

  output wire        input_ready,
  input  wire        input_valid,
  input  wire [7:0]  input_data,

  
  input  wire        load_enable,
  input  wire [31:0] load_addr,
  input  wire [31:0] load_data
);
  wire [31:0] cpu_mem_addr;
  wire [31:0] cpu_mem_wdata;
  wire [ 3:0] cpu_mem_wmask;
  wire [31:0] cpu_mem_rdata;
  wire        cpu_mem_rstrb;
  wire        cpu_mem_rbusy;
  wire        cpu_mem_wbusy;

  wire [31:0] mem_addr;
  wire [31:0] mem_wdata;
  wire [ 3:0] mem_wmask;
  wire [31:0] mem_rdata;
  wire        mem_rbusy;
  wire        mem_wbusy;

  FemtoRV32 #(
    .RESET_ADDR(32'h0000_0000)
  ) u_cpu (
    .clk       (clk),

    .mem_addr  (cpu_mem_addr),
    .mem_wdata (cpu_mem_wdata),
    .mem_wmask (cpu_mem_wmask),
    .mem_rdata (cpu_mem_rdata),
    .mem_rstrb (cpu_mem_rstrb),
    .mem_rbusy (cpu_mem_rbusy),
    .mem_wbusy (cpu_mem_wbusy),

    .reset     (resetn)
  );

  femto_mmio_bridge #() u_bridge (
    .clk            (clk),
    .resetn         (resetn),

    .cpu_mem_addr   (cpu_mem_addr),
    .cpu_mem_wdata  (cpu_mem_wdata),
    .cpu_mem_wmask  (cpu_mem_wmask),
    .cpu_mem_rdata  (cpu_mem_rdata),
    .cpu_mem_rstrb  (cpu_mem_rstrb),
    .cpu_mem_rbusy  (cpu_mem_rbusy),
    .cpu_mem_wbusy  (cpu_mem_wbusy),

    .mem_addr       (mem_addr),
    .mem_wdata      (mem_wdata),
    .mem_wmask      (mem_wmask),
    .mem_rdata      (mem_rdata),

    .output_data_ready (output_data_ready),
    .output_data       (output_data),

    .input_ready    (input_ready),
    .input_valid    (input_valid),
    .input_data     (input_data)
  );

  ram #() u_ram (
    .clk      (clk),

    .mem_addr (mem_addr),
    .mem_wdata(mem_wdata),
    .mem_wmask(mem_wmask),
    .mem_rdata(mem_rdata),
    .mem_rbusy(mem_rbusy),
    .mem_wbusy(mem_wbusy),

    .load_enable(load_enable),
    .load_addr(load_addr),
    .load_data(load_data)
  );
endmodule