import json
from functools import reduce
import pickle


class FunctionSerializer:
    seperator_token = '~~~'
    kwargs_seperator_token = '***'

    def serialized_fun(self, computed_fun, *args, **kwargs):
        args = self._serialized_args(args, computed_fun.arg_deps)
        kwargs = self._serialized_kwargs(kwargs)
        elements = [json.dumps(computed_fun.id)] + args
        return reduce(lambda x, y: x + self.seperator_token + y, elements) + \
            kwargs

    def deserialized_fun(self, fun_key):
        rest, kwargs = self._split_kwargs_from_rest(fun_key)
        elements = rest.split(self.seperator_token)
        return self._fun_name(elements), \
            self._deserialized_args(elements), \
            kwargs

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

    def _serialized_kwargs(self, kwargs):
        if kwargs == {}:
            return ''
        return self.kwargs_seperator_token + pickle.dumps(kwargs)

    def _deserialized_kwargs(self, kwargs):
        return pickle.loads(kwargs)

    def _serialized_arg(self, argument, arg_type):
        return json.dumps(arg_type.serialize(argument))

    def _split_kwargs_from_rest(self, fun_key):
        elements = fun_key.split(self.kwargs_seperator_token)
        if len(elements) > 1:
            return elements[0], pickle.loads(elements[1])
        else:
            return elements[0], {}
