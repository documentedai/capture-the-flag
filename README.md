# Capture The Flag (CTF)
[![PyPI Latest Release](https://img.shields.io/pypi/v/capture-the-flag.svg)](https://pypi.org/project/capture-the-flag/)
[![Package Status](https://img.shields.io/pypi/status/capture-the-flag.svg)](https://pypi.org/project/capture-the-flag/)
[![License](https://img.shields.io/pypi/l/capture-the-flag.svg)](https://github.com/documentedai/capture-the-flag/blob/master/LICENSE)
[![Upload Python Package](https://github.com/documentedai/capture-the-flag/workflows/Upload%20Python%20Package/badge.svg?branch=master)](https://github.com/documentedai/capture-the-flag/actions?query=branch%3Amaster)
[![Coverage](https://codecov.io/github/documentedai/capture-the-flag/coverage.svg?branch=master)](https://codecov.io/gh/documentedai/capture-the-flag)

Capture The Flag (CTF) is a Python package for reinforcement learning. This package is not related to [CTF Hacking](https://en.wikipedia.org/wiki/Capture_the_flag#Computer_security) competitions.
## Installation
```
pip install capture-the-flag
```
## Dependencies
- [numpy](https://www.numpy.org)
- [pyglet](http://www.pyglet.org)
## Usage
For a random game.
```python
import random
import time

import ctf


game = ctf.Ctf()
game.new_game()

fps = 30

while not game.winner:
    for unit in game.need_to_move:
        started = time.time()

        game.render()

        legal_moves = game.legal_moves()
        game.move(unit=unit, direction=random.choice(legal_moves[unit]))

        finished = time.time()
        sleeptime = 1.0/fps - (finished - started)
        if sleeptime > 0:
            time.sleep(sleeptime)

    print(game.board)

print(game.score)
print(game.winner)
```
## [Documentation](https://capture-the-flag.readthedocs.io/en/latest/)
