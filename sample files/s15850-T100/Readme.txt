1.Home directory includes:

1.1 src
	---s15850_scan.v	for both Trojan inserted and free designs	

2.Trojan
Trojan Description
	The Trojan trigger consists of two comparators and one flip-flop at the output of each comparator. 
	The comparators drive the clock inputs of the flip-flops. The data input of the first flip-flop is '1' and 
	the output of the first flip-flop is connected to the data input of the second flip-flop. 
	The output of the second flip-flop is gated by the inverted test enable signal to ensure Trojan activation only 
	in the functional mode. The Trojan payload is a MUX on an output port. Unless the Trojan gets activated, 
	the output port functions as normal; otherwise, the output port leaks an internal signal. 

Trojan Taxonomy
	Insertion phase: Design
	Abstraction level: gate level 
	Activation mechanism: Internally conditionally triggered
	Effects: Denial of Service, Change functionality
	Location: Processor
	Physical characteristics: Functional