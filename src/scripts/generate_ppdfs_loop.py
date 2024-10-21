import pyspebt
import numpy as np
import sys

configFname = sys.argv[1]
config = pyspebt._system.specification.yaml.parse(configFname)
outf=pyspebt._system.fileio.get_hdf5_handle(configFname)
ntasks, idmap = pyspebt.fileio.get_idmap()
fov_subdivs = pyspebt.get_fov_subdivs(config["mmpvx"], config["fov nsub"])
dset = pyspebt.fileio.get_dset_mpi(outf, config)

for idx in range(0, ntasks):
    dset[idmap[idx, 0], idmap[idx, 1], idmap[idx, 2], idmap[idx, 3], idmap[idx, 4]] = (
        pyspebt.get_pair_ppdf(
            idmap[idx, 4],
            idmap[idx, 3],
            idmap[idx, 2],
            idmap[idx, 1],
            idmap[idx, 0],
            fov_subdivs,
            config,
        )
    )

pyspebt.fileio.save_dict2hdf5(config, outf)
outf.close()
