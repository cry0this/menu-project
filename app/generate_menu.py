#!/usr/bin/env python3

import argparse
import json
import os
from pickletools import optimize
import sys
import tempfile
import traceback

from datetime import datetime
from functools import wraps
from jinja2 import Template
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
from typing import Union

from lib.config import get_config
from lib.logger import get_logger


logger = get_logger('menu_generator')


def die(msg: Union[str, None] = None):
    if msg:
        logger.error(msg)

    sys.exit(1)


def exception_wrapper(fn):
    def get_full_class_name(obj):
        module = obj.__class__.__module__

        if module is None or module == str.__class__.__module__:
            return obj.__class__.__name__

        return module + '.' + obj.__class__.__name__

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            die(
                "{}: {}\nTraceback:\n{}".format(
                    get_full_class_name(e), str(e), ''.join(traceback.format_tb(e.__traceback__))
                )
            )
        return result

    return wrapper


def parse_args() -> argparse.Namespace:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    date_str = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    parser = argparse.ArgumentParser(
        description='Script to get json data and render html-table',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-l', '--log',
        default=os.path.join(dir_path, 'log', f'app_{date_str}.log'),
        help='path to app log'
    )

    parser.add_argument(
        '-s', '--selenium-log',
        default=os.path.join(dir_path, 'log', f'selenium_{date_str}.log'),
        help='path to selenium log'
    )

    parser.add_argument(
        '-f', '--fake-data',
        default=os.path.join(dir_path, 'fake_data', 'example.json'),
        help='path to fake data file'
    )

    parser.add_argument(
        '-t', '--template',
        default=os.path.join(dir_path, 'templates', 'example.html.j2'),
        help='path to html template'
    )

    parser.add_argument(
        '-i', '--images-dir',
        default=os.path.join(dir_path, 'images'),
        help='path to images directory'
    )

    return parser.parse_args()


def get_data(filename: Union[str, None] = None) -> dict:
    if not filename:
        return {}

    with open(filename, 'r') as f:
        data = json.loads(f.read())

    return data

@exception_wrapper
def main():
    args = parse_args()

    if not os.path.exists(os.path.dirname(args.log)):
        os.makedirs(os.path.dirname(args.log), exist_ok=True)
    if not os.path.isdir(os.path.dirname(args.log)):
        die(f'{os.path.dirname(args.log)} is not a directory!')

    logger.init_file_handler(args.log)
    logger.debug(f'Running with args: {args}')

    config = get_config()
    logger.debug(f'Got env config: {config}')

    if not os.path.exists(os.path.dirname(args.selenium_log)):
        os.makedirs(os.path.dirname(args.selenium_log), exist_ok=True)
    if not os.path.isdir(os.path.dirname(args.selenium_log)):
        die(f'{os.path.dirname(args.selenium_log)} is not a directory!')

    if not os.path.exists(args.fake_data):
        die(f"Fake data file '{args.fake_data}' doesn't exists!")
    if not os.path.isfile(args.fake_data):
        die(f"'{args.fake_data}' is not a file!")

    if not os.path.exists(args.template):
        die(f"Template file '{args.template}' doesn't exists!")
    if not os.path.isfile(args.template):
        die(f"'{args.template}' is not a file!")

    if not os.path.exists(args.images_dir):
        os.makedirs(args.images_dir, exist_ok=True)
    if not os.path.isdir(args.images_dir):
        die(f"'{args.images_dir}' is not a directory!")

    data = get_data(args.fake_data)

    logger.debug(f"Got data: {data}")

    with open(args.template, 'r') as f:
        html_src = f.read()

    template = Template(html_src)
    template_str = template.render(data=data['result'])

    logger.debug('Templated html:\n{}'.format(template_str))

    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        tmp_file.write(template_str.encode())
    finally:
        tmp_file.close()

    firefox_options = Options()
    firefox_options.headless = True

    logger.info("Running headless firefox...")
    browser = webdriver.Firefox(
        executable_path='/usr/bin/geckodriver',
        service_log_path=args.selenium_log,
        options=firefox_options
    )
    browser.set_window_size(1920, 1080)

    browser.get(f'file://{tmp_file.name}')
    browser.implicitly_wait(5)

    logger.info("Page rendered")

    date_str = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    image_path = os.path.join(args.images_dir, f'{date_str}.png')
    browser.save_screenshot(image_path)
    logger.info(f"Image saved to '{image_path}'")

    browser.quit()

    os.unlink(tmp_file.name)

    logger.info("DONE")

if __name__ == '__main__':
    main()
