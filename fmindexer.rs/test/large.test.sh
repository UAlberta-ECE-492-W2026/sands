seqgen.py 50000 >seq

fmindexer build seq seq.fmi

# Case: substring using `cut`, 24999 must be a result
fmindexer search seq.fmi "$(cut -b 25000-25500 seq)" | grep '^24999$'
