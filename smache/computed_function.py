from .smache_logging import debug


class ComputedFunction:

    @staticmethod
    def id_from_fun(fun):
        return '/'.join([fun.__module__, fun.__name__])

    def __init__(self, fun, arg_deps, **options):
        self.fun = fun
        self.arg_deps = arg_deps
        self.data_source_deps = []
        self.relation_deps = []
        self.ttl = options.get('ttl', None)
        self.in_flask_context = False

    def __call__(self, *args, **kwargs):
        args_with_types = zip(self.arg_deps, args)
        args = [arg_type.find(arg) for arg_type, arg in args_with_types]
        debug("Calling real function {} with serialized args {}".format(
            self.fun.__name__,
            args
        ))
        return self.fun(*args, **kwargs)

    def is_in_app_context(self):
        return self.in_flask_context

    def set_to_execute_in_flask_context(self):
        self.in_flask_context = True

    def set_data_source_deps(self, new_data_source_deps):
        self.data_source_deps = new_data_source_deps

    def set_relation_deps(self, relation_deps):
        self.relation_deps = relation_deps

    @property
    def id(self):
        return ComputedFunction.id_from_fun(self.fun)
