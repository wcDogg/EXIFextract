import logging
log = logging.getLogger(__name__)

import googlemaps
from pathlib import Path
from PIL import Image, ExifTags, TiffImagePlugin
from PIL.ExifTags import GPSTAGS, TAGS
from rich import print
import typer
import warnings
warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)

import configure


class EXIFimage:
  '''Extract EXIF and GPS data from a single JPEG, PNG, or TIFF file. 
  '''
  def __init__(self, file, get_exif, get_gps):

    self.file: Path = file
    self.format: str = None
    self.mb: float = None
    self.px: int = None

    self.get_exif: bool  = get_exif
    self.has_exif: bool = None
    self.exif_data: dict = {}

    self.get_gps: bool = get_gps
    self.has_gps: bool = None
    self.gps_data: dict = {}

    self.proc_result: str = None
    self.proc_msg: list = []

    self.run()

  def __repr__(self):
    '''Returns a JSON serializable dictionary of this class.
    Deals with pathlib Path not being JSON serializable. 
    '''
    _reper = {}

    for key, val in self.__dict__.items():
      if key == 'file':
        _reper[key] = self.file.name
      else:
        _reper[key] = val

    return _reper
    
  def run(self):
    '''Primary method to extract EXIF data.
    ''' 
    log.debug('Start')
    try:
      if not self.check_is_file():
        log.debug('End')
        return
      if not self.check_max_mb():
        log.debug('End')
        return   

      self.extract()
      self.set_decimal_degrees()
      self.set_gmaps_url()
      self.get_gmaps_addr()

    except Image.UnidentifiedImageError:
      self.proc_result = configure.PROC_FALSE
      self.proc_msg.append(configure.PROC_MSG_NOT_IMAGE)
      log.debug('End: Not an image')
      return

    except Exception as e:
      self.proc_result = configure.PROC_ERROR
      self.proc_msg.append(repr(e))
      print(e)
      log.debug('End: ERROR')
      log.error(e)
      return

    finally:
      self.print_data()
    
    log.debug('End')

  def check_is_file(self):
    '''Returns bool indicating if file exists.
    '''
    log.debug('Start')

    if not self.file.is_file():
      self.proc_result = configure.PROC_ERROR
      self.proc_msg.append(configure.PROC_MSG_NOT_FOUND)
      log.debug(f'End: False: File not found: {self.file}')
      return False

    log.debug(f'End: True: File found')
    return True

  def check_max_mb(self):
    '''Returns bool indicating if file size is 
    less than or equal to the configured MAX_MB.
    '''
    log.debug('Start')

    self.mb = (self.file.stat().st_size)/1024/1024
    
    if self.mb > configure.MAX_MB:
      self.proc_result = configure.PROC_FALSE
      self.proc_msg.append(configure.PROC_MSG_MAX_PX)
      log.debug(f'End: False: {self.mb} exceeds {configure.MAX_MB} MAX_MB')
      return False

    log.debug(f'End: True: {self.mb}')
    return True

  def extract(self):
    '''Opens and checks image for format, pixels, and existence of data.
    If found, runs extraction methods.
    '''
    with Image.open(self.file) as opened:

      if not self.check_format(opened):
        return
      if not self.check_max_pixels(opened):
        return

      if self.format == 'PNG':
        opened.load()

      if not opened.getexif():
        self.has_exif = False
        self.has_gps = False
        self.proc_result = configure.PROC_TRUE  
        return

      if self.get_exif:
        self.extract_exif(opened)

      if self.get_gps:
        self.extract_gps(opened)

      self.proc_result = configure.PROC_TRUE   

  def check_format(self, opened):
    '''Returns bool indicating if file is a supported format.
    '''
    log.debug('Start')
    self.format = opened.format

    if self.format not in configure.FILE_FORMATS:
      self.proc_result = configure.PROC_FALSE
      self.proc_msg.append(configure.PROC_MSG_FORMAT)
      log.debug(f'End: False: {self.format} unsupported format')
      return False

    log.debug(f'End: True: {self.format}')
    return True

  def check_max_pixels(self, opened):
    '''Returns bool indicating if the total
    number of pixels is less than the configured MAX_PX.
    '''
    log.debug('Start')
    self.px= opened.width * opened.height

    if self.px > configure.MAX_PX:
      self.proc_result = configure.PROC_FALSE
      self.proc_msg.append(configure.PROC_FALSE)
      log.debug(f'End: False: {self.px} exceeds {configure.MAX_PX} MAX_PX')
      return False

    log.debug(f'End: True: {self.px} pixels')
    return True

  def extract_exif(self, opened):
    '''Primary method to extract EXIF data.
    '''
    log.debug('Start') 
    # Get EXIF data.
    # o.getexif().items() returns a list of tuples: [(int,val), (int,val)]
    # [0] is an int that maps to a human-readable tag name using TAGS.get().
    # [1] is the value of the tag - a str or int.
    items = opened.getexif().items()

    if items: 
      self.has_exif = True
      log.debug('EXIF items True')

      for tup in items:
        tag = ExifTags.TAGS.get(tup[0])
        val = tup[1]

        if tag not in configure.IGNORE_TAGS:

          if isinstance(val, TiffImagePlugin.IFDRational):
            val = float(val)
          elif isinstance(val, tuple):
            val = tuple(float(_t) if isinstance(_t, TiffImagePlugin.IFDRational) else _t for _t in val)
          elif isinstance(val, bytes):
            val = val.decode(errors="replace")

          self.exif_data[tag] = val  

    # Get EXIF data.
    # o.getexif().get_ifd(0x8769) provides direct access to EXIF dictionary.
    # Each key is an int that maps to a human-readable name using TAGS.get().
    # Note this data is different from .items()
    exif = opened.getexif().get_ifd(0x8769)

    if exif:
      self.has_exif = True
      log.debug('EXIF IFD True')

      for key, val in exif.items():
        tag = ExifTags.TAGS.get(key)

        if tag not in configure.IGNORE_TAGS:
        
          if isinstance(val, TiffImagePlugin.IFDRational):
            val = float(val)
          elif isinstance(val, tuple):
            val = tuple(float(_t) if isinstance(_t, TiffImagePlugin.IFDRational) else _t for _t in val)
          elif isinstance(val, bytes):
            val = val.decode(errors="replace")

          self.exif_data[tag] = val

    # Final status
    if not items and not exif:
      self.has_exif = False
      log.debug('End: EXIF False')

  def extract_gps(self, opened):
    '''Primary method to extract EXIF data.
    '''  
    log.debug('Start')  
    # Check for and get GPS data.
    # o.getexif().get_ifd(0x8825) provides direct access to the GPS IFD dictionary.
    # Each key is an int that maps to a human-readable name using GPSTAGS.get().
    gps: dict = opened.getexif().get_ifd(0x8825)

    if not gps:
      self.has_gps = False
      log.debug('End: False: No GPS')
      return
  
    self.has_gps = True

    for key, val in gps.items():
      tag = ExifTags.GPSTAGS.get(key)
      
      if tag not in configure.IGNORE_TAGS:
      
        if isinstance(val, TiffImagePlugin.IFDRational):
          val = float(val)
        elif isinstance(val, tuple):
          val = tuple(float(_t) if isinstance(_t, TiffImagePlugin.IFDRational) else _t for _t in val)
        elif isinstance(val, bytes):
          val = val.decode(errors="replace")

        self.gps_data[tag] = val
      
    log.debug('End: True: Has GPS')

  def set_decimal_degrees(self):
    '''Sets a lat and lon in decimal degree format for Google Maps URL.
    '''
    log.debug('Start')

    if not self.has_gps:
      log.debug('End: No GPS')
      return

    self.gps_data['lat_dec_degs'] = self.to_decimal_degrees(self.gps_data['GPSLatitude'], self.gps_data['GPSLatitudeRef'])

    self.gps_data['lon_dec_degs'] = self.to_decimal_degrees(self.gps_data['GPSLongitude'], self.gps_data['GPSLongitudeRef'])

    log.debug(f"End: {self.gps_data['lat_dec_degs']} : {self.gps_data['lon_dec_degs']}")

  def to_decimal_degrees(self, dms:tuple, direction:str):
    '''Converts multiple data points into a lat or lon 
    in decimal degrees format.
    '''
    log.debug('Start')

    _d = float(dms[0])
    _m = float(dms[1])
    _s = float(dms[2])

    decimal_degrees = _d + (_m / 60) + (_s / 3600)

    if direction == "S" or direction == "W":
        decimal_degrees *= -1

    log.debug(f'End: {decimal_degrees}')
    return decimal_degrees

  def set_gmaps_url(self):
    '''Uses lon and lat in decimal degrees format
    to build a Google Maps URL. 
    '''
    log.debug('Start')

    if not self.has_gps:
      self.gps_data['gmaps_url'] = None
      log.debug('End: No GPS')
      return

    lat = self.gps_data['lat_dec_degs']
    lon = self.gps_data['lon_dec_degs']
    url = f'https://www.google.com/maps/search/?api=1&query={lat}%2C{lon}'
  
    self.gps_data['gmaps_url'] = url

    log.debug(f'End: {url}')

  def get_gmaps_addr(self):
    '''Use the Google Maps Geocoding API to get a 
    human-readable address from lat and lon.
    '''
    log.debug('Start')

    if not self.has_gps or not configure.GMAPS_API_KEY:
      self.gps_data['gmaps_address'] = None
      log.debug('End: GPS False or Key False')
      return

    lat = self.gps_data['lat_dec_degs']
    lon = self.gps_data['lon_dec_degs']
    types = ['street_address', 'plus_code']

    # Set client and make request.
    gmaps = googlemaps.Client(key=configure.GMAPS_API_KEY)
    gmaps_resp = gmaps.reverse_geocode((lat, lon), result_type=types)

    # Check we have a response.
    if not gmaps_resp:
      self.gps_data['gmaps_address'] = None
      self.proc_msg.append(configure.PROC_MSG_API)
      log.debug('End: No API response')
      return

    # Response is a list of dictionaries. 
    # The first dictionary is the most specific. 
    _dict = gmaps_resp[0]
    
    # The address we want is in the `formatted_address` key.
    self.gps_data['gmaps_address'] = _dict['formatted_address']

    log.debug(f'End: {_dict["formatted_address"]}')

  def print_data(self):
    '''Prints image results to console.
    '''
    log.debug('Start')

    for key, val in self.__repr__().items():
      if type(val) is dict:
        for k, v in val.items():
          print(f'{k}: {v}')

      elif type(val) is list:
        for i in val:
          print(f'{i}')
          
      else:
        print(f'{key}: {val}')

    log.debug('End')

#
# Run this puppy :)
def main(
  file: Path = typer.Argument(
    ...,
    resolve_path=True,
    help=configure.FILE_HELP
  ),
  exif: bool = typer.Option(
    default=configure.EXIF_DEFAULT, 
    help=configure.EXIF_HELP
  ),
  gps: bool = typer.Option(
    default=configure.GPS_DEFAULT, 
    help=configure.GPS_HELP
  )
):
  '''Extract EXIF and GPS data from a single JPEG, PNG, or TIFF. 
  '''
  # Logging
  import logging
  from helpers import logger
  logger.setup_logging()
  # logger.test_logging()
  log = logging.getLogger(__name__)

  task = EXIFimage(file, exif, gps)


if __name__ == '__main__':
    typer.run(main)

