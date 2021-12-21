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
parser.add_argument('-d', '--debug', action='store_true')

VALID_TYPES = ('image/jpeg', 'image/png')


def make_hash(path):
    with path.open(mode='rb') as fh:
        image = Image.open(fh)
        return phash(image, hash_size=7)


def is_image(file):
    type_, _ = mimetypes.guess_type(file)
    return type_ in VALID_TYPES


def parse_args():
    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    directory = Path(args.directory)

    if not directory.exists() and not directory.is_dir():
        raise SystemExit('Directory does not exist: %s' % args.directory)

    reference = Path(args.file)

    if not reference.exists():
        raise SystemExit('File does not exist: %s' % args.file)

    return directory, reference


def main():
    top, reference = parse_args()
    reference_hash = make_hash(reference)

    log.info('Search for images similar to %s', reference.name)
    log.info('Reference hash: %s', reference_hash)

    found = 0

    for dirname, _, files in os.walk(top):
        cwd = Path(dirname)
        for file in files:
            path = cwd / Path(file)

            if cwd / reference != path and is_image(path):
                image_hash_ = make_hash(path)
                log.debug('Image: %s', path.resolve())
                log.debug('Hash: %s', image_hash_)

                if image_hash_ == reference_hash:
                    found += 1
                    log.info('\nFound match!\nfile://%s\n', path.resolve())

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
