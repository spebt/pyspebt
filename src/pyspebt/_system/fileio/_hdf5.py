import h5py
import numpy as np
import pyspebt


def get_hdf5_handle_mpi(comm, configFname):
    import re
    match = re.match("^(.+?)[.](yaml|yml)$", configFname)
    if match is not None:
        outFname = match.group(1) + ".hdf5"
    else:
        raise ValueError("Invalid config file name")
    return h5py.File(outFname, "w", driver="mpio", comm=comm)
  
def get_hdf5_handle_nonmpi(configFname):
    import re
    match = re.match("^(.+?)[.](yaml|yml)$", configFname)
    if match is not None:
        outFname = match.group(1) + ".hdf5"
    else:
        raise ValueError("Invalid config file name")
    return h5py.File(outFname, "w")

def get_dset_mpi(file, config):
    Nfov = np.prod(config["fov nvx"])
    Ndet = config["active dets"].shape[0]
    Nrot = config["rotation"].shape[0]
    Nrshift = config["r shift"].shape[0]
    Ntshift = config["t shift"].shape[0]
    ntasks = Nfov * Ndet * Nrot * Nrshift * Ntshift
    return file.create_dataset(
        "sysmat", (Ntshift, Nrshift, Nrot, Ndet, Nfov), dtype=np.float64
    )

def save_dict2hdf5(config, h5f, group="configs"):
    h5group = h5f.create_group(group)
    for key in config.keys():
        if isinstance(config[key], dict):
            save_dict2hdf5(config[key], h5f, group + "/" + key)
        elif isinstance(config[key], str):
            h5group.attrs[key] = config[key]
        else:
            h5group.create_dataset(key, data=config[key])
