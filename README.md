# computer_drill_sergeant
Keeps reading text lines from a file, with random timing between. Good for irregular timed pushups!

To run using the default file 'pushups',

	$ ./run_set.sh 

or the same called as,

	$ ./run_set.sh pushups
	
where the input file is in format,

```
# first sleep, then do thing
rand,up
rand,down
randsmall,up
randsmall,down
```

'rand' is a random sleep
'randsmall' is a small random sleep
