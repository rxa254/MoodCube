From the top level directory try running:

`$ LOG_LEVEL=info python3 -m synapse -p audio`

That should show a time series plot of the data from your mic.  It
launches a 'source' program for each data source (only 'audio' right
now), all of which send their data as numpy arrays to the 'mux', which
collects them together and publishes the resultant collection:
```
source -+
source -+-> mux --> plotter
source -+
```
Just a proof of concept.  

To make new sources using 'audio' as a template and they should "just work".
A NN element could just subscribe to the mux output, or the NN element could be put in place of the mux
with the same zmq sink pattern.  

Not very many lines of code.  zmq is very sweet.
