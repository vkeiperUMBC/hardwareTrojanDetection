module simple_circuit ( A, B, C, E, F, G, H);
    input wire A, 
    B, 
    C; 
    output wire E, //thing
    F, 
    G, 
    H;
    wire INTERMEDIATE1, INTERMEDIATE2; 

    assign E = AND_OUT; // Output E is the result of the first AND gate
    assign F = OR_OUT;  // Output F is the result of the OR gate    
    assign G = INV_OUT; // Output G is the result of the NOT gate
    assign H = FINAL_OUT; // Output H is the final result of the circuit

    // AND gates with scrambled connections
    and u1 (AND_OUT, A, B);
    or u2 (OR_OUT, A, C);
    not u3 (INV_OUT, C);
    and u4 (INTERMEDIATE1, OR_OUT, INV_OUT);
    or u5 (INTERMEDIATE2, AND_OUT, INTERMEDIATE1);
    and u6 (FINAL_OUT, INTERMEDIATE2, C);


endmodule