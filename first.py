import streamlit as st
import ply.lex as lex
import ply.yacc as yacc

# Reserved keywords
reserved = {
    'IF': 'IF',
    'THEN': 'THEN',
    'ELSE': 'ELSE',
    'ELIF': 'ELIF',
    'FOR': 'FOR',
    'TO': 'TO',
    'WHILE': 'WHILE',
    'greater': 'GREATER_THAN',
    'less': 'LESS_THAN',
    'equals': 'EQUALS',
    'PRINT': 'PRINT',
    'END': 'END',
}

# Tokens
tokens = [
    'IDENTIFIER', 'NUMBER', 'ASSIGN', 'PLUS', 'MINUS', 'STRING'
] + list(reserved.values())

# Token definitions
t_ASSIGN = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_ignore = ' \t'  # Ignore spaces and tabs

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\".*?\"'
    t.value = t.value.strip('"')  # Remove the quotes
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_error(t):
    st.error(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

precedence = (
    ('left', 'PLUS', 'MINUS'),
)

def p_program(p):
    'program : statement_list'
    p[0] = p[1]

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]}\n{p[2]}"

def p_statement(p):
    '''statement : if_statement
                 | assign_statement
                 | for_statement
                 | while_statement
                 | print_statement'''
    p[0] = p[1]

def p_if_statement(p):
    '''if_statement : IF expression THEN statement_list END
                    | IF expression THEN statement_list ELSE statement_list END
                    | IF expression THEN statement_list ELIF expression THEN statement_list END'''
    if len(p) == 6:
        p[0] = f"if {p[2]}:\n    {p[4]}"
    elif len(p) == 8:
        p[0] = f"if {p[2]}:\n    {p[4]}\nelse:\n    {p[6]}"
    else:
        p[0] = f"if {p[2]}:\n    {p[4]}\nelif {p[6]}:\n    {p[8]}"

def p_assign_statement(p):
    'assign_statement : IDENTIFIER ASSIGN expression'
    p[0] = f"{p[1]} = {p[3]}"

def p_for_statement(p):
    'for_statement : FOR IDENTIFIER ASSIGN NUMBER TO NUMBER THEN statement_list END'
    p[0] = f"for {p[2]} in range({p[4]}, {p[6]} + 1):\n    {p[8]}"

def p_while_statement(p):
    'while_statement : WHILE expression THEN statement_list END'
    p[0] = f"while {p[2]}:\n    {p[4]}"

def p_print_statement(p):
    'print_statement : PRINT expression'
    p[0] = f"print({p[2]})"

def p_expression_comparison(p):
    '''expression : IDENTIFIER GREATER_THAN NUMBER
                  | IDENTIFIER LESS_THAN NUMBER
                  | IDENTIFIER EQUALS NUMBER'''
    if p[2] == 'greater':
        p[0] = f"{p[1]} > {p[3]}"
    elif p[2] == 'less':
        p[0] = f"{p[1]} < {p[3]}"
    elif p[2] == 'equals':
        p[0] = f"{p[1]} == {p[3]}"

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression'''
    p[0] = f"({p[1]} {p[2]} {p[3]})"

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = str(p[1])

def p_expression_identifier(p):
    'expression : IDENTIFIER'
    p[0] = p[1]

def p_expression_string(p):
    'expression : STRING'
    p[0] = f'"{p[1]}"'

def p_error(p):
    st.error("Syntax error in input!")

parser = yacc.yacc()

# Streamlit UI
st.title("English-like Algorithm to Python Code Converter")
st.write("Enter an English-like algorithm and get the corresponding Python code.")

input_data = st.text_area("Enter your algorithm:", height=200)

if st.button("Convert"):
    if input_data.strip():
        lexer.input(input_data)
        tokens_output = []
        for token in lexer:
            tokens_output.append(str(token))
        
        st.subheader("Tokens:")
        st.write(tokens_output)

        st.subheader("Generated Python Code:")
        try:
            parsed_output = parser.parse(input_data)
            st.code(parsed_output, language='python')
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter some input!")
