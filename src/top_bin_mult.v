`default_nettype none
`timescale 1ns/1ns

module top_bin_mult #(
    parameter BW         = 7
    // =========================================================================
  ) (
    input clk,
    input rst,
    input c_rst,
    input [31:0] data_high,
    input [31:0] data_low,
    output wire [6:0] be_out
  );
  genvar i;
  genvar j;
  genvar k;
  wire [48:0] img;
  wire [48:0] wgt;

  for (i = 0; i < 4; i = i + 1)
  begin: pack_imgh
    assign img[((i + 1) * BW) - 1: i * BW] = data_high[(i * BW)+:7];
  end

  for (j = 3; j > 0; j = j - 1)
  begin: pack_imgl
    assign img[((7 - (j - 1)) * BW) - 1: (7 - j) * BW] = data_low[(j * BW)+:7];
  end

  for (k = 0; k < 7; k = k + 1)
  begin: pack_wgt
    assign wgt[((k + 1) * BW) - 1: k * BW] =  data_low[0+:7];
  end
  //instance
  bin_mult BE0(.clk(clk),
               .rst(rst),
               .c_rst(c_rst),
               .img(img),
               .w(wgt),
               .popcount_ret(be_out));
endmodule
