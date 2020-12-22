""" unimolecular TS example
"""
import numpy
import automol

# (CH3)2[CH]CH2CH2O[O] => (CH3)2[C]CH2CH2O[OH]
RCT_ICHS = list(map(automol.smiles.inchi, ['C(C)(C)CCO[O]']))
PRD_ICHS = list(map(automol.smiles.inchi, ['[C](C)(C)CCOO']))

RCT_GEOS = list(map(automol.inchi.geometry, RCT_ICHS))
PRD_GEOS = list(map(automol.inchi.geometry, PRD_ICHS))

RCT_GRAS = list(map(automol.graph.without_stereo_parities,
                    map(automol.geom.graph, RCT_GEOS)))
PRD_GRAS = list(map(automol.graph.without_stereo_parities,
                    map(automol.geom.graph, PRD_GEOS)))

RCT_GRAS, RCT_KEYS_DCT = automol.graph.standard_keys_for_sequence(RCT_GRAS)
PRD_GRAS, PRD_KEYS_DCT = automol.graph.standard_keys_for_sequence(PRD_GRAS)

TRAS, _, _ = automol.graph.reac.hydrogen_migration(RCT_GRAS, PRD_GRAS)
TRA = TRAS[0]
FRM_BND_KEYS = list(automol.graph.trans.formed_bond_keys(TRA))
BRK_BND_KEYS = list(automol.graph.trans.broken_bond_keys(TRA))

GRA = automol.graph.union_from_sequence(RCT_GRAS)
KEYS = sorted(automol.graph.atom_keys(GRA))
FRM_BNDS_DCT = {bnd: (1.6, 1.6) for bnd in FRM_BND_KEYS}
print(FRM_BNDS_DCT)
print(RCT_GEOS)
LMAT, UMAT = automol.graph.embed.ts_distance_bounds_matrices(
        GRA, KEYS, FRM_BNDS_DCT, rct_geos=RCT_GEOS, relax_torsions=True)

print(numpy.round(LMAT, 2))
print(numpy.round(UMAT, 2))

SYMS = list(map(automol.graph.atom_symbols(GRA).__getitem__, KEYS))
XMAT = automol.embed.sample_raw_distance_coordinates(LMAT, UMAT, dim4=True)
XMAT, CONV = automol.embed.cleaned_up_coordinates(XMAT, LMAT, UMAT)
print(CONV)
GEO = automol.embed.geometry_from_coordinates(XMAT, SYMS)
print(automol.geom.string(GEO))

GRA2 = automol.geom.connectivity_graph(GEO)
print(GRA == GRA2)

# ZMA = automol.geom.zmatrix(GEO)
# print(automol.zmatrix.string(ZMA))
# GEO2 = automol.zmatrix.geometry(ZMA)
# print(automol.geom.string(GEO2))
