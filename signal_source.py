import numpy as np

## simulation scope: 10ms


class signal_source:
    ## package rate = expected num of packages per second
    def __init__(self, lamb, ms_num):
        self.ms_num = ms_num
        self.lamb = np.array(lamb)  # 10ms

    def generate(self):
        n = np.random.poisson(lam=self.lamb, size=(1, self.ms_num))
        return n[0]


if __name__ == "__main__":
    SS = signal_source([200, 100, 50, 800, 1600], [8, 8, 8, 8, 8], 5)
    print(SS.generate())
