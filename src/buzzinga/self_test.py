"""Check that an installation has everything Buzzinga loads at runtime.

Run with `buzzinga --self-test`. Missing bundled files or packages in the
executable built by setup.sh / setup.bat only show up when a game uses them,
so the CI runs this against the built executable.
"""
import os
import subprocess

import pygame

from .static import Static

STATIC_IMAGES = (
    [f"Buzzinga-{n}.png" for n in range(1, 8)]
    + [f"sound_animation-{n}.png" for n in range(1, 11)]
    + ["user.bmp"]
)
STATIC_SOUNDS = ["buzzer.wav", "countdown.wav", "countdown_end.wav"]


def _check_static_images():
    for name in STATIC_IMAGES:
        pygame.image.load(os.path.join(Static.STATIC_FOLDER, name))
    return f"{len(STATIC_IMAGES)} images"


def _check_static_sounds():
    pygame.mixer.init()
    for name in STATIC_SOUNDS:
        pygame.mixer.Sound(os.path.join(Static.STATIC_FOLDER, name))
    return f"{len(STATIC_SOUNDS)} sounds"


def _check_video_playback():
    # Importing moviepy also imports imageio, which reads its own package
    # metadata; PyInstaller only bundles that with --copy-metadata imageio
    from moviepy import VideoFileClip  # noqa: F401
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg, "-version"], check=True, capture_output=True)
    return ffmpeg


def _check_avif():
    from PIL import features
    if not features.check("avif"):
        raise RuntimeError("Pillow has no AVIF support")
    return "Pillow AVIF plugin"


def _check_buzzer_library():
    import pybuzzers  # noqa: F401  (loads the native hidapi library)
    return "pybuzzers / hidapi"


CHECKS = [
    ("static images", _check_static_images),
    ("static sounds", _check_static_sounds),
    ("video playback", _check_video_playback),
    ("AVIF images", _check_avif),
    ("USB buzzers", _check_buzzer_library),
]


def run_self_test():
    """Run all checks, print one line per check and return the exit code."""
    failed = 0
    for name, check in CHECKS:
        try:
            print(f"OK    {name}: {check()}")
        except Exception as e:
            failed += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    print("Self-test passed." if not failed else f"Self-test failed: {failed} of {len(CHECKS)} checks.")
    return 1 if failed else 0
