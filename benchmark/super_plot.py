# a bar plot with errorbars
import numpy as np
import matplotlib.pyplot as pl
import json
from .db_helper import test_sets
from itertools import groupby

class BenchmarkStat:
    def __init__(self, benchmark):
        self.benchmark = benchmark

    @property
    def mean(self):
        return self.stats['mean']

    @property
    def stddev(self):
        return self.stats['stddev']

    @property
    def x_value(self):
        return int(self.name.split('_')[-1])

    @property
    def x_label(self):
        return '_'.join(self.name.split('__')[-1].split('_')[:-1])

    @property
    def group_name(self):
        return self.name.split('__')[0]

    @property
    def name(self):
        return self.benchmark['name']

    @property
    def stats(self):
        return self.benchmark['stats']

class Benchmark:
    def __init__(self, benchmarks, name):
        self.benchmarks = benchmarks
        self.name = name

    @property
    def means(self):
        return [bm_stat.mean for bm_stat in self.benchmarks]

    @property
    def stddevs(self):
        return [bm_stat.stddev for bm_stat in self.benchmarks]

    @property
    def x_values(self):
        return [bm_stat.x_value for bm_stat in self.benchmarks]

    @property
    def x_label(self):
        return self.benchmarks[0].x_label


class BenchmarkRepo:
    @classmethod
    def load_stats(cls, report_path):
        bm_dicts = cls.load_benchmark_dicts(report_path)
        return [BenchmarkStat(bm) for bm in bm_dicts]

    @classmethod
    def load_benchmark_dicts(cls, report_path):
        filename = '/'.join(['benchmark', 'results', report_path])
        with open(filename) as f:
            return json.loads(f.read())['benchmarks']

    @classmethod
    def load_grouped_benchmarks(cls, report_path):
        benhcmark_dicts = cls.load_stats(report_path)
        grouped_benchmarks = groupby(benhcmark_dicts, lambda bm: bm.group_name)
        return [Benchmark(list(benchmarks), bm_name)
                for bm_name, benchmarks in grouped_benchmarks]

def show_custom_plot(report_name):
    old_benchmarks = BenchmarkRepo.load_grouped_benchmarks("current/{}".format(report_name))
    benchmarks = BenchmarkRepo.load_grouped_benchmarks(report_name)

    fig = pl.figure()

    nrows = len(benchmarks)
    ncols = 1

    for index, benchmark in enumerate(benchmarks):
        a1 = pl.subplot(nrows, ncols, index + 1)
        build_axis(
            a1,
            benchmark.means,
            benchmark.stddevs,
            old_benchmarks[index].means,
            benchmark.x_values,
            benchmark.x_label,
            benchmark.name
        )

    fig.tight_layout()
    pl.show()

def build_axis(axis, means, stddevs, old_means, x_axis, x_label, name):
    axis.errorbar(x_axis, means, stddevs)
    axis.errorbar(x_axis, old_means)
    axis.set_ylabel('Time (ms)')
    axis.set_xlabel(x_label)
    axis.set_title(name)
    annotate_db_names(axis, x_axis, means, x_axis)


def annotate_db_names(axis, x_axis, y_axis, db_names):
    for index, xy in enumerate(zip(x_axis, y_axis)):
        axis.annotate(db_names[index], xy=xy, textcoords='data')
