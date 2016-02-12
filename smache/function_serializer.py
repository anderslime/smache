import json

class FunctionSerializer:
    seperator_token = '~~~'

    def serialized_fun(self, entity_deps, fun, *args, **kwargs):
        args = self._serialized_args(args, entity_deps)
        elements = [json.dumps(fun.__name__)] + args
        return reduce(lambda x, y: x + self.seperator_token + y, elements)

    def _serialized_args(self, arguments, entity_deps):
        return [self._serialized_arg(argument, index, entity_deps) for index, argument in enumerate(arguments)]

    def _serialized_arg(self, argument, argument_index, entity_deps):
        if argument_index < len(entity_deps):
            return json.dumps(argument.id)
        else:
            return json.dumps(argument)

    def deserialized_fun(self, fun_key):
        elements = fun_key.split(self.seperator_token)
        deserialized_fun_name = json.loads(elements[0])
        deserialized_args = [json.loads(element) for element in elements[1:]]
        return deserialized_fun_name, deserialized_args
