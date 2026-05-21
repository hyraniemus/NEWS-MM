#!/usr/bin/env python3
"""
Render watermark-cover overlay as ProRes 4444 (with alpha).

Install once:
    pip install moderngl numpy

Usage:
    python render.py <duration_seconds> [output.mov]

Example (20-second test):
    python render.py 20 overlay_test.mov

Example (full 3-hour master):
    python render.py 10800 overlay_full.mov
"""

import sys
import subprocess
from pathlib import Path

# ── Deps check ────────────────────────────────────────────────────────────────
try:
    import moderngl
    import numpy as np
except ImportError:
    print("Missing deps. Run:  pip install moderngl numpy")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1920, 1080
FPS           = 25
SHADER_PATH   = Path(__file__).parent / "shader" / "cover.frag"

VERT_SRC = """
#version 330 core
in vec2 in_vert;
void main() { gl_Position = vec4(in_vert, 0.0, 1.0); }
"""


def main():
    duration = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
    out_file  = sys.argv[2]        if len(sys.argv) > 2 else "overlay.mov"

    num_frames = int(round(duration * FPS))
    print(f"Rendering {num_frames} frames  ({duration:.1f}s @ {FPS}fps)  →  {out_file}")

    # ── OpenGL headless context ───────────────────────────────────────────────
    ctx     = moderngl.create_standalone_context()
    texture = ctx.texture((WIDTH, HEIGHT), components=4, dtype='f1')
    fbo     = ctx.framebuffer(color_attachments=[texture])

    prog = ctx.program(
        vertex_shader=VERT_SRC,
        fragment_shader=SHADER_PATH.read_text(),
    )

    quad_verts = np.array([-1,-1,  1,-1,  -1,1,  1,1], dtype='f4')
    vao = ctx.simple_vertex_array(prog, ctx.buffer(quad_verts), 'in_vert')

    prog['resolution'].value = (float(WIDTH), float(HEIGHT))

    # ── FFmpeg pipe: raw RGBA in → ProRes 4444 (yuva444p10le) out ─────────────
    ff_cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-f',         'rawvideo',
        '-vcodec',    'rawvideo',
        '-s',         f'{WIDTH}x{HEIGHT}',
        '-pix_fmt',   'rgba',
        '-r',         str(FPS),
        '-i',         'pipe:0',
        '-vcodec',    'prores_ks',
        '-profile:v', '4444',        # full alpha
        '-pix_fmt',   'yuva444p10le',
        '-vendor',    'apl0',        # macOS ProRes compatibility flag
        out_file,
    ]
    ff_proc = subprocess.Popen(ff_cmd, stdin=subprocess.PIPE)

    # ── Render loop ───────────────────────────────────────────────────────────
    fbo.use()
    for i in range(num_frames):
        prog['time'].value = i / FPS

        ctx.clear(0.0, 0.0, 0.0, 0.0)
        vao.render(moderngl.TRIANGLE_STRIP)

        ff_proc.stdin.write(fbo.read(components=4, dtype='f1'))

        if i % (FPS * 5) == 0:
            pct = i / num_frames * 100
            print(f"  {i//FPS:6d}s / {int(duration)}s  ({pct:.0f}%)", flush=True)

    ff_proc.stdin.close()
    code = ff_proc.wait()
    if code != 0:
        print(f"FFmpeg exited with code {code}")
        sys.exit(code)
    print(f"Done → {out_file}")


if __name__ == '__main__':
    main()
