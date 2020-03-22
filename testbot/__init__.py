import asyncio
import logging
import os
import sys

DEBUG = os.environ.get('DEBUG', False)

logging.basicConfig(
    format='%(asctime)s | %(name)-24s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG if DEBUG else logging.INFO,
    handlers=(logging.StreamHandler(stream=sys.stdout),)
)

if DEBUG != 2:
    logging.getLogger('asyncio').setLevel(logging.ERROR)
    logging.getLogger('discord').setLevel(logging.ERROR)
    logging.getLogger('websockets').setLevel(logging.ERROR)

if os.name == 'nt':
    # Required by aiodns.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
