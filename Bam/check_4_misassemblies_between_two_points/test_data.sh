
conda activate python-2.7
export PYTHONPATH=~/miniconda2/envs/python-2.7/lib/python2.7:~/miniconda2/envs/python-2.7/lib/python2.7/site-packages

R="test_data/SLtruncations.regions2check4misassemblies.bed"
B="test_data/aligned_reads.bam"
OUT="test_data/test.SLtruncations.regions2check4misassemblies.bed"
ORIG="test_data/orig.SLtruncations.regions2check4misassemblies.bed"

## Using old Input/Output formats
python check_4_misassemblies_between_two_points___Old_InOut_Format.py --region_size 20 --min_ok_reads 10 -b $B -r $R -o $OUT.local.check_misassembly.old_format --position_info $OUT.local.position_info.old_format > $OUT.local.log.old_format
md5sum $ORIG.local.check_misassembly $OUT.local.check_misassembly.old_format
md5sum <(sed -e 's/\.0//' $ORIG.local.position_info) $OUT.local.position_info.old_format


## Using new concise Input/Output formats
python check_4_misassemblies_between_two_points___Old_Window_Coords.py --region_size 20 --min_ok_reads 10 -b $B -r $R -o $OUT.local.check_misassembly.Old_Window_Coords --position_info $OUT.local.position_info.Old_Window_Coords > $OUT.local.log.Old_Window_Coords
md5sum <(cut -f1,2,5,7,8 $ORIG.local.check_misassembly | awk 'NR>1') <(awk 'NR>1' $OUT.local.check_misassembly.Old_Window_Coords)
md5sum <(sed -e 's/\.0//' $ORIG.local.position_info | awk 'NR>1') <(awk 'NR>1' $OUT.local.position_info.Old_Window_Coords)


## Using new concise Input/Output formats + New windoe bounds check
python check_4_misassemblies_between_two_points.py --region_size 20 --min_ok_reads 10 -b $B -r $R -o $OUT.local.check_misassembly --position_info $OUT.local.position_info > $OUT.local.log
md5sum <(cut -f1,2,5,7,8 $ORIG.local.check_misassembly | awk 'NR>1') <(awk 'NR>1' $OUT.local.check_misassembly)
md5sum <(sed -e 's/\.0//' $ORIG.local.position_info | awk 'NR>1') <(awk 'NR>1' $OUT.local.position_info)
## NOTE: will not match as results are now slightly different



