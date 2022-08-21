"""
Example of plotext usage

Includes conversion of MxNx3 color array to MxNx(3-tuple) for use with color images.

See docs for more:
https://github.com/piccolomo/plotext
"""

import numpy as np
import plotext as plt


def img2list(img) -> list:
    zlist = []

    sz = zmat.shape
    for r in range(sz[0]):
        tmp = []
        for c in range(sz[1]):
            px = zmat[r,c,:]
            tmp.append((px[0], px[1], px[2]))
        zlist.append(tmp)
    return zlist


cols, rows = 200, 45
p = 1
matrix = [[(abs(r - rows / 2) + abs(c - cols / 2)) ** p for c in range(cols)] for r in range(rows)]

plt.matrix_plot(matrix)
plt.show()

zmat = np.zeros((100,100,3),np.uint8)
zmat[50,50,:] = [100,100,200]

zlist = img2list(zmat)

plt.clc()
plt.matrix_plot(zlist)
plt.show()
