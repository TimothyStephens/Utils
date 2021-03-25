

IN="test_data/input.gff3.gz"
OUT="test_data/test.CDS_splice_sites.bed.gz"
ORIG="test_data/orig.CDS_splice_sites"
./splice_site_positions_along_CDS.py -i $IN -o $OUT

md5sum <(zcat $ORIG.bed.gz | sort) <(zcat $OUT | sort)

