import numpy as np

def get_idmap(config):
    Nfov = np.prod(config["fov nvx"])
    Ndet = config["active dets"].shape[0]
    Nrot = config["rotation"].shape[0]
    Nrshift = config["r shift"].shape[0]
    Ntshift = config["t shift"].shape[0]
    ntasks = Nfov * Ndet * Nrot * Nrshift * Ntshift
    return ntasks, np.indices((Ntshift, Nrshift, Nrot, Ndet, Nfov)).reshape(5, ntasks).T
  
def get_procIds(ntasks: np.uint64, nprocs: int) -> np.ndarray:
    """
    Calculate the indices of tasks assigned to each process.

    :param ntasks: The total number of tasks.
    :type ntasks: np.uint64
    :param nprocs: The total number of processes.
    :type nprocs: np.uint64
    :return: A 2D array containing the start and end indices of tasks assigned to each process.
    :rtype: np.ndarray
    """
    nPerProc_add = np.zeros(nprocs)
    nPerProc_add[0 : ntasks % nprocs] = np.ones(ntasks % nprocs)
    idxsPerProc = np.cumsum(
        np.insert(np.ones(nprocs) * (ntasks // nprocs) + nPerProc_add, 0, 0),
        dtype=np.uint32,
    )
    idxsPerProc = np.vstack((idxsPerProc[:-1], idxsPerProc[1:]))
    return idxsPerProc