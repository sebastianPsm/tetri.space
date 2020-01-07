# tetri.space

## Dependencies:
- flask
- numpy
- windows-curses (on windows)

## Get

### Linux
```console
git clone https://github.com/sebastianPsm/tetri.space
cd tetri.space
```

### Windows
```console
git clone https://github.com/sebastianPsm/tetri.space
python3.7.exe -m pip install windows-curses
cd ./tetri.space
```

## Start REST-api with:
### Linux
```console
export FLASK_APP=rest.py
export FLASK_ENV=development
flask run
```

### Windows
```console
$env:FLASK_APP = "rest.py"
$env:FLASK_ENV = "development"
python3.7.exe -m flask run
```

## Start client with:

```console
python3.7.exe .\tetrispace\core.py
```

### Screenshot
![test client](https://github.com/sebastianPsm/tetri.space/raw/master/img/test%20client.png "test client")