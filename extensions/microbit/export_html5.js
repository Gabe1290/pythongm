// micro:bit simulator -- HTML5 export (docs/MICROBIT_STAGE_P_PLAN.md).
//
// Concatenated into engine.js at the __PYGM_EXTENSION_JS__ marker, like the
// other extensions' export_html5.js. H1: the pure simulator, a line-for-line
// port of extensions/microbit/simulator.py (+ sound.py and radio.py). H2: the
// 16 actions, the events and the per-frame update (handlers.py, runtime.py).
// H3: the layout and the canvas drawing (layout.py, renderer.py), through the
// engine's instance-overlay hook. Field names stay snake_case, identical to the Python object, so
// tools/microbit_js_parity.py can diff the two frame by frame. Later units add
// the actions, drawing and input on top. Everything lives in one function
// scope and is exposed on window.__pygmMicrobit.

(function () {
// <generated:tables> -- tools/gen_microbit_js_tables.py; do not edit by hand
const MB_GLYPHS = {"32": [0, 0, 0, 0, 0], "33": [8, 8, 8, 0, 8], "34": [10, 10, 0, 0, 0], "35": [10, 31, 10, 31, 10], "36": [14, 25, 14, 19, 14], "37": [25, 18, 4, 9, 19], "38": [12, 18, 12, 18, 13], "39": [8, 8, 0, 0, 0], "40": [4, 8, 8, 8, 4], "41": [8, 4, 4, 4, 8], "42": [0, 10, 4, 10, 0], "43": [0, 4, 14, 4, 0], "44": [0, 0, 0, 4, 8], "45": [0, 0, 14, 0, 0], "46": [0, 0, 0, 8, 0], "47": [1, 2, 4, 8, 16], "48": [12, 18, 18, 18, 12], "49": [4, 12, 4, 4, 14], "50": [28, 2, 12, 16, 30], "51": [30, 2, 4, 18, 12], "52": [6, 10, 18, 31, 2], "53": [31, 16, 30, 1, 30], "54": [2, 4, 14, 17, 14], "55": [31, 2, 4, 8, 16], "56": [14, 17, 14, 17, 14], "57": [14, 17, 14, 4, 8], "58": [0, 8, 0, 8, 0], "59": [0, 4, 0, 4, 8], "60": [2, 4, 8, 4, 2], "61": [0, 14, 0, 14, 0], "62": [8, 4, 2, 4, 8], "63": [14, 17, 6, 0, 4], "64": [14, 17, 21, 19, 12], "65": [12, 18, 30, 18, 18], "66": [28, 18, 28, 18, 28], "67": [14, 16, 16, 16, 14], "68": [28, 18, 18, 18, 28], "69": [30, 16, 28, 16, 30], "70": [30, 16, 28, 16, 16], "71": [14, 16, 19, 17, 14], "72": [18, 18, 30, 18, 18], "73": [28, 8, 8, 8, 28], "74": [31, 2, 2, 18, 12], "75": [18, 20, 24, 20, 18], "76": [16, 16, 16, 16, 30], "77": [17, 27, 21, 17, 17], "78": [17, 25, 21, 19, 17], "79": [12, 18, 18, 18, 12], "80": [28, 18, 28, 16, 16], "81": [12, 18, 18, 12, 6], "82": [28, 18, 28, 18, 17], "83": [14, 16, 12, 2, 28], "84": [31, 4, 4, 4, 4], "85": [18, 18, 18, 18, 12], "86": [17, 17, 17, 10, 4], "87": [17, 17, 21, 27, 17], "88": [18, 18, 12, 18, 18], "89": [17, 10, 4, 4, 4], "90": [30, 4, 8, 16, 30], "91": [14, 8, 8, 8, 14], "92": [16, 8, 4, 2, 1], "93": [14, 2, 2, 2, 14], "94": [4, 10, 0, 0, 0], "95": [0, 0, 0, 0, 31], "96": [8, 4, 0, 0, 0], "97": [0, 14, 18, 18, 15], "98": [16, 16, 28, 18, 28], "99": [0, 14, 16, 16, 14], "100": [2, 2, 14, 18, 14], "101": [12, 18, 28, 16, 14], "102": [6, 8, 28, 8, 8], "103": [14, 18, 14, 2, 12], "104": [16, 16, 28, 18, 18], "105": [8, 0, 8, 8, 8], "106": [2, 0, 2, 2, 12], "107": [16, 20, 24, 20, 18], "108": [8, 8, 8, 8, 6], "109": [0, 27, 21, 17, 17], "110": [0, 28, 18, 18, 18], "111": [0, 12, 18, 18, 12], "112": [0, 28, 18, 28, 16], "113": [0, 14, 18, 14, 2], "114": [0, 14, 16, 16, 16], "115": [0, 6, 8, 4, 24], "116": [8, 8, 14, 8, 7], "117": [0, 18, 18, 18, 15], "118": [0, 17, 17, 10, 4], "119": [0, 17, 17, 21, 27], "120": [0, 18, 12, 12, 18], "121": [0, 17, 10, 4, 24], "122": [0, 30, 4, 8, 30], "123": [6, 4, 12, 4, 6], "124": [8, 8, 8, 8, 8], "125": [24, 8, 12, 8, 24], "126": [0, 0, 12, 3, 0]};
const MB_IMAGES = {"HEART": ["09090", "99999", "99999", "09990", "00900"], "HEART_SMALL": ["00000", "09090", "09990", "00900", "00000"], "HAPPY": ["00000", "09090", "00000", "90009", "09990"], "SMILE": ["00000", "00000", "00000", "90009", "09990"], "SAD": ["00000", "09090", "00000", "09990", "90009"], "CONFUSED": ["00000", "09090", "00000", "09090", "90909"], "ANGRY": ["90009", "09090", "00000", "99999", "90909"], "ASLEEP": ["00000", "99099", "00000", "09990", "00000"], "SURPRISED": ["09090", "00000", "00900", "09090", "00900"], "SILLY": ["90009", "00000", "99999", "00909", "00999"], "FABULOUS": ["99999", "99099", "00000", "09090", "09990"], "MEH": ["09090", "00000", "00090", "00900", "09000"], "YES": ["00000", "00009", "00090", "90900", "09000"], "NO": ["90009", "09090", "00900", "09090", "90009"], "CLOCK12": ["00900", "00900", "00900", "00000", "00000"], "CLOCK1": ["00090", "00090", "00900", "00000", "00000"], "CLOCK2": ["00000", "00099", "00900", "00000", "00000"], "CLOCK3": ["00000", "00000", "00999", "00000", "00000"], "CLOCK4": ["00000", "00000", "00900", "00099", "00000"], "CLOCK5": ["00000", "00000", "00900", "00090", "00090"], "CLOCK6": ["00000", "00000", "00900", "00900", "00900"], "CLOCK7": ["00000", "00000", "00900", "09000", "09000"], "CLOCK8": ["00000", "00000", "00900", "99000", "00000"], "CLOCK9": ["00000", "00000", "99900", "00000", "00000"], "CLOCK10": ["00000", "99000", "00900", "00000", "00000"], "CLOCK11": ["09000", "09000", "00900", "00000", "00000"], "ARROW_N": ["00900", "09990", "90909", "00900", "00900"], "ARROW_NE": ["00999", "00099", "00909", "09000", "90000"], "ARROW_E": ["00900", "00090", "99999", "00090", "00900"], "ARROW_SE": ["90000", "09000", "00909", "00099", "00999"], "ARROW_S": ["00900", "00900", "90909", "09990", "00900"], "ARROW_SW": ["00009", "00090", "90900", "99000", "99900"], "ARROW_W": ["00900", "09000", "99999", "09000", "00900"], "ARROW_NW": ["99900", "99000", "90900", "00090", "00009"], "TRIANGLE": ["00000", "00900", "09090", "99999", "00000"], "TRIANGLE_LEFT": ["90000", "99000", "90900", "90090", "99999"], "CHESSBOARD": ["09090", "90909", "09090", "90909", "09090"], "DIAMOND": ["00900", "09090", "90009", "09090", "00900"], "DIAMOND_SMALL": ["00000", "00900", "09090", "00900", "00000"], "SQUARE": ["99999", "90009", "90009", "90009", "99999"], "SQUARE_SMALL": ["00000", "09990", "09090", "09990", "00000"], "RABBIT": ["90900", "90900", "99990", "99090", "99990"], "COW": ["90009", "90009", "99999", "09990", "00900"], "MUSIC_CROTCHET": ["00900", "00900", "00900", "99900", "99900"], "MUSIC_QUAVER": ["00900", "00990", "00909", "99900", "99900"], "MUSIC_QUAVERS": ["09999", "09009", "09009", "99099", "99099"], "PITCHFORK": ["90909", "90909", "99999", "00900", "00900"], "XMAS": ["00900", "09990", "00900", "09990", "99999"], "PACMAN": ["09999", "99090", "99900", "99990", "09999"], "TARGET": ["00900", "09990", "99099", "09990", "00900"], "TSHIRT": ["99099", "99999", "09990", "09990", "09990"], "ROLLERSKATE": ["00099", "00099", "99999", "99999", "09090"], "DUCK": ["09900", "99900", "09999", "09990", "00000"], "HOUSE": ["00900", "09990", "99999", "09990", "09090"], "TORTOISE": ["00000", "09990", "99999", "09090", "00000"], "BUTTERFLY": ["99099", "99999", "00900", "99999", "99099"], "STICKFIGURE": ["00900", "99999", "00900", "09090", "90009"], "GHOST": ["99999", "90909", "99999", "99999", "90909"], "SWORD": ["00900", "00900", "00900", "09990", "00900"], "GIRAFFE": ["99000", "09000", "09000", "09990", "09090"], "SKULL": ["09990", "90909", "99999", "09990", "09990"], "UMBRELLA": ["09990", "99999", "00900", "90900", "09900"], "SNAKE": ["99000", "99099", "09090", "09990", "00000"], "SCISSORS": ["99009", "99090", "00900", "99090", "99009"]};
const MB_MELODIES = {"DADADADUM": ["r4:2", "g", "g", "g", "eb:8", "r:2", "f", "f", "f", "d:8"], "ENTERTAINER": ["d4:1", "d#", "e", "c5:2", "e4:1", "c5:2", "e4:1", "c5:3", "c:1", "d", "d#", "e", "c", "d", "e:2", "b4:1", "d5:2", "c:4"], "PRELUDE": ["c4:1", "e", "g", "c5", "e", "g4", "c5", "e", "c4", "e", "g", "c5", "e", "g4", "c5", "e", "c4", "d", "g", "d5", "f", "g4", "d5", "f", "c4", "d", "g", "d5", "f", "g4", "d5", "f", "b3", "d4", "g", "d5", "f", "g4", "d5", "f", "b3", "d4", "g", "d5", "f", "g4", "d5", "f", "c4", "e", "g", "c5", "e", "g4", "c5", "e", "c4", "e", "g", "c5", "e", "g4", "c5", "e"], "ODE": ["e4", "e", "f", "g", "g", "f", "e", "d", "c", "c", "d", "e", "e:6", "d:2", "d:8", "e:4", "e", "f", "g", "g", "f", "e", "d", "c", "c", "d", "e", "d:6", "c:2", "c:8"], "NYAN": ["f#5:2", "g#", "c#:1", "d#:2", "b4:1", "d5:1", "c#", "b4:2", "b", "c#5", "d", "d:1", "c#", "b4:1", "c#5:1", "d#", "f#", "g#", "d#", "f#", "c#", "d", "b4", "c#5", "b4", "d#5:2", "f#", "g#:1", "d#", "f#", "c#", "d#", "b4", "d5", "d#", "d", "c#", "b4", "c#5", "d:2", "b4:1", "c#5", "d#", "f#", "c#", "d", "c#", "b4", "c#5:2", "b4", "c#5", "b4", "f#:1", "g#", "b:2", "f#:1", "g#", "b", "c#5", "d#", "b4", "e5", "d#", "e", "f#", "b4:2", "b", "f#:1", "g#", "b", "f#", "e5", "d#", "c#", "b4", "f#", "d#", "e", "f#", "b:2", "f#:1", "g#", "b:2", "f#:1", "g#", "b", "b", "c#5", "d#", "b4", "f#", "g#", "f#", "b:2", "b:1", "a#", "b", "f#", "g#", "b", "e5", "d#", "e", "f#", "b4:2", "c#5"], "RINGTONE": ["c4:1", "d", "e:2", "g", "d:1", "e", "f:2", "a", "e:1", "f", "g:2", "b", "c5:4"], "FUNK": ["c2:2", "c", "d#", "c:1", "f:2", "c:1", "f:2", "f#", "g", "c", "c", "g", "c:1", "f#:2", "c:1", "f#:2", "f", "d#"], "BLUES": ["c2:2", "e", "g", "a", "a#", "a", "g", "e", "c2:2", "e", "g", "a", "a#", "a", "g", "e", "f", "a", "c3", "d", "d#", "d", "c", "a2", "c2:2", "e", "g", "a", "a#", "a", "g", "e", "g", "b", "d3", "f", "f2", "a", "c3", "d#", "c2:2", "e", "g", "e", "g", "f", "e", "d"], "BIRTHDAY": ["c4:3", "c:1", "d:4", "c:4", "f", "e:8", "c:3", "c:1", "d:4", "c:4", "g", "f:8", "c:3", "c:1", "c5:4", "a4", "f", "e", "d", "a#:3", "a#:1", "a:4", "f", "g", "f:8"], "WEDDING": ["c4:4", "f:3", "f:1", "f:8", "c:4", "g:3", "e:1", "f:8", "c:4", "f:3", "a:1", "c5:4", "a4:3", "f:1", "f:4", "e:3", "f:1", "g:8"], "FUNERAL": ["c3:4", "c:3", "c:1", "c:4", "d#:3", "d:1", "d:3", "c:1", "c:3", "b2:1", "c3:4"], "PUNCHLINE": ["c4:3", "g3:1", "f#", "g", "g#:3", "g", "r", "b", "c4"], "PYTHON": ["d5:1", "b4", "r", "b", "b", "a#", "b", "g5", "r", "d", "d", "r", "b4", "c5", "r", "c", "c", "r", "d", "e:5", "c:1", "a4", "r", "a", "a", "g#", "a", "f#5", "r", "e", "e", "r", "c", "b4", "r", "b", "b", "r", "c5", "d:5", "d:1", "b4", "r", "b", "b", "a#", "b", "b5", "r", "g", "g", "r", "d", "c#", "r", "a", "a", "r", "a", "a:5", "g:1", "f#:2", "a:1", "a", "g#", "a", "e:2", "a:1", "a", "g#", "a", "d", "r", "c#", "d", "r", "c#", "d:2", "r:3"], "BADDY": ["c3:3", "r", "d:2", "d#", "r", "c", "r", "f#:8"], "CHASE": ["a4:1", "b", "c5", "b4", "a:2", "r", "a:1", "b", "c5", "b4", "a:2", "r", "a:2", "e5", "d#", "e", "f", "e", "d#", "e", "b4:1", "c5", "d", "c", "b4:2", "r", "b:1", "c5", "d", "c", "b4:2", "r", "b:2", "e5", "d#", "e", "f", "e", "d#", "e"], "BA_DING": ["b5:1", "e6:3"], "WAWAWAWAA": ["e3:3", "r:1", "d#:3", "r:1", "d:4", "r:1", "c#:8"], "JUMP_UP": ["c5:1", "d", "e", "f", "g"], "JUMP_DOWN": ["g5:1", "f", "e", "d", "c"], "POWER_UP": ["g4:1", "c5", "e", "g:2", "e:1", "g:3"], "POWER_DOWN": ["g5:1", "d#", "c", "g4:2", "b:1", "c5:3"]};
const MB_EVENT_FIXED = {"button:a": "microbit_button_a", "button:b": "microbit_button_b", "button:ab": "microbit_button_ab", "logo:touched": "microbit_logo_touched", "pin:0": "microbit_pin_0", "pin:1": "microbit_pin_1", "pin:2": "microbit_pin_2", "sound:loud": "microbit_loud_sound", "sound:quiet": "microbit_quiet_sound", "display_done:": "microbit_display_done", "sound_done:": "microbit_sound_done"};
const MB_GESTURE_EVENTS = {"shake": "shake", "up": "logo_up", "down": "logo_down", "left": "tilt_left", "right": "tilt_right", "face up": "screen_up", "face down": "screen_down", "freefall": "free_fall", "2g": "2g", "3g": "3g", "6g": "6g", "8g": "8g"};
// </generated:tables>

const WIDTH = 5;
const HEIGHT = 5;
const MAX_BRIGHTNESS = 9;
const SCROLL_DELAY = 0.150;
const MAX_QUEUE = 16;
const MAX_SOUND_QUEUE = 16;
const MAX_RADIO_OUTBOX = 32;

const SAMPLE_PERIOD = 0.020;
const TILT_TOLERANCE = 200;
const FREEFALL_TOLERANCE = 400;
const SHAKE_TOLERANCE = 400;
const SHAKE_COUNT_THRESHOLD = 4;
const SHAKE_DAMPING = 10;
const SHAKE_RTX = 30;
const GESTURE_DAMPING = 5;
const IMPULSES = [['2g', 2048], ['3g', 3072], ['6g', 6144], ['8g', 8192]];
const MAX_SAMPLES_PER_UPDATE = 50;
const REST_ACCELERATION = [0, 0, -1024];
const LOUD_THRESHOLD = 196;
const QUIET_THRESHOLD = 118;
const BUTTONS = ['a', 'b'];
const PINS = [0, 1, 2];

const DEFAULT_BPM = 120;
const DEFAULT_TICKS = 4;
const DEFAULT_OCTAVE = 4;
const DEFAULT_DURATION = 4;
const ARTICULATION = 0.010;
const MAX_FREQUENCY = 20000;
const PERIODS_US = {A: 2273, B: 2025, C: 3822, D: 3405, E: 3034, F: 2863, G: 2551};
const SHARPS_US = {A: 2145, C: 3608, D: 3214, F: 2703, G: 2408};
const ENHARMONIC = {'E#': ['F', 0], 'B#': ['C', 1], 'Cb': ['B', -1], 'Fb': ['E', 0]};
const FLAT_OF = {A: 'G', B: 'A', D: 'C', E: 'D', G: 'F'};

const MIN_GROUP = 0;
const MAX_GROUP = 255;
const MAX_MESSAGE = 32;

function sameValue(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
function isDigits(s) { return /^[0-9]+$/.test(s); }
function pyInt(v) { return Math.trunc(Number(v)); }
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
function blank() {
    const g = [];
    for (let y = 0; y < HEIGHT; y++) g.push(new Array(WIDTH).fill(0));
    return g;
}
function copyGrid(g) { return g.map(row => row.slice()); }

// -- display --------------------------------------------------------------

function parseImage(spec) {
    if (typeof spec !== 'string') throw new Error('not an image: ' + spec);
    const text = spec.trim();
    let rows = MB_IMAGES[text.toUpperCase()];
    if (rows === undefined) {
        rows = text.replace(/:+$/, '').split(':');
        if (rows.length !== HEIGHT || rows.some(r => r.length !== WIDTH || !isDigits(r))) {
            throw new Error('not an image: ' + spec);
        }
    }
    return rows.map(row => Array.from(row).map(ch => parseInt(ch, 10)));
}

function glyph(ch) {
    const rows = MB_GLYPHS[String(ch.codePointAt(0))];
    return rows !== undefined ? rows : MB_GLYPHS['63'];   // 63 = '?'
}

function glyphImage(ch) {
    const rows = glyph(ch);
    return rows.map(row => {
        const out = [];
        for (let x = 0; x < WIDTH; x++) out.push((row & (0x10 >> x)) ? MAX_BRIGHTNESS : 0);
        return out;
    });
}

function textColumns(text) {
    const columns = [];
    Array.from(text).forEach((ch, i) => {
        if (i) columns.push(new Array(HEIGHT).fill(0));
        const grid = glyphImage(ch);
        for (let x = 0; x < WIDTH; x++) {
            const col = [];
            for (let y = 0; y < HEIGHT; y++) col.push(grid[y][x]);
            columns.push(col);
        }
    });
    return columns;
}

function scrollFrames(text) {
    const blankCol = new Array(HEIGHT).fill(0);
    const pad = [];
    for (let i = 0; i < WIDTH; i++) pad.push(blankCol);
    const strip = pad.concat(textColumns(text), pad);
    const frames = [];
    for (let start = 1; start < strip.length - WIDTH + 1; start++) {
        const win = strip.slice(start, start + WIDTH);
        const frame = [];
        for (let y = 0; y < HEIGHT; y++) {
            const row = [];
            for (let x = 0; x < WIDTH; x++) row.push(win[x][y]);
            frame.push(row);
        }
        frames.push(frame);
    }
    return frames;
}

function formatNumber(value) {
    return String(value);
}

class Frame {
    constructor(grid, hold) { this.kind = 'frame'; this.frames = [grid]; this.step = Math.max(0.0, Number(hold)); }
    get duration() { return this.step; }
}
class Scroll {
    constructor(frames, step) { this.kind = 'scroll'; this.frames = frames; this.step = Math.max(0.001, Number(step)); }
    get duration() { return this.step * this.frames.length; }
}

// -- sound ----------------------------------------------------------------

function periodUs(letter, sharp, octave) {
    const base = sharp ? SHARPS_US[letter] : PERIODS_US[letter];
    const shift = octave - 4;
    return shift >= 0 ? Math.floor(base / Math.pow(2, shift)) : base * Math.pow(2, -shift);
}

function noteFrequency(letter, accidental, octave) {
    letter = letter.toUpperCase();
    const key = letter + accidental;
    let sharp;
    if (Object.prototype.hasOwnProperty.call(ENHARMONIC, key)) {
        const e = ENHARMONIC[key];
        letter = e[0];
        octave += e[1];
        sharp = false;
    } else if (accidental === '#') {
        sharp = true;
    } else if (accidental === 'b') {
        letter = FLAT_OF[letter];
        sharp = true;
    } else {
        sharp = false;
    }
    const period = periodUs(letter, sharp, octave);
    return period > 0 ? Math.min(MAX_FREQUENCY, 1000000.0 / period) : 0.0;
}

function parseNote(text, state) {
    const token = text.trim();
    if (!token) throw new Error('empty note');
    const letter = token[0].toUpperCase();
    if ('ABCDEFGR'.indexOf(letter) < 0) throw new Error('not a note: ' + text);
    let pos = 1;
    let accidental = '';
    if (letter !== 'R' && pos < token.length && (token[pos] === '#' || token[pos] === 'b')) {
        accidental = token[pos];
        pos += 1;
    }
    if (pos < token.length && token[pos] !== ':') {
        if (!isDigits(token[pos])) throw new Error('bad octave in ' + text);
        state.octave = parseInt(token[pos], 10);
        pos += 1;
    }
    if (pos < token.length) {
        if (token[pos] !== ':' || !isDigits(token.slice(pos + 1))) throw new Error('bad duration in ' + text);
        state.duration = parseInt(token.slice(pos + 1), 10);
    }
    const freq = letter === 'R' ? 0.0 : noteFrequency(letter, accidental, state.octave);
    return [freq, state.duration];
}

function melodyNotes(spec, bpm, ticks) {
    if (bpm === undefined) bpm = DEFAULT_BPM;
    if (ticks === undefined) ticks = DEFAULT_TICKS;
    if (typeof spec === 'string') {
        const named = MB_MELODIES[spec.trim().toUpperCase()];
        spec = named !== undefined ? named : spec.split(/\s+/).filter(s => s.length);
    }
    if (!spec || !spec.length) throw new Error('no notes');
    bpm = Math.max(1, pyInt(bpm));
    const tickSeconds = (60.0 / bpm) / ticks;
    const state = {octave: DEFAULT_OCTAVE, duration: DEFAULT_DURATION};
    const steps = [];
    for (const text of spec) {
        const fd = parseNote(String(text), state);
        const sounding = Math.max(ARTICULATION, tickSeconds * fd[1] - ARTICULATION);
        steps.push([fd[0], sounding]);
        steps.push([0.0, ARTICULATION]);
    }
    return steps;
}

function toneNotes(frequency, milliseconds) {
    const freq = Math.max(0.0, Math.min(MAX_FREQUENCY, Number(frequency)));
    return [[freq, Math.max(0.001, Number(milliseconds) / 1000.0)]];
}

// -- radio ----------------------------------------------------------------

function clampGroup(value) {
    const n = parseFloat(value);
    if (!isFinite(n)) return MIN_GROUP;
    return Math.max(MIN_GROUP, Math.min(MAX_GROUP, Math.trunc(n)));
}

function cleanMessage(value) {
    if (typeof value === 'boolean') return value ? 1 : 0;
    if (typeof value === 'number') return value;
    return String(value).slice(0, MAX_MESSAGE);
}

function asNumber(value) {
    if (typeof value === 'number') return value;
    const text = String(value).trim();
    if (text === '' || isNaN(Number(text))) return 0;
    return Number(text);
}

function deliver(sims) {
    let delivered = 0;
    for (const sender of sims) {
        const messages = sender.take_radio_outbox();
        if (!messages.length) continue;
        for (const receiver of sims) {
            if (receiver === sender || receiver.radio_group !== sender.radio_group) continue;
            for (const message of messages) {
                receiver.radio_receive(message);
                delivered += 1;
            }
        }
    }
    return delivered;
}

// -- the simulator --------------------------------------------------------

class MicrobitSimulator {
    constructor() {
        this.display = blank();
        this.brightness = 255;
        this._queue = [];
        this._elapsed = 0.0;
        this.buttons = {a: false, b: false};
        this.logo_touched = false;
        this.pins_touched = {0: false, 1: false, 2: false};
        this.pins_analog = {0: 0, 1: 0, 2: 0};
        this.acceleration = REST_ACCELERATION.slice();
        this.compass_heading = 0;
        this.light_level = 0;
        this.temperature = 21;
        this.sound_level = 0;
        this.tone = 0.0;
        this._sound = [];
        this._step = 0;
        this._step_elapsed = 0.0;
        this.radio_group = 0;
        this._radio_outbox = [];
        this._pending = [];
        this._sample_clock = 0.0;
        this.current_gesture = '';
        this._candidate = null;
        this._sigma = 0;
        this._shake_sign = {x: false, y: false, z: false};
        this._shake_count = 0;
        this._shake_timer = 0;
        this._shaken = false;
        this._impulses = new Set();
        this._impulse_sigma = 0;
        this._sound_state = 'quiet';
    }

    get_pixel(x, y) { return this.display[y][x]; }
    set_pixel(x, y, value) {
        if (x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT) {
            this.display[y][x] = Math.max(0, Math.min(MAX_BRIGHTNESS, pyInt(value)));
        }
    }
    set_brightness(value) { this.brightness = clamp(pyInt(value), 0, 255); }
    clear() { this._queue.length = 0; this._elapsed = 0.0; this.display = blank(); }
    get busy() { return this._queue.length > 0; }

    show_image(spec, hold) { return this._enqueue(new Frame(parseImage(spec), hold || 0.0)); }
    scroll_text(text, delay) { return this._enqueue(new Scroll(scrollFrames(String(text)), delay === undefined ? SCROLL_DELAY : delay)); }
    show_number(value, delay) {
        const text = formatNumber(value);
        if (Array.from(text).length === 1) return this._enqueue(new Frame(glyphImage(text), 0.0));
        return this.scroll_text(text, delay);
    }

    _enqueue(item) {
        if (!this._queue.length && item.kind === 'frame' && item.step === 0 &&
                sameValue(item.frames[0], this.display)) return true;
        if (this._queue.length && this._same(this._queue[this._queue.length - 1], item)) return true;
        if (this._queue.length >= MAX_QUEUE) return false;
        this._queue.push(item);
        if (this._queue.length === 1) {
            this._elapsed = 0.0;
            this.display = copyGrid(item.frames[0]);
        }
        return true;
    }
    _same(a, b) { return a.kind === b.kind && a.step === b.step && sameValue(a.frames, b.frames); }

    _advance_display(dt) {
        if (!this._queue.length) return;
        let remaining = dt;
        while (this._queue.length) {
            const item = this._queue[0];
            const left = item.duration - this._elapsed;
            if (remaining < left) {
                this._elapsed += remaining;
                const index = item.step ? Math.min(pyInt(this._elapsed / item.step), item.frames.length - 1) : 0;
                this.display = copyGrid(item.frames[index]);
                return;
            }
            remaining -= Math.max(0.0, left);
            this.display = copyGrid(item.frames[item.frames.length - 1]);
            this._queue.shift();
            this._elapsed = 0.0;
            if (this._queue.length) this.display = copyGrid(this._queue[0].frames[0]);
        }
        this._pending.push(['display_done', null]);
    }

    get sound_busy() { return this._sound.length > 0; }
    play_tone(frequency, milliseconds) {
        return this._enqueue_sound(toneNotes(frequency, milliseconds === undefined ? 500 : milliseconds));
    }
    play_melody(spec, bpm) { return this._enqueue_sound(melodyNotes(spec, bpm === undefined ? DEFAULT_BPM : bpm)); }
    stop_sound() {
        const wasBusy = this._sound.length > 0 || this.tone;
        this._sound.length = 0;
        this._step = 0;
        this._step_elapsed = 0.0;
        this.tone = 0.0;
        if (wasBusy) this._pending.push(['sound_stop', null]);
    }
    _enqueue_sound(steps) {
        if (this._sound.length && sameValue(this._sound[this._sound.length - 1], steps)) return true;
        if (this._sound.length >= MAX_SOUND_QUEUE) return false;
        this._sound.push(steps);
        if (this._sound.length === 1) {
            this._step = 0;
            this._step_elapsed = 0.0;
            this._begin_step();
        }
        return true;
    }
    _begin_step() {
        const hs = this._sound[0][this._step];
        this.tone = hs[0];
        this._pending.push(['sound_note', [hs[0], hs[1]]]);
    }
    _advance_sound(dt) {
        if (!this._sound.length) return;
        let remaining = dt;
        while (this._sound.length) {
            const seconds = this._sound[0][this._step][1];
            const left = seconds - this._step_elapsed;
            if (remaining < left) {
                this._step_elapsed += remaining;
                return;
            }
            remaining -= left;
            this._step += 1;
            this._step_elapsed = 0.0;
            if (this._step >= this._sound[0].length) {
                this._sound.shift();
                this._step = 0;
            }
            if (this._sound.length) this._begin_step();
        }
        if (this.tone) {
            this.tone = 0.0;
            this._pending.push(['sound_stop', null]);
        }
        this._pending.push(['sound_done', null]);
    }

    set_radio_group(group) { this.radio_group = clampGroup(group); }
    radio_send(value) {
        if (this._radio_outbox.length >= MAX_RADIO_OUTBOX) return false;
        this._radio_outbox.push(cleanMessage(value));
        return true;
    }
    take_radio_outbox() { const m = this._radio_outbox; this._radio_outbox = []; return m; }
    radio_receive(value) { this._pending.push(['radio', value]); }

    set_button(name, pressed) {
        name = String(name).toLowerCase();
        if (!(name in this.buttons)) throw new Error('no button ' + name);
        const was = this.buttons[name];
        this.buttons[name] = !!pressed;
        if (pressed && !was) {
            this._pending.push(['button', name]);
            const other = name === 'a' ? 'b' : 'a';
            if (this.buttons[other]) this._pending.push(['button', 'ab']);
        }
    }
    is_pressed(name) {
        name = String(name).toLowerCase();
        if (name === 'ab') return this.buttons.a && this.buttons.b;
        return this.buttons[name];
    }
    set_logo_touched(touched) {
        if (touched && !this.logo_touched) this._pending.push(['logo', 'touched']);
        this.logo_touched = !!touched;
    }
    set_pin_touched(pin, touched) {
        if (!(pin in this.pins_touched)) throw new Error('no touch pin ' + pin);
        if (touched && !this.pins_touched[pin]) this._pending.push(['pin', pin]);
        this.pins_touched[pin] = !!touched;
    }
    set_pin_analog(pin, value) {
        if (!(pin in this.pins_analog)) throw new Error('no pin ' + pin);
        this.pins_analog[pin] = clamp(pyInt(value), 0, 1023);
    }

    set_acceleration(x, y, z) { this.acceleration = [pyInt(x), pyInt(y), pyInt(z)]; }
    shake() {
        if (!this._shaken) {
            this._shaken = true;
            this._shake_count = SHAKE_COUNT_THRESHOLD;
            this._shake_timer = 0;
            this.current_gesture = 'shake';
            this._pending.push(['gesture', 'shake']);
        }
    }
    set_compass_heading(degrees) { const d = pyInt(degrees); this.compass_heading = ((d % 360) + 360) % 360; }
    set_light_level(value) { this.light_level = clamp(pyInt(value), 0, 255); }
    set_temperature(celsius) { this.temperature = pyInt(celsius); }
    set_sound_level(value) {
        this.sound_level = clamp(pyInt(value), 0, 255);
        if (this._sound_state !== 'loud' && this.sound_level > LOUD_THRESHOLD) {
            this._sound_state = 'loud';
            this._pending.push(['sound', 'loud']);
        } else if (this._sound_state !== 'quiet' && this.sound_level < QUIET_THRESHOLD) {
            this._sound_state = 'quiet';
            this._pending.push(['sound', 'quiet']);
        }
    }

    _posture() {
        const [x, y, z] = this.acceleration;
        let detected = false;
        for (const [axis, value] of [['x', x], ['y', y], ['z', z]]) {
            const sign = this._shake_sign[axis];
            if ((value < -SHAKE_TOLERANCE && sign) || (value > SHAKE_TOLERANCE && !sign)) {
                detected = true;
                this._shake_sign[axis] = !sign;
            }
        }
        if (detected && this._shake_count < SHAKE_COUNT_THRESHOLD) {
            this._shake_count += 1;
            if (this._shake_count === 1) this._shake_timer = 0;
            if (this._shake_count === SHAKE_COUNT_THRESHOLD) {
                this._shaken = true;
                this._shake_timer = 0;
                return 'shake';
            }
        }
        if (this._shake_count > 0) {
            this._shake_timer += 1;
            if (this._shaken && this._shake_timer >= SHAKE_RTX) {
                this._shaken = false;
                this._shake_timer = 0;
                this._shake_count = 0;
            } else if (!this._shaken && this._shake_timer >= SHAKE_DAMPING) {
                this._shake_timer = 0;
                this._shake_count -= 1;
            }
        }
        if (x * x + y * y + z * z < FREEFALL_TOLERANCE * FREEFALL_TOLERANCE) return 'freefall';
        if (x < -1000 + TILT_TOLERANCE) return 'left';
        if (x > 1000 - TILT_TOLERANCE) return 'right';
        if (y < -1000 + TILT_TOLERANCE) return 'down';
        if (y > 1000 - TILT_TOLERANCE) return 'up';
        if (z < -1000 + TILT_TOLERANCE) return 'face up';
        if (z > 1000 - TILT_TOLERANCE) return 'face down';
        return '';
    }

    _sample() {
        const [x, y, z] = this.acceleration;
        const force = x * x + y * y + z * z;
        if (force > IMPULSES[0][1] * IMPULSES[0][1]) {
            for (const [name, tolerance] of IMPULSES) {
                if (force > tolerance * tolerance && !this._impulses.has(name)) {
                    this._impulses.add(name);
                    this._pending.push(['gesture', name]);
                }
            }
            this._impulse_sigma = 0;
        }
        if (this._impulse_sigma < GESTURE_DAMPING) this._impulse_sigma += 1;
        else this._impulses.clear();

        const posture = this._posture();
        if (posture === 'shake') {
            this.current_gesture = 'shake';
            this._pending.push(['gesture', 'shake']);
            return;
        }
        if (posture === this._candidate) {
            if (this._sigma < GESTURE_DAMPING) this._sigma += 1;
        } else {
            this._candidate = posture;
            this._sigma = 0;
        }
        if (this._candidate !== this.current_gesture && this._sigma >= GESTURE_DAMPING) {
            this.current_gesture = this._candidate;
            if (this.current_gesture) this._pending.push(['gesture', this.current_gesture]);
        }
    }

    update(dt) {
        dt = Math.max(0.0, Number(dt));
        this._sample_clock += dt;
        let samples = 0;
        while (this._sample_clock >= SAMPLE_PERIOD && samples < MAX_SAMPLES_PER_UPDATE) {
            this._sample_clock -= SAMPLE_PERIOD;
            this._sample();
            samples += 1;
        }
        if (samples === MAX_SAMPLES_PER_UPDATE) this._sample_clock = 0.0;
        this._advance_display(dt);
        this._advance_sound(dt);
        const events = this._pending;
        this._pending = [];
        return events;
    }
}

// -- boards, values, events (H2) -------------------------------------------
// A board is any instance of a microbit*-named object, an object with
// is_microbit, or a room entry that sets it (mirrors on_instance_created in
// extensions/microbit/__init__.py). The simulator is attached lazily.

function boardOf(inst) {
    if (!inst) return null;
    if (inst._mb !== undefined) return inst._mb;
    const name = String(inst.name || '').toLowerCase();
    const od = inst.objectData || {};
    const id = inst.instanceData || {};
    const isBoard = name.startsWith('microbit') || !!inst.is_microbit || !!od.is_microbit || !!id.is_microbit;
    inst._mb = isBoard ? new MicrobitSimulator() : null;
    return inst._mb;
}

// A value param: blank -> default; "quoted" -> that text; a number; else an
// expression / variable through the engine's evaluator (as _parse_value does).
function mbValue(inst, raw, game, dflt) {
    if (raw === undefined || raw === null || raw === '') return dflt;
    if (typeof raw === 'number' || typeof raw === 'boolean') return raw;
    const t = String(raw).trim();
    if (t === '') return dflt;
    if (t.length >= 2 && t[0] === '"' && t[t.length - 1] === '"') return t.slice(1, -1);
    const n = Number(t);
    if (!isNaN(n)) return n;
    let v;
    if (typeof gmExpressionValue === 'function') v = gmExpressionValue(t, inst, game);
    if (v === undefined || v === null || v === '') return /^[A-Za-z_][A-Za-z0-9_.]*$/.test(t) ? t : dflt;
    return v;
}
function mbInt(inst, raw, game, dflt) {
    const n = Math.trunc(Number(mbValue(inst, raw, game, dflt)));
    return isNaN(n) ? dflt : n;
}
function mbSeconds(inst, raw, game, dfltMs) {
    return Math.max(0.0, mbInt(inst, raw, game, dfltMs) / 1000.0);
}

const COMPARE = {
    '<': (a, b) => a < b, '<=': (a, b) => a <= b, '==': (a, b) => a === b,
    '>=': (a, b) => a >= b, '>': (a, b) => a > b, '!=': (a, b) => a !== b,
};
function mbCompare(left, comparison, right) {
    const fn = COMPARE[String(comparison).trim()] || COMPARE['>'];
    return fn(left, right);
}

function readSensor(sim, sensor) {
    const [x, y, z] = sim.acceleration;
    if (sensor === 'accelerometer x') return x;
    if (sensor === 'accelerometer y') return y;
    if (sensor === 'accelerometer z') return z;
    if (sensor === 'acceleration strength') return Math.round(Math.sqrt(x * x + y * y + z * z));
    if (sensor === 'compass heading') return sim.compass_heading;
    if (sensor === 'light level') return sim.light_level;
    if (sensor === 'temperature') return sim.temperature;
    if (sensor === 'sound level') return sim.sound_level;
    const m = /^pin ([0-9]+) analog$/.exec(sensor);
    if (m && Object.prototype.hasOwnProperty.call(sim.pins_analog, m[1])) return sim.pins_analog[m[1]];
    return null;
}

// What a simulator report fires: (kind, detail) -> event name (events.py).
function eventNameFor(kind, detail) {
    if (kind === 'radio') return 'microbit_radio_received';
    if (kind === 'gesture') {
        const suffix = MB_GESTURE_EVENTS[detail];
        return suffix ? 'microbit_gesture_' + suffix : null;
    }
    const name = MB_EVENT_FIXED[kind + ':' + (detail === null || detail === undefined ? '' : detail)];
    return name || null;
}

// Sound hooks (H5 fills these in; the reports are already delivered here).
const soundHooks = {note: null, stop: null};

// One step of every board in the room: radio delivery, the simulator, then the
// events each one reported (runtime.py's update_microbits).
function updateMicrobits(game) {
    const room = game && game.currentRoom;
    if (!room) return;
    const boards = [];
    for (const inst of room.instances) {
        const sim = boardOf(inst);
        if (sim) boards.push([inst, sim]);
    }
    if (!boards.length) return;
    deliver(boards.map(b => b[1]));
    const dt = 1.0 / Math.max(1, room.roomSpeed || 60);
    for (const [inst, sim] of boards) {
        const reported = sim.update(dt);
        if (!reported.length) continue;
        for (const [kind, detail] of reported) {
            if (kind === 'radio') {
                inst.radio_string = String(detail);
                inst.radio_number = asNumber(detail);
            } else if (kind === 'sound_note' && soundHooks.note) {
                soundHooks.note(detail[0], detail[1]);
            } else if (kind === 'sound_stop' && soundHooks.stop) {
                soundHooks.stop();
            }
        }
        const events = inst.events;
        if (!events) continue;
        for (const [kind, detail] of reported) {
            const name = eventNameFor(kind, detail);
            if (name && events[name]) inst.executeActions(events[name].actions || [], game);
        }
    }
}

// -- actions and conditions (handlers.py) -----------------------------------

const MB_ACTIONS = {
    microbit_show_image(inst, p, game, sim) {
        const spec = String(p.image === undefined ? 'HEART' : p.image).trim();
        try { sim.show_image(spec, mbSeconds(inst, p.hold, game, 0)); }
        catch (e) { console.warn('micro:bit: not an image: ' + spec); }
    },
    microbit_scroll_text(inst, p, game, sim) {
        const text = mbValue(inst, p.text === undefined ? '' : p.text, game, '');
        const delay = mbSeconds(inst, p.delay, game, SCROLL_DELAY * 1000);
        sim.scroll_text(String(text), delay || SCROLL_DELAY);
    },
    microbit_show_number(inst, p, game, sim) {
        let n = Number(mbValue(inst, p.value === undefined ? 0 : p.value, game, 0));
        if (isNaN(n)) n = 0;
        sim.show_number(n);
    },
    microbit_set_pixel(inst, p, game, sim) {
        sim.set_pixel(mbInt(inst, p.x, game, 0), mbInt(inst, p.y, game, 0),
            mbInt(inst, p.brightness === undefined ? MAX_BRIGHTNESS : p.brightness, game, MAX_BRIGHTNESS));
    },
    microbit_clear_display(inst, p, game, sim) { sim.clear(); },
    microbit_set_brightness(inst, p, game, sim) {
        sim.set_brightness(mbInt(inst, p.brightness === undefined ? 255 : p.brightness, game, 255));
    },
    microbit_play_tone(inst, p, game, sim) {
        sim.play_tone(mbInt(inst, p.frequency, game, 440), mbInt(inst, p.duration, game, 500));
    },
    microbit_play_melody(inst, p, game, sim) {
        const raw = p.melody === undefined ? '' : p.melody;
        const spec = String(String(raw).startsWith('"') ? mbValue(inst, raw, game, '') : raw).trim();
        try { sim.play_melody(spec, mbInt(inst, p.tempo, game, 120)); }
        catch (e) { console.warn('micro:bit: cannot play melody ' + spec); }
    },
    microbit_stop_sound(inst, p, game, sim) { sim.stop_sound(); },
    microbit_radio_set_group(inst, p, game, sim) { sim.set_radio_group(mbInt(inst, p.group, game, 0)); },
    microbit_radio_send(inst, p, game, sim) {
        sim.radio_send(mbValue(inst, p.value === undefined ? 1 : p.value, game, 1));
    },
    microbit_read_sensor(inst, p, game, sim) {
        const sensor = String(p.sensor || 'accelerometer x').trim().toLowerCase();
        const name = String(p.variable || 'sensor_value').trim();
        const value = readSensor(sim, sensor);
        if (value === null || !name) return;
        if (name.startsWith('global.')) game.globalVariables[name.slice(7)] = value;
        else inst[name] = value;
    },
};

const MB_CONDITIONS = {
    microbit_if_button(inst, p, game, sim) {
        const button = String(p.button === undefined ? 'a' : p.button).trim().toLowerCase();
        if (button === 'logo') return sim.logo_touched;
        return !!sim.is_pressed(button);
    },
    microbit_if_gesture(inst, p, game, sim) {
        return sim.current_gesture === String(p.gesture === undefined ? 'shake' : p.gesture).trim().toLowerCase();
    },
    microbit_if_tilt(inst, p, game, sim) {
        const axis = String(p.axis === undefined ? 'x' : p.axis).trim().toLowerCase();
        if (axis !== 'x' && axis !== 'y' && axis !== 'z') return false;
        return mbCompare(sim.acceleration['xyz'.indexOf(axis)], p.comparison === undefined ? '>' : p.comparison,
            mbInt(inst, p.value, game, 0));
    },
    microbit_if_pixel(inst, p, game, sim) {
        const x = mbInt(inst, p.x, game, 0), y = mbInt(inst, p.y, game, 0);
        if (!(x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT)) return false;
        return mbCompare(sim.get_pixel(x, y), p.comparison === undefined ? '>' : p.comparison,
            mbInt(inst, p.value, game, 0));
    },
};

// Only inside the engine: this file is also loaded on its own by the parity tool.
if (typeof registerExtensionAction === 'function') {
    for (const name of Object.keys(MB_ACTIONS)) {
        registerExtensionAction(name, (inst, params, game) => {
            const sim = boardOf(inst);
            if (sim) MB_ACTIONS[name](inst, params, game, sim);
        });
    }
    for (const name of Object.keys(MB_CONDITIONS)) {
        registerExtensionCondition(name, (inst, params, game) => {
            const sim = boardOf(inst);
            return sim ? MB_CONDITIONS[name](inst, params, game, sim) : false;
        });
    }
    registerFrameUpdate(updateMicrobits);
}

// -- layout (layout.py): where everything on the drawn board sits -------------

const BODY_W = 276;
const BODY_H = 224;
const LED_PITCH = 30;
const LED_SIZE = 18;
const LED_CENTER_DY = -10;
const BUTTON_DX = 106;
const BUTTON_RADIUS = 19;
const LOGO_DY = -95;
const LOGO_RX = 18;
const LOGO_RY = 11;
const PAD_PITCH = 45;
const PAD_W = 33;
const PAD_H = 28;
const PAD_NAMES = ['0', '1', '2', '3V', 'GND'];
const TOUCH_PINS = [0, 1, 2];
const OFF_COLOR = [62, 22, 22];
const ON_COLOR = [255, 52, 40];

const STRIP_GAP = 25;
const STRIP_PAD = 10;
const TILT_SIZE = 126;
const SHAKE_H = 28;
const RIGHT_CONTENT_W = 138;
const RIGHT_TOP_GAP = 18;
const SLIDER_STEP = 28;
const SLIDER_TRACK_H = 10;
const TILT_FULL = 1024;
const SLIDERS = {light: [0, 255], temperature: [-5, 50], compass: [0, 359], sound: [0, 255]};

// Python's round() goes to the even neighbour on an exact half; Math.round
// doesn't, and the layout is integer-snapped, so it has to match.
function pyRound(x) {
    const f = Math.floor(x), d = x - f;
    if (d < 0.5) return f;
    if (d > 0.5) return f + 1;
    return f % 2 === 0 ? f : f + 1;
}

function boardLayout(cx, cy, scale) {
    scale = Math.max(0.1, Number(scale));
    const s = v => v * scale;
    const bodyW = pyRound(s(BODY_W)), bodyH = pyRound(s(BODY_H));
    const body = [pyRound(cx - bodyW / 2), pyRound(cy - bodyH / 2), bodyW, bodyH];
    const gridCy = cy + s(LED_CENTER_DY);
    const leds = [];
    for (let y = 0; y < 5; y++) {
        const row = [];
        for (let x = 0; x < 5; x++) {
            row.push([pyRound(cx + (x - 2) * s(LED_PITCH)), pyRound(gridCy + (y - 2) * s(LED_PITCH))]);
        }
        leds.push(row);
    }
    const buttons = {
        a: [pyRound(cx - s(BUTTON_DX)), pyRound(gridCy), pyRound(s(BUTTON_RADIUS))],
        b: [pyRound(cx + s(BUTTON_DX)), pyRound(gridCy), pyRound(s(BUTTON_RADIUS))],
    };
    const logo = [pyRound(cx), pyRound(cy + s(LOGO_DY)), pyRound(s(LOGO_RX)), pyRound(s(LOGO_RY))];
    const padW = pyRound(s(PAD_W)), padH = pyRound(s(PAD_H));
    const padY = body[1] + bodyH - padH;
    const pads = {};
    PAD_NAMES.forEach((name, i) => {
        pads[name] = [pyRound(cx + (i - 2) * s(PAD_PITCH) - padW / 2), padY, padW, padH];
    });
    const speaker = [pyRound(cx + s(BUTTON_DX)), pyRound(cy + s(LOGO_DY)), Math.max(3, pyRound(s(7)))];
    return {cx, cy, scale, body, led_size: Math.max(2, pyRound(s(LED_SIZE))), leds, buttons, logo, pads, speaker};
}

function ledColor(level, brightness) {
    if (brightness === undefined) brightness = 255;
    const amount = Math.max(0, Math.min(9, level)) / 9.0 * Math.max(0, Math.min(255, brightness)) / 255.0;
    return OFF_COLOR.map((o, i) => Math.trunc(pyRound(o + (ON_COLOR[i] - o) * amount)));
}

function stripLayout(layout) {
    const s = layout.scale;
    const [bx, by, bw, bh] = layout.body;
    const cy = by + bh / 2;
    const pad = pyRound(STRIP_PAD * s);
    const gap = pyRound(STRIP_GAP * s);
    const tiltSize = pyRound(TILT_SIZE * s);
    const leftW = tiltSize + 2 * pad, leftH = tiltSize + 2 * pad;
    const leftX = bx - gap - leftW;
    const leftY = pyRound(cy - leftH / 2);
    const panelLeft = [leftX, leftY, leftW, leftH];
    const tilt = [leftX + pad, leftY + pad, tiltSize, tiltSize];
    const colW = pyRound(RIGHT_CONTENT_W * s);
    const shakeH = pyRound(SHAKE_H * s);
    const step = pyRound(SLIDER_STEP * s);
    const trackH = Math.max(3, pyRound(SLIDER_TRACK_H * s));
    const firstDy = pad + shakeH + pyRound(RIGHT_TOP_GAP * s);
    const rightH = firstDy + 3 * step + trackH + pad;
    const rightW = colW + 2 * pad;
    const rightX = bx + bw + gap;
    const rightY = pyRound(cy - rightH / 2);
    const panelRight = [rightX, rightY, rightW, rightH];
    const shake = [rightX + pad, rightY + pad, colW, shakeH];
    const sliders = {};
    Object.keys(SLIDERS).forEach((name, i) => {
        sliders[name] = [rightX + pad, rightY + firstDy + i * step, colW, trackH];
    });
    return {panel_left: panelLeft, panel_right: panelRight, tilt, shake, sliders};
}

function tiltToPos(rect, ax, ay) {
    const [px, py, pw, ph] = rect;
    const u = Math.max(-1.0, Math.min(1.0, ax / TILT_FULL));
    const v = Math.max(-1.0, Math.min(1.0, ay / TILT_FULL));
    return [pyRound(px + pw / 2 + u * pw / 2), pyRound(py + ph / 2 - v * ph / 2)];
}

function sliderFraction(name, value) {
    const [lo, hi] = SLIDERS[name];
    return Math.max(0.0, Math.min(1.0, (value - lo) / (hi - lo)));
}

// An authored per-board option: an instance variable wins, else the object's.
function optionOf(inst, name, dflt) {
    let v = inst[name];
    if (v === undefined || v === null) v = (inst.objectData || {})[name];
    return v === undefined || v === null ? dflt : v;
}

function scaleOf(inst) {
    const v = parseFloat(optionOf(inst, 'microbit_scale', 1.0));
    return isNaN(v) ? 1.0 : Math.max(0.1, v);
}

// The point the board is centred on: the instance's own point with no sprite,
// else the middle of its sprite.
function centerOf(inst) {
    const info = inst.sprite && inst.spriteInfo;
    if (!info) return [inst.x, inst.y];
    return [inst.x - info.origin_x + info.width / 2, inst.y - info.origin_y + info.height / 2];
}

function layoutFor(inst) {
    const [cx, cy] = centerOf(inst);
    return boardLayout(cx, cy, scaleOf(inst));
}

function stripVisible(inst) {
    const v = optionOf(inst, 'microbit_show_sensors', true);
    if (typeof v === 'string') return ['false', '0', 'no', ''].indexOf(v.trim().toLowerCase()) < 0;
    return !!v;
}

// -- drawing (renderer.py) on a canvas 2D context ------------------------------

const BODY_COLOR = [34, 36, 40];
const BODY_EDGE = [12, 12, 14];
const LED_WELL = [18, 8, 8];
const LED_CHIP = [140, 142, 148];
const BUTTON_COLOR = [205, 205, 200];
const BUTTON_DOWN = [255, 214, 90];
const BUTTON_EDGE = [110, 110, 105];
const LOGO_COLOR = [54, 199, 149];
const LOGO_TOUCHED = [150, 255, 210];
const LOGO_DOT = [16, 80, 62];
const PAD_COLOR = [196, 150, 60];
const PAD_TOUCHED = [255, 240, 150];
const PAD_EDGE = [80, 60, 20];
const PAD_HOLE = [70, 52, 18];
const LABEL_COLOR = [200, 200, 200];
const CORNER_GREEN = [54, 199, 149];
const TAG_LABEL = [16, 54, 42];
const PANEL_COLOR = [46, 48, 54];
const PANEL_EDGE = [20, 20, 24];
const PAD_WELL = [24, 26, 30];
const PAD_DOT = [255, 214, 90];
const TRACK_COLOR = [90, 92, 100];
const TRACK_FILL = [96, 170, 255];
const KNOB_COLOR = [230, 230, 235];
const SHAKE_COLOR = [96, 110, 150];
const SHAKE_ACTIVE = [255, 214, 90];
const SPEAKER_ON = [120, 220, 255];
const SPEAKER_OFF = [60, 62, 70];
const SLIDER_TITLES = {light: 'Light', temperature: 'Temp', compass: 'Compass', sound: 'Sound'};

function css(c) { return 'rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')'; }

function fillRect(ctx, color, r, radius) {
    ctx.fillStyle = css(color);
    if (radius && ctx.roundRect) { ctx.beginPath(); ctx.roundRect(r[0], r[1], r[2], r[3], radius); ctx.fill(); }
    else ctx.fillRect(r[0], r[1], r[2], r[3]);
}
// pygame's width-w outline sits INSIDE the rect.
function edgeRect(ctx, color, r, w, radius) {
    ctx.strokeStyle = css(color);
    ctx.lineWidth = w;
    const h = w / 2;
    if (radius && ctx.roundRect) { ctx.beginPath(); ctx.roundRect(r[0] + h, r[1] + h, r[2] - w, r[3] - w, radius); ctx.stroke(); }
    else ctx.strokeRect(r[0] + h, r[1] + h, r[2] - w, r[3] - w);
}
function disc(ctx, color, cx, cy, r) {
    ctx.fillStyle = css(color);
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, 2 * Math.PI); ctx.fill();
}
function ring(ctx, color, cx, cy, r, w) {
    ctx.strokeStyle = css(color);
    ctx.lineWidth = w;
    ctx.beginPath(); ctx.arc(cx, cy, Math.max(0, r - w / 2), 0, 2 * Math.PI); ctx.stroke();
}
function line(ctx, color, x1, y1, x2, y2) {
    ctx.strokeStyle = css(color);
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x1 + 0.5, y1 + 0.5); ctx.lineTo(x2 + 0.5, y2 + 0.5); ctx.stroke();
}
function polygon(ctx, color, pts) {
    ctx.fillStyle = css(color);
    ctx.beginPath();
    pts.forEach((p, i) => { if (i) ctx.lineTo(p[0], p[1]); else ctx.moveTo(p[0], p[1]); });
    ctx.closePath(); ctx.fill();
}
// Text: pygame's default font at `size` is ~0.72 of that in CSS pixels.
function label(ctx, text, size, color, x, y, align) {
    ctx.fillStyle = css(color);
    ctx.font = 'bold ' + Math.max(7, Math.round(size * 0.72)) + 'px sans-serif';
    ctx.textAlign = (align === 'center' || align === 'center-bottom') ? 'center' : 'left';
    ctx.textBaseline = align === 'center' ? 'middle' : (align === 'center-bottom' ? 'bottom' : 'top');
    ctx.fillText(text, x, y);
}

function sliderValue(sim, name) {
    return {light: sim.light_level, temperature: sim.temperature,
        compass: sim.compass_heading, sound: sim.sound_level}[name];
}

function drawStrip(ctx, strip, sim, scale) {
    const radius = Math.max(2, Math.trunc(8 * scale));
    for (const panel of [strip.panel_left, strip.panel_right]) {
        fillRect(ctx, PANEL_COLOR, panel, radius);
        edgeRect(ctx, PANEL_EDGE, panel, 1, radius);
    }
    const [tx, ty, tw, th] = strip.tilt;
    fillRect(ctx, PAD_WELL, strip.tilt);
    line(ctx, TRACK_COLOR, tx + Math.trunc(tw / 2), ty, tx + Math.trunc(tw / 2), ty + th - 1);
    line(ctx, TRACK_COLOR, tx, ty + Math.trunc(th / 2), tx + tw - 1, ty + Math.trunc(th / 2));
    edgeRect(ctx, PANEL_EDGE, strip.tilt, 1);
    const [ax, ay] = sim.acceleration;
    const dot = tiltToPos(strip.tilt, ax, ay);
    disc(ctx, PAD_DOT, dot[0], dot[1], Math.max(3, Math.trunc(6 * scale)));
    label(ctx, 'TILT', Math.max(11, Math.trunc(19 * scale)), LABEL_COLOR, tx + 3, ty + 2);

    const [sx, sy, sw, sh] = strip.shake;
    const active = sim.current_gesture === 'shake';
    fillRect(ctx, active ? SHAKE_ACTIVE : SHAKE_COLOR, strip.shake, 4);
    label(ctx, 'SHAKE', Math.max(12, Math.trunc(21 * scale)), active ? [20, 20, 20] : [235, 235, 240],
        sx + Math.trunc(sw / 2), sy + Math.trunc(sh / 2), 'center');

    for (const name of Object.keys(strip.sliders)) {
        const [kx, ky, kw, kh] = strip.sliders[name];
        const value = sliderValue(sim, name);
        const size = Math.max(11, Math.trunc(19 * scale));
        label(ctx, SLIDER_TITLES[name] + ' ' + value, size, LABEL_COLOR, kx, ky - Math.round(size * 0.72) - 3);
        fillRect(ctx, TRACK_COLOR, [kx, ky, kw, kh], Math.trunc(kh / 2));
        const filled = Math.trunc(kw * sliderFraction(name, value));
        if (filled) fillRect(ctx, TRACK_FILL, [kx, ky, filled, kh], Math.trunc(kh / 2));
        disc(ctx, KNOB_COLOR, kx + filled, ky + Math.trunc(kh / 2), Math.max(3, Math.trunc(kh / 2) + 2));
    }
}

function drawBoard(ctx, layout, sim, drawBody) {
    if (drawBody) {
        const [bx, by, bw, bh] = layout.body;
        fillRect(ctx, BODY_COLOR, layout.body);
        edgeRect(ctx, BODY_EDGE, layout.body, 2);
        polygon(ctx, CORNER_GREEN, [[bx, by], [bx + bw * 0.42, by], [bx + bw * 0.30, by + bh * 0.12],
            [bx + bw * 0.22, by + bh * 0.05], [bx + bw * 0.12, by + bh * 0.20],
            [bx + bw * 0.05, by + bh * 0.10], [bx, by + bh * 0.36]]);
    }
    const size = layout.led_size, half = Math.trunc(size / 2);
    const chipW = Math.max(2, Math.trunc(size * 0.18)), chipMargin = Math.max(1, Math.trunc(size * 0.05));
    const chipHalfH = Math.max(2, half - chipMargin - 1), chipR = Math.max(1, Math.trunc(chipW / 2));
    for (let y = 0; y < 5; y++) {
        for (let x = 0; x < 5; x++) {
            const [px, py] = layout.leds[y][x];
            fillRect(ctx, LED_WELL, [px - half - 1, py - half - 1, size + 2, size + 2]);
            fillRect(ctx, ledColor(sim.display[y][x], sim.brightness), [px - half, py - half, size, size]);
            if (sim.display[y][x] === 0) {
                const cx0 = px - Math.trunc(chipW / 2);
                fillRect(ctx, LED_CHIP, [cx0, py - half + chipMargin, chipW, chipHalfH], [chipR, chipR, 0, 0]);
                fillRect(ctx, LED_CHIP, [cx0, py + 1, chipW, chipHalfH], [0, 0, chipR, chipR]);
            }
        }
    }
    for (const name of ['a', 'b']) {
        const [bx, by, br] = layout.buttons[name];
        disc(ctx, sim.buttons[name] ? BUTTON_DOWN : BUTTON_COLOR, bx, by, br);
        ring(ctx, BUTTON_EDGE, bx, by, br, 2);
        label(ctx, name.toUpperCase(), Math.max(12, Math.trunc(28 * layout.scale)), [40, 40, 40], bx, by, 'center');
        if (drawBody) buttonTag(ctx, name, bx, by, br, layout);
    }
    const [kx, ky, kr] = layout.speaker;
    const playing = (sim.tone || 0) > 0;
    disc(ctx, playing ? SPEAKER_ON : SPEAKER_OFF, kx, ky, kr);
    if (playing) { ring(ctx, SPEAKER_ON, kx, ky, kr + 4, 1); ring(ctx, SPEAKER_ON, kx, ky, kr + 9, 1); }

    const [lx, ly, rx, ry] = layout.logo;
    ctx.fillStyle = css(sim.logo_touched ? LOGO_TOUCHED : LOGO_COLOR);
    ctx.beginPath(); ctx.ellipse(lx, ly, rx, ry, 0, 0, 2 * Math.PI); ctx.fill();
    const dotR = Math.max(1, Math.trunc(ry * 0.35)), dotDx = rx * 0.45;
    if (dotDx > dotR) {
        disc(ctx, LOGO_DOT, Math.trunc(lx - dotDx), ly, dotR);
        disc(ctx, LOGO_DOT, Math.trunc(lx + dotDx), ly, dotR);
    }
    for (const name of PAD_NAMES) {
        const [x, y, w, h] = layout.pads[name];
        const isPin = /^[0-9]$/.test(name) && TOUCH_PINS.indexOf(parseInt(name, 10)) >= 0;
        const touched = isPin && !!sim.pins_touched[parseInt(name, 10)];
        fillRect(ctx, touched ? PAD_TOUCHED : PAD_COLOR, [x, y, w, h], 3);
        edgeRect(ctx, PAD_EDGE, [x, y, w, h], 1, 3);
        const holeR = Math.max(1, Math.trunc(Math.min(w, h) * 0.18));
        const holeCy = y + holeR + Math.max(1, Math.trunc(2 * layout.scale));
        if (holeCy + holeR < y + h - Math.max(4, Math.trunc(4 * layout.scale))) {
            disc(ctx, PAD_HOLE, x + Math.trunc(w / 2), holeCy, holeR);
        }
        label(ctx, name, Math.max(10, Math.trunc(19 * layout.scale)), LABEL_COLOR, x + Math.trunc(w / 2), y - 2, 'center-bottom');
    }
}

// The 'A'/'B' silkscreen flag beside a button.
function buttonTag(ctx, name, bx, by, br, layout) {
    const sc = layout.scale;
    const tw = Math.max(6, Math.trunc(20 * sc)), th = Math.max(6, Math.trunc(18 * sc));
    const tx = bx - Math.trunc(tw / 2), gap = Math.max(2, Math.trunc(4 * sc));
    let pts, centroid;
    if (name === 'a') {
        const ty = by + br + gap;
        pts = [[tx, ty + th], [tx + tw, ty + th], [tx + tw, ty]];
        centroid = [tx + tw * 2 / 3, ty + th * 2 / 3];
    } else {
        const ty = by - br - gap - th;
        pts = [[tx + tw, ty], [tx, ty], [tx, ty + th]];
        centroid = [tx + tw / 3, ty + th / 3];
    }
    polygon(ctx, CORNER_GREEN, pts);
    label(ctx, name.toUpperCase(), Math.max(8, Math.trunc(14 * sc)), TAG_LABEL,
        Math.trunc(centroid[0]), Math.trunc(centroid[1]), 'center');
}

// Instance-overlay hook: draw the board for a micro:bit instance.
function drawOverlay(inst, ctx) {
    const sim = boardOf(inst);
    if (!sim || inst.visible === false) return;
    ctx.save();
    const layout = layoutFor(inst);
    drawBoard(ctx, layout, sim, !(inst.sprite && inst.spriteInfo));
    if (stripVisible(inst)) drawStrip(ctx, stripLayout(layout), sim, layout.scale);
    ctx.restore();
}

if (typeof registerInstanceOverlay === 'function') registerInstanceOverlay(drawOverlay);

window.__pygmMicrobit = {
    MicrobitSimulator, parseImage, glyphImage, textColumns, scrollFrames,
    melodyNotes, toneNotes, noteFrequency, clampGroup, cleanMessage, asNumber,
    deliver, formatNumber, REST_ACCELERATION,
    boardOf, eventNameFor, updateMicrobits, readSensor, mbValue, soundHooks,
    MB_ACTIONS, MB_CONDITIONS,
    pyRound, boardLayout, stripLayout, ledColor, tiltToPos, sliderFraction, layoutFor, centerOf,
    drawBoard, drawStrip, drawOverlay,
};
})();
