module cleaned_circuit (
A,B,C,E,F,G,H
);

  input A;
  input B;
  input C;
  output E;
  output F;
  output G;
  output H;

  wire OR_OUT, MODIFIED_OUT, INTERMEDIATE1, INV_OUT, AND_OUT, INTERMEDIATE2;
  assign E = AND_OUT;
  assign F = OR_OUT;
  assign G = INV_OUT;
  assign H = MODIFIED_OUT;

  and u1 (AND_OUT, A, B);
  or u2 (OR_OUT, A, C);
  not u3 (INV_OUT, C);
  and u4 (INTERMEDIATE1, OR_OUT, INV_OUT);
  or u5 (INTERMEDIATE2, AND_OUT, INTERMEDIATE1);
  and u6 (MODIFIED_OUT, INTERMEDIATE2, C);

endmodule
