module simple_circuit ( input wire A, input wire B, input wire C, output wire AND_OUT, output wire OR_OUT, output wire INV_OUT, output wire FINAL_OUT );

and u1 (AND_OUT, A, B);
or u2 (OR_OUT, A, C);
not u3 (INV_OUT, C);
wire INTERMEDIATE1, INTERMEDIATE2;
and u4 (INTERMEDIATE1, OR_OUT, INV_OUT);
or u5 (INTERMEDIATE2, AND_OUT, INTERMEDIATE1);
and u6 (FINAL_OUT, INTERMEDIATE2, C);

endmodule
