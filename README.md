# How to Install
You'll need [python 3.4.3](https://www.python.org/downloads/) or better.

The emulator also uses [bitstring](https://pypi.python.org/pypi/bitstring/3.1.3). In order to install it just execute the command `pip install bitstring` into a terminal.

# How to use
	mips.py twoints|array|noinp <filename> [-d] [-m <# words>] [-s <start addr>]

### Mandatory Arguments
- `twoints|array|noinp` the type of the program to run
- `<filename>` path to your mips program

### Optional Arguments
- `[-d]` display memory dump upon program completion (default: off)
- `[-m <# words>]` size of memory available *in words* (default: 100)
- `[-s <start addr>]` starting address of the program in memory (must be a multiple of 4) (default 0)