# make original
python3 ./make_database.py dataset md_old.pickle --old

# make new with 4 differnet alpha value
for alpha in 0.0 0.3 0.6 1.0; do
    python3 ./make_database.py dataset md_${alpha}.pickle -a ${alpha}
done

for c_num in 0 1 2 3 4; do
    echo "c=$c_num"
    python3 ./get_experiment_data.py md_old.pickle -c $c_num
    for alpha in 0.0 0.3 0.6 1.0; do
        python3 ./get_experiment_data.py md_${alpha}.pickle -c $c_num --no-deletion
    done
done
