#!/usr/bin/env python
# coding: utf-8

from capytaine.bodies_collection import CollectionOfFloatingBodies
from capytaine.geometric_bodies import *
from capytaine.symmetries import ReflectionSymmetry


def test_dof():
    nodes = np.array([[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]])
    faces = np.array([[0, 1, 2, 3]])
    body = FloatingBody(Mesh(nodes, faces), name="one_face")
    assert body.dofs == {}

    body.add_translation_dof(direction=(1.0, 0.0, 0.0), name="1")
    assert body.dofs["1"] == np.array([0.0])

    body.add_translation_dof(direction=(0.0, 1.0, 0.0), name="2")
    assert body.dofs["2"] == np.array([1.0])

    body.add_rotation_dof(axis_direction=(0.0, 0.0, 1.0), name="3")
    assert body.dofs["3"] == np.array([1.0])

    body.add_rotation_dof(axis_point=(0.5, 0, 0), axis_direction=(0.0, 0.0, 1.0), name="4")
    assert body.dofs["4"] == np.array([0.0])


def test_collection():
    body_1 = generate_sphere()
    body_1.name = 'body_1'
    body_1.dofs['Dummy'] = body_1.mesh.faces_normals @ (0, 0, 0)
    body_1.dofs['Heave'] = body_1.mesh.faces_normals @ (0, 0, 1)
    assert isinstance(body_1, FloatingBody)
    assert isinstance(body_1.as_FloatingBody(), FloatingBody)

    body_2 = generate_sphere(z0=-5.0)
    body_2.name = 'body_2'
    body_2.dofs['Surge'] = body_2.mesh.faces_normals @ (1, 0, 0)
    coll = body_1 + body_2
    assert isinstance(coll, CollectionOfFloatingBodies)
    assert isinstance(coll.as_FloatingBody(), FloatingBody)
    assert coll.name == 'CollectionOfFloatingBodies([body_1, body_2])'

    assert np.all(coll.mesh.faces_areas[coll.indices_of_body(0)] == body_1.mesh.faces_areas)
    assert np.all(coll.mesh.faces_areas[coll.indices_of_body(1)] == body_2.mesh.faces_areas)

    # Test dofs
    assert len(coll.dofs) == 3
    for name, dof in coll.dofs.items():
        assert name in ['body_1_Dummy', 'body_1_Heave', 'body_2_Surge']
        assert dof.shape[0] == coll.mesh.faces_normals.shape[0]
        assert np.all(dof[:dof.shape[0]//2] == np.zeros(coll.mesh.faces_normals.shape[0]//2)) \
                or np.all(dof[dof.shape[0]//2:] == np.zeros(coll.mesh.faces_normals.shape[0]//2))

    body_3 = generate_sphere(z0=-10.0)
    body_3.name = 'body_3'
    coll = body_1 + body_2 + body_3
    assert isinstance(coll, CollectionOfFloatingBodies)
    assert coll.name == 'CollectionOfFloatingBodies([body_1, body_2, body_3])'
    assert body_1 in coll.subbodies
    assert body_2 in coll.subbodies
    assert body_3 in coll.subbodies

    assert coll.mesh.nb_vertices == coll.as_FloatingBody().mesh.nb_vertices == generate_sphere().mesh.nb_vertices*3
    assert coll.mesh.nb_faces == coll.as_FloatingBody().mesh.nb_faces == generate_sphere().mesh.nb_faces*3

    # Test the merging of identical vertices
    assert (generate_sphere() + generate_sphere()).as_FloatingBody().mesh.nb_vertices == generate_sphere().mesh.nb_vertices


def test_symmetric_bodies():
    half_sphere = generate_half_sphere(nphi=5)
    half_sphere.name = 'half_sphere'
    full_sphere = ReflectionSymmetry(half_sphere, xOz_Plane)
    assert isinstance(full_sphere, CollectionOfFloatingBodies)
    assert half_sphere in full_sphere.subbodies
    assert full_sphere.as_FloatingBody().mesh.nb_vertices == generate_sphere(nphi=10).mesh.nb_vertices

    other_sphere = generate_sphere(z0=-5.0)
    coll = full_sphere + other_sphere
    assert full_sphere in coll.subbodies


def test_reference_bodies():
    sphere = generate_sphere(ntheta=10, nphi=10)
    # sphere.show()
    sphere = generate_sphere(ntheta=10, nphi=10, clip_free_surface=True)
    # sphere.show()
    half_sphere = generate_half_sphere(ntheta=10, nphi=10)
    # half_sphere.show()
    cylinder = generate_horizontal_cylinder()
    cylinder.add_rotation_dof(axis_point=(5, 0, 0))
    # cylinder.show_matplotlib(normal_vectors=True, scale_normal_vector=cylinder.dofs["Rotation_dof_0"])
    clever_cylinder = generate_clever_horizontal_cylinder()
    # clever_cylinder.show()
    rectangle = generate_one_sided_rectangle()
    # rectangle.show()
    clever_rectangle = generate_clever_one_sided_rectangle()
    # clever_rectangle.show()
    parallelepiped = generate_open_rectangular_parallelepiped()
    # parallelepiped.show()
    parallelepiped = generate_clever_open_rectangular_parallelepiped()
    # parallelepiped.show()
    parallelepiped = generate_rectangular_parallelepiped()
    # parallelepiped.show()
    parallelepiped = generate_horizontal_open_rectangular_parallelepiped()
    # parallelepiped.show()
    parallelepiped = generate_clever_horizontal_open_rectangular_parallelepiped()
    # parallelepiped.show()
