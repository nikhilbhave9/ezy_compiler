import ply.lex as lex   #  Lex = Lexer-generator 
import ply.yacc as yacc # Yacc = Parser-generator
import sys

# Reserved KEYWORDS (# -- => doubtful) 
# Possible additions: GOTO, CALL, READ, PRINT VARIABLE, PRINT STRING, PRINT LN
reserved = {
   'if' : 'IF',
   # 'then' : 'THEN', (don't need)
   'else' : 'ELSE',
   'while' : 'WHILE',
   'return' : 'RETURN',
   'proc' : 'PROC', # --
   'exit' : 'EXIT', # --
   'var' : 'VAR', # --
   'in' : 'IN',
   'out' : 'OUT',
   'inout' : 'INOUT',
}

# List of token names 
# Tokens still to be added: COMMA, COLON
tokens = (
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'COMP',
   'EQUALS',
   'LPAREN',
   'RPAREN',
   'ID',
   'LABEL', # Might have to re-order 
   #'MODE', # --
)

# tokens = [] + list(reserved.values())

# Regular expression rules for simple tokens
# ==========================================
t_PLUS    = r'\+'
t_MINUS   = r'\-'
t_TIMES   = r'\*'
t_DIVIDE  = r'\/'
t_COMP    = r'\=\='
t_EQUALS  = r'\='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'

# Regular expression string containing ignored characters (spaces and tabs)
# ==========================================
t_ignore  = ' \t'

# Regular expression rules with some action code
# ==========================================
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Define a rule for identifiers
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID') 
    # .get() method is called on a dictionary to get the value of given key ()
    # First parameter is the key
    # Second parameter is optional. It returns a value if key doesn't exist
    return t

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# ======================= End of Token Definitions ======================= 

# ==========================================
# Building the lexer and start parsing
# ==========================================


# Build the lexer
lexer = lex.lex()

# Testing (you can use triple quotes as a string)
data = "20 = 30 + 40 == 50"

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    print(tok)     # Prints in the following format: TYPE OF TOKEN + VALUE + LINE NUMBER + LINE POSITION