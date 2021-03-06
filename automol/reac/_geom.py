""" TS geometries for specific reaction classes
"""
import itertools
import more_itertools as mit
import automol.convert.graph
import automol.geom.ts
from automol import par
from automol.graph import ts
from automol.graph import atom_keys
from automol.reac._util import ring_forming_scission_chain
from automol.reac._util import hydrogen_abstraction_is_sigma


# Unimolecular reactions
def hydrogen_migration_ts_geometry(rxn, rct_geos,
                                   max_dist_err=2e-1, log=False):
    """ geometry for a hydrogen migration transition state

    :param rxn: a Reaction object
    :param rct_geos: the reactant geometries
    """
    assert rxn.class_ == par.ReactionClass.HYDROGEN_MIGRATION
    assert rxn.has_standard_keys()
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    frm_bnd_dist = 1.7

    dist_dct = automol.geom.ts.distances(rct_geos, angstrom=True)
    dist_dct[frm_bnd_key] = frm_bnd_dist

    gra = ts.reactants_graph(rxn.forward_ts_graph)
    dist_range_dct = automol.graph.embed.distance_ranges_from_coordinates(
        gra, dist_dct, angstrom=True)

    geo_init, = rct_geos
    relax_ang = True
    relax_tors = True

    geo = _geometry_from_info(
        gra, rct_geos, geo_init, dist_range_dct,
        relax_ang=relax_ang, relax_tors=relax_tors,
        max_dist_err=max_dist_err, log=log)
    return geo


def beta_scission_ts_geometry(rxn, rct_geos,
                              max_dist_err=2e-1, log=False):
    """ geometry for a beta scission transition state

    :param rxn: a Reaction object
    :param rct_geos: the reactant geometries
    """
    assert rxn.class_ == par.ReactionClass.BETA_SCISSION
    assert rxn.has_standard_keys()
    brk_bnd_key, = ts.breaking_bond_keys(rxn.forward_ts_graph)
    brk_bnd_dist = 1.5

    dist_dct = automol.geom.ts.distances(rct_geos, angstrom=True)
    dist_dct[brk_bnd_key] = brk_bnd_dist

    gra = ts.reactants_graph(rxn.forward_ts_graph)
    dist_range_dct = automol.graph.embed.distance_ranges_from_coordinates(
        gra, dist_dct, angstrom=True)

    geo_init, = rct_geos
    relax_ang = False
    relax_tors = False

    geo = _geometry_from_info(
        gra, rct_geos, geo_init, dist_range_dct,
        relax_ang=relax_ang, relax_tors=relax_tors,
        max_dist_err=max_dist_err, log=log)
    return geo


def ring_forming_scission_ts_geometry(rxn, rct_geos,
                                      max_dist_err=2e-1, log=False):
    """ geometry for a ring-forming scission transition state

    :param rxn: a Reaction object
    :param rct_geos: the reactant geometries
    """
    assert rxn.class_ == par.ReactionClass.RING_FORM_SCISSION
    assert rxn.has_standard_keys()
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    brk_bnd_key, = ts.breaking_bond_keys(rxn.forward_ts_graph)
    frm_bnd_dist = 2.0
    brk_bnd_dist = 1.5
    d1234 = 180.

    dist_dct = automol.geom.ts.distances(rct_geos, angstrom=True)
    dist_dct[frm_bnd_key] = frm_bnd_dist
    dist_dct[brk_bnd_key] = brk_bnd_dist

    # Note that this will not set the angle to exactly 180, because we don't
    # yet know the 1-3 and 2-4 distances.
    chain_keys = ring_forming_scission_chain(rxn)
    key1, key2, key3, key4 = chain_keys[:4]
    dih_dct = {(key1, key2, key3, key4): (d1234, None)}

    gra = ts.reactants_graph(rxn.forward_ts_graph)
    dist_range_dct = automol.graph.embed.distance_ranges_from_coordinates(
        gra, dist_dct, dih_dct=dih_dct, degree=True, angstrom=True)

    geo_init, = rct_geos
    relax_ang = True
    relax_tors = True

    geo = _geometry_from_info(
        gra, rct_geos, geo_init, dist_range_dct,
        relax_ang=relax_ang, relax_tors=relax_tors,
        max_dist_err=max_dist_err, log=log)

    # Rerun the optimization, enforcing planarity on the ring
    dist_dct = automol.geom.ts.distances([geo], angstrom=True)
    dist_dct[frm_bnd_key] = frm_bnd_dist
    dist_dct[brk_bnd_key] = brk_bnd_dist
    pla_dct = {}
    for key1, key2, key3, key4 in mit.windowed(chain_keys, 4):
        pla_dct[(key1, key2, key3, key4)] = (0.0, 0.0)

    gra = ts.reactants_graph(rxn.forward_ts_graph)
    dist_range_dct = automol.graph.embed.distance_ranges_from_coordinates(
        gra, dist_dct, degree=True, angstrom=True)

    geo = _geometry_from_info(
        gra, [geo], geo, dist_range_dct,
        relax_ang=relax_ang, relax_tors=relax_tors,
        pla_dct=pla_dct,
        max_dist_err=max_dist_err, log=log)

    return geo


def elimination_ts_geometry(rxn, rct_geos,
                            max_dist_err=2e-1, log=False):
    """ geometry for an elimination transition state

    :param rxn: a Reaction object
    :param rct_geos: the reactant geometries
    """
    assert rxn.class_ == par.ReactionClass.ELIMINATION
    assert rxn.has_standard_keys()
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    frm_bnd_dist = 1.6
    frm_rng_keys, = ts.forming_rings_atom_keys(rxn.forward_ts_graph)

    dist_dct = automol.geom.ts.distances(rct_geos, angstrom=True)
    dist_dct[frm_bnd_key] = frm_bnd_dist

    gra = ts.reactants_graph(rxn.forward_ts_graph)
    dist_range_dct = automol.graph.embed.distance_ranges_from_coordinates(
        gra, dist_dct, rings_keys=[frm_rng_keys], degree=True,
        angstrom=True)

    geo_init, = rct_geos
    relax_ang = True
    relax_tors = True

    geo = _geometry_from_info(
        gra, rct_geos, geo_init, dist_range_dct,
        relax_ang=relax_ang, relax_tors=relax_tors,
        max_dist_err=max_dist_err, log=log)
    return geo


# Bimolecular reactions
def hydrogen_abstraction_ts_geometry(rxn, rct_geos,
                                     max_dist_err=2e-1, log=False):
    """ geometry for a hydrogen abstraction transition state

    :param rxn: a Reaction object
    :param rct_geos: the reactant geometries
    """
    assert rxn.class_ == par.ReactionClass.HYDROGEN_ABSTRACTION
    assert rxn.has_standard_keys()
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    frm_bnd_dist = 1.6
    a123 = 170.
    if hydrogen_abstraction_is_sigma(rxn):
        a234 = 180.
    else:
        a234 = 85.

    dist_dct = automol.geom.ts.distances(rct_geos, angstrom=True)
    dist_dct[frm_bnd_key] = frm_bnd_dist

    # key2 the hydrogen atom and key3 is the attacking atom; this is guaranteed
    # to be true since the Reaction has been standardized
    key2, key3 = sorted(frm_bnd_key)
    ang_dct = {(None, key2, key3): a123, (key2, key3, None): a234}

    gra = ts.reactants_graph(rxn.forward_ts_graph)
    dist_range_dct = automol.graph.embed.distance_ranges_from_coordinates(
        gra, dist_dct, ang_dct=ang_dct, degree=True, angstrom=True)

    geo1, geo2 = rct_geos
    geo_init = automol.geom.ts.join(geo1, geo2, key2=key2, key3=key3,
                                    r23=frm_bnd_dist, a123=a123, a234=a234)
    relax_ang = False
    relax_tors = False

    geo = _geometry_from_info(
        gra, rct_geos, geo_init, dist_range_dct,
        relax_ang=relax_ang, relax_tors=relax_tors,
        max_dist_err=max_dist_err, log=log)
    return geo


def addition_ts_geometry(rxn, rct_geos,
                         max_dist_err=2e-1, log=False):
    """ geometry for an addition transition state

    :param rxn: a Reaction object
    :param rct_geos: the reactant geometries
    """
    assert rxn.class_ == par.ReactionClass.ADDITION
    assert rxn.has_standard_keys()
    frm_bnd_key, = ts.forming_bond_keys(rxn.forward_ts_graph)
    frm_bnd_dist = 1.9
    a123 = 85.
    a234 = 85.
    d1234 = 85.

    dist_dct = automol.geom.ts.distances(rct_geos, angstrom=True)
    dist_dct[frm_bnd_key] = frm_bnd_dist

    # key2 the hydrogen atom and key3 is the attacking atom; this is guaranteed
    # to be true since the Reaction has been standardized
    key2, key3 = sorted(frm_bnd_key)
    ang_dct = {(None, key2, key3): a123, (key2, key3, None): a234}
    dih_dct = {(None, key2, key3, None): d1234}

    gra = ts.reactants_graph(rxn.forward_ts_graph)
    dist_range_dct = automol.graph.embed.distance_ranges_from_coordinates(
        gra, dist_dct, ang_dct=ang_dct, dih_dct=dih_dct, degree=True,
        angstrom=True)

    geo1, geo2 = rct_geos
    geo_init = automol.geom.ts.join(geo1, geo2, key2=key2, key3=key3,
                                    r23=frm_bnd_dist, a123=a123, a234=a234,
                                    d1234=d1234)
    relax_ang = False
    relax_tors = False

    geo = _geometry_from_info(
        gra, rct_geos, geo_init, dist_range_dct,
        relax_ang=relax_ang, relax_tors=relax_tors,
        max_dist_err=max_dist_err, log=log)
    return geo


def insertion_ts_geometry(rxn, rct_geos,
                          max_dist_err=2e-1, log=False):
    """ geometry for an insertion transition state

    :param rxn: a Reaction object
    :param rct_geos: the reactant geometries
    """
    assert rxn.class_ == par.ReactionClass.INSERTION
    assert rxn.has_standard_keys()

    # set the formed bond distance based on the number of hydrogens
    frm_bnd_dist_dct = {
        0: 1.9,
        1: 1.6,
        2: 1.2,
    }

    tsg = rxn.forward_ts_graph

    frm_bnd_key1, frm_bnd_key2 = ts.forming_bond_keys(tsg)
    hcnt1 = automol.graph.atom_count_by_type(tsg, 'H', keys=frm_bnd_key1)
    hcnt2 = automol.graph.atom_count_by_type(tsg, 'H', keys=frm_bnd_key2)
    frm_bnd_dist1 = frm_bnd_dist_dct[hcnt1]
    frm_bnd_dist2 = frm_bnd_dist_dct[hcnt2]
    a123 = 170.
    frm_rng_keys, = ts.forming_rings_atom_keys(tsg)

    dist_dct = automol.geom.ts.distances(rct_geos, angstrom=True)
    dist_dct[frm_bnd_key1] = frm_bnd_dist1
    dist_dct[frm_bnd_key2] = frm_bnd_dist2

    gra = ts.reactants_graph(tsg)
    dist_range_dct = automol.graph.embed.distance_ranges_from_coordinates(
        gra, dist_dct, rings_keys=[frm_rng_keys], angstrom=True)

    # Join on the end without hydrogen, if there is one
    if hcnt1 <= hcnt2:
        key2, key3 = sorted(frm_bnd_key1)
    else:
        key2, key3 = sorted(frm_bnd_key2)

    geo1, geo2 = rct_geos
    geo_init = automol.geom.ts.join(geo1, geo2, key2=key2, key3=key3,
                                    r23=frm_bnd_dist1, a123=a123)
    relax_ang = True
    relax_tors = True

    geo = _geometry_from_info(
        gra, rct_geos, geo_init, dist_range_dct,
        relax_ang=relax_ang, relax_tors=relax_tors,
        max_dist_err=max_dist_err, log=log)
    return geo


def substitution_ts_geometry(rxn, rct_geos,
                             max_dist_err=2e-1, log=False):
    """ geometry for a substitution transition state

    :param rxn: a Reaction object
    :param rct_geos: the reactant geometries
    """
    assert rxn.class_ == par.ReactionClass.SUBSTITUTION
    assert rxn.has_standard_keys()

    # set the formed bond distance based on the number of hydrogens
    frm_bnd_dist_dct = {
        0: 1.9,
        1: 1.6,
        2: 1.2,
    }

    tsg = rxn.forward_ts_graph
    a123 = 170.
    a234 = 95.

    frm_bnd_key, = ts.forming_bond_keys(tsg)
    hcnt = automol.graph.atom_count_by_type(tsg, 'H', keys=frm_bnd_key)
    frm_bnd_dist = frm_bnd_dist_dct[hcnt]

    dist_dct = automol.geom.ts.distances(rct_geos, angstrom=True)
    dist_dct[frm_bnd_key] = frm_bnd_dist

    # key2 the hydrogen atom and key3 is the attacking atom; this is guaranteed
    # to be true since the Reaction has been standardized
    key2, key3 = sorted(frm_bnd_key)
    ang_dct = {(None, key2, key3): a123, (key2, key3, None): a234}

    gra = ts.reactants_graph(tsg)
    dist_range_dct = automol.graph.embed.distance_ranges_from_coordinates(
        gra, dist_dct, ang_dct=ang_dct, degree=True, angstrom=True)

    geo1, geo2 = rct_geos
    geo_init = automol.geom.ts.join(geo1, geo2, key2=key2, key3=key3,
                                    r23=frm_bnd_dist, a123=a123, a234=a234)
    relax_ang = True
    relax_tors = True

    geo = _geometry_from_info(
        gra, rct_geos, geo_init, dist_range_dct,
        relax_ang=relax_ang, relax_tors=relax_tors,
        max_dist_err=max_dist_err, log=log)
    return geo


def ts_geometry(rxn, rct_geos, max_dist_err=2e-1, log=False):
    """ reaction-class-specific embedding info

    :param rxn: a Reaction object
    :param rct_geos: the reactant geometries
    :returns: the TS geometry
    """
    function_dct = {
        # unimolecular
        par.ReactionClass.HYDROGEN_MIGRATION: hydrogen_migration_ts_geometry,
        par.ReactionClass.BETA_SCISSION: beta_scission_ts_geometry,
        par.ReactionClass.RING_FORM_SCISSION:
        ring_forming_scission_ts_geometry,
        par.ReactionClass.ELIMINATION: elimination_ts_geometry,
        # bimolecular
        par.ReactionClass.HYDROGEN_ABSTRACTION:
        hydrogen_abstraction_ts_geometry,
        par.ReactionClass.ADDITION: addition_ts_geometry,
        par.ReactionClass.INSERTION: insertion_ts_geometry,
        par.ReactionClass.SUBSTITUTION: substitution_ts_geometry,
    }

    fun_ = function_dct[rxn.class_]
    geo = fun_(rxn, rct_geos, max_dist_err=max_dist_err, log=log)
    return geo


# helpers
def _geometry_from_info(gra, rct_geos, geo_init, dist_range_dct,
                        relax_ang=False, relax_tors=False,
                        pla_dct=None,
                        max_dist_err=2e-1, log=False):
    keys = sorted(atom_keys(gra))
    xmat = automol.geom.coordinates(geo_init, angstrom=True)
    lmat, umat = automol.graph.embed.join_distance_bounds_matrices(
        gra, keys, dist_range_dct, geos=rct_geos, relax_angles=relax_ang,
        relax_torsions=relax_tors)

    pla_dct = {} if pla_dct is None else pla_dct
    chi_dct = automol.graph.embed.chirality_constraint_bounds(gra, keys)
    pla_dct.update(automol.graph.embed.planarity_constraint_bounds(gra, keys))

    xmat, conv = automol.embed.cleaned_up_coordinates(
        xmat, lmat, umat, chi_dct=chi_dct, pla_dct=pla_dct,
        max_dist_err=max_dist_err, log=log)

    if log:
        print("Converged!" if conv else "Did not converge.")

    syms = list(itertools.chain(*map(automol.geom.symbols, rct_geos)))
    geo = automol.embed.geometry_from_coordinates(xmat, syms)
    return geo
