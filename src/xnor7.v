`default_nettype none
`timescale 1ns/1ns

module xnor7(
    input[6:0] img,
    input[6:0] w,
    output wire[6:0] x_out
    );
    
    wire [6:0] img_cal;
    assign img_cal[6] = img[6] ;
    assign img_cal[5] = img[5];
    assign img_cal[4] = img[4];
    assign img_cal[3] = img[3];
    assign img_cal[2] = img[2];
    assign img_cal[1] = img[1];
    assign img_cal[0] = img[0];
    assign x_out = img_cal~^w;
endmodule
