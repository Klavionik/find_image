#!/usr/bin/env python3
"""
Find images similar to a given reference image using a perceptual hashing algorithm.
May work even if the search target (or the reference) if cropped, resized, rotated,
color-manipulated etc.
"""
import argparse
import logging
import mimetypes
import os
from pathlib import Path
from typing import Tuple, Optional, Iterator

from PIL import Image
from imagehash import phash, ImageHash

log = logging.getLogger('find_image')
logging.basicConfig(format='%(message)s')
log.setLevel(logging.INFO)

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, epilog=__doc__)
parser.add_argument('file', help='Path to the reference image')
parser.add_argument('top', help='Path to the top search directory')
parser.add_argument('-s', '--sensitivity', help='Hashing sensitivity (2 - 8)', type=int, default=7)
parser.add_argument('-d', '--distance', help='Max. Hamming distance', type=int, default=0)
parser.add_argument('-e', '--exclude', help='Directories to exclude from search (a comma-separated list)')
parser.add_argument('--debug', action='store_true', help="Output debug messages")

VALID_TYPES = ('image/jpeg', 'image/png')


def make_hash(path: Path, sensitivity: int) -> Optional[ImageHash]:
    try:
        with path.open(mode='rb') as fh:
            image = Image.open(fh)
            return phash(image, hash_size=sensitivity)
    except Exception as exc:
        log.info('Error occured when trying to hash an image: %r', exc)


def is_image(file: Path) -> bool:
    type_, _ = mimetypes.guess_type(file)
    return type_ in VALID_TYPES


def parse_dirs(dirs: str) -> list:
    if dirs is None:
        return []
    return dirs.replace(' ', '').split(',')


def next_image(top: Path, reference_path: Path, excluded: list) -> Iterator[Path]:
    for dirpath, _, files in os.walk(top):
        directory = Path(dirpath)

        if directory.resolve().name in excluded:
            log.info('Directory %s is excluded, skip', dirpath)
            continue

        for file in files:
            filepath = directory / Path(file)

            if reference_path != filepath and is_image(filepath):
                yield filepath.resolve()


def ask_if_continue() -> None:
    kbinterrupt = False
    answer = None

    try:
        answer = input('Continue search? [y/n] ')
    except KeyboardInterrupt:
        # This is just to make a consistent
        # amount of newlines.
        print()
        kbinterrupt = True

    if kbinterrupt or answer in ('n', 'no'):
        raise SystemExit


def parse_args() -> Tuple[Path, Path, int, int, list]:
    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    top = Path(args.top)

    if not top.exists() or not top.is_dir():
        raise SystemExit('Directory does not exist: %s' % args.directory)

    reference = Path(args.file)

    if not reference.exists():
        raise SystemExit('File does not exist: %s' % args.file)

    sensitivity = args.sensitivity

    if not (2 <= sensitivity <= 8):
        raise SystemExit('Sensitivity must be in range from 2 to 8, you passed: %s' % sensitivity)

    exclude = parse_dirs(args.exclude)

    return top, reference, args.sensitivity, args.distance, exclude


def main() -> None:
    top, reference, sensitivity, max_distance, excluded = parse_args()
    reference_hash = make_hash(reference, sensitivity)

    log.info('Search for images similar to %s', reference.name)
    log.info('Reference hash: %s', reference_hash)

    processed = 0
    found = 0

    for image_path in next_image(top, reference, excluded):
        image_hash = make_hash(image_path, sensitivity)

        if not image_hash:
            continue

        distance = image_hash - reference_hash

        log.debug('Image: %s', image_path)
        log.debug('Hash: %s. Distance: %s', image_hash, distance)

        processed += 1
        print('Processed %s images' % processed, end='\r')

        if distance <= max_distance:
            found += 1
            log.info('\nFound match!\n%s', image_path.as_uri())

            try:
                ask_if_continue()
            except SystemExit:
                break

    log.info('\nFound %s similar images.', found)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.info('\nExiting.')
