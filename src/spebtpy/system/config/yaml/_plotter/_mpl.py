"""
Plot with matplotlib
====================
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
from typing import TypedDict

Transform = TypedDict("Transform", {"angle": float, "trans_r": float, "trans_t": float})


def transform_verts(verts: np.ndarray, trans: Transform) -> np.ndarray:
    angle = np.deg2rad(trans["angle"])
    trans_r = trans["trans_r"]
    trans_t = trans["trans_t"]
    mtrans = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return np.array(
        [np.matmul(mtrans, vert + np.array([trans_r, trans_t])) for vert in verts]
    )


def geom2verts(geom: np.ndarray, trans: Transform) -> np.ndarray:
    verts = np.array(
        [
            [geom[0], geom[2]],
            [geom[1], geom[2]],
            [geom[1], geom[3]],
            [geom[0], geom[3]],
            [geom[0], geom[2]],
        ]
    )
    return transform_verts(verts, trans)


def verts_to_patch(verts: np.ndarray) -> patches.PathPatch:
    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.CLOSEPOLY,
    ]
    path = Path(verts, codes)
    return patches.PathPatch(path, facecolor="orange", ec="none")


def geoms_to_patchcollection(
    geoms: np.ndarray,
    trans_list: list[Transform],
    fc: str = "orange",
    ec: str = "none",
    lw: float = 0.5,
) -> PatchCollection:
    verts_list = []
    for trans in trans_list:
        for geom in geoms:
            verts_list.append(geom2verts(geom, trans))
    return PatchCollection(
        [verts_to_patch(verts) for verts in verts_list], fc=fc, ec=ec, lw=lw
    )


def plot_system(config: dict, basename: str):
    geoms = np.array(config["det geoms"])
    fov_dims = np.array(config["fov nvx"]) * np.array(config["mmpvx"])
    trans_t = -(np.max(geoms[:, 3]) + np.min(geoms[:, 2])) / 2
    det_dims = np.array(
        [
            np.max(geoms[:, 1]) - np.min(geoms[:, 0]),
            np.max(geoms[:, 3]) - np.min(geoms[:, 2]),
            np.max(geoms[:, 5]) - np.min(geoms[:, 4]),
        ]
    )
    trans_r = config["r shift"][0]
    trans_t = config["t shift"][0]-det_dims[1]*0.5
    angles = config["rotation"]
    trans_list = [
        Transform({"angle": angle, "trans_r": trans_r, "trans_t": trans_t})
        for angle in angles
    ]
    # patch = verts2rect(transform_verts(verts,trans))
    active_det_geoms = geoms[geoms[:, 6] != 0]
    plate_geoms = geoms[geoms[:, 6] == 0]

    det_coll = geoms_to_patchcollection(
        active_det_geoms, trans_list, fc="orange", ec="k", lw=0.5
    )
    plate_coll = geoms_to_patchcollection(plate_geoms, trans_list, fc="gray")

    coll = geoms_to_patchcollection(geoms, trans_list)
    fig, ax = plt.subplots(figsize=(11, 10), dpi=600)
    ax.add_patch(
        patches.Rectangle(
            (-fov_dims[0] // 2, -fov_dims[1] // 2),
            fov_dims[0],
            fov_dims[1],
            fc="none",
            ec="k",
            ls="--",
        )
    )
    ax.add_collection(det_coll)
    ax.add_collection(plate_coll)
    ax.set_xlim((trans_r + det_dims[0]) * (-1.1), (trans_r + det_dims[0]) * 1.1)
    ax.set_ylim((trans_r + det_dims[0]) * (-1.1), (trans_r + det_dims[0]) * 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    print("Saving figure")
    fig.savefig("%s.png" % basename)
    del fig, ax, det_coll, plate_coll, coll
