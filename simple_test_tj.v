module simple_circuit ( A, B, C, E, F, G, H);
    input A, 
    B, 
    C; 
    output E,
    F, 
    G, 
    H;
    wire INTERMEDIATE1, INTERMEDIATE2, TRIGGER, PAYLOAD, MODIFIED_OUT; 

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

    and t1 (TRIGGER, A, INV_OUT);     
    not t2 (PAYLOAD, INTERMEDIATE1);   
    or t3 (MODIFIED_OUT, FINAL_OUT, PAYLOAD); 

endmodule