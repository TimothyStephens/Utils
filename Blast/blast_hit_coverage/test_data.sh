




awk -F'\t' '( (($8-$7)+1) > ($13*0.2) || (($7-$8)+1) > ($13*0.2) ) && ( (($10-$9)+1) > ($14*0.2) || (($9-$10)+1) > ($14*0.2) )' test_data/test_small1.outfmt6 | md5sum
744c09ac29423bb0bb16d707736c4f0a  -
./blast_hit_coverage.py -q 20 -s 20 -i test_data/test_small1.outfmt6 | md5sum
744c09ac29423bb0bb16d707736c4f0a  -



awk -F'\t' '( (($8-$7)+1) > ($13*0.3) || (($7-$8)+1) > ($13*0.3) ) && ( (($10-$9)+1) > ($14*0.3) || (($9-$10)+1) > ($14*0.3) )' test_data/test_small1.outfmt6 | md5sum
7b7455579bcf42aa14cd00f9f5532961  -
./blast_hit_coverage.py -q 30 -s 30 -i test_data/test_small1.outfmt6 | md5sum
7b7455579bcf42aa14cd00f9f5532961  -



awk -F'\t' '( (($8-$7)+1) > ($13*0.5) || (($7-$8)+1) > ($13*0.5) ) && ( (($10-$9)+1) > ($14*0.5) || (($9-$10)+1) > ($14*0.5) )' test_data/test_small1.outfmt6 | md5sum
9dac58c13705fe9c19c83cd545d3a225  -
./blast_hit_coverage.py -q 50 -s 50 -i test_data/test_small1.outfmt6 | md5sum
9dac58c13705fe9c19c83cd545d3a225  -





