import numpy as np

list_test = np.array([[0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 2],
                      [1, 1, 1, 1, 1]])

list_back = np.array([[3, 3, 3, 3, 3],
                      [3, 3, 3, 3, 3],
                      [3, 3, 3, 3, 3],
                      [3, 3, 3, 3, 3],
                      [3, 3, 3, 3, 3]])

(i, j) = (1, 1)

print(list_test[-1:5, 2:5])
