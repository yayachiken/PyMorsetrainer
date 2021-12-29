A simple Morse code trainer written in Python for the Koch method with
Farnsworth timing.

Installation
------------

This program requires Python 3 with PyQt5, PySounddevice and Scipy installed.

The recommended way to install these is by your distributions package manager
or pip.

For example, on Arch Linux you can use

    pacman -S python-pyqt5 python-pysounddevice python-scipy

to install the required dependencies.

About the Koch method
---------------------

The Koch method was developed by German psychologist Ludwig Koch to speed up
training of new telegraphy operators.

To quickly recognize Morse characters, the operator needs to intuitively
tell the characters apart by their sound alone, because cognitive decoding
processes are too slow. Before Koch developed his method, Morse operators
would often "hit a wall" at around 10 words per minute, and take a lot of
(often frustrating) practice to proceed past that "wall".

For that reason, training takes place at a speed of at least 20 words per
minute. At this speed, cognition is not able to keep up with decoding each
letter, and the brain is forced to associate the sounds directly with the
letters, without unconsciously constructing "decoding tables".

Afterwards, the operator will be able to use Morse code at a comfortable
speed with potential to get faster with even more practice.

To allow training to drop to lower speeds, the Farnsworth timing was developed.
In Farnsworth timing, the letters are unchanged, but the pauses between letters
and words may be lengthened.

At first, newer operators will only be required to distinguished between two
characters of morse code. When they are able to copy a random stream of these
two characters accurately (i.e. with 90% accuracy or larger), they have mastered
these two letters. After that they can proceed to the next lesson, where another
letter is introduced, until the whole alphabet is learned.

Koch noted during experiments, that certain orders of letters allowed his
students to learn a lot quicker. For that reason, the letters in this
applications are ordered according to such a recommendation.

License
-------

This program is licensed under the GNU General Public License version 3.

See file COPYING for details.
