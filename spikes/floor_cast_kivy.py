#!/usr/bin/env python3
"""THROWAWAY timing spike — raycast floor casting on Kivy (deferred unit 5b).

Measures whether the desktop low-res floor-casting algorithm
(runtime/game_runner._cast_floor_plane) is fast enough to port into the Kivy
exporter's scene renderer. Each "frame" builds a small RGBA buffer per-pixel
from a tiled floor texture and uploads it with Texture.blit_buffer (the real
per-frame CPU + GPU-upload cost; the scaled draw of the resulting texture is a
single constant-cost Rectangle and is not the bottleneck).

Two implementations are timed so unit 5b can choose:
  * naive  — a line-for-line Python port of the desktop set_at loops (what a
             literal transcription would land, matching the other targets).
  * numpy  — a vectorised cast (fast; the realistic choice if naive misses
             budget), correctness-equivalent.

Defaults match raycast_1: 480x480 display, 240-px floor region, 32x32 floor
texture. Run it on a REAL desktop (it opens a Kivy window to get a GL context):

    py -3.12 spikes/floor_cast_kivy.py

Read-off: pick the smallest `res` whose median is comfortably under ~8 ms (the
floor is one of ~4 passes per frame; 8 ms leaves room for walls/sky/billboards
inside a 16.7 ms 60fps budget). If even res=8 naive fails and numpy is
unavailable/also fails, unit 5b should ship a FLAT floor fill on Kivy (the
documented fallback), same as HTML5 3b.

Delete this file once the numbers are recorded in docs/RAYCAST_2_5D_PLAN.md.
"""
import math
import statistics
import sys
import time

W, H = 480, 480
TEX = 32
ITERS = 300
RES_FACTORS = (1, 2, 4, 8)
FOV = math.radians(66)
CAM_CX, CAM_CY = 3.5, 3.5

try:
    import numpy as np
except ImportError:
    np = None


def make_texture_bytes(size):
    """A `size`x`size` RGBA checker+gradient (bytes), so per-pixel sampling
    isn't a constant the JIT/interpreter could hoist."""
    buf = bytearray(size * size * 4)
    k = 0
    for y in range(size):
        for x in range(size):
            chk = ((x >> 2) + (y >> 2)) & 1
            if chk:
                buf[k] = (120 + x) & 255; buf[k + 1] = (90 + y) & 255; buf[k + 2] = 70
            else:
                buf[k] = 70; buf[k + 1] = (90 + y) & 255; buf[k + 2] = (120 + x) & 255
            buf[k + 3] = 255
            k += 4
    return bytes(buf)


def cast_naive(tex, tw, th, res, facing):
    """Faithful port of _cast_floor_plane's inner loops -> RGBA bytes."""
    half_h = H // 2
    region_h = H - half_h
    sw = max(1, W // res)
    sh = max(1, region_h // res)
    out = bytearray(sw * sh * 4)
    dir_x, dir_y = math.cos(facing), math.sin(facing)
    plane = math.tan(FOV / 2)
    plane_x, plane_y = -dir_y * plane, dir_x * plane
    rdx0, rdy0 = dir_x - plane_x, dir_y - plane_y
    rdx1, rdy1 = dir_x + plane_x, dir_y + plane_y
    pos_z = 0.5 * H
    step_scale = res / W
    floor = math.floor
    for j in range(sh):
        y = half_h + j * res
        p = y - half_h
        if p <= 0:
            p = 1
        rowd = pos_z / p
        stepx = rowd * (rdx1 - rdx0) * step_scale
        stepy = rowd * (rdy1 - rdy0) * step_scale
        fx = CAM_CX + rowd * rdx0
        fy = CAM_CY + rowd * rdy0
        di = j * sw * 4
        for _ in range(sw):
            tx = int(tw * (fx - floor(fx)))
            ty = int(th * (fy - floor(fy)))
            if tx >= tw:
                tx = tw - 1
            if ty >= th:
                ty = th - 1
            si = (ty * tw + tx) * 4
            out[di] = tex[si]; out[di + 1] = tex[si + 1]
            out[di + 2] = tex[si + 2]; out[di + 3] = 255
            di += 4
            fx += stepx
            fy += stepy
    return bytes(out), sw, sh


def cast_numpy(tex_arr, tw, th, res, facing):
    """Vectorised equivalent of cast_naive -> RGBA bytes."""
    half_h = H // 2
    region_h = H - half_h
    sw = max(1, W // res)
    sh = max(1, region_h // res)
    dir_x, dir_y = math.cos(facing), math.sin(facing)
    plane = math.tan(FOV / 2)
    plane_x, plane_y = -dir_y * plane, dir_x * plane
    rdx0, rdy0 = dir_x - plane_x, dir_y - plane_y
    rdx1, rdy1 = dir_x + plane_x, dir_y + plane_y
    pos_z = 0.5 * H
    step_scale = res / W

    j = np.arange(sh)
    p = np.maximum((half_h + j * res) - half_h, 1)
    rowd = pos_z / p                                    # (sh,)
    i = np.arange(sw)
    stepx = rowd * (rdx1 - rdx0) * step_scale           # (sh,)
    stepy = rowd * (rdy1 - rdy0) * step_scale
    fx = CAM_CX + rowd[:, None] * rdx0 + i[None, :] * stepx[:, None]
    fy = CAM_CY + rowd[:, None] * rdy0 + i[None, :] * stepy[:, None]
    tx = (tw * (fx - np.floor(fx))).astype(np.intp)
    ty = (th * (fy - np.floor(fy))).astype(np.intp)
    np.clip(tx, 0, tw - 1, out=tx)
    np.clip(ty, 0, th - 1, out=ty)
    out = tex_arr[ty, tx]                               # (sh, sw, 4)
    return out.astype(np.uint8).tobytes(), sw, sh


def run_bench():
    from kivy.graphics.texture import Texture

    tex_bytes = make_texture_bytes(TEX)
    tex_arr = (np.frombuffer(tex_bytes, np.uint8).reshape(TEX, TEX, 4)
               if np is not None else None)

    print(f"\nFloor-cast spike — display {W}x{H}, floor region {W}x{H - H // 2}, "
          f"texture {TEX}x{TEX}, {ITERS} iters/res")
    print(f"Python {sys.version.split()[0]}, numpy {'yes' if np is not None else 'MISSING'}\n")
    header = f"{'res':>4} {'grid':>10} {'naive med':>11} {'naive mean':>11} "
    if np is not None:
        header += f"{'numpy med':>11} {'numpy mean':>11}"
    print(header)
    print("-" * len(header))

    for res in RES_FACTORS:
        sw = max(1, W // res)
        sh = max(1, (H - H // 2) // res)
        gputex = Texture.create(size=(sw, sh), colorfmt='rgba')

        def timed(fn, arg):
            for k in range(8):                          # warm up
                buf, _, _ = fn(arg, TEX, TEX, res, k * 0.01)
                gputex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
            samples = []
            for k in range(ITERS):
                t0 = time.perf_counter()
                buf, _, _ = fn(arg, TEX, TEX, res, k * 0.017)
                gputex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
                samples.append((time.perf_counter() - t0) * 1000.0)
            return statistics.median(samples), statistics.fmean(samples)

        nmed, nmean = timed(cast_naive, tex_bytes)
        line = f"{res:>4} {f'{sw}x{sh}':>10} {nmed:>11.3f} {nmean:>11.3f} "
        if np is not None:
            pmed, pmean = timed(cast_numpy, tex_arr)
            line += f"{pmed:>11.3f} {pmean:>11.3f}"
        print(line)

    print("\nBudget guide: floor is ~1 of 4 passes/frame; aim < 8 ms (60fps-"
          "friendly), 33 ms is the hard 30fps whole-frame ceiling.")
    print("Record the winning (impl, res) in docs/RAYCAST_2_5D_PLAN.md, then "
          "delete this spike.\n")


def main():
    try:
        from kivy.app import App
        from kivy.uix.widget import Widget
        from kivy.clock import Clock
    except ImportError:
        print("Kivy is not installed — this spike needs it (the native export "
              "feature does too). `pip install --user kivy` and re-run.")
        return

    class SpikeApp(App):
        def build(self):
            # Run once GL is live (after the first frame), then quit.
            Clock.schedule_once(self._go, 0.4)
            return Widget()

        def _go(self, _dt):
            try:
                run_bench()
            finally:
                self.stop()

    SpikeApp().run()


if __name__ == "__main__":
    main()
