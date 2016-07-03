# thcparse: Convert The Hindu Crossword to ipuz, xpf and puz formats #

This webapp is written entirely in Python and is currently hosted at
[https://thcparse-jith.rhcloud.com/](https://thcparse-jith.rhcloud.com/).

It converts [The Hindu Crossword](http://www.thehindu.com/crossword/), a daily
crytpic crossword puzzle published by the Indian newspaper [The
Hindu](http://www.thehindu.com), to some common crossword puzzle formats which
can be read by third party mobile/desktop apps.

Currently, conversion to [`ipuz`](http://www.ipuz.org/),
[`xpf](http://www.xwordinfo.com/XPF/) and [`puz`](http://www.litsoft.com/)
formats has been implemented.

`ipuz_module.py` - Module for converting to `ipuz` format.
`xpf_module.py` - Module for converting to `xpf` format.
`puz_module.py` - Module for converting to `puz` format.

There are no plans to add more formats, but requests are welcome.

## Acknowledgement ##
I would like to thank Alex DeJarnatt for the excellent python library
[puz.py](https://github.com/alexdej/puzpy) for parsing the `puz` format.

MIT License..
