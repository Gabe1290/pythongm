# Third-party data in this extension

`font.py` and `images.py` are generated from MIT-licensed micro:bit
sources. Their notices follow, as the MIT License requires.

## font.py — micro:bit runtime (microbit-dal), `source/core/MicroBitFont.cpp`

https://github.com/lancaster-university/microbit-dal

```
The MIT License (MIT)

Copyright (c) 2016 British Broadcasting Corporation.
This software is provided by Lancaster University by arrangement with the BBC.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
```

## images.py — MicroPython for micro:bit, `source/microbit/microbitconstimage.cpp`

https://github.com/bbcmicrobit/micropython

```
The MIT License (MIT)

Copyright (c) 2015 Damien P. George

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

## melodies.py — MicroPython for micro:bit, `source/microbit/modmusictunes.c`

https://github.com/bbcmicrobit/micropython -- the same MIT License and
Damien P. George notice as `images.py` above, plus:

```
Copyright (c) 2015 Nicholas H. Tollervey

The music encoded herein is either in the public domain, composed by
Nicholas H.Tollervey or the composer is untraceable and covered by fair
(educational) use.
```

`sound.py` follows the timing and note format of `modmusic.cpp` from the same
repository (octave/duration persistence, 4 ticks per beat, 120 bpm, 10 ms
articulation).

## `export/firmware/micropython-microbit-v1.1.1.hex` — vendored firmware binary

https://github.com/bbcmicrobit/micropython/releases/tag/v1.1.1 (release asset,
SHA-256 `d3686e669677d456ece9d206a44b8acbe73ddf73e1a3211ff89b93972b953152`),
used by Stage X unit X8 (`extensions/microbit/export/hex_build.py`) to build a
ready-to-flash combined hex for a V1 board with no prior MicroPython flash
needed. The repository's top-level `LICENSE` (MIT) covers the compiled
release binary the same as its source — confirmed directly, not assumed:

```
The MIT License (MIT)

Copyright (c) 2013-2016 The MicroPython-on-micro:bit Developers, as listed
in the accompanying AUTHORS file

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

No SoftDevice/Nordic BLE binary blob is bundled in this firmware -- confirmed
via microbit-foundation/micropython-microbit-v2#51, which states MicroPython
does not support BLE from Python at all on either hardware revision, so there
is no third-party proprietary blob entangled with this release to separately
license.

## `export/hex_build.py` — ported from `tools/hexlifyscript.py` + `tools/makecombinedhex.py`

https://github.com/bbcmicrobit/micropython/blob/master/tools/hexlifyscript.py
https://github.com/bbcmicrobit/micropython/blob/master/tools/makecombinedhex.py

Same repository, same MIT License and copyright notice as the firmware binary
above. The embedding algorithm (the fixed `SCRIPT_ADDR`, the "MP" + length
header, the UICR-aware insertion point) is ported line-for-line in spirit;
only the file/argparse-based I/O is adapted to work on in-memory
strings/bytes, for testability without real hardware.

