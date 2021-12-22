#!/usr/bin/env python3

import argparse
import logging
import mimetypes
import os
import sys
from pathlib import Path

from PIL import Image
from imagehash import phash

log = logging.getLogger('find_image')
logging.basicConfig(format='%(message)s')
log.setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('file', help='Путь к файлу-образцу')
parser.add_argument('directory', help='Путь к директории, с которой начнется поиск')
parser.add_argument('-s', '--sensitivity', help='Чувствительность хэширования, от 2 до 8', type=int, default=7)
parser.add_argument('-d', '--distance', help='Максимальное расстояние Хэмминга', type=int, default=0)
parser.add_argument('--debug', action='store_true')

VALID_TYPES = ('image/jpeg', 'image/png')


def make_hash(path, sensitivity):
    with path.open(mode='rb') as fh:
        image = Image.open(fh)
        return phash(image, hash_size=sensitivity)


def is_image(file):
    type_, _ = mimetypes.guess_type(file)
    return type_ in VALID_TYPES


def parse_args():
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

    return directory, reference, args.sensitivity, args.distance


def main():
    top, reference, sensitivity, max_distance = parse_args()
    reference_hash = make_hash(reference, sensitivity)

    log.info('Search for images similar to %s', reference.name)
    log.info('Reference hash: %s', reference_hash)

    found = 0

    for dirname, _, files in os.walk(top):
        cwd = Path(dirname)
        for file in files:
            path = cwd / Path(file)

            if cwd / reference != path and is_image(path):
                image_hash_ = make_hash(path, sensitivity)
                distance = image_hash_ - reference_hash

                log.debug('Image: %s', path.resolve())
                log.debug('Hash: %s. Distance: %s', image_hash_, distance)

                if distance <= max_distance:
                    found += 1
                    log.info('\nFound match!\n%s\n', path.resolve().as_uri())

                    try:
                        continue_ = input('Continue search? [y/n] ')
                    except KeyboardInterrupt:
                        log.info('\nFound %s similar images.', found)
                        sys.exit()

                    if continue_ in ('n', 'no'):
                        log.info('Found %s similar images.', found)
                        sys.exit()

    log.info('Found %s similar images.', found)


if __name__ == '__main__':
    main()
