# a bar plot with errorbars
import numpy as np
import matplotlib.pyplot as pl
import json
from .db_helper import test_sets

class BenchmarkRepo:
    @classmethod
    def load(cls, report_path):
        filename = '/'.join(['benchmark', 'results', report_path])
        with open(filename) as f:
            return BenchmarkRepo(json.loads(f.read()))

    def __init__(self, raw_benchmark_dict):
        self.raw_benchmark_dict = raw_benchmark_dict

    @property
    def means(self):
        return [bm_stats['mean'] * 1000 for bm_stats in self.stats]

    @property
    def stddevs(self):
        return [bm_stats['stddev'] * 1000 for bm_stats in self.stats]

    @property
    def name(self):
        return self.benchmarks[0]['fullname'].split('::')[0]

    def benchmark_names(self, split_by='__'):
        return [bm['name'].split(split_by)[-1] for bm in self.benchmarks]

    @property
    def stats(self):
        return [bm['stats'] for bm in self.benchmarks]

    @property
    def benchmarks(self):
        return self.raw_benchmark_dict['benchmarks']


def show_plot(report_name):
    new_bm_repo = BenchmarkRepo.load(report_name)
    old_bm_repo = BenchmarkRepo.load("current/{}".format(report_name))

    benchmark_json = new_bm_repo.raw_benchmark_dict
    old_benchmark_json = old_bm_repo.raw_benchmark_dict

    old_means = old_bm_repo.means
    mean = new_bm_repo.means

    name           = new_bm_repo.name
    std            = new_bm_repo.stddevs
    db_names       = new_bm_repo.benchmark_names('_')

    users = [test_set.num_of_users for test_set in test_sets]
    handins = [test_set.num_of_handins for test_set in test_sets]
    users_per_handin = [test_set.num_of_users_per_handin for test_set in test_sets]

    def build_axis(axis, x_axis, x_label):
        axis.errorbar(x_axis, mean, std)
        axis.errorbar(x_axis, old_means)
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
