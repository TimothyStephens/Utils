
python grepf_column.py -i test_data/test_input.txt -o test_data/test_output1.txt -f test_data/test_ids1.txt -c 1
diff test_data/test_output1.txt test_data/test_output1.txt.expected 

python grepf_column.py -i test_data/test_input.txt -o test_data/test_output1-v.txt -f test_data/test_ids1.txt -c 1 -v
diff test_data/test_output1-v.txt test_data/test_output1-v.txt.expected 

python grepf_column.py -i test_data/test_input.txt -o test_data/test_output2.txt -f test_data/test_ids2.txt -c 2
diff test_data/test_output2.txt test_data/test_output2.txt.expected

python grepf_column.py -i test_data/test_input.txt -o test_data/test_output2-v.txt -f test_data/test_ids2.txt -c 2 -v
diff test_data/test_output2-v.txt test_data/test_output2-v.txt.expected

