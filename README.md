# How to Install
You'll need [python 3.4.3](https://www.python.org/downloads/) or newer. 

The emulator also uses [bitstring](https://pypi.python.org/pypi/bitstring/3.1.3). In order to install it just execute the command `pip install bitstring`.

### For Windows

If you want to run the debugger, you'll also need **curses**. To get this on Windows you'll need to the [windows port](http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses) of the library (you'll probably want to install curses-2.2-cpXX-none-win32.whl). To install the .whl you'll need **wheel** support for `pip`. This can be installed by running `pip install wheel`. After that, just run `pip install <path-to-package>.whl` to install curses.

# How to use
	mips.py twoints|array|noinp <filename> [-d] [-m <# words>] [-s <start addr>] [-D]

### Mandatory Arguments
- `twoints|array|noinp` the type of the program to run
- `<filename>` path to your mips program

### Optional Arguments
- `[-d]` display memory dump upon program completion (default: off)
- `[-m <# words>]` size of memory available **in words** (default: 100)
- `[-s <start addr>]` starting address of the program in memory (must be a multiple of 4) (default 0)
- `[-D]` run the **debugger**

### Debugger Controls
- `UP/PAGE UP DOWN/PAGE DOWN` to shift through memory (PAGE UP/PAGE DOWN allow you to move quicker)
- `LEFT/RIGHT` to cycle through the registers
- `s` brings up stdout. Press `s` again to close it
- `q` to close the debugger
- `SPACE` to execute the next instruction

# Screenshots

[screen1](/screenshots/screen1.png)
[screen2](/screenshots/screen2.png)
[screen3](/screenshots/screen3.png)

# Contact

Name: Marco Lilek
Email: marco@lilek.ca