from soma import aims
import numpy as np
import copy
import sys

def vertices_and_faces_to_mesh(vertices, faces):
    '''
    Create an aims 3D mesh using precomputed vertices and faces. Vertices and faces are assumed to be compatible
    :param vertices: ndarray
    :param faces: ndarray
    :return: aims mesh
    '''
    # determine the mesh type based on polygon type (does not work for quads polygon !)
    poly_type = faces.shape[-1]
    mesh = aims.TimeSurface(dim=poly_type)
    v = mesh.vertex()
    p = mesh.polygon()

    v.assign([aims.Point3df(x) for x in vertices])

    p.assign([aims.AimsVector(x, dtype='U32', dim=poly_type) for x in faces])
    # recompute normals, not mandatory but to have coherent mesh
    # rem does not work for 2D meshes normals need to be added manually (works like a texture)
    mesh.updateNormals()
    return mesh


def mesh_2D_Merge(mesh_base, added_mesh, update_normals=True):
    '''
    Merge 2d-meshes (Aims.SurfaceManip.meshMerge only handle 3D-meshes)
    The mesh_base parameter will be overwritten by the fusion
    :param mesh_base: AimsTimeSurface_2D_VOID
    :param added_mesh: AimsTimeSurface_2D_VOID
    :return: a reference to mesh_base
    '''
    # Fixing sizes of the respective mesh
    # copies are mandatory due to prevent from update on the fly of objects
    s1 = copy.copy(mesh_base.vertex().size())
    s2 = copy.copy(added_mesh.vertex().size())
    p1 = copy.copy(mesh_base.polygon().size())
    p2 = copy.copy(added_mesh.polygon().size())
    # Vertices fusion
    # Allocating space for fusion
    mesh_base.vertex().resize(s1 + s2)
    mesh_base.vertex()[s1:] = added_mesh.vertex()[:]
    # Polygons fusion
    # Allocating space for fusion
    mesh_base.polygon().resize(p1 + p2)
    # Due to weird comportment of polygons need to be done with for loop
    for i, p in enumerate(added_mesh.polygon()):
        p = p + s1
        mesh_base.polygon()[p1 + i] = p

    # Not necessary but could be a good thing to have a coherent mesh.
    # Useless if a lot of fusions are performed in a row.

    if update_normals:
        mesh_base.updateNormals()

    pass


def build_2D_line(n):
    '''
    Build polygons (lines) of a set of n vertices assuming the mesh is a line without loop
    :param n: number of vertices (at least 2)
    :return: indices of mesh faces.
    '''
    faces = np.zeros((n - 1, 2), dtype=np.int16)
    faces[:, 0] = np.arange(n - 1)
    faces[:, 1] = np.arange(1, n)
    return faces


def vertices_to_2d_line(vertices):
    '''
    :param vertices: a Nx3 ndarray
    :return: mesh
    '''
    faces = build_2D_line(vertices.shape[0])
    mesh = vertices_and_faces_to_mesh(vertices, faces)
    return mesh


def bundle_to_mesh(bundle):
    '''
    :param streamline: streamlines coordinates
    :return: mesh
    '''
    for i, s in enumerate(bundle):
        faces = build_2D_line(len(s))
        streamline = vertices_and_faces_to_mesh(s, faces)
        if i == 0:
            mesh = streamline
        else:
            mesh_2D_Merge(mesh, streamline)
    return mesh


def main(arguments):
    streamlines_coord = arguments[1]
    bundle = np.load(streamlines_coord, allow_pickle=True)

    out = arguments[2]

    mesh = bundle_to_mesh(bundle)
    aims.write(mesh, out)

    print('Mesh created successfully :D')

if __name__ == '__main__':
    main(sys.argv)