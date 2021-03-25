


./head_groupby.py -c 1 -n 2 -i test_data/list.txt -o test_data/test.list_head2.txt
md5sum test_data/orig.list_head2.txt test_data/test.list_head2.txt

./head_groupby_unique.py -c 1 -n 2 -u 2 -i test_data/list.txt -o test_data/test.list_head_uniq2.txt
md5sum test_data/orig.list_head_uniq2.txt test_data/test.list_head_uniq2.txt



