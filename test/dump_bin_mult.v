module dump();
    initial begin
        $dumpfile ("wb_top_bin_mult.vcd");
        $dumpvars (0, wb_top_bin_mult);
        #1;
    end
endmodule