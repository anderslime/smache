import json
from functools import reduce


class FunctionSerializer:
    seperator_token = '~~~'

    def serialized_fun(self, computed_fun, *args, **kwargs):
        args = self._serialized_args(args, computed_fun.arg_deps)
        elements = [json.dumps(computed_fun.id)] + args
        return reduce(lambda x, y: x + self.seperator_token + y, elements)

    def deserialized_fun(self, fun_key):
        elements = fun_key.split(self.seperator_token)
        return self._fun_name(elements), self._deserialized_args(elements)

    def fun_name(self, fun_key):
        elements = fun_key.split(self.seperator_token)
        return json.loads(elements[0])

    def _fun_name(self, elements):
        return json.loads(elements[0])

    def _deserialized_args(self, elements):
        return [json.loads(element) for element in elements[1:]]

    def _serialized_args(self, arguments, arg_types):
        return [self._serialized_arg(argument, arg_type)
                for argument, arg_type in zip(arguments, arg_types)]

    def _serialized_arg(self, argument, arg_type):
        return json.dumps(arg_type.serialize(argument))
