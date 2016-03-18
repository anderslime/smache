import dagger
import os


def draw_graph(nodes, filename):
    dag = dagger.dagger()
    _recursive_add(dag, nodes)
    dag.run()
    dotfile = "{}.dot".format(filename)
    dag.dot(dotfile)
    os.system("dot -Tpng {} > {}.png".format(dotfile, filename))


def _recursive_add(dag, nodes):
    for node in nodes:
        parent_values = [parent.id for parent in node.parents]
        dag.add(node.id, parent_values)
