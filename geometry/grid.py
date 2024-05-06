import numpy as np


def grid_lines(size=50, unit=1):
    n = size * 2
    x = np.tile(np.arange(n + 1), (n + 1, 1))
    x = (x - n / 2) * unit
    y = np.tile(np.zeros(n + 1), (n + 1, 1))
    z = x.T
    p = np.dstack((x, y, z))

    v_i = np.tile(np.arange(n), (n, 1))
    u_i = v_i.T
    u_i = u_i.flatten()
    v_i = v_i.flatten()

    # 1 - 3
    # |   |
    # 2 - 4
    p1 = p[u_i + 0, v_i + 0]
    p2 = p[u_i + 1, v_i + 0]
    p3 = p[u_i + 0, v_i + 1]
    p4 = p[u_i + 1, v_i + 1]
    lines = np.stack((p1, p2, p2, p4, p4, p3, p3, p1), axis=1).flatten().tolist()
    return lines


if __name__ == "__main__":
    print(grid_lines(2))
