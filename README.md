Fork of [deepblueLXXXIV/arknights-auto-separate-or-cut-pause](https://github.com/deepblueLXXXIV/arknights-auto-separate-or-cut-pause).

This fork's dependencies prefer Python 3.12+

## Changes from the original repo:
- Slight speed improvements
- Ui refactoring
- Support for cn/en/ja languages
- Better dependency organization

## How to run:
### Windows:
- Download and run the binaries from the [releases tab](https://github.com/simpleblackshirt/arknights-auto-separate-or-cut-pause/releases) 

or

1. ``setup.bat``
2. ``venv\Scripts\activate.bat``
3. ``python cut_tool.py``

### Linux:
  1. ``sudo apt-get install python3.12 python3-venv ffmpeg``
  2. ``python3 -m venv venv``
  3. ``source venv/bin/activate``
  4. ``pip install -r requirements.txt``
  5. ``python cut_tool.py``