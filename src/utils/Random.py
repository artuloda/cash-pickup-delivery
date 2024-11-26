import random
import numpy as np

class Random:

    def __init__(self, seed=None):
        self.seed = self.set_seed(seed)

    def set_seed(self, seed=None):
        """Set the seed for the random number generator.""" 
        if seed is None:
            random_seed = self.get_random_int(1, 1000000000)
        else:
            random_seed = seed
        random.seed(random_seed)
        np.random.seed(random_seed)
        return random_seed

    def get_random_int(self, start: int, end: int) -> int:
        """Return a random integer between start and end (inclusive)."""
        return random.randint(start, end)

    def get_random_float(self, start: float, end: float) -> float:
        """Return a random float between start and end."""
        return random.uniform(start, end)

    def get_random_choice(self, sequence):
        """Return a random element from the non-empty sequence."""
        return random.choice(sequence)

    def shuffle_list(self, sequence: list) -> list:
        """Shuffle the sequence in place and return it."""
        random.shuffle(sequence)
        return sequence

    def get_random_sample(self, population, k: int):
        """Return a k length list of unique elements chosen from the population sequence."""
        return random.sample(population, k)
    
    def get_random_gauss(self, mean: float, std: float) -> float:
        """Return a random float from a Gaussian distribution with the given mean and standard deviation."""
        return random.gauss(mean, std)

if __name__ == '__main__':
    random_instance = Random(seed=42)
    # random_instance = Random()
    print(random_instance.get_random_int(1, 10))
    print(random_instance.get_random_float(1.0, 10.0))
    print(random_instance.get_random_choice([1, 2, 3, 4, 5]))
    print(random_instance.shuffle_list([1, 2, 3, 4, 5]))
    print(random_instance.get_random_sample([1, 2, 3, 4, 5], 3))
