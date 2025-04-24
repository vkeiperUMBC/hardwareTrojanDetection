1.Home directory includes:

1.1 src
	---s35932_scan.v	for both Trojan inserted and free designs	

2.Trojan
Trojan Description
	The Trojan trigger is a comparator which gets only activated in the functional mode. 
	The Trojan payload is a ring oscillator along a path. It is expected the path slows down when the ring oscillates.

Trojan Taxonomy
	Insertion phase: Design
	Abstraction level: gate level 
	Activation mechanism: Internally conditionally triggered
	Effects: Denial of Service, Degrade Performance
	Location: Processor
	Physical characteristics: Functional