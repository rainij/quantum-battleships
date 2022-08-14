import itertools, math, time, getpass # normal python stuff

from projectq import MainEngine, types  # import the main compiler engine
from projectq.ops import H, S, T, X, CNOT, get_inverse, Measure  # import the operations we want to perform

###############################################################################
### global configuration
###############################################################################

play_game = True
timeout = 1 # seconds
num_samples_for_game = 1000

###############################################################################
### global constants
###############################################################################

INVALID_INPUT_MSG = "u wot m8? Try that again."

# A ship (its positions) is represented by two of five qubits.
ship_bit_positions = dict(
    a = [0, 1],
    b = [0, 2],
    c = [1, 2],
    d = [2, 4],
    e = [2, 3],
    f = [3, 4],
)

###############################################################################
### Auxiliary functions
###############################################################################

def display_intro():
    print("\n\n\n\n===== Welcome to Quantum Battleships! =====\n\n")
    print("  ~~ A game by the Decodoku project ~~ ")
    print("\n\n")
    print("When in doubt, press any key to continue!")
    input()
    print("This is a game for two players.")
    input()
    print("Player 1 will choose the position of a Battleship.")
    input()
    print("Player 2 will try to bomb it.")
    input()

def display_intro_player_1():
    # get player 1 to position boat
    print("We start with Player 1.")
    print("Look away Player 2!")
    input()
    print("The lines in the bowtie shape below are the places you can place your ship.\n")
    print("|\     /|")
    print("| d   b |")
    print("|  \ /  |")
    print("f   X   a")
    print("|  / \  |")
    print("| e   c |")
    print("|/     \|\n")
    # note: at time of release, ProjectQ does not actually put the qubits in the places you'd expect on the IBM chip
    input()

def display_intro_player_2():
    # get player 2 to position three bombs
    time.sleep(timeout)
    print("\nPlayer 2: You're up!")
    input()
    print("The numbers below mark places you can bomb.\n")
    print("4       0")
    print("|\     /|")
    print("| \   / |")
    print("|  \ /  |")
    print("|   2   |")
    print("|  / \  |")
    print("| /   \ |")
    print("|/     \|")
    print("3       1\n")
    input()

def display_intermidiate_message():
    time.sleep(timeout)
    print("\nNow let's see how intact the ship is.")
    print("Between 1% and 100% intact means it's still afloat.")
    print("Between -1% and -100% intact means it's swimming with the fishes.")
    print("0% intact could go either way.\n")

def display_results(damage, rounding = False):
    time.sleep(timeout)
    conv = int if rounding else float # crude way to round
    print(f"The ship is {conv( 100*(1 - 2*damage) )}% intact")
    if play_game:
        print(f"(which means {conv( -100*(1 - 2*damage) )}% broken).\n")
        if (damage > 0.5):
            print("It has been destroyed!\nPlayer 2 wins!\n\n")
        else:
            print("It's still afloat!\nPlayer 1 wins!\n\n")


def prompt_for_ship(default_ship = None):
    """Ask user for the ship. If default_ship is given skip asking user."""
    available_ships = ship_bit_positions.keys()

    if default_ship is not None and default_ship in available_ships:
        return default_ship

    while True:
        ship = getpass.getpass(f"Choose a line for your ship. ({', '.join(available_ships)})\n")
        if ship in available_ships:
            return ship
        else:
            print(INVALID_INPUT_MSG)


def prompt_for_bombs(default_bombs = None):
    """Ask user for bombs. If default_bombs is given skip asking user."""
    bombs = []
    if default_bombs is None: default_bombs = []

    ordinals = ["first", "second"]

    while (len(bombs) < 2):
        bomb = default_bombs[len(bombs)] if len(bombs) < len(default_bombs) else None

        if bomb is None:
            try:
                bomb = int(input(f"\nChoose a position for your {ordinals[len(bombs)]} bomb. (0, 1, 2, 3 or 4)\n"))
            except:
                print(INVALID_INPUT_MSG)
                continue

        if (bomb >= 0) and (bomb < 5) :
            if bomb not in bombs:
                bombs.append(bomb)
            else:
                print("That's already been bombed. Choose again.")
        else:
            print(INVALID_INPUT_MSG)

    return bombs


def entangle_CHSH(qubits, bobs, i, j):
    """Make entangled pair of qubits prepared for a CHSH experiment.

    qubits and bobs are output parameters. i and j are the desired positions of
    the qubits representing the ship.
    """
    # Make Bell-Pair:
    H | qubits[i]
    CNOT | (qubits[i], qubits[j])
    # Use an X to anticocorrelate Z basis (measurements will be made in x-y
    # plane of the Bloch-Sphere):
    X | qubits[i]
    # Do a phase-shift of angle pi/4 on any Bobs
    bobs[i] = 1
    T | qubits[i]


def get_probabilities(qubits: types.Qureg):
    eng = qubits.engine
    return { bit_string: eng.backend.get_probability(bit_string, qubits)
        for bit_string in itertools.product(*5*[[0, 1]])}


def run_scenario(eng, ship, bombs, do_measurements = True):
    qubits = eng.allocate_qureg(5)
    bobs = 5 * [0] # 0="no bob", 1="is bob".

    # prepare the two ship-qubits and mark which one is the bob
    entangle_CHSH(qubits, bobs, *ship_bit_positions[ship])

    # apply the bombs
    # whether or not a bomb is applied corresponds to the two measurment choices for CHSH (in x-y plane)
    for bomb in bombs:
        if (bobs[bomb] == 1):
            get_inverse(S) | qubits[bomb]
        else:
            S | qubits[bomb]

    # TODO: Better name
    results = None

    if do_measurements:
        # measure should be done in X basis, therefore we apply Hadamard here
        for i in range(5):
            H | qubits[i]
            Measure | qubits[i]
        eng.flush()  # flush all gates (and execute measurements)

        # get measurement results (note: the keys are tuples)
        results = get_probabilities(qubits) # discrete results (in theory only zeros or ones)
    else:
        for i in range(5):
            H | qubits[i]
            # NOTE: No measurement!
        eng.flush()

        # Here we immediately get the theoretical probabilities
        results = get_probabilities(qubits)

        for i in range(5):
            # Dummy-measurement since projectq complains about it if we leave it out
            Measure | qubits[i]
        eng.flush()

    return results

###############################################################################
### Main code
###############################################################################

def main(ship = None, bombs = None):
    eng = MainEngine() # Uses a simulation of a quantum computer

    if play_game: display_intro()

    if play_game: display_intro_player_1()
    ship = prompt_for_ship(ship)

    if play_game: display_intro_player_2()
    bombs = prompt_for_bombs(bombs)

    # If we do not play the game we directly get the probabilities, hence we do
    # not need more then one run.
    num_samples = num_samples_for_game if play_game else 1

    if play_game: print(f"\nWe'll now run {num_samples} samples of this scenario and see what happens.")

    # Not sure if this loop is really necessary, but the approach from the
    # original script didn't work anymore (for the Simulator backend).
    results = dict()
    for i in range(1, num_samples + 1):
        if play_game: print(f"{int(100*(i/num_samples)):3}% Done.", end="\r" if i != num_samples else "\n")
        r = run_scenario(eng, ship, bombs, do_measurements=play_game)

        for bs, prob in r.items():
            results.setdefault(bs, 0.0)
            results[bs] += prob / num_samples

    if play_game: display_intermidiate_message()

    # determine damage for ship
    damage = 0
    for bs0 in itertools.product(*3*[[0, 1]]):
        for bits in [[0, 1], [1, 0]]:
            bit_string = list(bs0)
            bit_string.insert(ship_bit_positions[ship][0], bits[0])
            bit_string.insert(ship_bit_positions[ship][1], bits[1])
            bit_string = tuple(bit_string)
            damage += results[bit_string]

    display_results(damage, rounding=play_game)


if __name__ == "__main__":
    if play_game:
        main()
    else:
        timeout = 0
        ships = ship_bit_positions.keys()
        #ships = ["a"]
        for ship in ships:
            bomb_combis = itertools.combinations([0, 1, 2, 3, 4], 2)
            for bombs in bomb_combis:
                print(f"ship={ship}, bombs={bombs}", end=": ")
                main(ship, bombs)
            print()
