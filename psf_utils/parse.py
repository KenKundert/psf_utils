"""
Parse ASCII PSF Files
"""

# Imports {{{1
import ply.lex, ply.yacc
from inform import Info, is_str, is_mapping


# Globals {{{1
Filename = None


# Utility classes {{{1
class Type(Info):
    pass

class Struct(Info):
    pass

class Sweep(Info):
    pass

class Trace(Info):
    pass

# Exceptions {{{1
# ParseError {{{2
class ParseError(Exception):
    def __init__(self, text, loc=None):
        self.text = text
        self.loc = loc

    def __str__(self):
        "Return a formatted error message."
        if self.loc:
            return self.loc.message(Filename, self.text)
        if Filename:
            return "%s: %s" % (Filename, self.text)
        return self.text


# Record the location of a token {{{2
class TokenLocation(object):
    def __init__(self, token, index=None):
        "Records information about the location of a token."
        lexdata = token.lexer.lexdata
        if index:
            lexpos = token.lexpos(index)
        else:
            lexpos = token.lexpos
        bol = lexdata.rfind('\n', 0, lexpos) + 1
        if bol < 0:
            bol = 0
        eol = lexdata.find('\n', lexpos)
        if eol < 0:
            eol = len(lexdata)
        self.line = lexdata[bol:eol]
        self.col = (lexpos - bol)
        self.row = lexdata[0:lexpos].count('\n') + 1

    def annotateLine(self, prefix=None):
        """
        Produces a two or three line result, possibly a prefix, then the line 
        that contains the token, and then a pointer to the token.  If a prefix 
        is given, it will be printed before the line and will be separated from 
        the line by ': '.  Generally the prefix contains the filename and line 
        number.
        """
        if prefix:
            return "%s\n    %s\n    %s^" % (
                prefix
              , self.line
              , self.col*' '
            )
        return "%s\n%s^" % (self.line, (self.col-1)*' ')

    def message(self, filename, msg):
        """
        Produces a message about the token.  The line containing the token is
        shown, along with a pointer to the token.  Finally the message is
        returned.
        """
        #if self.row:
        #    loc = "%s.%s" % (self.row, self.col)
        if self.row:
            loc = "%s" % (self.row)
        else:
            loc = ""
        if filename:
            loc = "%s(%s)" % (filename, loc)
        if loc:
            return self.annotateLine("%s: %s" % (loc, msg))
        return self.annotateLine(msg)

# Lexer {{{1
# List of the token names
reserved = {
    'HEADER'  : 'HEADER',
    'TYPE'    : 'TYPE',
    'SWEEP'   : 'SWEEP',
    'TRACE'   : 'TRACE',
    'VALUE'   : 'VALUE',
    'FLOAT'   : 'FLOAT',
    'COMPLEX' : 'COMPLEX',
    'DOUBLE'  : 'DOUBLE',
    'STRUCT'  : 'STRUCT',
    'PROP'    : 'PROP',
    'END'     : 'END',
}
tokens = [
    'INTEGER',
    'REAL',
    'STRING',
] + list(reserved.values())

# Literal tokens
literals = r'()'

# Regular expression tokens
# Regular expressions that define numbers
t_INTEGER = r"-?[0-9]+"
t_REAL = r"[+-]?[0-9]+\.[0-9]*([eE][+-][[0-9]+)?"

# Regular expression for a string
t_STRING = r'"[^\\\n"]*"'

# Identifiers
def t_ID(t):
    r'[A-Z]+'
    t.type = reserved.get(t.value, 'ID')    # check for reserved words
    return t

# ignore whitespace
t_ignore = ' \t\n'

def t_error(t):
    c = t.value[0]
    loc = TokenLocation(t)
    t.lexer.skip(1)
    raise ParseError("illegal character '%s'." % c, loc)

# Parser {{{1
def p_contents(p):
    "contents : header_section type_section sweep_section trace_section value_section end"
    p[0] = (p[1], p[2], p[3], p[4], p[5])

def p_header_section(p):
    "header_section : HEADER named_values"
    p[0] = dict(p[2])

def p_named_values(p):
    "named_values : named_values named_value"
    p[1].append(p[2])
    p[0] = p[1]

def p_named_values_last(p):
    "named_values : named_value"
    p[0] = [p[1]]

def p_named_value(p):
    "named_value : string value"
    p[0] = (p[1], p[2])

def p_string_value(p):
    "value : string"
    p[0] = p[1]

def p_integer_value(p):
    "value : INTEGER"
    p[0] = int(p[1])

def p_real_value(p):
    "value : REAL"
    p[0] = float(p[1])

def p_string(p):
    "string : STRING"
    p[0] = p[1][1:-1]

def p_type_section(p):
    "type_section : TYPE types"
    p[0] = dict(p[2])

def p_types(p):
    "types : types type"
    p[1].append(p[2])
    p[0] = p[1]

def p_types_last(p):
    "types : type"
    p[0] = [p[1]]

def p_type(p):
    "type : string kinds"
    n = p[1]
    meta = {}
    kind = ' '.join(s for s in p[2] if is_str(s)).lower()
    if kind:
        meta['kind'] = kind
    for each in p[2]:
        if is_mapping(each):
            meta.update(each)
        elif isinstance(each, Struct):
            meta['struct'] = each
    p[0] = (n, Type(name=n, **meta))

def p_kinds(p):
    "kinds : kinds kind"
    p[1].append(p[2])
    p[0] = p[1]

def p_kinds_last(p):
    "kinds : kind"
    p[0] = [p[1]]

def p_kind(p):
    """
        kind : FLOAT
             | DOUBLE
             | COMPLEX
             | struct
             | prop
    """
    p[0] = p[1]

def p_struct(p):
    "struct : STRUCT '(' types ')'"
    p[0] = Struct(types=dict(p[3]))

def p_prop(p):
    "prop : PROP '(' named_values ')'"
    p[0] = dict(p[3])

def p_sweep_section(p):
    "sweep_section : SWEEP sweeps"
    p[0] = p[2]

def p_sweeps(p):
    "sweeps : sweeps sweep"
    p[1].append(p[2])
    p[0] = p[1]

def p_sweeps_last(p):
    "sweeps : sweep"
    p[0] = [p[1]]

def p_sweep(p):
    "sweep : string string kinds"
    p[0] = Sweep(name=p[1], type=p[2], **p[3][0])

def p_trace_section(p):
    "trace_section : TRACE traces"
    p[0] = p[2]

def p_traces(p):
    "traces : traces trace"
    p[1].append(p[2])
    p[0] = p[1]

def p_traces_last(p):
    "traces : trace"
    p[0] = [p[1]]

def p_trace(p):
    "trace : named_value"
    name, type = p[1]
    p[0] = Trace(name=name, type=type)

def p_value_section(p):
    "value_section : VALUE values"
    values = {}
    for n, v in p[2]:
        if n not in values:
            values[n] = []
        values[n].append(v)
    p[0] = values

def p_values(p):
    "values : values named_signal_value"
    p[1].append(p[2])
    p[0] = p[1]

def p_values_last(p):
    "values : named_signal_value"
    p[0] = [p[1]]

def p_named_signal_scalar(p):
    "named_signal_value : string number"
    p[0] = (p[1], p[2])

def p_named_signal_group(p):
    "named_signal_value : string '(' numbers ')'"
    p[0] = (p[1], tuple(p[3]))

def p_integer_number(p):
    "number : INTEGER"
    p[0] = int(p[1])

def p_reals_number(p):
    "number : REAL"
    p[0] = float(p[1])

def p_numbers(p):
    "numbers : numbers number"
    p[1].append(p[2])
    p[0] = p[1]

def p_numbers_last(p):
    "numbers : number"
    p[0] = [p[1]]

def p_end(p):
    "end : END"


# Error rule for syntax errors
def p_error(p):
    if p:
        loc = TokenLocation(p)
        raise ParseError("syntax error at '%s'." % (p.value), loc)
    else:
        raise ParseError("premature end of content.")

# ParsePSF class {{{1
class ParsePSF:
    def __init__(self):
        self.lexer = ply.lex.lex(
            debug = False,
            optimize = True,
        )
        self.parser = ply.yacc.yacc(
            debug = False,
            optimize = True,
            method = "SLR",
        )

    def parse(self, filename, content):
        global Filename
        Filename = filename

        result = self.parser.parse(content, tracking=False, lexer=self.lexer)
        return result


