These functions convert from an OpenPMD file to a bmad-compatible file (with time offset tracked).

To do this, call: 

OpenPMD_to_Bmad(filename,tOffset=None)

where if tOffset is not specified, it will be the weighted average of the live particles' time.


To confirm that this works, convert a bmad file to OpenPMD and back, with and without the tOffset.

For example: 

Pdict=bmad_to_OpenPMD(filename)
OpenPMD_to_Bmad(filename,Pdict['timeOffset'])

This works

But:

Pdict=bmad_to_OpenPMD(filename)
OpenPMD_to_Bmad(filename)

Will produce erroneous results.
