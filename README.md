# Quantum Battleships (originally by James Wootton)

This repo contains the game `Quantum Battleships` originally created by James Wootton. His original python script was "published" in [this medium article](https://decodoku.medium.com/quantum-battleships-the-first-multiplayer-game-for-a-quantum-computer-e4d600ccb3f3).

We heavily refactored the script. Most notably we
- Give the code some structure and added some explanatory comments (accepting more verbosity),
- tweaked the code to be compatible with a newer version of `projectq` (unfortunately some things got more complicated because of that),
- use `projectq`'s `Simulator` backend instead of the `IBMBackend` to avoid registering with a quantum computation provider,
- added some functionality beyond the game,
- catched *some* more errors (though, certainly not perfect).

In particular we added an option to not play the game but to instead print the expected outcomes of all possible scenarios. There are not that many ways the game can be played. Just set `PLAY_GAME = False` (see the config section of the script).

You might be disappointed that we just use a simulator. But it is actually easy to tweak the script to use any other backend, including any real quantum computer. See [the docs of projectq](https://projectq.readthedocs.io/en/latest/index.html) on how to do that.

The game is still not very fancy (actually it should still essentially look like before). I just did the rewrite for my own pleasure while studying the theory behind the game - which in contrast is very fascinating (for me). My main motivation for the rewrite was to simplify the (very small) part of the code which is actually doing the hard work and to refactor everything in a way to be easily adjustable for further experiments (as domenstrated by the config). It was a "design-goal" to essentially leave the game as is when using the script in `PLAY_GAME=True`-mode. Feel free to use the script for whatever purpose. I doubt that the original author has anything against it.

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

The game is for two players. Player 1 chooses a position for their ship from six possibilities (labeled `a`, `b`, ..., `f`). Each of the possibilities occupies two of five available positions (labeled `0`, `1`, ..., `5`). For example `a` represents a ship occupying `0` and `1`. Player 2 has two bombs available and has to choose two (different) of the five positions to throw the bombs at. After this is done, the game calculates the *intactness* of the ship. This is a (more or less random) value between -100% and +100%. A positive value means that player 1 wins, otherwise player 2 wins. In practice player 2 wins if and only if they land two hits with their bombs. The reason is that the intactness is usually close to 70% or -70% depending on the number of bombs which hit their target.

YSo you see that the intactness has essentially no contribution to the outcome of the game (who wins?). Moreover what does it tell me about quantum effects? See below for a brief explanation and further reading.

There is a little section `global configruation` at the top of the script. You can adjust the parameters to tweak the behavior of the game. In particular you can print out the (statistically) expected outcomes of all possible ways the game can be played by setting `PLAY_GAME = False`.

## Background information

As already noted the game is very simple. As for the observable behavior (if you just play it and do not look into the script), it *approximately* behaves as follows: If two bombs hit the ship player 2 wins, otherwise player 1 wins. You may ask: **OK, but what does this have to do with "quantum"?**. Independently of that you may also ask: **Why does the game bother to display "intactness" if it does not alter the result of the game?** At least those are the questions I had. We try to elaborate on that in the following.

### The observable behavior of the game

Actually the game behaves slightly different than stated above. *In theory* there is indeed a chance to lose for player 2 *even* if they land two hits, and there is a chance to win for player 2 *even* if they hit the ship less than two times. The probabilities for these abnormal cases are extremely low (in theory).

Therefore we introduced the configurable parameter `NUM_SAMPLES_FOR_GAME`. At the moment it is set to 1000. It means that for calculating the intactness 1000 samples of the same *scenario* (representing the choices of the two players) are done. Each sample can *randomly* have the outcomes +1 or -1 (in other words +100% or -100% intactness). All these outcomes are added and averaged (devided by thousand) resulting in the overall intactness value which finally gets displayed.

You can set `NUM_SAMPLES_FOR_GAME = 1` to get a game which behaves more random. Still it helps player 2 to try to hit two times but now the probability for winning is only about 85%. On the other hand player 2 has still a 15% chance to win if they do not hit two times. If you wonder about the numbers, please note that a bernoulli distribution with outcomes +1 for 85% of the time and -1 for 15% of the time has an expected outcome of 0.7 (or 70% intactness in our case).

### What the script actually does

For all practical purposes the above (in theory) exactly describes the observable behavior of the game. So a simple *non-quantum* python script involving a few calls to a random-number-generator actually suffices to implement it. We hope this explains the purpose of *intactness*. **On the other hand, now you probably wonder even more: What does this have to do with quantum mechanics?**

**The short answer is**: The game is implemented in a way which does *not* involve a ("normal") random number generator and instead relies on calls to a *5-bit quantum computer* for each sample.

If you know a little bit about random number generation you probably know that generating "truly" random numbers is not that easy. We mention that in case you wonder why we point out that we don't need a (normal) random number generator.

To understand what exactly is going on you might want to study the function `run_scenario` and in particular `entangle_CHSH`. In the following we try to give you some insight. In case you are not familiar with quantum-stuff you will certainly not understand everything but this is unavoidable. At the end I provide further material to fill the gaps.

For each sample five qubits are (implicitly) initialized to the value 0 in Z-basis. Then the two qubits representing the ship are *entangled* in a particular way. All qubits which are "hit" by a bomb are modified by a phase-gate (`S`). More precisely one of the two entangled qubits is called "Bob" and if Bob is hit it will be modified by the inverse of `S`. After these preparations are done, each qubit is measured in X-basis - returning the result in the form of a classical bit `0` or `1`. The `Measure` operator normally measures the qubit in Z-basis, however the Hadamard-Gate (`H`) acts as a change of coordinates from Z-basis to X-basis.

To actually *read out* the results we use `get_probability` to get the measurement results of all five qubits (e.g. the result could be the bit-pattern `00100`). To determine the intactness (of a single sample) we are only interested in the two bits representing the ship. If they agree (`00` or `11`) we say the ship is 100% intact, else if they disagree (`01` or `10`) we say that the ship is 100% broken. That's it!

### Further reading

To fill the gaps I highly recommend the Book *Quantum Computation and Quantum Information* by *Nielsen, Michael A. and Chuang, Isaac L.*. Have a look into Chapters 1 and 2 for a basic introduction to quantum mechanics and quantum computation. Those helped me allot to understand the script in detail.

Of particluar interest is the section about *EPR and the Bell inequality*. If you add up the three expected intactness values for the cases of up to 1 hit and the negative of the expected intactness for two hits you get four times 70% which is 240%. This is more than 200%. This probably does not sound very exciting but in a sense it is. At least if you assume that the two qubits of the ship "don't know" if the other qubit was bombed and what the outcome of the measurement was, there is a family of theorems called "Bell-type Inequalities" which state that under "common sense"-assumptions the above quantity should indeed be at most 200%. There are realworld-experiments ensuring the preconditions of the Bell-Inequalities (in some way). The situation described in the book is slightly different then what is done in the script. In particular the *Bell State* is (a little bit) different. But it should be easy the adjust the reasoning to the present situation. So, in a sense, quantum mechanics violates "common sense".
