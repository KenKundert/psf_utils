"""
Parse ASCII PSF Files
"""

# License {{{1
# Copyright (C) 2016-2023 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.


# Imports {{{1
import ply.lex
import ply.yacc
from inform import Info, is_str, is_mapping
import numpy as np


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


class Traces(Info):
    pass


class Value(Info):
    pass


class Array(Info):
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
                prefix,
                self.line,
                self.col*' '
            )
        return "%s\n%s^" % (self.line, (self.col-1)*' ')

    def message(self, filename, msg):
        """
        Produces a message about the token.  The line containing the token is
        shown, along with a pointer to the token.  Finally the message is
        returned.
        """
        # if self.row:
        #     loc = "%s.%s" % (self.row, self.col)
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
# Reserved name tokens {{{2
reserved = {rw: rw for rw in [
    'ARRAY',
    'BYTE',
    'COMPLEX',
    'DOUBLE',
    'END',
    'FLOAT',
    'GROUP',
    'HEADER',
    'INT',
    'LONG',
    'NAN',
    'PROP',
    'SINGLE',
    'STRING',
    'STRUCT',
    'SWEEP',
    'TRACE',
    'TYPE',
    # 'VALUE',  # Removed to handle manually
]}
tokens = [
    'INTEGER',
    'REAL',
    'QUOTED_STRING',
    'VALUE',
    'FAST_VALUES',
] + list(reserved.values())

# Literal tokens {{{2
literals = r'()*'

# Number tokens {{{2
t_INTEGER = r"-?[0-9]+"
real_w_fract = r"[+-]?[0-9]+\.[0-9]*([eE][+-][0-9]+)?"
real_w_exp = r"[+-]?[0-9]+(\.[0-9]*)?[eE][+-][0-9]+"
t_REAL = f'({real_w_fract})|({real_w_exp})'


# NaN must be given as a function rather than a simple string.
# Doing so causes Ply to give it priority over keyword recognition
# because it is defined first.
def t_NAN(t):
    r"nan|NaN|inf"
    t.value = float(t.value)
    return t


# String tokens {{{2
t_QUOTED_STRING = r'"([^\\\n"]|(\\.))*"'
    # The complexity is because of the case "He yelled \"You are a fool!\".".
    # The first part says string cannot contain a backslash, newline, or a
    # quote. The second case allows backslashes when combined with any other
    # character, which allows \" and \\.

# Special handling for VALUE to enable fast reading
def t_VALUE(t):
    r'VALUE'
    # Try to fast read the entire section
    # Look ahead for END
    lexdata = t.lexer.lexdata
    lexpos = t.lexer.lexpos
    
    # First, check if there are GROUP traces in the TRACE section
    # TRACE section comes before VALUE
    trace_start = lexdata.rfind('TRACE', 0, lexpos)
    if trace_start != -1:
        trace_section = lexdata[trace_start:lexpos]
        if 'GROUP' in trace_section:
            # GROUP traces have different VALUES format, can't fast parse
            t.type = 'VALUE'
            return t
    
    end_idx = lexdata.find('END', lexpos)
    
    if end_idx != -1:
        # Check if the content between VALUE and END is "simple"
        # i.e. no composite values (parentheses)
        
        section_content = lexdata[lexpos:end_idx]
        
        # Heuristic: if '(' is present, fallback to slow parsing
        # This handles complex/composite values
        if '(' in section_content:
             t.type = 'VALUE'
             return t
             
        # Try fast parsing with numpy
        try:
            tokens_list = section_content.split()
            if not tokens_list:
                t.type = 'VALUE'
                return t
                
            # Identify signals
            # "name" value "name" value ...
            # Find cycle length
            if len(tokens_list) < 2:
                 t.type = 'VALUE'
                 return t
                 
            first_name = tokens_list[0]
            cycle_len = 0
            for i in range(2, len(tokens_list), 2):
                if tokens_list[i] == first_name:
                    cycle_len = i // 2
                    break
            
            if cycle_len == 0:
                 t.type = 'VALUE'
                 return t
            
            names = [tok.strip('"') for tok in tokens_list[0:cycle_len*2:2]]
            
            total_tokens = len(tokens_list)
            num_rows = total_tokens // (2 * cycle_len)
            
            if num_rows == 0:
                t.type = 'VALUE'
                return t
                
            # Truncate to full cycles
            tokens_list = tokens_list[:num_rows * 2 * cycle_len]
            
            # Convert to numpy array
            # This is the critical speedup
            values = np.array(tokens_list[1::2], dtype=float)
            data = values.reshape((num_rows, cycle_len))
            
            # Success!
            # Return FAST_VALUES token
            t.type = 'FAST_VALUES'
            t.value = (names, data)
            
            # Update lexer position to skip the consumed content
            # We consumed up to end_idx.
            # But we didn't consume 'END'.
            # So lexpos should be end_idx.
            t.lexer.lexpos = end_idx
            
            return t
            
        except Exception:
            # Fallback on any error
            t.type = 'VALUE'
            return t
            
    t.type = 'VALUE'
    return t


# Identifier tokens {{{2
def t_ID(t):
    r'[A-Z]+'
    t.type = reserved.get(t.value)
    if t.type is None:
        loc = TokenLocation(t)
        t.lexer.skip(1)
        raise ParseError(f"unknown keyword '{t.value}'.", loc)
    return t


# Whitespace {{{2
# ignore whitespace
t_ignore = ' \t\n'


# Error {{{2
def t_error(t):
    c = t.value[0]
    loc = TokenLocation(t)
    t.lexer.skip(1)
    raise ParseError("illegal character '%s'." % c, loc)


# Parser rules {{{1
def p_contents(p):
    "contents : header_section type_section sweep_section trace_section value_section end"
    p[0] = (p[1], p[2], p[3], p[4], p[5])


def p_contents_without_sweep(p):
    "contents : header_section type_section value_section end"
    p[0] = (p[1], p[2], None, None, p[3])


def p_contents_only_header(p):
    "contents : header_section end"
    p[0] = (p[1], {}, None, None, {})


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
    """
    value : REAL
          | NAN
    """
    p[0] = float(p[1])


def p_string(p):
    "string : QUOTED_STRING"
    p[0] = (p[1][1:-1]).replace('\\', '')


def p_star(p):
    "star : '*'"
    p[0] = p[1]


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
             | INT
             | BYTE
             | LONG
             | SINGLE
             | STRING
             | array
             | struct
             | prop
             | star
    """
    p[0] = p[1]


def p_struct(p):
    "struct : STRUCT '(' types ')'"
    p[0] = Struct(types=dict(p[3]))


def p_array(p):
    "array : ARRAY '(' star ')'"
    p[0] = Array(members=p[3])


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
    # Partition out the groups from the traces.
    # A group will have one entry in the list of traces, and it will have a
    # corresponding entry in the groups directory.  The entry is also a
    # dictionary that maps the member name to the member type.
    traces = []
    groups = {}
    index = None
    for trace in p[2]:
        name = trace.name
        try:
            count = int(trace.type)
            index = 0
            group_name = name
            groups[group_name] = {}
            trace.type = 'GROUP'
            traces.append(trace)
            continue
        except ValueError:
            pass
        if index is None:
            traces.append(trace)
        else:
            groups[group_name][trace.name] = trace.type
            index += 1
            if index == count:
                index = None
    p[0] = (traces, groups)


def p_traces(p):
    "traces : traces trace"
    p[1].append(p[2])
    p[0] = p[1]


def p_traces_last(p):
    "traces : trace"
    p[0] = [p[1]]


def p_traces_empty(p):
    "traces : "
    p[0] = []


def p_trace(p):
    "trace : named_value"
    name, type = p[1]
    p[0] = Trace(name=name, type=type)


def p_group_trace(p):
    "trace : string GROUP INTEGER"
    name = p[1]
    count = p[3]
    p[0] = Trace(name=name, type=count)


def p_trace_with_props(p):
    "trace : named_value prop"
    # some psf files place a units property on terminal current traces,
    # but the information seems redundant and can be ignored.
    name, type = p[1]
    p[0] = Trace(name=name, type=type)


def p_value_section(p):
    "value_section : VALUE values"
    p[0] = p[2]

def p_value_section_fast(p):
    "value_section : FAST_VALUES"
    names, data = p[1]
    values = {}
    
    # Construct values dict
    # We need to handle escaped names here too?
    # The names come from fast reader which might have escapes.
    # But standard parser unescapes strings in p_string.
    # So we should probably unescape here to match standard parser output.
    
    for i, name in enumerate(names):
        clean_name = name.replace('\\', '')
        col = data[:, i]
        # Wrap in Value object. 
        # Note: Standard parser produces Value(type=..., values=[list])
        # We produce Value(values=numpy_array, is_fast=True)
        # We don't have type info here, but __init__ handles that.
        values[clean_name] = Value(values=col, is_fast=True)
        
    p[0] = values


def p_values(p):
    "values : values signal_value"
    if p[2][0] not in p[1]:
        p[1][p[2][0]] = Value(type=p[2][1], values=[p[2][2]])
    else:
        p[1][p[2][0]].values.append(p[2][2])
    p[0] = p[1]


def p_values_last(p):
    "values : signal_value"
    p[0] = {p[1][0]: Value(type=p[1][1], values=[p[1][2]])}


def p_named_signal_scalar(p):
    """
    signal_value : string numbers
    """
    p[0] = (p[1], None, p[2])


def p_named_signal_with_type(p):
    """
    signal_value : string string numbers
    """
    p[0] = (p[1], p[2], p[3])


def p_named_string_signal_with_type(p):
    """
    signal_value : string string string
    """
    p[0] = (p[1], p[2], p[3])


def p_numbers(p):
    "numbers : numbers number"
    p[1].append(p[2])
    p[0] = p[1]


def p_last_number(p):
    "numbers : number"
    p[0] = [p[1]]


def p_number(p):
    """
    number : simple_number
           | composite_number
    """
    p[0] = p[1]


def p_integer_number(p):
    "simple_number : INTEGER"
    p[0] = int(p[1])


def p_real_number(p):
    # props are redundant, so ignore them
    """
    simple_number : REAL
                  | REAL prop
                  | NAN
                  | NAN prop
    """
    p[0] = float(p[1])


def p_composite_number(p):
    """
    composite_number : '(' numbers ')'
                     | '(' numbers ')' prop
    """
    p[0] = tuple(p[2])


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
        self.lexer = ply.lex.lex()
        self.parser = ply.yacc.yacc(write_tables=False, debug=False)

    def parse(self, filename, content):
        global Filename
        Filename = filename

        result = self.parser.parse(content, tracking=False, lexer=self.lexer)
        return result
