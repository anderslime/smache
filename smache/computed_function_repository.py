from .computed_function import ComputedFunction


class ComputedFunctionRepository:

    def __init__(self, function_serializer):
        self._function_serializer = function_serializer
        self.computed_funs = {}

    def get(self, fun):
        return self.get_from_id(self._id(fun))

    def get_from_id(self, fun_id):
        try:
            return self.computed_funs[fun_id]
        except KeyError:
            funs = self.computed_funs.keys()
            raise KeyError(self._function_not_found_message(fun_id, funs))

    def add(self, computed_fun):
        self.computed_funs[self._id(computed_fun.fun)] = computed_fun

    def computed_key(self, fun, *args, **kwargs):
        computed_fun = self.get(fun)
        return self._function_serializer.serialized_fun(
            computed_fun,
            *args,
            **kwargs
        )

    def _id(self, fun):
        return ComputedFunction.id_from_fun(fun)

    def _function_not_found_message(self, fun_id, funs):
        return "Could not find computed function {} from list: {}".format(
            fun_id,
            funs
        )
