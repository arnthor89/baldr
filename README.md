# baldr

## Getting started

### Prerequisites

You will need a Python 3.7 installation and [poetry](https://python-poetry.org/).
The instructions for installation of poetry are [here](https://python-poetry.org/docs/master/#installation).

Install Poetry on osx/linux:
```sh
curl -sSL https://install.python-poetry.org | python3 -
```

Install dependencies:
```sh
poetry install
```

## Run the project

Run the project:
```sh
poetry shell
python3 baldr/main.py --image-path=assets/sample.png
```

## Options

| Short | Long          | Default | Description                                      |
| ----- | ------------- | ------- | ------------------------------------------------ |
| -h    | --help        |         | Show help message                                |
| -i    | --image-path  |         | Path to the image to get the color pallet from   |
|       | --width       | 10      | Generated image width [1-50]                     |
|       | --height      | 10      | Generated image height [1-50]                    |
|       | --square-size | 128     | Pixel size of each square [1-256]                |
| -s    | --save        | False   | Save the image to the current path as a png file |
| -o    | --open        | False   | Open the image                                   |

Example:
```sh
python3 baldr/main.py --image-path=assets/sample.png --width=5 --height=5 --square-size=32 -s -o
```
