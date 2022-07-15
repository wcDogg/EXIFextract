# EXIFextract

* Python 3.10+ command line tools to extract EXIF metadata from JPG, TIFF, and PNG files.
* Extract data for a single image or all images in a directory.
* For images with GPS data, generates a Google Maps URL.
* Add an optional Google Maps Geocoding API key to automatically get the address. 
* Auto-writes results to terminal
* For directory processing, optionally write results to JSON, and Markdown.


## Windows Prerequisite

For TIFF, Pillow requires `numpy` and `libtiff`. When installing `libtiff` you may get an error that includes: 

```
error: subprocess-exited-with-error
...
from numpy.distutils.core import setup, Extension
```

If this happens, install [Build Tools for Visual Studio 2022](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022). This provides MSVC - a common requirement when you need to use Python bindings for C, which is what `libtiff` is. 

* Install **Workload: Desktop development with C++** - note it has MVSVC.
* Use the default options - the MSVC box is under **Optional** and should be checked.


## Environment 

1. Clone repo.
2. Create a Python 3.10+ virtual env inside `EXIFextract` directory.
3. `py -m pip install -r requirements.txt --upgrade`.
4. **IMPORTANT**: Rename `.env.example` to `.env`. 
5. **IMPORTANT**: Ensure `.env` is added to `.gitignore` - never upload `.env` files!
6. Optional: Add Google Maps Geocoding API key to `.env`.
7. Optional: Use `configure.py` to adjust defaults.


## Test Images

* `test-images` contains JPEG, TIFF, and PNG files with and without GPS data for testing. 
* Here you can also view sample JSON and Markdown result files. 


## The Options

Use `configure.py` to adjust defaults. 

EXIFextract gets both EXIF and GPS data by default. It gets these data separately, so you can disable one or the other. I'm interested in GPS data, so I often disable EXIF data so there's less to look at.

```
# Single image + directory

--no-exif   # Disable EXIF data
--no-gps    # Disable GPS data
```

Image processing results are written to the console. When processing a directory, you can optionally save results to Markdown and / or JSON. These files are automatically saved to the proc directory.

```
# Directory

--md    # Write to Markdown
--json  # Write to JSON
```

You can also adjust the option defaults in `configure.py`.

## Process a Directory

```
py EXIFextract.py --help
py EXIFextract.py "D:\GitHub\EXIFextract\test-images\jpeg"
py EXIFextract.py --json --md "D:\GitHub\EXIFextract\test-images\jpeg"
py EXIFextract.py --json --md "D:\GitHub\EXIFextract\test-images\png"
py EXIFextract.py --json --md "D:\GitHub\EXIFextract\test-images\tiff"
py EXIFextract.py --json --md "D:\GitHub\EXIFextract\test-images\other"
```

## Process a Single Image

```
py EXIFimage --help

# JPEG
py EXIFimage.py "D:\GitHub\EXIFextract\test-images\jpeg\001.jpg"
py EXIFimage.py "D:\GitHub\EXIFextract\test-images\jpeg\003.jpg"
py EXIFimage.py "D:\GitHUb\EXIFextract\test-images\jpeg\004.jpg"

# PNG
py EXIFimage.py "D:\GitHub\EXIFextract\test-images\png\003.png"
py EXIFimage.py "D:\GitHub\EXIFextract\test-images\png\004.png"

# TIFF
py EXIFimage.py "D:\GitHub\EXIFextract\test-images\tiff\003.tiff"
py EXIFimage.py "D:\GitHub\EXIFextract\test-images\tiff\004.tiff"
py EXIFimage.py "D:\GitHub\EXIFextract\test-images\tiff\texture.tif"
```

## .env + Google Maps Geocoding API

If an image has geolocation data, a Google Maps URL is generated using longitude & latitude. In addition, if you add a Geocoding API key, the script will also get the street or plus code address.

* In either case, rename `.env.example` to `.env`.
* Ensure `.env` is added to `.gitignore` - never upload `.env` files!
* If you do NOT want to use the API, leave as `GMAPS_API_KEY = False`.
* If you DO want to use the API, set `GMAPS_API_KEY = 'yourkeyhere'` - note the single 'quotes'.
  

## Ignored Tags

Some tags contain gobbledygook that isn't human-readable. In `configure.py` there is a list of `IGNORE_TAGS` that are omitted when writing results. Add or remove tags to this list as you see fit. 


## File Size Maximums

What constitutes a decompression bomb is scenario-specific. Use `configure.py` to set a reasonable `MAX_MB` and `MAX_PX` for your work.


## Why `sleep()`?

Opening, reading, then closing a file is super fast. So fast that sometimes, my console can't print results fast enough and lines get skipped. Adding `sleep()` was the easiest way to combat this. 

The `sleep()` duration is set in `configure.py`. You can't delete this global, but you can change it to `0.0` or another float value if you'd like. 

