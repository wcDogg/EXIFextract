from ctypes import cast
from pathlib import Path
from decouple import config

#
# Project
APP_NAME = 'EXIFextract'
APP_DIR = Path(__file__).parent
APP_AUTHOR = 'wcDogg'
APP_REPO = 'https://github.com/wcDogg/EXIFextract'
APP_DESC = 'Extract EXIF and GPS data from JPG, TIFF, PNG.\nOptionally save results as JSON & Markdown.'

#
# Supported file formats.
FILE_FORMATS = ['JPEG', 'TIFF', 'PNG']
MIME_TYPES = ['image/jpeg', 'image/tiff', 'image/png']

#
# Max file size to process. Out-of-range are skipped. 
MAX_MB = 60

#
# Max width * height px to process.
# Decompression bomb threshold.
MAX_PX = 144000000

#
# Task
DIR_HELP = 'The path to a directory with images to process.'
FILE_HELP = 'The path to an image file.'

EXIF_DEFAULT = True
EXIF_HELP = 'Extract EXIF data.'

GPS_DEFAULT = True
GPS_HELP = 'Extract GPS data.'

MD_DEFAULT = False
MD_HELP = 'Write results to Markdown.'

JSON_DEFAULT = False
JSON_HELP = 'Write results to JSON.'

TASK_CONF = 'Are the options above correct?'

#
# Goggle Maps API
# !!! Add key to .env - do not edit here !!!
if config('GMAPS_API_KEY') == 'False':
  GMAPS_API_KEY = config('GMAPS_API_KEY', default=False, cast=bool)
else: 
  GMAPS_API_KEY = config('GMAPS_API_KEY')

#
# Sleep allows results time to print to terminal
SLEEP = 0.10

#
# Tags with a bunch of gobbledygook that isn't human-readable.
# IMPORTANT: Do not delete 'GPSInfo'! 
# It's ignored here because it's retrieved as its own dictionary.
IGNORE_TAGS = ['GPSInfo', 'MakerNote', 'UserComment', 'InterColorProfile', 'XMLPacket', 'ImageResources', 'icc_profile', 'transparency', 'PrintImageMatching', 'StripOffsets', 'StripByteCounts']

#
# An image is either processed, not processed, or has error.
# Each result type has associated messages.
# These are here vs msgs.py because they're used 
# in validations and post-process sifting. 
PROC_TRUE = 'Processed'
PROC_MSG_API = 'Problem with Google Maps API'

PROC_FALSE = 'Not processed'
PROC_MSG_NOT_IMAGE = 'File is not an image' 
PROC_MSG_FORMAT = 'Unsupported image format'
PROC_MSG_MAX_MB = f'File exceeds the {MAX_MB} MB max'
PROC_MSG_MAX_PX = f'File exceeds the {MAX_PX} pixel max'

PROC_ERROR = 'Error'
PROC_MSG_NOT_FOUND = 'File not found'


#
# Logging (logger.py)

# 'NOTSET' 0, 'DEBUG' 10, 'INFO' 20, 'WARNING' 30, 'ERROR' 40, 'CRITICAL' 50
LOG_CONSOLE_LEVEL = 'INFO'
# 'standard', 'complete'
LOG_FORMAT = 'standard'

LOG_DIR = APP_DIR / 'logs'

LOG_FILE_INFO = APP_NAME + '_info.log'
LOG_PATH_INFO = Path(LOG_DIR / LOG_FILE_INFO) 

LOG_FILE_DEBUG = APP_NAME + '_debug.log'
LOG_PATH_DEBUG = Path(LOG_DIR / LOG_FILE_DEBUG) 

LOG_FILE_WARN = APP_NAME + '_warning.log'
LOG_PATH_WARN = Path(LOG_DIR / LOG_FILE_WARN)

LOG_FILE_ERROR = APP_NAME + '_error.log'
LOG_PATH_ERROR = Path(LOG_DIR / LOG_FILE_ERROR)

LOG_FILE_CRIT = APP_NAME + '_critical.log'
LOG_PATH_CRIT = Path(LOG_DIR / LOG_FILE_CRIT)


