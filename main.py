"""Entry program for news-image-20261118 (round 2).

Writes the pre-rendered front-page image (entry.png, shipped beside
this file in the repository) to the output directory. The image is a
single 1024x1024 newspaper front page, "The World in One Day", dated
Wednesday 18 November 2026: 1 lead story + 9 panels + 34 briefs +
a schematic world map + masthead (44 stories in total).

STDLIB ONLY: no third-party packages, no external fonts, no network,
no randomness, no clock. The program only reads entry.png next to
itself and writes one file into the output directory, so it runs
fine with a read-only program directory.

Before copying, the image is validated strictly: it must exist, be a
real PNG (magic bytes 89 50 4E 47), carry a valid IHDR chunk with
width and height exactly 1024x1024, end with an IEND chunk, and be
no larger than 1 MiB. A missing or corrupt file fails loudly
(exit != 0 with a clear message) instead of producing a broken entry.
"""
import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1 << 20  # 1 MiB


def fail(message):
    """Abort with a clear error on stderr and a non-zero exit code."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_png_bytes():
    """Return the raw bytes of entry.png, or fail loudly."""
    if not SOURCE.is_file():
        fail("entry.png is missing (expected next to main.py)")
    data = SOURCE.read_bytes()
    if len(data) > MAX_BYTES:
        fail(f"entry.png is {len(data)} bytes, over the 1 MiB limit")
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        fail("entry.png is not a PNG image (bad magic bytes)")
    return data


def parse_ihdr(data):
    """Parse the IHDR chunk; return (width, height). Fail on bad layout."""
    # Chunk layout after the 8-byte signature: 4-byte length, 4-byte type.
    if len(data) < 8 + 8 + 13:
        fail("entry.png is truncated (no complete IHDR chunk)")
    length = struct.unpack(">I", data[8:12])[0]
    chunk_type = data[12:16]
    if chunk_type != b"IHDR":
        fail("entry.png has no IHDR chunk as its first chunk")
    if length != 13:
        fail(f"entry.png IHDR length is {length}, expected 13")
    width, height = struct.unpack(">II", data[16:24])
    bit_depth = data[24]
    color_type = data[25]
    if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
        fail(
            f"entry.png is {width}x{height}, "
            f"expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )
    if bit_depth not in (1, 2, 4, 8, 16):
        fail(f"entry.png has invalid bit depth {bit_depth}")
    if color_type not in (0, 2, 3, 4, 6):
        fail(f"entry.png has invalid color type {color_type}")
    return width, height


def check_iend(data):
    """Require a proper IEND chunk at the end of the file."""
    # IEND chunk: 4-byte length (0) + 4-byte type "IEND" + 4-byte CRC.
    if len(data) < 12 or data[-12:-8] != b"\x00\x00\x00\x00":
        fail("entry.png is truncated (no IEND chunk at the end)")
    if data[-8:-4] != b"IEND":
        fail("entry.png does not end with an IEND chunk")


def main():
    data = read_png_bytes()
    width, height = parse_ihdr(data)
    check_iend(data)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "out"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(SOURCE, target)
    print(
        f"wrote {target} ({width}x{height}, {len(data)} bytes)"
    )


if __name__ == "__main__":
    main()
