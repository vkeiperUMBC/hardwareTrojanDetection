1.Home directory includes:

1.1 src
	---s35932_scan.v	for both Trojan inserted and free designs	

2.Trojan
Trojan Description
	The Trojan trigger is a comparator which only gets activated in the functional mode. 
	After activation, it bypasses four gates of the main design by applying a corresponding dominant input value.

Trojan Taxonomy
	Insertion phase: Design
	Abstraction level: gate level 
	Activation mechanism: Internally conditionally triggered
	Effects: Change Functionality, Leak Information
	Location: Processor
	Physical characteristics: Functional