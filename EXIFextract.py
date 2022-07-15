import logging
log = logging.getLogger(__name__)

import filetype
import json
from os import listdir
from pathlib import Path
from PIL import Image
from rich import print
from rich.prompt import Confirm
from time import sleep
import typer
import warnings
warnings.filterwarnings('ignore', category=Image.DecompressionBombWarning)

import configure
from EXIFimage import EXIFimage
from helpers import msgs
from helpers.TaskTimer import TaskTimer


class EXIFextract:
  '''Extract EXIF data from JPEG, PNG & TIF files.
  Optionally save results to JSON and Markdown.
  '''
  def __init__(self, proc_dir, exif, gps, md, json):

    self.proc_dir: Path = proc_dir
    self.exif: bool = exif
    self.gps: bool = gps
    self.md: bool = md
    self.json: bool = json

    self.timer = TaskTimer()
    self.sleep = configure.SLEEP
  
    self.files: list = []
    self.files_processed: list = []
    self.files_not_processed: list = []
    self.files_error: list = []
    self.files_with_exif: list = []
    self.files_with_gps: list = []
    
    self.timer_summary: dict = {}
    self.files_summary: dict = {}
    self.gps_summary: list = []     # of dicts
    self.files_results: list = []   # of dicts

    self.run()


  def __repr__(self):
    '''Returns a JSON serializable dictionary of this class.
    Deals with objects not being JSON serializable (Path, TaskTimer). 
    '''
    _reper = {}
    _files = []

    for f in self.files:
      _files.append(f.name)

    for key, val in self.__dict__.items():

      if key == 'proc_dir':
        _reper[key] = str(val)

      elif key == 'timer':
        pass

      elif key == 'sleep':
        pass

      elif key == 'files':
        _reper[key] = _files

      else:
        _reper[key] = val

    return _reper

  #
  # Class methods
  def run(self):
    '''The main controller method - runs the entire task.
    '''
    log.debug('Start')

    try: 
      self.timer_start()

      if not self.get_files():
        self.timer_stop()
        self.goodbye()
        return

      self.process_files()
      self.timer_stop()
      self.generate_summaries()
      self.write_terminal()
      self.write_json()
      self.write_md()
      self.goodbye()

    except KeyboardInterrupt:
      self.stopped()
      return

    except Exception as e:
      self.error(e)
      log.error(e)
      return


  def timer_start(self):
    '''Starts the image processing timer
    and captures the start time.
    '''
    self.timer.start()


  def get_files(self):
    '''Gathers a list of JPEG, PNG, and TIFF files in proc_dir.
    Returns bool indicating if there are images to process.
    '''
    log.debug('Start')
    print(msgs.hr)
    print(f'{msgs.files_start}')

    if not listdir(self.proc_dir):
      print(f'[yellow]{msgs.files_false}')
      log.debug('End: False: No files found')
      return False

    temp = []

    for f in listdir(self.proc_dir):
      path = Path(self.proc_dir.joinpath(f)) 

      if path.is_file():
        guess = filetype.guess(path)
        if guess and guess.mime in configure.MIME_TYPES:
          temp.append(path)

    if not temp:
      print(f'[yellow]{msgs.files_false}')
      log.debug('End: False: No files found')
      return False

    self.files = temp
    print(f'[green]{len(self.files)} {msgs.files_true}')
    log.debug(f'End: True: {len(self.files)} files found')
    return True 
  

  def process_files(self):
    '''Extract data from files and capture results.
    '''
    log.debug('Start')
    print(msgs.proc_start)

    for f in self.files:

      print(msgs.hr)

      this = EXIFimage(f, self.exif, self.gps)
      self.files_results.append(this.__repr__())

      if this.proc_result == configure.PROC_TRUE:
        self.files_processed.append(this.file.name)

      if this.proc_result == configure.PROC_FALSE:
        self.files_not_processed.append(this.file.name)

      if this.proc_result == configure.PROC_ERROR:
        self.files_error.append(this.file.name)

      if this.has_exif:
        self.files_with_exif.append(this.file.name)

      if this.has_gps: 
        self.files_with_gps.append(this.file.name)
    
    print(msgs.hr)
    print(msgs.proc_end)
    log.debug('End')


  def timer_stop(self):
    '''Stops the image processing timer
    and captures the stop + elapsed times.
    '''
    self.timer.stop()
    self.timer.elapsed()


  def generate_summaries(self):
    '''Populates multiple task summary dicts.
    '''
    log.debug('Start')
    print(msgs.write_gather)

    # Time
    self.timer_summary = self.timer.timer_results

    # Files
    self.files_summary['files_found'] = len(self.files)
    self.files_summary['files_processed'] = len(self.files_processed)
    self.files_summary['files_not_processed'] = len(self.files_not_processed)
    self.files_summary['files_error'] = len(self.files_error)
    self.files_summary['files_with_exif'] = len(self.files_with_exif)
    self.files_summary['files_with_gps'] = len(self.files_with_gps)

    # GPS
    for _d in self.files_results:
      _result = {}

      if _d['has_gps']:
        _file = _d['file']
        _url = _d['gps_data']['gmaps_url']
        
        _result['file'] = _file
        _result['gmaps_url'] = _url

        if _d['gps_data']['gmaps_address']:
          _addr = _d['gps_data']['gmaps_address']

          _result['gmaps_address'] = _addr
          _result['string'] = f'{_file}: [{_addr}]({_url})'
          _result['string_console'] = f'[white]{_file}[/white]: [yellow]{_addr}[/yellow]: {_url}'
        
        else:
          _result['gmaps_address'] = None
          _result['string'] = f'{_file}: [{_url}]({_url})'
          _result['string_console'] = f'[white]{_file}[/white]: {_url}'

        self.gps_summary.append(_result)

    sleep(self.sleep)
    log.debug('End')


  def write_terminal(self):
    '''Prints task summaries to the terminal.
    '''
    log.debug('Start')

    print(msgs.hr)
    print('TIMER SUMMARY')
    for k, v in self.timer_summary.items():
      print(f'{k}: {v}')
    sleep(self.sleep)

    print(msgs.hr)
    print('FILES SUMMARY')
    for k, v in self.files_summary.items():
      print(f'{k}: {v}')
    sleep(self.sleep)

    if self.files_not_processed:
      print(msgs.hr)
      print('FILES NOT PROCESSED')
      for f in self.files_not_processed:
        print(f'* {f}')
      sleep(self.sleep)

    if self.files_error:
      print(msgs.hr)
      print('FILES ERROR')
      for f in self.files_error:
        print(f'* {f}')
      sleep(self.sleep)
       
    if self.gps_summary: 
      print(msgs.hr)
      print('GPS SUMMARY')
      for d in self.gps_summary:
        print(f'* {d["string_console"]}')    
      sleep(self.sleep)

    log.debug('End')

  
  def write_json(self):
    '''Write results to a JSON file inside proc directory.
    '''
    log.debug('Start')

    if not self.json:
      log.debug('End: JSON False')
      return

    print(msgs.hr)
    print(msgs.write_start_json)

    _file = f'{self.proc_dir.name}.json'
    _path = Path(self.proc_dir / _file)

    try: 
      with Path(_path).open('w', encoding='utf-8') as o:
        o.write(json.dumps(self.__repr__(), indent=4))
      log.debug('End')

    except Exception as e:
      print(msgs.write_error)
      print(repr(e))
      log.error(e)
      return


  def write_md(self):
    '''Write results to Markdown file inside proc directory.
    '''
    log.debug('Start')

    if not self.md:
      log.debug('End: MD False')
      return
    
    file = f'{self.proc_dir.name}.md'
    path = Path(self.proc_dir / file)

    print(msgs.hr)
    print(msgs.write_start_md) 

    try:
      with Path(path).open('w', encoding='utf-8') as o: 
        o.write(f'# {path.name} \n')

        o.write('\n')
        o.write(f'## Task Summary \n')
        o.write('\n')

        o.write(f'* proc_dir: {self.proc_dir}\n')
        o.write(f'* get_exif: {self.exif}\n')
        o.write(f'* get_gps: {self.gps}\n')
        o.write(f'* write_json: {self.json}\n')
        o.write(f'* write_md: {self.md}\n')

        for k, v in self.timer_summary.items():
          o.write(f'* {k}: {v} \n')
        
        o.write('\n')
        o.write(f'## Files Summary \n')
        o.write('\n')

        for k, v in self.files_summary.items():
          o.write(f'* {k}: {v} \n') 

        if self.files_error:
          o.write('\n')
          o.write(f'### Files with Errors \n')
          o.write('\n')
          
          for f in self.files_error:
            o.write(f'* {f} \n')

        if self.files_not_processed:
          o.write('\n')
          o.write(f'### Files Not Processed \n')
          o.write('\n')
          
          for f in self.files_not_processed:
            o.write(f'* {f} \n')

        if self.gps_summary:
          o.write('\n')
          o.write(f'## GPS Summary \n')
          o.write('\n')
          for d in self.gps_summary:
            o.write(f'* {d["string"]}\n')

        o.write('\n')
        o.write(f'## Results \n')

        for d in self.files_results:
          o.write('\n')  
          o.write(f'### {d["file"]}\n')
          o.write('\n') 
          o.write('```')
          for k, v in d.items(): 
            if type(v) is dict:
              for k, v in v.items():
                o.write(f'{k}: {v}\n')

            elif type(v) is list:
              for i in v:
                o.write(f'{i}\n')
                
            else:
              o.write(f'{k}: {v}\n')
          o.write('```')
      
      log.debug('End')

    except Exception as e:
      print(msgs.write_error)
      print(repr(e))
      log.error(e)
      return


  #
  # Endings
  def stopped(self):
    '''Famous last words.
    '''
    self.timer_stop()
    print('\n')
    print(msgs.hr)
    print(f'[red]{msgs.task_stopped}')
    print(msgs.div)  
    log.debug('Goodbye stopped')  

  def error(self, error):
    '''Famous last words.
    '''
    self.timer_stop()
    print(msgs.hr)
    print(error)
    print(msgs.hr)
    print(f'[red]{msgs.task_error}')
    print(msgs.div)
    log.debug('Goodbye error')

  def goodbye(self):
    '''Famous last words.
    '''
    print(msgs.hr)
    print(f'[green]{msgs.task_end}')
    print(msgs.div)  
    log.debug('Goodbye') 


#
# Run this puppy :)
def hello():
  '''Prints the app banner to console.
  '''
  print(f'[blue]{msgs.div}')
  print(f'{configure.APP_NAME}: {configure.APP_REPO}')
  print(configure.APP_DESC)
  print(f'[blue]{msgs.div}')

def main(
  proc_dir: Path = typer.Argument(
    ...,
    exists=True,
    file_okay=False,
    dir_okay=True,
    writable=True,
    readable=True,
    resolve_path=True,
    help=configure.DIR_HELP
  ),
  exif: bool = typer.Option(
    default=configure.EXIF_DEFAULT, 
    help=configure.EXIF_HELP
  ),
  gps: bool = typer.Option(
    default=configure.GPS_DEFAULT, 
    help=configure.GPS_HELP
  ),
  md: bool = typer.Option(
    default=configure.MD_DEFAULT, 
    help=configure.MD_HELP
  ),
  json: bool = typer.Option(
    default=configure.JSON_DEFAULT, 
    help=configure.JSON_HELP
  )
):
  '''Extract EXIF and GPS data from JPEG, PNG, and TIFF. 
  '''
  # Logging
  import logging
  from helpers import logger
  logger.setup_logging()
  log = logging.getLogger(__name__)

  # Hello + confirmation
  hello()
  typer.echo(f'proc_dir {proc_dir}')
  typer.echo(f'--exif {exif}')
  typer.echo(f'--gps {gps}')
  typer.echo(f'--md {md}')
  typer.echo(f'--json {json}')

  typer.echo(msgs.hr)
  conf = Confirm.ask(configure.TASK_CONF, default=True)
  if not conf:
      print(f'[red]{msgs.task_stopped}')
      print(msgs.hr)
      raise typer.Exit()

  # Start 
  print(f'Starting task. [yellow]{msgs.task_stop}')
  task = EXIFextract(proc_dir, exif, gps, md, json)


if __name__ == '__main__':
    typer.run(main)

