import inspect
import pycparser
import cairocffi

ALL_THE_CODE = ''.join(
    line
    for module in [
        cairocffi, cairocffi.surfaces, cairocffi.patterns, cairocffi.context]
    for line in inspect.getsourcelines(module)[0])


class Visitor(pycparser.c_ast.NodeVisitor):
    def visit_Decl(self, node):
        for _, child in node.children():
            if isinstance(child, pycparser.c_ast.FuncDecl):
                if ('cairo.' + node.name) not in ALL_THE_CODE:
                    print(node.name)
                break

print('cairo functions never used in cairocffi:\n')
Visitor().visit(pycparser.CParser().parse(cairocffi._CAIRO_HEADERS))
