from .smache_logging import logger


class ComputedFunction:

    @staticmethod
    def id_from_fun(fun):
        return '/'.join([fun.__module__, fun.__name__])

    def __init__(self, fun, arg_deps, computed_deps, data_source_deps=[]):
        self.fun = fun
        self.arg_deps = arg_deps
        self.data_source_deps = data_source_deps
        self.computed_deps = computed_deps
        self.relation_deps = []
        self.app = None

    def __call__(self, *args, **kwargs):
        args_with_types = zip(self.arg_deps, args)
        args = [arg_type.find(arg) for arg_type, arg in args_with_types]
        logger.debug("Calling real function {} with serialized args {}".format(
            self.fun.__name__,
            args
        ))
        return self.fun(*args, **kwargs)

    def is_in_app_context(self):
        return self.app is not None

    def set_app(self, app):
        self.app = app

    def set_data_source_deps(self, new_data_source_deps):
        self.data_source_deps = new_data_source_deps

    def set_relation_deps(self, relation_deps):
        self.relation_deps = relation_deps

    @property
    def id(self):
        return ComputedFunction.id_from_fun(self.fun)
