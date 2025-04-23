module simple_circuit (
    input A, B, C, D,
    output E, F, G, H
);

    // Internal wires
    wire W1, W2, W3, W4, W5, W6, W7, W8, W9, W10;

    // AND gates with scrambled connections
    and u1 (W1, A, B);       // W1 = A AND B
    and u2 (W2, W1, C);      // W2 = W1 AND C
    and u3 (W3, D, W2);      // W3 = D AND W2
    and u4 (W4, W3, A);      // W4 = W3 AND A
    and u5 (W5, W4, W1);     // W5 = W4 AND W1
    and u6 (W6, W5, W2);     // W6 = W5 AND W2
    and u7 (W7, W6, W3);     // W7 = W6 AND W3
    and u8 (W8, W7, W4);     // W8 = W7 AND W4
    and u9 (W9, W8, W5);     // W9 = W8 AND W5

    // Outputs connected to scrambled wires
    assign E = W6;           // Output E = W6
    assign F = W7;           // Output F = W7
    assign G = W8;           // Output G = W8
    assign H = W9;           // Output H = W9

endmodule