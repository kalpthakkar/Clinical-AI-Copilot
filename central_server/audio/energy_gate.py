import numpy as np


class EnergyGate:

    def __init__(self, threshold=0.01):
        self.threshold = threshold

    def has_energy(self, audio):

        rms = np.sqrt(np.mean(audio ** 2))

        return rms > self.threshold