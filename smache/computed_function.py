class ComputedFunction:

    @staticmethod
    def id_from_fun(fun):
        return '/'.join([fun.__module__, fun.__name__])

    def __init__(self, fun, arg_deps, data_source_deps, computed_deps):
        self.fun = fun
        self.arg_deps = arg_deps
        self.data_source_deps = data_source_deps
        self.computed_deps = computed_deps

    def __call__(self, *args):
        args_with_types = zip(self.arg_deps, args)
        args = [arg_type.find(arg) for arg_type, arg in args_with_types]
        return self.fun(*args)

    @property
    def id(self):
        return ComputedFunction.id_from_fun(self.fun)
