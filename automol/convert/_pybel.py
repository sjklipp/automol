""" pybel interface
"""

import pybel
from phydat import ptab
from automol import create


# geometry
def to_geometry(pbm):
    """ Build an automol geometry data structure from a Pybel molecule object.

        :param pbm: Pybel molecule object
        :type pbm: Pybel object
        :rtype: automol geometry data structure
    """

    pbm.addh()
    pbm.make3D()
    nums = [atm.atomicnum for atm in pbm.atoms]
    symbs = list(map(ptab.to_symbol, nums))
    xyzs = tuple(tuple(atm.coords) for atm in pbm.atoms)
    geo = create.geom.from_data(symbs, xyzs, angstrom=True)

    return geo


# inchi
def from_inchi(ich):
    """ Build a Pybel molecule object from an InChI string.

        :param ich: InChI string for a species
        :type ich: str
        :rtype: Pybel molecule object
    """
    return pybel.readstring('inchi', ich)


def to_inchi(pbm):
    """ Build an InChI string from a Pybel molecule object.

        :param pbm: Pybel molecule object
        :type pbm: Pybel object
        :rtype: str
    """
    return pbm.write('inchi').strip()
