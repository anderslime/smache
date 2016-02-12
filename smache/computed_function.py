class ComputedFunction:
    def __init__(self, fun, arg_deps, data_source_deps, computed_deps):
        self.fun              = fun
        self.fun_name         = fun.__name__
        self.arg_deps         = arg_deps
        self.data_source_deps = data_source_deps
        self.computed_deps    = computed_deps

    def __call__(self, *args):
        args_with_types = zip(self.arg_deps, args)
        args = [arg_type.find(arg) for arg_type, arg in args_with_types]
        return self.fun(*args)

