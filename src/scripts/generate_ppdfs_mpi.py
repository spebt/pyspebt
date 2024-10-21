import sys
import pyspebt
from mpi4py import MPI

comm = MPI.COMM_WORLD
nprocs=comm.Get_size()
rank=comm.Get_rank()

time_start = MPI.Wtime()
configFname = sys.argv[1]
config = pyspebt._system.specification.yaml.parse(configFname)
outf=pyspebt._system.fileio.get_hdf5_handle_mpi(comm,configFname)
ntasks, idmap = pyspebt.fileio.get_idmap()
fov_subdivs = pyspebt.get_fov_subdivs(config["mmpvx"], config["fov nsub"])
procTaskIds = pyspebt.get_procIds(ntasks, nprocs)
dset = pyspebt.fileio.get_dset_mpi(outf, config)

if rank == 0:
    print("Configurations:")
    print("{:30s}{:,}".format("N total tasks:", ntasks))
    print("{:30s}{:,}\n".format("N Process:", nprocs))
    sys.stdout.flush()

for idx in range(procTaskIds[0, rank], procTaskIds[1, rank]):
    dset[idmap[idx, 0], idmap[idx, 1], idmap[idx, 2], idmap[idx, 3], idmap[idx, 4]] = (
        pyspebt._system.matrix.raytracing.get_pair_ppdf(
            idmap[idx, 4],
            idmap[idx, 3],
            idmap[idx, 2],
            idmap[idx, 1],
            idmap[idx, 0],
            fov_subdivs,
            config,
        )
    )
    
if rank == 0:
    pyspebt.fileio.save_dict2hdf5(config, outf)
    
outf.close()
time_end = MPI.Wtime()
print("Rank:", rank, "elapsed time:", str(time_end - time_start))
