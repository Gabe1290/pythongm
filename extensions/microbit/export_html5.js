// micro:bit simulator -- HTML5 export (docs/MICROBIT_STAGE_P_PLAN.md).
//
// Concatenated into engine.js at the __PYGM_EXTENSION_JS__ marker, like the
// other extensions' export_html5.js. This is unit H1: the pure simulator, a
// line-for-line port of extensions/microbit/simulator.py (+ sound.py and
// radio.py). Field names stay snake_case, identical to the Python object, so
// tools/microbit_js_parity.py can diff the two frame by frame. Later units add
// the actions, drawing and input on top. Everything lives in one function
// scope and is exposed on window.__pygmMicrobit.

(function () {
// <generated:tables> -- tools/gen_microbit_js_tables.py; do not edit by hand
const MB_GLYPHS = {"32": [0, 0, 0, 0, 0], "33": [8, 8, 8, 0, 8], "34": [10, 10, 0, 0, 0], "35": [10, 31, 10, 31, 10], "36": [14, 25, 14, 19, 14], "37": [25, 18, 4, 9, 19], "38": [12, 18, 12, 18, 13], "39": [8, 8, 0, 0, 0], "40": [4, 8, 8, 8, 4], "41": [8, 4, 4, 4, 8], "42": [0, 10, 4, 10, 0], "43": [0, 4, 14, 4, 0], "44": [0, 0, 0, 4, 8], "45": [0, 0, 14, 0, 0], "46": [0, 0, 0, 8, 0], "47": [1, 2, 4, 8, 16], "48": [12, 18, 18, 18, 12], "49": [4, 12, 4, 4, 14], "50": [28, 2, 12, 16, 30], "51": [30, 2, 4, 18, 12], "52": [6, 10, 18, 31, 2], "53": [31, 16, 30, 1, 30], "54": [2, 4, 14, 17, 14], "55": [31, 2, 4, 8, 16], "56": [14, 17, 14, 17, 14], "57": [14, 17, 14, 4, 8], "58": [0, 8, 0, 8, 0], "59": [0, 4, 0, 4, 8], "60": [2, 4, 8, 4, 2], "61": [0, 14, 0, 14, 0], "62": [8, 4, 2, 4, 8], "63": [14, 17, 6, 0, 4], "64": [14, 17, 21, 19, 12], "65": [12, 18, 30, 18, 18], "66": [28, 18, 28, 18, 28], "67": [14, 16, 16, 16, 14], "68": [28, 18, 18, 18, 28], "69": [30, 16, 28, 16, 30], "70": [30, 16, 28, 16, 16], "71": [14, 16, 19, 17, 14], "72": [18, 18, 30, 18, 18], "73": [28, 8, 8, 8, 28], "74": [31, 2, 2, 18, 12], "75": [18, 20, 24, 20, 18], "76": [16, 16, 16, 16, 30], "77": [17, 27, 21, 17, 17], "78": [17, 25, 21, 19, 17], "79": [12, 18, 18, 18, 12], "80": [28, 18, 28, 16, 16], "81": [12, 18, 18, 12, 6], "82": [28, 18, 28, 18, 17], "83": [14, 16, 12, 2, 28], "84": [31, 4, 4, 4, 4], "85": [18, 18, 18, 18, 12], "86": [17, 17, 17, 10, 4], "87": [17, 17, 21, 27, 17], "88": [18, 18, 12, 18, 18], "89": [17, 10, 4, 4, 4], "90": [30, 4, 8, 16, 30], "91": [14, 8, 8, 8, 14], "92": [16, 8, 4, 2, 1], "93": [14, 2, 2, 2, 14], "94": [4, 10, 0, 0, 0], "95": [0, 0, 0, 0, 31], "96": [8, 4, 0, 0, 0], "97": [0, 14, 18, 18, 15], "98": [16, 16, 28, 18, 28], "99": [0, 14, 16, 16, 14], "100": [2, 2, 14, 18, 14], "101": [12, 18, 28, 16, 14], "102": [6, 8, 28, 8, 8], "103": [14, 18, 14, 2, 12], "104": [16, 16, 28, 18, 18], "105": [8, 0, 8, 8, 8], "106": [2, 0, 2, 2, 12], "107": [16, 20, 24, 20, 18], "108": [8, 8, 8, 8, 6], "109": [0, 27, 21, 17, 17], "110": [0, 28, 18, 18, 18], "111": [0, 12, 18, 18, 12], "112": [0, 28, 18, 28, 16], "113": [0, 14, 18, 14, 2], "114": [0, 14, 16, 16, 16], "115": [0, 6, 8, 4, 24], "116": [8, 8, 14, 8, 7], "117": [0, 18, 18, 18, 15], "118": [0, 17, 17, 10, 4], "119": [0, 17, 17, 21, 27], "120": [0, 18, 12, 12, 18], "121": [0, 17, 10, 4, 24], "122": [0, 30, 4, 8, 30], "123": [6, 4, 12, 4, 6], "124": [8, 8, 8, 8, 8], "125": [24, 8, 12, 8, 24], "126": [0, 0, 12, 3, 0]};
const MB_IMAGES = {"HEART": ["09090", "99999", "99999", "09990", "00900"], "HEART_SMALL": ["00000", "09090", "09990", "00900", "00000"], "HAPPY": ["00000", "09090", "00000", "90009", "09990"], "SMILE": ["00000", "00000", "00000", "90009", "09990"], "SAD": ["00000", "09090", "00000", "09990", "90009"], "CONFUSED": ["00000", "09090", "00000", "09090", "90909"], "ANGRY": ["90009", "09090", "00000", "99999", "90909"], "ASLEEP": ["00000", "99099", "00000", "09990", "00000"], "SURPRISED": ["09090", "00000", "00900", "09090", "00900"], "SILLY": ["90009", "00000", "99999", "00909", "00999"], "FABULOUS": ["99999", "99099", "00000", "09090", "09990"], "MEH": ["09090", "00000", "00090", "00900", "09000"], "YES": ["00000", "00009", "00090", "90900", "09000"], "NO": ["90009", "09090", "00900", "09090", "90009"], "CLOCK12": ["00900", "00900", "00900", "00000", "00000"], "CLOCK1": ["00090", "00090", "00900", "00000", "00000"], "CLOCK2": ["00000", "00099", "00900", "00000", "00000"], "CLOCK3": ["00000", "00000", "00999", "00000", "00000"], "CLOCK4": ["00000", "00000", "00900", "00099", "00000"], "CLOCK5": ["00000", "00000", "00900", "00090", "00090"], "CLOCK6": ["00000", "00000", "00900", "00900", "00900"], "CLOCK7": ["00000", "00000", "00900", "09000", "09000"], "CLOCK8": ["00000", "00000", "00900", "99000", "00000"], "CLOCK9": ["00000", "00000", "99900", "00000", "00000"], "CLOCK10": ["00000", "99000", "00900", "00000", "00000"], "CLOCK11": ["09000", "09000", "00900", "00000", "00000"], "ARROW_N": ["00900", "09990", "90909", "00900", "00900"], "ARROW_NE": ["00999", "00099", "00909", "09000", "90000"], "ARROW_E": ["00900", "00090", "99999", "00090", "00900"], "ARROW_SE": ["90000", "09000", "00909", "00099", "00999"], "ARROW_S": ["00900", "00900", "90909", "09990", "00900"], "ARROW_SW": ["00009", "00090", "90900", "99000", "99900"], "ARROW_W": ["00900", "09000", "99999", "09000", "00900"], "ARROW_NW": ["99900", "99000", "90900", "00090", "00009"], "TRIANGLE": ["00000", "00900", "09090", "99999", "00000"], "TRIANGLE_LEFT": ["90000", "99000", "90900", "90090", "99999"], "CHESSBOARD": ["09090", "90909", "09090", "90909", "09090"], "DIAMOND": ["00900", "09090", "90009", "09090", "00900"], "DIAMOND_SMALL": ["00000", "00900", "09090", "00900", "00000"], "SQUARE": ["99999", "90009", "90009", "90009", "99999"], "SQUARE_SMALL": ["00000", "09990", "09090", "09990", "00000"], "RABBIT": ["90900", "90900", "99990", "99090", "99990"], "COW": ["90009", "90009", "99999", "09990", "00900"], "MUSIC_CROTCHET": ["00900", "00900", "00900", "99900", "99900"], "MUSIC_QUAVER": ["00900", "00990", "00909", "99900", "99900"], "MUSIC_QUAVERS": ["09999", "09009", "09009", "99099", "99099"], "PITCHFORK": ["90909", "90909", "99999", "00900", "00900"], "XMAS": ["00900", "09990", "00900", "09990", "99999"], "PACMAN": ["09999", "99090", "99900", "99990", "09999"], "TARGET": ["00900", "09990", "99099", "09990", "00900"], "TSHIRT": ["99099", "99999", "09990", "09990", "09990"], "ROLLERSKATE": ["00099", "00099", "99999", "99999", "09090"], "DUCK": ["09900", "99900", "09999", "09990", "00000"], "HOUSE": ["00900", "09990", "99999", "09990", "09090"], "TORTOISE": ["00000", "09990", "99999", "09090", "00000"], "BUTTERFLY": ["99099", "99999", "00900", "99999", "99099"], "STICKFIGURE": ["00900", "99999", "00900", "09090", "90009"], "GHOST": ["99999", "90909", "99999", "99999", "90909"], "SWORD": ["00900", "00900", "00900", "09990", "00900"], "GIRAFFE": ["99000", "09000", "09000", "09990", "09090"], "SKULL": ["09990", "90909", "99999", "09990", "09990"], "UMBRELLA": ["09990", "99999", "00900", "90900", "09900"], "SNAKE": ["99000", "99099", "09090", "09990", "00000"], "SCISSORS": ["99009", "99090", "00900", "99090", "99009"]};
const MB_MELODIES = {"DADADADUM": ["r4:2", "g", "g", "g", "eb:8", "r:2", "f", "f", "f", "d:8"], "ENTERTAINER": ["d4:1", "d#", "e", "c5:2", "e4:1", "c5:2", "e4:1", "c5:3", "c:1", "d", "d#", "e", "c", "d", "e:2", "b4:1", "d5:2", "c:4"], "PRELUDE": ["c4:1", "e", "g", "c5", "e", "g4", "c5", "e", "c4", "e", "g", "c5", "e", "g4", "c5", "e", "c4", "d", "g", "d5", "f", "g4", "d5", "f", "c4", "d", "g", "d5", "f", "g4", "d5", "f", "b3", "d4", "g", "d5", "f", "g4", "d5", "f", "b3", "d4", "g", "d5", "f", "g4", "d5", "f", "c4", "e", "g", "c5", "e", "g4", "c5", "e", "c4", "e", "g", "c5", "e", "g4", "c5", "e"], "ODE": ["e4", "e", "f", "g", "g", "f", "e", "d", "c", "c", "d", "e", "e:6", "d:2", "d:8", "e:4", "e", "f", "g", "g", "f", "e", "d", "c", "c", "d", "e", "d:6", "c:2", "c:8"], "NYAN": ["f#5:2", "g#", "c#:1", "d#:2", "b4:1", "d5:1", "c#", "b4:2", "b", "c#5", "d", "d:1", "c#", "b4:1", "c#5:1", "d#", "f#", "g#", "d#", "f#", "c#", "d", "b4", "c#5", "b4", "d#5:2", "f#", "g#:1", "d#", "f#", "c#", "d#", "b4", "d5", "d#", "d", "c#", "b4", "c#5", "d:2", "b4:1", "c#5", "d#", "f#", "c#", "d", "c#", "b4", "c#5:2", "b4", "c#5", "b4", "f#:1", "g#", "b:2", "f#:1", "g#", "b", "c#5", "d#", "b4", "e5", "d#", "e", "f#", "b4:2", "b", "f#:1", "g#", "b", "f#", "e5", "d#", "c#", "b4", "f#", "d#", "e", "f#", "b:2", "f#:1", "g#", "b:2", "f#:1", "g#", "b", "b", "c#5", "d#", "b4", "f#", "g#", "f#", "b:2", "b:1", "a#", "b", "f#", "g#", "b", "e5", "d#", "e", "f#", "b4:2", "c#5"], "RINGTONE": ["c4:1", "d", "e:2", "g", "d:1", "e", "f:2", "a", "e:1", "f", "g:2", "b", "c5:4"], "FUNK": ["c2:2", "c", "d#", "c:1", "f:2", "c:1", "f:2", "f#", "g", "c", "c", "g", "c:1", "f#:2", "c:1", "f#:2", "f", "d#"], "BLUES": ["c2:2", "e", "g", "a", "a#", "a", "g", "e", "c2:2", "e", "g", "a", "a#", "a", "g", "e", "f", "a", "c3", "d", "d#", "d", "c", "a2", "c2:2", "e", "g", "a", "a#", "a", "g", "e", "g", "b", "d3", "f", "f2", "a", "c3", "d#", "c2:2", "e", "g", "e", "g", "f", "e", "d"], "BIRTHDAY": ["c4:3", "c:1", "d:4", "c:4", "f", "e:8", "c:3", "c:1", "d:4", "c:4", "g", "f:8", "c:3", "c:1", "c5:4", "a4", "f", "e", "d", "a#:3", "a#:1", "a:4", "f", "g", "f:8"], "WEDDING": ["c4:4", "f:3", "f:1", "f:8", "c:4", "g:3", "e:1", "f:8", "c:4", "f:3", "a:1", "c5:4", "a4:3", "f:1", "f:4", "e:3", "f:1", "g:8"], "FUNERAL": ["c3:4", "c:3", "c:1", "c:4", "d#:3", "d:1", "d:3", "c:1", "c:3", "b2:1", "c3:4"], "PUNCHLINE": ["c4:3", "g3:1", "f#", "g", "g#:3", "g", "r", "b", "c4"], "PYTHON": ["d5:1", "b4", "r", "b", "b", "a#", "b", "g5", "r", "d", "d", "r", "b4", "c5", "r", "c", "c", "r", "d", "e:5", "c:1", "a4", "r", "a", "a", "g#", "a", "f#5", "r", "e", "e", "r", "c", "b4", "r", "b", "b", "r", "c5", "d:5", "d:1", "b4", "r", "b", "b", "a#", "b", "b5", "r", "g", "g", "r", "d", "c#", "r", "a", "a", "r", "a", "a:5", "g:1", "f#:2", "a:1", "a", "g#", "a", "e:2", "a:1", "a", "g#", "a", "d", "r", "c#", "d", "r", "c#", "d:2", "r:3"], "BADDY": ["c3:3", "r", "d:2", "d#", "r", "c", "r", "f#:8"], "CHASE": ["a4:1", "b", "c5", "b4", "a:2", "r", "a:1", "b", "c5", "b4", "a:2", "r", "a:2", "e5", "d#", "e", "f", "e", "d#", "e", "b4:1", "c5", "d", "c", "b4:2", "r", "b:1", "c5", "d", "c", "b4:2", "r", "b:2", "e5", "d#", "e", "f", "e", "d#", "e"], "BA_DING": ["b5:1", "e6:3"], "WAWAWAWAA": ["e3:3", "r:1", "d#:3", "r:1", "d:4", "r:1", "c#:8"], "JUMP_UP": ["c5:1", "d", "e", "f", "g"], "JUMP_DOWN": ["g5:1", "f", "e", "d", "c"], "POWER_UP": ["g4:1", "c5", "e", "g:2", "e:1", "g:3"], "POWER_DOWN": ["g5:1", "d#", "c", "g4:2", "b:1", "c5:3"]};
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

window.__pygmMicrobit = {
    MicrobitSimulator, parseImage, glyphImage, textColumns, scrollFrames,
    melodyNotes, toneNotes, noteFrequency, clampGroup, cleanMessage, asNumber,
    deliver, formatNumber, REST_ACCELERATION,
};
})();
