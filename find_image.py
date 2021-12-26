#!/usr/bin/env python3

import argparse
import logging
import mimetypes
import os
import sys
from pathlib import Path
from typing import Tuple, Optional

from PIL import Image
from imagehash import phash, ImageHash

log = logging.getLogger('find_image')
logging.basicConfig(format='%(message)s')
log.setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('file', help='Путь к файлу-образцу')
parser.add_argument('directory', help='Путь к директории, с которой начнется поиск')
parser.add_argument('-s', '--sensitivity', help='Чувствительность хэширования, от 2 до 8', type=int, default=7)
parser.add_argument('-d', '--distance', help='Максимальное расстояние Хэмминга', type=int, default=0)
parser.add_argument('-e', '--exclude', help='Директории, которые нужно исключить из поиска (через запятую)')
parser.add_argument('--debug', action='store_true')

VALID_TYPES = ('image/jpeg', 'image/png')


def make_hash(path: Path, sensitivity: int) -> Optional[ImageHash]:
    with path.open(mode='rb') as fh:
        image = Image.open(fh)
        return phash(image, hash_size=sensitivity)


def is_image(file: Path) -> bool:
    type_, _ = mimetypes.guess_type(file)
    return type_ in VALID_TYPES


def parse_dirs(dirs: str) -> list:
    if dirs is None:
        return []
    return dirs.replace(' ', '').split(',')


def parse_args() -> Tuple[Path, Path, int, int, list]:
    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    directory = Path(args.directory)

    if not directory.exists() or not directory.is_dir():
        raise SystemExit('Directory does not exist: %s' % args.directory)

    reference = Path(args.file)

    if not reference.exists():
        raise SystemExit('File does not exist: %s' % args.file)

    sensitivity = args.sensitivity

    if not (2 <= sensitivity <= 8):
        raise SystemExit('Sensitivity must be in range from 2 to 8, you passed: %s' % sensitivity)

    exclude = parse_dirs(args.exclude)

    return directory, reference, args.sensitivity, args.distance, exclude


def main() -> None:
    top, reference, sensitivity, max_distance, excluded = parse_args()
    reference_hash = make_hash(reference, sensitivity)

    log.info('Search for images similar to %s', reference.name)
    log.info('Reference hash: %s', reference_hash)

    processed = 0
    found = 0

    for dirpath, _, files in os.walk(top):
        directory = Path(dirpath)

        if directory.resolve().name in excluded:
            log.info('Directory %s is excluded, skip', dirpath)
            continue

        for file in files:
            filepath = directory / Path(file)

            if reference != filepath and is_image(filepath):
                image_hash = make_hash(filepath, sensitivity)
                distance = image_hash - reference_hash

                log.debug('Image: %s', filepath.resolve())
                log.debug('Hash: %s. Distance: %s', image_hash, distance)

                if distance <= max_distance:
                    found += 1
                    log.info('\nFound match!\n%s\n', filepath.resolve().as_uri())

                    try:
                        continue_ = input('Continue search? [y/n] ')
                    except KeyboardInterrupt:
                        log.info('\nFound %s similar images.', found)
                        sys.exit()

                    if continue_ in ('n', 'no'):
                        log.info('Found %s similar images.', found)
                        sys.exit()

            processed += 1
            print('Processed %s images' % processed, end='\r')

    log.info('Found %s similar images.', found)


if __name__ == '__main__':
    main()
