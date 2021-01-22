""" geometry conversions
"""

import itertools
import numpy
from automol import create
from automol.convert import _pyx2z
from automol.convert import _util
import automol.graph
import automol.geom
import automol.zmat
import automol.convert.graph
import automol.convert.inchi


# geometry => z-matrix
def zmatrix(geo, ts_bnds=()):
    """ Generate a corresponding Z-Matrix for a molecular geometry
        using internal autochem procedures.

        :param geo: molecular geometry
        :type geo: automol geometry data structure
        :param ts_bnds: keys for the breaking/forming bonds in a TS
        :type ts_bnds: tuple(frozenset(int))
    """

    if ts_bnds:
        raise NotImplementedError

    geo, dummy_key_dct = automol.geom.insert_dummies_on_linear_atoms(geo)
    gra = connectivity_graph(geo, dummy=True)
    vma, zma_keys = automol.graph.vmat.vmatrix(gra)
    geo = automol.geom.from_subset(geo, zma_keys)
    zma = automol.zmat.from_geometry(vma, geo)
    return zma, zma_keys, dummy_key_dct


def zmatrix_x2z(geo, ts_bnds=()):
    """ Generate a corresponding Z-Matrix for a molecular geometry
        using x2z interface.

        :param geo: molecular geometry
        :type geo: automol geometry data structure
        :param ts_bnds: keys for the breaking/forming bonds in a TS
        :type ts_bnds: tuple(frozenset(int))
    """

    symbs = automol.geom.symbols(geo)
    if len(symbs) == 1:
        key_mat = [[None, None, None]]
        val_mat = [[None, None, None]]
        zma = create.zmat.from_data(symbs, key_mat, val_mat)
    else:
        x2m = _pyx2z.from_geometry(geo, ts_bnds=ts_bnds)
        zma = _pyx2z.to_zmatrix(x2m)
    zma = automol.zmat.standard_form(zma)

    return zma


def zmatrix_torsion_coordinate_names(geo, ts_bnds=()):
    """ Generate a list of torsional coordinates using x2z interface. These
        names corresond to the Z-Matrix generated using the same algorithm.

        :param geo: molecular geometry
        :type geo: automol geometry data structure
        :param ts_bnds: keys for the breaking/forming bonds in a TS
        :type ts_bnds: tuple(frozenset(int))
        :rtype: tuple(str)
    """

    symbs = automol.geom.symbols(geo)
    if len(symbs) == 1:
        names = ()
    else:
        x2m = _pyx2z.from_geometry(geo, ts_bnds=ts_bnds)
        names = _pyx2z.zmatrix_torsion_coordinate_names(x2m)

        zma = _pyx2z.to_zmatrix(x2m)
        name_dct = automol.zmat.standard_names(zma)
        names = tuple(map(name_dct.__getitem__, names))

    return names


def zmatrix_atom_ordering(geo, ts_bnds=()):
    """ Generate a dictionary which maps the order of atoms from the input
        molecular geometry to the order of atoms of the resulting Z-Matrix
        that is generated by the x2z interface.

        :param geo: molecular geometry
        :type geo: automol geometry data structure
        :param ts_bnds: keys for the breaking/forming bonds in a TS
        :type ts_bnds: tuple(frozenset(int))
        :rtype: dict[int: int]
    """

    symbs = automol.geom.symbols(geo)
    if len(symbs) == 1:
        idxs = (0,)
    else:
        x2m = _pyx2z.from_geometry(geo, ts_bnds=ts_bnds)
        idxs = _pyx2z.zmatrix_atom_ordering(x2m)

    return idxs


def external_symmetry_factor(geo):
    """ Obtain the external symmetry factor for a geometry using x2z interface
        which determines the initial symmetry factor and then divides by the
        enantiomeric factor.

        :param geo: molecular geometry
        :type geo: automol geometry data structure
        :rtype: float
    """

    if automol.geom.is_atom(geo):
        ext_sym_fac = 1.
    else:
        oriented_geom = _pyx2z.to_oriented_geometry(geo)
        ext_sym_fac = oriented_geom.sym_num()
        if oriented_geom.is_enantiomer():
            ext_sym_fac *= 0.5

    return ext_sym_fac


# geometry => graph
def connectivity_graph(geo, dummy=True,
                       rqq_bond_max=3.45, rqh_bond_max=2.6, rhh_bond_max=1.9):
    """ Generate a molecular graph from the molecular geometry that has information
        about bond connectivity.

        :param rqq_bond_max: maximum distance between heavy atoms
        :type rqq_bond_max: float
        :param rqh_bond_max: maximum distance between heavy atoms and hydrogens
        :type rqh_bond_max: float
        :param rhh_bond_max: maximum distance between hydrogens
        :type rhh_bond_max: float
        :param dummy: parameter to incude bonds to dummy atoms
        :type dummy: bool
        :rtype: automol molecular graph structure
    """

    symbs = automol.geom.symbols(geo)
    xyzs = automol.geom.coordinates(geo)

    def _distance(idx_pair):
        xyz1, xyz2 = map(xyzs.__getitem__, idx_pair)
        dist = numpy.linalg.norm(numpy.subtract(xyz1, xyz2))
        return dist

    def _are_bonded(idx_pair):
        sym1, sym2 = map(symbs.__getitem__, idx_pair)
        dist = _distance(idx_pair)
        return (False if 'X' in (sym1, sym2) else
                (dist < rqh_bond_max) if 'H' in (sym1, sym2) else
                (dist < rhh_bond_max) if (sym1 == 'H' and sym2 == 'H') else
                (dist < rqq_bond_max))

    idxs = range(len(xyzs))
    atm_symb_dct = dict(enumerate(symbs))
    bnd_keys = tuple(
        map(frozenset, filter(_are_bonded, itertools.combinations(idxs, r=2))))

    bnd_ord_dct = {bnd_key: 1 for bnd_key in bnd_keys}

    if dummy:
        dummy_idxs = automol.geom.dummy_atom_indices(geo)
        for idx1 in dummy_idxs:
            idx2, dist = min(
                [[i, _distance([idx1, i])] for i in idxs if i != idx1],
                key=lambda x: x[1])
            if dist < rhh_bond_max:
                bnd_key = frozenset({idx1, idx2})
                bnd_keys += (bnd_key,)
                bnd_ord_dct[bnd_key] = 0

    gra = create.graph.from_data(atom_symbols=atm_symb_dct, bond_keys=bnd_keys,
                                 bond_orders=bnd_ord_dct)
    return gra


def graph(geo, stereo=True):
    """ Generate a molecular graph from the molecular geometry that has information
        about bond connectivity and if requested, stereochemistry.

        :param geo: molecular geometry
        :type geo: automol geometry data structure
        :param stereo: parameter to include stereochemistry information
        :type stereo: bool
        :rtype: automol molecular graph data structure
    """

    gra = connectivity_graph(geo)
    if stereo:
        gra = automol.graph.set_stereo_from_geometry(gra, geo)

    return gra


# geometry => inchi
def inchi(geo, stereo=True):
    """ Generate an InChI string from a molecular geometry.

        :param geo: molecular geometry
        :type geo: automol geometry data structure
        :param stereo: parameter to include stereochemistry information
        :type stereo: bool
        :rtype: str
    """

    ich, _ = inchi_with_sort(geo, stereo=stereo)

    return ich


def inchi_with_sort(geo, stereo=True):
    """ Generate an InChI string from a molecular geometry. (Sort?)

        :param geo: molecular geometry
        :type geo: automol geometry data structure
        :param stereo: parameter to include stereochemistry information
        :type stereo: bool
        :rtype: str
    """

    ich = automol.convert.inchi.object_to_hardcoded_inchi_by_key(
        'geom', geo, comp=_compare)
    nums = None

    if ich is None:
        gra = connectivity_graph(geo)
        if not stereo:
            geo = None
            geo_idx_dct = None
        else:
            geo_idx_dct = dict(enumerate(range(automol.geom.count(geo))))
        ich, nums = automol.convert.graph.inchi_with_sort_from_geometry(
            gra=gra, geo=geo, geo_idx_dct=geo_idx_dct)

    return ich, nums


def _compare(geo1, geo2):
    """ Check if the backbone atoms of two molecular geometries are similar.

        :param geo1: molecular geometry 1
        :type geo1: automol geometry data structure
        :param geo2: molecular geometry 2
        :type geo2: automol geometry data structure
        :rtype: bool
    """

    gra1 = automol.graph.without_dummy_atoms(connectivity_graph(geo1))
    gra2 = automol.graph.without_dummy_atoms(connectivity_graph(geo2))

    return automol.graph.backbone_isomorphic(gra1, gra2)


# geometry => formula
def formula(geo):
    """ Generate a stoichiometric formula dictionary from a molecular geometry.

        :param geo: molecular geometry
        :type geo: automol geometry data structure
        :type: dict[str: int]
    """

    symbs = automol.geom.symbols(geo)
    fml = _util.formula(symbs)

    return fml
