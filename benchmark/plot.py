# a bar plot with errorbars
import numpy as np
import matplotlib.pyplot as pl
import json
from .db_helper import test_sets

def show_plot(filename):
    json_benchmarks = []

    mean = []
    std  = []

    name = 'No title'

    with open(filename) as f:
        benchmark_json = json.loads(f.read())
        name           = benchmark_json['benchmarks'][0]['fullname'].split('::')[0]
        mean           = [bm['stats']['mean'] * 1000 for bm in benchmark_json["benchmarks"]]
        std            = [bm['stats']['stddev'] * 1000 for bm in benchmark_json["benchmarks"]]
        db_names       = [bm['name'].split('_')[-1] for bm in benchmark_json['benchmarks']]

        users = [test_set.num_of_users for test_set in test_sets]
        handins = [test_set.num_of_handins for test_set in test_sets]
        users_per_handin = [test_set.num_of_users_per_handin for test_set in test_sets]

        def build_axis(axis, x_axis, x_label):
            axis.errorbar(x_axis, mean, std)
            axis.set_ylabel('Time (ms)')
            axis.set_xlabel(x_label)
            axis.set_title(name)
            annotate_db_names(axis, x_axis, mean, db_names)

        fig = pl.figure()

        a1 = pl.subplot(311)
        build_axis(a1, handins, 'Handins')

        a2 = pl.subplot(312)
        build_axis(a2, users, 'Users')

        a3 = pl.subplot(313)
        build_axis(a3, users_per_handin, 'Users per Handin')

        fig.tight_layout()
        pl.show()


def annotate_db_names(axis, x_axis, y_axis, db_names):
    for index, xy in enumerate(zip(x_axis, y_axis)):
        axis.annotate(db_names[index], xy=xy, textcoords='data')
