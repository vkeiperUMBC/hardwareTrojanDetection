1.Home directory includes:

1.1 src
	---s38584_scan.v	for both Trojan inserted and free designs	

2.Trojan
Trojan Description
	The Trojan trigger is a comparator whose inputs are supplied by nets from unused QN pins of scan flip-flops. 
	The Trojan is only active in the functional mode by observing test enable signal. 
	The Trojan payload propagates erroneous values over an internal signal.

Trojan Taxonomy
	Insertion phase: Design
	Abstraction level: gate level 
	Activation mechanism: Internally conditionally triggered
	Effects: Change Functionality, Denial of Service
	Location: Processor
	Physical characteristics: Functional