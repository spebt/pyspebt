# 3D coordinate transformation, N x 3 Numpy array as input,
# The coordinate frame rotates counter-clock-wise by angle_rad
import math
import numpy as np


def get_mtransform(angle_deg: float, tx, ty, tz=0) -> tuple[np.ndarray, np.ndarray]:
    """
    Get the transformation matrix for a given angle in degrees and translation values.

    :param angle_deg: The angle in degrees.
    :param tx: The translation value along the x-axis.
    :param ty: The translation value along the y-axis.
    :param tz: The translation value along the z-axis.
    :return: The transformation matrix as a tuple of two numpy arrays.
    """
    # convert degrees to radians
    angle_rad = math.radians(angle_deg)
    return (
        np.array(
            [
                [math.cos(angle_rad), -math.sin(angle_rad), 0],
                [math.sin(angle_rad), math.cos(angle_rad), 0],
                [0, 0, 1],
            ]
        ),
        np.array([tx, ty, tz]),
    )


# M(x+M_inv*a)=Mx+a


def get_transformed(input: np.ndarray, deg, tx, ty, tz=0):
    """
    Apply coordinate transformation to the input array.

    :param m: A tuple containing two numpy arrays representing the transformation matrix.
    :type m: tuple[numpy.ndarray,numpy.ndarray]
    :param input: The input array to be transformed.
    :type input: numpy.ndarray
    :return: The transformed array.
    :rtype: numpy.ndarray
    """
    m = get_mtransform(deg, tx, ty, tz)
    return np.matmul(input, m[0]) + m[1]


def get_fov_subdivs(mmpvx, nsubs):
    """
    Get the subdivisions of an image.

    :param mmpvx: The maximum values of the x, y, and z coordinates.
    :type mmpvx: array-like
    :param nsubs: The number of subdivisions in the x, y, and z directions.
    :type nsubs: array-like
    :return: A dictionary containing the coordinates and increments of the subdivisions.
    :rtype: dict
    """
    xlin = np.linspace(0, mmpvx[0], int(nsubs[0]) + 1)
    ylin = np.linspace(0, mmpvx[1], int(nsubs[1]) + 1)
    zlin = np.linspace(0, mmpvx[2], int(nsubs[2]) + 1)
    return {
        "coords": np.array(
            np.meshgrid(
                0.5 * (xlin[1:] + xlin[:-1]),
                0.5 * (ylin[1:] + ylin[:-1]),
                0.5 * (zlin[1:] + zlin[:-1]),
            )
        ).T.reshape(int(nsubs.prod()), 3)
        - mmpvx * 0.5,
        "incs": mmpvx / nsubs,
    }


def get_det_subdivs(focs: np.ndarray, nsubs: np.ndarray):
    """
    Get the subdivisions of a detector.

    :param focs: The focal points of the detector.
    :type focs: ndarray
    :param nsubs: The number of subdivisions in the x, y, and z directions.
    :type nsubs: ndarray
    :return: A dictionary containing the subdivisions and increments.
    :rtype: dict
        - geoms (ndarray): The subdivisions of the detector.
        - incs (ndarray): The increments of the subdivisions.
    """
    nsubs_prod = np.prod(nsubs)
    focs_incrs = (focs[1:6:2] - focs[:6:2]) / nsubs
    incr_map = np.indices(np.flip(nsubs) + 1)
    map1 = (
        np.flip(
            incr_map[:, : nsubs[2], : nsubs[1], : nsubs[0]].reshape((3, nsubs_prod)).T,
            axis=1,
        )
        * focs_incrs
    )
    map2 = (
        np.flip(
            incr_map[:, 1 : nsubs[2] + 1, 1 : nsubs[1] + 1, 1 : nsubs[0] + 1]
            .reshape((3, nsubs_prod))
            .T,
            axis=1,
        )
        * focs_incrs
    )
    new_seq = np.array([0, 3, 1, 4, 2, 5])
    out = np.hstack((map1, map2, np.zeros((nsubs_prod, 1)), np.zeros((nsubs_prod, 1))))
    return {
        "geoms": np.hstack(
            (out[:, new_seq], np.zeros((nsubs_prod, 1)), np.zeros((nsubs_prod, 1)))
        )
        + focs[np.array([0, 0, 2, 2, 4, 4, 6, 7])],
        "incs": focs_incrs,
    }
    


def get_centroids(geoms: np.ndarray) -> np.ndarray:
    """
    Get the centroids of the subdivisions.

    :param geoms: The subdivisions of the detector.
    :type geoms: ndarray
    :return: The centroids of the subdivisions.
    :rtype: ndarray
    """
    return (geoms[:, :6:2] + geoms[:, 1:6:2]) * 0.5


def append_subdivs(geoms: np.ndarray, focs: np.ndarray, subdiv_geoms: np.ndarray):
    """
    Append subdivisions to the existing array of geometries.

    :param geoms: The existing subdivisions.
    :type geoms: ndarray
    :param focs: The detector units geometries in focus.
    :type focs: ndarray
    :param subdiv_geoms: The subdivisions geometries to be appended.
    :type subdiv_geoms: ndarray
    :return: The updated array of geometries.
    :rtype: ndarray
    """
    blocks = geoms[geoms[:, 6] != focs[6]]
    return np.vstack((blocks, subdiv_geoms))


def get_fov_voxel_center(
    id: np.uint64, nvx: np.ndarray, mmpvx: np.ndarray
) -> np.ndarray:
    """
    Calculate the center coordinates of a voxel given its index.

    :param id: The index of the voxel.
    :type id: np.uint64
    :param nvx: The number of voxels in each dimension.
    :type nvx: np.ndarray
    :param mmpvx: The size of each voxel in millimeters.
    :type mmpvx: np.ndarray
    :return: The center coordinates of the voxel.
    :rtype: np.ndarray
    :raises AssertionError: If the given voxel index is invalid.
    """
    # make sure the 1-D index given is valid
    assert id < np.prod(nvx), "Invalid voxel index!"
    # index order, slowest to quickest changing: z -> y -> x
    zid = id // (nvx[0] * nvx[1])
    xyid = id % (nvx[0] * nvx[1])
    yid = xyid // nvx[0]
    xid = xyid % nvx[0]
    # print('z -> y -> x:', '%d -> %d -> %d'%(zid, yid, xid))
    return (np.array([xid, yid, zid]) - np.append(nvx[:2], 0) * 0.5) * mmpvx


def get_AB_pairs(pAs, pBs):
    """
    Generate pairs of points from two arrays of points.

    :param pAs: Array of points A.
    :type pAs: numpy.ndarray
    :param pBs: Array of points B.
    :type pBs: numpy.ndarray
    :return: Array of pairs of points, where each row contains the coordinates of a pair (Ax, Ay, Az, Bx, By, Bz).
    :rtype: numpy.ndarray
    """
    na, nb = (len(pAs), len(pBs))
    return np.concatenate((np.repeat(pAs, nb, axis=0), np.tile(pBs, (na, 1))), axis=1)





