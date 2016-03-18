from .computed_function import ComputedFunction

class ComputedFunctionRepository:
    def __init__(self, computed_funs = None):
        self.computed_funs = computed_funs or {}

    def get(self, fun):
        return self.get_from_id(self._id(fun))

    def get_from_id(self, fun_id):
        try:
            return self.computed_funs[fun_id]
        except KeyError:
            funs = self.computed_funs.keys()
            raise KeyError(
                "Could not find computed function {} from computed_funs: {}".format(fun_id, funs)
            )


    def add(self, computed_fun):
        self.computed_funs[self._id(computed_fun.fun)] = computed_fun

    def _id(self, fun):
        return ComputedFunction.id_from_fun(fun)
