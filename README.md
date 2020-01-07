# tetri.space

## Dependencies:
- flask
- numpy
- windows-curses

## Start core with:
python3 core/core.py

## Start REST-api with:
~/workspace/tetri.space$ export FLASK_APP=rest.rest
~/workspace/tetri.space$ export FLASK_ENV=development
~/workspace/tetri.space$ flask run

## Start client with:

Linux:
    git clone https://github.com/sebastianPsm/tetri.space
    python3 tetri.space/tetrispace/core.py

Windows:
    git clone https://github.com/sebastianPsm/tetri.space
    python3 -m pip install windows-curses
    python3 tetri.space/tetrispace/core.py

![test client](https://github.com/sebastianPsm/tetri.space/raw/master/img/test%20client.png "test client")