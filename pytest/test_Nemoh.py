#!/usr/bin/env python
# coding: utf-8
"""
Compare results of Capytaine with results from Nemoh 2.0.
"""

import numpy as np

from capytaine.reference_bodies import *
from capytaine.symmetries import *
from capytaine.problems import DiffractionProblem, RadiationProblem
from capytaine.results import assemble_radiation_results_matrices
from capytaine.Nemoh import Nemoh


def test_immersed_sphere():
    sphere = generate_sphere(radius=1.0, ntheta=20, nphi=40)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)
    problem = RadiationProblem(body=sphere, free_surface=np.infty, sea_bottom=-np.infty)
    result = Nemoh().solve(problem)
    assert np.isclose(result.added_masses["Heave"],       2187, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"],  0.0, atol=1e-3*sphere.volume*problem.rho)


def test_floating_sphere_finite_freq():
    sphere = generate_sphere(radius=1.0, ntheta=6, nphi=12, clip_free_surface=True)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)

    solver = Nemoh()
    problem = RadiationProblem(body=sphere, omega=1.0, sea_bottom=-np.infty)
    result = solver.solve(problem, keep_details=True)
    assert np.isclose(result.added_masses["Heave"],       1819.6, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"], 379.39, atol=1e-3*sphere.volume*problem.rho)

    free_surface = generate_free_surface(width=125, length=125, nw=5, nl=5)
    eta = solver.get_free_surface_elevation(result, free_surface)
    ref = np.array(
            [[-0.4340802E-02-0.4742809E-03j, -0.7986111E-03+0.4840984E-02j, 0.2214827E-02+0.4700642E-02j, -0.7986111E-03+0.4840984E-02j, -0.4340803E-02-0.4742807E-03j],
             [-0.7986111E-03+0.4840984E-02j, 0.5733187E-02-0.2179381E-02j, 0.9460892E-03-0.7079404E-02j, 0.5733186E-02-0.2179381E-02j, -0.7986110E-03+0.4840984E-02j],
             [0.2214827E-02+0.4700643E-02j, 0.9460892E-03-0.7079403E-02j, -0.1381670E-01+0.6039315E-01j, 0.9460892E-03-0.7079405E-02j, 0.2214827E-02+0.4700643E-02j],
             [-0.7986111E-03+0.4840984E-02j, 0.5733186E-02-0.2179381E-02j, 0.9460891E-03-0.7079404E-02j, 0.5733187E-02-0.2179380E-02j, -0.7986113E-03+0.4840984E-02j],
             [-0.4340803E-02-0.4742807E-03j, -0.7986111E-03+0.4840984E-02j, 0.2214827E-02+0.4700643E-02j, -0.7986113E-03+0.4840983E-02j, -0.4340803E-02-0.4742809E-03j]]
        )
    assert np.allclose(eta.reshape((5, 5)), ref, rtol=1e-4)

    problem = DiffractionProblem(body=sphere, omega=1.0, sea_bottom=-np.infty)
    result = solver.solve(problem)
    assert np.isclose(result.forces["Heave"], 1834.9 * np.exp(-2.933j), rtol=1e-3)


def test_alien_sphere():
    sphere = generate_sphere(radius=1.0, ntheta=6, nphi=12, clip_free_surface=True)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)

    problem = RadiationProblem(body=sphere, rho=450.0, g=1.625, omega=1.0, sea_bottom=-np.infty)
    result = Nemoh().solve(problem)
    assert np.isclose(result.added_masses["Heave"],       515, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"], 309, atol=1e-3*sphere.volume*problem.rho)

    problem = DiffractionProblem(body=sphere, rho=450.0, g=1.625, omega=1.0, sea_bottom=-np.infty)
    result = Nemoh().solve(problem)
    assert np.isclose(result.forces["Heave"], 548.5 * np.exp(-2.521j), rtol=1e-2)


def test_floating_sphere_finite_depth():
    sphere = generate_sphere(radius=1.0, ntheta=6, nphi=12, clip_free_surface=True)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)

    problem = RadiationProblem(body=sphere, omega=1.0, sea_bottom=-10.0)
    result = Nemoh().solve(problem)
    assert np.isclose(result.added_masses["Heave"],       1740.6, atol=1e-3*sphere.volume*problem.rho)
    assert np.isclose(result.radiation_dampings["Heave"], 380.46, rtol=1e-3*sphere.volume*problem.rho)

    problem = DiffractionProblem(body=sphere, omega=1.0, sea_bottom=-10.0)
    result = Nemoh().solve(problem)
    assert np.isclose(result.forces["Heave"], 1749.4 * np.exp(-2.922j), rtol=1e-3)


def test_multibody():
    sphere = generate_sphere(radius=1.0, ntheta=10, nphi=20)
    sphere.translate_z(-2.0)
    sphere.dofs["Surge"] = sphere.faces_normals @ (1, 0, 0)
    sphere.dofs["Heave"] = sphere.faces_normals @ (0, 0, 1)

    cylinder = generate_horizontal_cylinder(length=5.0, radius=1.0, nx=10, nr=1, ntheta=10)
    cylinder.translate([-1.0, 3.0, -3.0])
    cylinder.dofs["Surge"] = cylinder.faces_normals @ (1, 0, 0)
    cylinder.dofs["Heave"] = cylinder.faces_normals @ (0, 0, 1)

    both = cylinder + sphere
    # both.show()

    problems = [RadiationProblem(body=both, radiating_dof=dof, omega=1.0, free_surface=0.0, sea_bottom=-np.infty)
                for dof in both.dofs]
    solver = Nemoh()
    results = [solver.solve(problem) for problem in problems]
    mass, damping = assemble_radiation_results_matrices(results)

    Nemoh_2 = np.array([
        [3961.86548, 50.0367661, -3.32347107, 6.36901855E-02, 172.704819, 19.2018471, -5.67303181, -2.98873377],
        [-3.08301544, 5.72392941E-02, 14522.1689, 271.796814, 128.413834, 6.03351116, 427.167358, 64.1587067],
        [161.125534, 17.8332844, 126.392113, 5.88006783, 2242.47412, 7.17850924, 1.29002571, 0.393169671],
        [-5.02560759, -2.75930357, 419.927460, 63.3179016, 1.23501396, 0.416424811, 2341.57593, 15.8266096],
    ])

    assert np.allclose(mass[0, :, :].values,    Nemoh_2[:, ::2],  atol=1e-3*both.volume*problems[0].rho)
    assert np.allclose(damping[0, :, :].values, Nemoh_2[:, 1::2], atol=1e-3*both.volume*problems[0].rho)
