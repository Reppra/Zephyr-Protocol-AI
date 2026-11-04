# oldmem - one big old memory file
Cold memory relocated out of the active workspace by `tools/cmem.py`.
Append-only, run-delimited: t=OLD-NNNN begin | rows | t=OLD-NNNN end.
Reached by pointer, never loaded whole. Pre-images in oldmem/pre/.
Not a tier: nothing here is read into context by the loop.
p=oldmem/README.md
