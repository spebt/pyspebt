import numpy as np
import yaml
from ._validator import validate

__all__ = ["parse"]


def _parse_transformation_data(idata: dict) -> np.ndarray:
    if idata["format"] == "range":
        try:
            start = float(idata["start"])
            ns = int(idata["N"])
            step = float(idata["step"])
        except Exception:
            raise SyntaxError("Invalid transformation range data!!")
        return start + np.arange(0, ns) * step
    elif idata["format"] == "list":
        try:
            iarr = np.array(idata["data"], dtype="d")
        except Exception:
            raise SyntaxError("Invalid transformation data enumerated")
        if len(iarr) == 0:
            raise SyntaxError(
                "Invalid transformation data enumerated, at least 1 number!!"
            )
        return iarr
    else:
        raise SyntaxError("Invalid transformation data format!!")


def parse(filename: str):
    """
    Load and validate a configuration file in YAML format.

    :param filename: The name of the configuration file.
    :type filename: str
    :return: A dictionary containing the parsed configuration values.
    :rtype: dict
    :raises: Exception if the configuration file fails validation or parsing.
    """
    with open(filename, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            validate(config, "base", version="v1")
        except Exception as err:
            print("Error:", "Failed validating configuration file!!")
            print("Error Messages:\n%s" % err.__str__)
            raise
    mydict = {}
    try:
        geoms = np.asarray(config["detector"]["detector geometry"], dtype="d")
        mydict["det geoms"] = np.asarray(
            config["detector"]["detector geometry"], dtype="d"
        )
        indices = np.asarray(
            config["detector"]["active geometry indices"], dtype=np.int32
        )
        active_dets = []
        for idx in indices:
            active_dets.append(geoms[geoms[:, 6] == idx][0])
        mydict["active indices"] = indices
        mydict["active dets"] = np.array(active_dets)
        mydict["det nsub"] = np.asarray(
            config["detector"]["N subdivision xyz"], dtype=np.int32
        )

        mydict["fov nsub"] = np.asarray(
            config["FOV"]["N subdivision xyz"], dtype=np.int32
        )

        mydict["fov nvx"] = np.asarray(config["FOV"]["N voxels xyz"], dtype=np.int32)
        mydict["mmpvx"] = np.asarray(config["FOV"]["mm per voxel xyz"], dtype="d")
        mydict["rotation"] = _parse_transformation_data(config["relation"]["rotation"])
        mydict["r shift"] = _parse_transformation_data(
            config["relation"]["radial shift"]
        )
        mydict["t shift"] = _parse_transformation_data(
            config["relation"]["tangential shift"]
        )

    except Exception as err:
        print("Parse Error!\n%s" % err)
        raise
    return mydict
