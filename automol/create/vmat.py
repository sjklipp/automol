""" vmatrix constructor
"""

import numpy
from phydat import ptab


def from_data(symbols, key_matrix, name_matrix=None, one_indexed=False):
    """ V-Matrix constructor (Z-Matrix without numerical coordinate values).

        :param symbols: atomic symbols
        :type symbols: tuple[str]
        :param key_matrix: key/index columns of the z-matrix, zero-indexed
        :type key_matrix: tuple[tuple[float, float or None, float or None]]
        :param name_matrix: coordinate name columns of the z-matrix
        :type name_matrix; tuple[tuple[str, str or None, str or None]]
        :param one_indexed: parameter to write keys in one-indexing
        :type one_indexed: bool
        :rtype: automol V-Matrix data structure
    """

    symbs = list(map(ptab.to_symbol, symbols))
    natms = len(symbs)

    key_mat = _key_matrix(key_matrix, natms, one_indexed)
    name_mat = _name_matrix(name_matrix, natms)

    vma = tuple(zip(symbs, key_mat, name_mat))

    return vma


def _key_matrix(key_mat, natms, one_indexed):
    """ Build name matrix of the V-Matrix that contains the
        coordinate keys by row and column.

        :param key_mat: key matrix of V-Matrix coordinate keys
        :type key_mat: tuple(tuple(int))
        :param natms: number of atoms
        :type natms: int
        :param one_indexed: parameter to write keys in one-indexing
        :type one_indexed: bool
        :rtype: tuple(tuple(str))
    """

    # Check dimensions and ensure proper formatting
    key_mat = [list(row) + [None]*(3-len(row)) for row in key_mat]
    key_mat = numpy.array(key_mat, dtype=numpy.object_)

    assert key_mat.ndim == 2 and key_mat.shape == (natms, 3)
    triu_idxs = numpy.triu_indices(natms, m=3)

    key_mat[1:, 0] -= 1 if one_indexed else 0
    key_mat[2:, 1] -= 1 if one_indexed else 0
    key_mat[3:, 2] -= 1 if one_indexed else 0

    key_mat[triu_idxs] = None

    return tuple(map(tuple, key_mat))


def _name_matrix(name_mat, natms):
    """ Build name matrix of the V-Matrix that contains the
        coordinate names by row and column.

        :param name_mat: key matrix of V-Matrix coordinate keys
        :type name_mat: tuple(tuple(int))
        :param natms: number of atoms
        :type natms: int
        :rtype: tuple(tuple(str))
    """

    if name_mat is None:
        name_mat = numpy.empty((natms, 3), dtype=numpy.object_)
        for row in range(0, natms):
            if row > 0:
                name_mat[row, 0] = 'R{:d}'.format(row)
            if row > 1:
                name_mat[row, 1] = 'A{:d}'.format(row)
            if row > 2:
                name_mat[row, 2] = 'D{:d}'.format(row)

    # Check dimensions and make sure there are Nones in the right places
    name_mat = [list(row) + [None]*(3-len(row)) for row in name_mat]
    name_mat = numpy.array(name_mat, dtype=numpy.object_)

    assert name_mat.ndim == 2 and name_mat.shape == (natms, 3)
    natms = name_mat.shape[0]
    triu_idxs = numpy.triu_indices(natms, m=3)
    tril_idxs = numpy.tril_indices(natms, -1, m=3)

    assert all(isinstance(name, str) for name in name_mat[tril_idxs])
    name_mat[triu_idxs] = None

    return tuple(map(tuple, name_mat))
