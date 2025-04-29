module simple_circuit ();
    input wire A, B, C;
    output wire E, F, G, H;
    wire INTERMEDIATE1, INTERMEDIATE2;
    assign E = AND_OUT;
    assign F = OR_OUT;
    assign G = INV_OUT;
    assign H = FINAL_OUT;
    and u1 (AND_OUT, A, B);
    or u2 (OR_OUT, A, C);
    not u3 (INV_OUT, C);
    and u4 (INTERMEDIATE1, OR_OUT, INV_OUT);
    or u5 (INTERMEDIATE2, AND_OUT, INTERMEDIATE1);
    and u6 (FINAL_OUT, INTERMEDIATE2, C);
endmodule