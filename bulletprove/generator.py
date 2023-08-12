#
#
#

import matplotlib.pyplot as plt
import numpy as np
import os


class Generator:

    def __init__(self, n_points=10):
        np.random.seed(3)
        self.n_points = n_points
        pass

    def randomize(self):
        np.random.seed(123)  # TODO: do it properly

    def generate(self, filename: str):
        """generate a single image"""
        # print(plt.style.available)

        plt.style.use("classic")

        # make the data
        x = 4 + np.random.normal(0, 2, self.n_points)
        y = 4 + np.random.normal(0, 2, len(x))
        # size and color:
        sizes = np.random.uniform(50, 50, len(x))
        # print(type(sizes))
        # colors = [ 'black' ] * len(x)
        colors = np.random.uniform(255, 255, len(x))

        # plot
        fig, ax = plt.subplots()

        ax.scatter(x, y, s=sizes, c=colors, vmin=0, vmax=100)
        ax.axis("off")

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        fig.savefig(filename)
        plt.close(fig)
