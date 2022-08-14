# Quantum Battleships (originally by James Wootton)

This repo contains the game `Quantum Battleships` originally devised by James Wootton. His original python script was "published" in [this medium article](https://decodoku.medium.com/quantum-battleships-the-first-multiplayer-game-for-a-quantum-computer-e4d600ccb3f3).

We heavily refactored the script. Most notably we
- Give the code some structure and added some explanatory comments (accepting more verbosity),
- tweaked the code to be compatible with a newer version of `projectq` (unfortunately some things got more complicated because of that),
- use `projectq`'s `Simulator` backend instead of the `IBMBackend` to avoid registering with a quantum computation provider,
- added some functionality beyond the game,
- catched *some* more errors (though, certainly not perfect).

In particular we added an option to not play the game but to instead print the expected outcomes of all possible scenarios. There are not that many ways the game can be played. Just set `PLAY_GAME = False` (see the config section of the script).

You might be disappointed that we just use a simulator. But it is actually easy to tweak the script to use any other backend, including any real quantum computer. See [the docs of projectq](https://projectq.readthedocs.io/en/latest/index.html) on how to do that.

The game is still not very fancy (actually it should look roughly the same). I just did the rewrite for my own pleasure while studying the theory behind the game - which in contrast is very fascinating (for me). My main motivation for the rewrite was to simplify the (very small) part of the code which is actually doing the hard work and to refactor everything in a way to be easily adjustable for further experiments (as domenstrated by the config). It was a "design-goal" to essentially leave the game as is when using the script in `PLAY_GAME=True`-mode. Feel free to use the script for whatever purpose. I doubt that the original author has anything against it.

## Setup

To play the game we suggest to create a virtual environment for python. Make sure you have a recent version of `python3` and do the following (here and in the following I demonstrate the steps as it would be done in a "usual" Linux distro):

```shell
$ # Open the terminal and navigate to the directory of this README.
$ python -m venv .venv
```

This creates a directory `.venv`. Activate the virtual environment by typing

```shell
$ source .venv/bin/activate
(.venv) $ # Usually this changes the command-prompt like here.
```

Now, if you type `python` the interpreter from that folder should be used. If in doubt you could use the command `type python` and check if the path points to a binary within the `.venv` folder.

Next we install the required packages:

```shell
(.venv) $ python -m pip install -r requirements.txt
```

## Play the game

After you successfully completed the setup you can start and play the game by running

```shell
(.venv) $ python quantum-battleships.py
```

Note that you have to run the script from within the virtual environment (see setup).

There is a little section `global configruation` at the top of the script. You can adjust the parameters to tweak the behavior of the game. In particular you can print out the (statistically) expected outcomes of all possible ways the game can be played by setting `PLAY_GAME = False`.
