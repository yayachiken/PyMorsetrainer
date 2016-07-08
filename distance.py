#!/usr/bin/env python3

"""
(C) 2016 David Kolossa

This file is part of PyMorsetrainer.

PyMorsetrainer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyMorsetrainer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyMorsetrainer.  If not, see <http://www.gnu.org/licenses/>.
"""


from enum import Enum

Action = Enum("Action", ("NONE", "MATCH", "DELETION", "INSERTION"))

def global_matching(a, b):
    """ Implementation of the Needle-Wunsch algorithm """
    len_a = len(a)
    len_b = len(b)
    distances = [[0 for j in range(len_b+1)] for i in range(len_a+1)]
    actions = [[Action.NONE for j in range(len_b+1)] for i in range(len_a+1)]
    for i in range(len_a+1):
        distances[i][0] = -i
        actions[i][0] = [Action.INSERTION]
    for j in range(len_b+1):
        distances[0][j] = -j
        actions[0][j] = [Action.DELETION]
    
    for i in range(1, len_a+1):
        for j in range(1, len_b+1):
            cost = {}
            cost[Action.MATCH]     = distances[i-1][j-1] + (1 if a[i-1] == b[j-1] else -1)
            cost[Action.DELETION]  = distances[i  ][j-1] - 1
            cost[Action.INSERTION] = distances[i-1][j  ] - 1
            action = max(cost, key=cost.get)
            minimum = cost[action]
            actions[i][j] = [a for a,c in cost.items() if c == minimum]
            distances[i][j] = cost[action]
    return tuple([distances[len_a][len_b]] + __traceback(a, b, distances, actions))
    
    
def __traceback(a, b, distances, actions):
    y = len(actions)-1
    x = len(actions[0])-1
    
    path = []
    pathactions = []
    while (x,y) != (0,0):
        path.append((x,y))
        action = actions[y][x][0]
        pathactions.append(action)
        if action == Action.MATCH:
            x -= 1
            y -= 1
            continue
        elif action == Action.INSERTION:
            x -= 0
            y -= 1
            continue
        elif action == Action.DELETION:
            x -= 1
            y -= 0
            continue
    path.append((0,0))
    path = [x for x in reversed(path)]
    pathactions = [x for x in reversed(pathactions)]
    i = 0
    j = 0
    matching = []
    for action in pathactions:
        if action == Action.MATCH:
            matching.append((a[i], b[j]))
            i += 1
            j += 1
        elif action == Action.INSERTION:
            matching.append((a[i], "-"))
            i += 1
        elif action == Action.DELETION:
            matching.append(("-", b[j]))
            j += 1
    
    return (["".join(x) for x in zip(*matching)])


def levenshtein(a, b):
    return __do_levenshtein(a, b, len(a), len(b))

def __do_levenshtein(a, b, i, j):
    if 0 in (i,j):
        return max(i,j)
    return min(__do_levenshtein(a, b, i-1, j  ) + 1,
               __do_levenshtein(a, b, i,   j-1) + 1,
               __do_levenshtein(a, b, i-1, j-1) + (1 if a[i-1] != b[j-1] else 0))
