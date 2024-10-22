import spebtpy
import numpy as np
import sys

configFname = sys.argv[1]
config = spebtpy.system.config.yaml.parse(configFname)
outf=spebtpy.fileio.get_hdf5_handle_nonmpi(configFname)
ntasks, idmap = spebtpy.fileio.get_idmap(config)
fov_subdivs = spebtpy.system.matrix.raytracing.get_fov_subdivs(config["mmpvx"], config["fov nsub"])
dset = spebtpy.fileio.get_dset_mpi(outf, config)

for idx in range(0, ntasks):
    dset[idmap[idx, 0], idmap[idx, 1], idmap[idx, 2], idmap[idx, 3], idmap[idx, 4]] = (
        spebtpy.system.matrix.raytracing.get_pair_ppdf(
            idmap[idx, 4],
            idmap[idx, 3],
            idmap[idx, 2],
            idmap[idx, 1],
            idmap[idx, 0],
            fov_subdivs,
            config,
        )
    )

spebtpy.fileio.save_dict2hdf5(config, outf)
outf.close()
