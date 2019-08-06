"""
n-gram hashing by simple dot products

The principle is as follows:
  1. A string is viewed as a succession of numbers (the ASCII or UTF8
     representation of its elements.
  2. Each n-gram is then an n-dimensional vector of integers "g". A simple
     hash function is then computed by taking the dot product with a
     given random vector "atom", modulo max-int (integers larger than
     max-int overflow). The corresponding operation defines a random
     order in the interval [-maxint, maxint]
  3. Computing this dot product over a sliding window (to compute it for
     every n-gram is a convolution
  4. We can then take the min (or the max) of the resulting sliding
  window

"""
import functools
import numpy as np

@functools.lru_cache(maxsize=1024)
def gen_atom(atom_len, dtype_size=32, seed=0):
    """ Generate a random integer atom

    Parameters
    ----------
    atom_len: int
        The length of the atom
    dtype_size: int, default=32
        The size of the integer used
    seed: int, default=0
        The seed of the random_number generator

    Returns
    -------
    atom: 1D array of integers
        An array of random integers of length atom_len and dtype int32 if
        dtype_size=32
    """
    rng = np.random.RandomState(seed)
    maxint = 2 ** (dtype_size - 1) - 1
    atom = rng.randint(-maxint, maxint, size=atom_len,
                       dtype=np.dtype('int%i' % dtype_size))
    return atom

# @profile
def ngram_min_hash(string, ngram_range=(2, 4), seed=0, return_minmax=False):
    """ Compute the min hash of the ngrams of the string

    Parameters
    ----------
    string: str
        String to min-hash
    ngram_range: list
        List of ngram sizes to compute hashes for
    seed: integer
        Integer used to seed the hashing function
    Return
    -------
    min_hash: integer
    """
    # Create a numerical 1D array from the string
    array = np.frombuffer(string.encode(), dtype='int8', count=len(string))
    dtype_size = 32

    max_hash = -np.inf
    min_hash = np.inf
    for atom_len in range(ngram_range[0], ngram_range[1]):
        atom = gen_atom(atom_len, dtype_size=dtype_size, seed=seed)
        # np.correlate is faster than np.convolve
        hashes = np.correlate(array, atom)
        new_min = hashes.min()
        min_hash = min(min_hash, new_min)
        if return_minmax:
            max_hash = max(max_hash, hashes.max())

    # We should check that longer windows do not have different
    # statistics from shorter ones
    if return_minmax:
        return min_hash, max_hash
    return min_hash


if __name__ == '__main__':
    # Download demo text
    from sklearn import datasets
    data = datasets.fetch_20newsgroups()
    a = data.data[0]

    h = ngram_min_hash(a)