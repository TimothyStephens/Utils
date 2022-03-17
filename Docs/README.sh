

## 
## How to run MaSuRCA parallel on any grid (not just SGE).
## 

##
## INSTALL
##

## You will most likely need to load the below modules before installing (and when running) MaSuRCA
module load python/2.7.14
module load mkl/2018.2
module load gnu/7.2.0
module load boost/1.65.1
export BOOST_ROOT=$BOOSTROOT

./install.sh


##
## RUNNING
##

## First setup your config file and generate the assemble.sh script (set 'USE_GRID=1' in the config.txt file):
~/MaSuRCA-3.2.8/bin/masurca config.txt
## MaSuRCA can restart after the last checkpoint if you recreate the assembly.sh
## script before rerunning the job. 


## To run the MaSuRCA workflow submit a job running the assembly.sh script

$ cat run_MaSuRCA.sh 
#PBS -l select=1:ncpus=24:mem=500GB:vmem=500GB:beegfs=True
#PBS -l walltime=336:00:00
#PBS -A NCMAS-d85
#PBS -k oe
#PBS -j oe
#PBS -q BeeGFS
#PBS -N CCMP1383_MaSuRCA

cd $PBS_O_WORKDIR

module load python/2.7.14
module load mkl/2018.2
module load gnu/7.2.0
module load boost/1.65.1
export BOOST_ROOT=$BOOSTROOT

./assemble.sh



## NOTE: MaSuRCA may use >500Gb of memory in one of the early stages (depending on how much short-read data you use).
## This stages will have to be run outside the BeeGFS system and on the BigMem node.


## Their are 5 main stages where MaSuRCA can be run on multiple nodes.
## mr_pass1
## mr_pass2
## 0-overlaptrim-overlap
## 1-overlapper
## 3-overlapcorrection
## 
## MaSuRCA can run these stages on multiple nodes using the SGE manager. Since we dont 
## have that we can submit the subjobs manually. 

## It's always a good idea after running a stage parallel that you recreate the assembly.sh script. 


## Run mr_pass1 on multiple nodes.
## 
## A new MaSuRCA assembly run it will eventually (after read error correction; will take a long time) 
## reach the mr_pass1 stage.
## 
## Need to set 'USE_GRID=1' in the config.txt file before MaSuRCA reaches this stage. 
## This will make MaSuRCA partition the file ready to be run on the grid 
## (partitions wont be make if USE_GRID=0). 
## MaSuRCA will then try to submit an array job using SGE however it will fail.
## All you need to do is process each partition yourself, and restart MaSuRCA. It will recognise that the output 
## files have been created move on to the next step. 
## If you want to change the ncpus you need to change it in the create_mega_reads.sh script (the `-t` argument). 
## Needs >180GB mem per job.
cd mr_pass1/

## Example PBS script to run mr_pass1 on multiple nodes.

#PBS -l select=1:ncpus=24:mem=500GB:vmem=500GB:beegfs=True
#PBS -l walltime=336:00:00
#PBS -A NCMAS-d85
#PBS -k oe
#PBS -j oe
#PBS -J 1-199
#PBS -q BeeGFS
#PBS -N CCMP1383_mega_reads_pass1

set -o errexit
cd $PBS_O_WORKDIR
source ~/run_cmd.sh
 
module load python/2.7.14
module load mkl/2018.2
module load gnu/7.2.0
module load boost/1.65.1
export BOOST_ROOT=$BOOSTROOT

echo "job $PBS_ARRAY_INDEX running"
 
export SGE_TASK_ID=$PBS_ARRAY_INDEX

./create_mega_reads.sh



## Once the above jobs have finished you can rerun MaSuRCA (best to recreate the assembly.sh script). 
## It will check to see if each subjob has already completed.
## MaSuRCA will combine all the partitions and remove the rm_pass1 directory.


## If the data for pass 2 will fit into 128Gb of RAM it will be run locally (even if USE_GRID=1 is set).
## If it is larger it will split it into a lot of partitions and run them on the grid. 
## The partition splitting process took around 5 days for me. It is extremely slow, not sure why. 

## Run all the partitions (see below).
## Needs ~20GB of mem per job.
cd mr_pass2/

## Example PBS script to run mr_pass2 on the grid.

#PBS -l select=1:ncpus=24:mem=500GB:vmem=500GB:beegfs=True
#PBS -l walltime=336:00:00
#PBS -A NCMAS-d85
#PBS -k oe
#PBS -j oe
#PBS -J 1-1000
#PBS -q BeeGFS
#PBS -N CCMP1383_mega_reads_pass2

set -o errexit
cd $PBS_O_WORKDIR
source ~/run_cmd.sh

module load python/2.7.14
module load mkl/2018.2
module load gnu/7.2.0
module load boost/1.65.1
export BOOST_ROOT=$BOOSTROOT

echo "job $PBS_ARRAY_INDEX running"

export SGE_TASK_ID=$PBS_ARRAY_INDEX

./jf_aligner.sh




## Once all jobs have finished recreate the assemble.sh script and rerun it.
## 
## This will take ~24 hrs. The mr_pass directory will be removed.
## 
## If the recombining step uses >500GB of memory edit the longest_path.sh script, reducing the number of ncpus
## used by each program (-t 3 seems to work well).
## 
## The CA.mr.xx.xx.xx.x.xxx directory will be created where the next stages will take place. 
## At this point when masurca was still running I killed the job removed the CA.mr.* directory and recreated
## assemble.sh with 'USE_GRID=0'. We now no longer need masurca to try to run stuff on the grid.
## Recreate and rerun assemble.sh. 
## 
## MaSuRCA will reach a stage where it starts running lots of commands 
## (check the CA.mr.xx.xx.xx.x.xxx.log for the 'overlap.sh' commands)
## It will be working in the directory CA.mr.xx.xx.xx.x.xxx/0-overlaptrim-overlap/
## Kill the MaSuRCA job and submit the below script.
## 
## To set the limits of the array job find the line in the CA.mr.*.log file where it talks about the 'Last batch' created
## Set array bounds to: 0-('Last batch' - 1) (printed in CA.mr.*.log)
## Check the number of processes used by the overlap.sh script (usually it is 2). This is why the $NCPUS is divided by 2 
## (to get the max number of running jobs).
cd CA.mr.41.15.17.0.029/0-overlaptrim-overlap

#PBS -l select=1:ncpus=24:mem=500GB:vmem=500GB:beegfs=True
#PBS -l walltime=336:00:00
#PBS -A NCMAS-d85
#PBS -k oe
#PBS -j oe
#PBS -J 0-51
#PBS -q BeeGFS
#PBS -N CCMP1383_MaSuRCA_3.2.8_PLOIDY_2_CorGenSizEst_0-overlaptrim-overlap

set -o errexit
cd $PBS_O_WORKDIR
source ~/run_cmd.sh

module load python/2.7.14
module load mkl/2018.2
module load gnu/7.2.0
module load boost/1.65.1
export BOOST_ROOT=$BOOSTROOT
module load parallel/20180322


parallel -j $((NCPUS/2)) '/mnt/beegfs/timothy.stephens/POLARELLA_GLACIALIS/CCMP1383/GENOME_ASSEMBLIES/MaSuRCA_3.2.8/ASSEMBLY/CA.mr.41.15.17.0.029/0-overlaptrim-overlap/overlap.sh {} > /mnt/beegfs/timothy.stephens/POLARELLA_GLACIALIS/CCMP1383/GENOME_ASSEMBLIES/MaSuRCA_3.2.8/ASSEMBLY/CA.mr.41.15.17.0.029/0-overlaptrim-overlap/{}.out_overlaptrim_overlap 2>&1; echo "Finished job: {}"' ::: $(seq ${PBS_ARRAY_INDEX}000 ${PBS_ARRAY_INDEX}999)



## Once all jobs have finished you can recreate the assemble.sh script and resubmit your main job.
## MaSuRCA will check all partitions finished correctly and will continue to the next stage, which 
## is similar to the last stage and will require you to stop the assembler and run the subjobs across
## multiple nodes. 
cd CA.mr.41.15.17.0.029/1-overlapper

#PBS -l select=1:ncpus=24:mem=500GB:vmem=500GB:beegfs=True
#PBS -l walltime=336:00:00
#PBS -A NCMAS-d85
#PBS -k oe
#PBS -j oe
#PBS -J 0-51
#PBS -q BeeGFS
#PBS -N CCMP1383_MaSuRCA_3.2.8_PLOIDY_2_CorGenSizEst_1-overlapper

set -o errexit
cd $PBS_O_WORKDIR
source ~/run_cmd.sh

module load python/2.7.14
module load mkl/2018.2
module load gnu/7.2.0
module load boost/1.65.1
export BOOST_ROOT=$BOOSTROOT
module load parallel/20180322


parallel -j $((NCPUS/2)) '/mnt/beegfs/timothy.stephens/POLARELLA_GLACIALIS/CCMP1383/GENOME_ASSEMBLIES/MaSuRCA_3.2.8/ASSEMBLY/CA.mr.41.15.17.0.029/1-overlapper/overlap.sh {} > /mnt/beegfs/timothy.stephens/POLARELLA_GLACIALIS/CCMP1383/GENOME_ASSEMBLIES/MaSuRCA_3.2.8/ASSEMBLY/CA.mr.41.15.17.0.029/1-overlapper/{}.out_overlapper 2>&1; echo "Finished job: {}"' ::: $(seq ${PBS_ARRAY_INDEX}000 ${PBS_ARRAY_INDEX}999)




## As before re-run the main MaSuRCA assembly.sh script and wait for it to progress to the next state. 
##
## The next stage '3-overlapcorrection' will have two phases where you can stop it and run the jobs parallel. 
## After this stage the remaining stages run fast enough that you don't need to run them parallel. 
cd CA.mr.41.15.17.0.029/3-overlapcorrection

## NOTE: for both phases in '3-overlapcorrection' to get the range for the array, you need
## to look in the frgcorr.sh or ovlcorr.sh script and see what the max index it will accept is. 

cat run_frgcorr.sh 
#PBS -l select=1:ncpus=24:mem=500GB:vmem=500GB:beegfs=True
#PBS -l walltime=336:00:00
#PBS -A NCMAS-d85
#PBS -k oe
#PBS -j oe
#PBS -J 1-1090
#PBS -q BeeGFS
#PBS -N CCMP1383_MaSuRCA_3.2.8_PLOIDY_2_CorGenSizEst_3-overlapcorrection_frgcorr

set -o errexit
cd $PBS_O_WORKDIR
source ~/run_cmd.sh

module load python/2.7.14
module load mkl/2018.2
module load gnu/7.2.0
module load boost/1.65.1
export BOOST_ROOT=$BOOSTROOT

/mnt/beegfs/timothy.stephens/POLARELLA_GLACIALIS/CCMP1383/GENOME_ASSEMBLIES/MaSuRCA_3.2.8/ASSEMBLY/CA.mr.41.15.17.0.029/3-overlapcorrection/frgcorr.sh ${PBS_ARRAY_INDEX} > /mnt/beegfs/timothy.stephens/POLARELLA_GLACIALIS/CCMP1383/GENOME_ASSEMBLIES/MaSuRCA_3.2.8/ASSEMBLY/CA.mr.41.15.17.0.029/3-overlapcorrection/${PBS_ARRAY_INDEX}.err_frgcorr 2>&1


cat run_ovlcorr.sh 
#PBS -l select=1:ncpus=24:mem=500GB:vmem=500GB:beegfs=True
#PBS -l walltime=336:00:00
#PBS -A NCMAS-d85
#PBS -k oe
#PBS -j oe
#PBS -J 0-21
#PBS -q BeeGFS 
#PBS -N CCMP1383_MaSuRCA_3.2.8_PLOIDY_2_CorGenSizEst_3-overlapcorrection_ovlcorr
 
set -o errexit
cd $PBS_O_WORKDIR
module load python/2.7.14
module load mkl/2018.2
module load gnu/7.2.0
module load boost/1.65.1
export BOOST_ROOT=$BOOSTROOT
module load parallel/20180322

parallel -j $NCPUS '/mnt/beegfs/timothy.stephens/POLARELLA_GLACIALIS/CCMP1383/GENOME_ASSEMBLIES/MaSuRCA_3.2.8/ASSEMBLY/CA.mr.41.15.17.0.029/3-overlapcorrection/ovlcorr.sh {} > /mnt/beegfs/timothy.stephens/POLARELLA_GLACIALIS/CCMP1383/GENOME_ASSEMBLIES/MaSuRCA_3.2.8/ASSEMBLY/CA.mr.41.15.17.0.029/3-overlapcorrection/{}.err_ovlcorr 2>&1; echo "Finished job: {}"' ::: $(seq ${PBS_ARRAY_INDEX}00 ${PBS_ARRAY_INDEX}99)










