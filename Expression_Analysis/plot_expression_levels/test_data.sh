

conda activate r_env
export R_LIBS=~/R_LIBS_CONDA

Rscript plot_time_course_expression_data.R test_data/data_matrix.melted.gz test_data/test.plots.pdf test_data/order2plot.txt



