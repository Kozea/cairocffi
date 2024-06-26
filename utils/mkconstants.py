import os
import re
import sys
import textwrap

import pycparser.c_generator


def parse_constant(node):
    if isinstance(node, pycparser.c_ast.Constant):
        return node.value
    elif isinstance(node, pycparser.c_ast.UnaryOp) and node.op == '-':
        return '-' + parse_constant(node.expr)
    else:
        raise TypeError(node)


class PrintEnumsVisitor(pycparser.c_ast.NodeVisitor):
    def visit_Decl(self, node):  # noqa: N802
        if node.name and node.name.startswith('CAIRO_'):  # len('CAIRO_') == 6
            if node.init.type == 'string':
                print('%s = b%s' % (node.name[6:], node.init.value))
            else:
                print('%s = %s' % (node.name[6:], node.init.value))
            print('')

    def visit_Enum(self, node):  # noqa: N802
        value = 0
        for enumerator in node.values.enumerators:
            if enumerator.value is not None:
                value_string = parse_constant(enumerator.value)
                value = int(value_string, 0)
            else:
                value_string = str(value)
            assert enumerator.name.startswith('CAIRO_')  # len('CAIRO_') == 6
            print('%s = %s' % (enumerator.name[6:], value_string))
            value += 1
        print('')


def read_cairo_header(cairo_git_dir, suffix):
    filename = os.path.join(cairo_git_dir, 'src', 'cairo%s.h' % suffix)
    source = open(filename, encoding='iso-8859-1').read()
    source = re.sub(
        '/\\*.*?\\*/'
        '|CAIRO_(BEGIN|END)_DECLS'
        '|cairo_public '
        r'|^\s*#.*?[^\\]\n',
        '',
        source,
        flags=re.DOTALL | re.MULTILINE)
    source = re.sub('\n{3,}', '\n\n', source)
    return source


def generate(cairo_git_dir):
    # Remove comments, preprocessor instructions and macros.
    source = read_cairo_header(cairo_git_dir, '')

    source += 'const int CAIRO_PDF_OUTLINE_ROOT = 0;\n'
    source += read_cairo_header(cairo_git_dir, '-pdf')

    source += read_cairo_header(cairo_git_dir, '-ps')

    source += read_cairo_header(cairo_git_dir, '-svg')

    source += '''
        typedef void* HDC;
        typedef void* HFONT;
        typedef void LOGFONTW;
    '''
    source += read_cairo_header(cairo_git_dir, '-win32')

    source += '''
        typedef void* CGContextRef;
        typedef void* CGFontRef;
        typedef void* ATSUFontID;
    '''
    source += read_cairo_header(cairo_git_dir, '-quartz')

    ast = pycparser.CParser().parse(source)

    print(textwrap.dedent('''\
        # *** Do not edit this file ***
        # Generated by utils/mkconstants.py
        # flake8: noqa

        TAG_DEST = b"cairo.dest"
        TAG_LINK = b"Link"\n'''))
    PrintEnumsVisitor().visit(ast)
    print('_CAIRO_HEADERS = r"""%s"""' % source)

    source = read_cairo_header(cairo_git_dir, '-xcb')
    print('_CAIRO_XCB_HEADERS = r"""%s"""' % source)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        generate(sys.argv[1])
    else:
        print('Usage: %s path/to/cairo_source.git' % sys.argv[0])
