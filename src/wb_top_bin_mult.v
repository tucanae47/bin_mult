`default_nettype none
`timescale 1ns/1ns

module wb_top_bin_mult #(
    parameter   [31:0]  BASE_ADDRESS    = 32'h3000_0000,        // base address
    /*

    DATA PARTITION  NAME            DESCRIPTION
    15:0            period          clock cycles between putting next data on the output
    23:16           ram_end_addr    where to start reading the data in the shared RAM
    24              run             if high, set the design running

    */
    parameter   [15:0]  PERIOD          = 8'd8,                 // default period
    parameter   [7:0]   RAM_END_ADDR  = 8'd0                  // default start address in RAM to read pattern
)(
    // CaravelBus peripheral ports
    input wire          caravel_wb_clk_i,       // clock, runs at system clock
    input wire          caravel_wb_rst_i,       // main system reset
    input wire          caravel_wb_stb_i,       // write strobe
    input wire          caravel_wb_cyc_i,       // cycle
    input wire          caravel_wb_we_i,        // write enable
    input wire  [3:0]   caravel_wb_sel_i,       // write word select
    input wire  [31:0]  caravel_wb_dat_i,       // data in
    input wire  [31:0]  caravel_wb_adr_i,       // address
    output reg          caravel_wb_ack_o,       // ack
    output reg  [31:0]  caravel_wb_dat_o,       // data out

    // output for binary multiplier

    output wire [6:0] be_out,

    // debug outputs
    output wire         dbg_caravel_wb_stb
);

    // rename some signals
    wire clk = caravel_wb_clk_i;
    wire reset = caravel_wb_rst_i;

    // debug outputs
    assign dbg_caravel_wb_stb = caravel_wb_stb_i;


    // CaravelBus registers
    reg [15:0] period;
    reg [7:0] ram_end_addr;
    reg run;
    reg run2;
    reg [32:0] ram_data;
    reg [31:0]  mem_data_high;
    reg [31:0]  mem_data_low;

    // CaravelBus writes
  // CaravelBus writes
    always @(posedge clk) begin
        if(reset) begin
            period          <= PERIOD;
            ram_end_addr    <= RAM_END_ADDR;
            run             <= 1'b0;
        end
        else if(caravel_wb_stb_i && caravel_wb_cyc_i && caravel_wb_we_i && caravel_wb_adr_i == BASE_ADDRESS) begin 
                mem_data_low          <= caravel_wb_dat_i;
        end
        else if(caravel_wb_stb_i && caravel_wb_cyc_i && caravel_wb_we_i && caravel_wb_adr_i == (BASE_ADDRESS + 1)) begin 
                mem_data_high          <= caravel_wb_dat_i;
        end
    end

    // CaravelBus reads
    always @(posedge clk) begin
        if(reset)
            caravel_wb_dat_o <= 0;
        else if(caravel_wb_stb_i && caravel_wb_cyc_i && !caravel_wb_we_i && caravel_wb_adr_i == BASE_ADDRESS) begin
            // caravel_wb_dat_o <= {6'b0, mem_data_high};
            caravel_wb_dat_o <= {6'b0, mem_data_low};
        end
        else if(caravel_wb_stb_i && caravel_wb_cyc_i && !caravel_wb_we_i && caravel_wb_adr_i == (BASE_ADDRESS + 1)) begin
            caravel_wb_dat_o <= {6'b0, mem_data_high};
            run2             <= 1'b1;
            // caravel_wb_dat_o <= {ram_data};
        end
    end


    // CaravelBus acks
    always @(posedge clk) begin
        if(reset)
            caravel_wb_ack_o <= 0;
        else
            // return ack immediately
            // caravel_wb_ack_o <= (caravel_wb_stb_i && (caravel_wb_adr_i == BASE_ADDRESS) || (caravel_wb_adr_i == BASE_ADDRESS + 1));
            caravel_wb_ack_o <= (caravel_wb_stb_i && (caravel_wb_adr_i == BASE_ADDRESS )) || 
                            (caravel_wb_stb_i && (caravel_wb_adr_i == BASE_ADDRESS + 1)) ;
    end

    top_bin_mult xor_pc (
        .clk(clk),
        .rst(reset),
        .c_rst(run2),
        .data_high(mem_data_high),
        .data_low(mem_data_low),
        .be_out(be_out)
    );
    

endmodule