# coding: utf-8

import inspect
import pycparser
import cairocffi

ALL_THE_CODE = ''.join(
    line
    for module in [
        cairocffi, cairocffi.surfaces, cairocffi.patterns,
        cairocffi.fonts, cairocffi.context, cairocffi.matrix]
    for line in inspect.getsourcelines(module)[0])


class Visitor(pycparser.c_ast.NodeVisitor):
    def visit_Decl(self, node):
        for _, child in node.children():
            if isinstance(child, pycparser.c_ast.FuncDecl):
                if ('cairo.' + node.name) not in ALL_THE_CODE and not (
                        node.name.endswith('user_data')):
                    print(node.name)
                break

print('cairo functions never used in cairocffi:\n')
Visitor().visit(pycparser.CParser().parse(cairocffi.constants._CAIRO_HEADERS))
