


~/programs/ncbi-blast-2.10.1+/bin/makeblastdb -dbtype prot -in long.fa

~/programs/ncbi-blast-2.10.1+/bin/blastp -query short.fa -db long.fa -outfmt 6 | awk -F'\t' '$3==100 {print $2"\t"$9-1"\t"$10"\t"$1}' > out.bed

rm long.fa.*

