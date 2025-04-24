1.Home directory includes:

1.1 src
	---s38584_scan.v	for both Trojan inserted and free designs	

2.Trojan
Trojan Description
	The Trojan trigger is a counter of a rear vector. When the counter value is between 100 and 110, 
	the Trojan payload leaks the value of one internal signal through a primary output.  

Trojan Taxonomy
	Insertion phase: Design
	Abstraction level: gate level 
	Activation mechanism: Internally conditionally triggered
	Effects: Change Functionality, Leak Information
	Location: Processor
	Physical characteristics: Functional