import ply.lex as lex   #  Lex = Lexer-generator 
import ply.yacc as yacc # Yacc = Parser-generator
import sys


reserved = {
    'begin'     : 'BEGIN',
    'end'       : 'END',
    'var'       : 'VAR',
    'proc'      : 'PROC',
    'inout'     : 'INOUT',
    'in'        : 'IN',
    'out'       : 'OUT',
    'return'    : 'RETURN',
    'exit'      : 'EXIT',
    'if'        : 'IF',
    'goto'      : 'GOTO',
    'read'      : 'READ',
    'println'   : 'PRINTLN',
    'print'     : 'PRINT',
    'call'      : 'CALL',
}

labels = []

# tokens = ['NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'COMP', 'EQUALS', 'LPAREN', 'RPAREN', 'ID', 'LABEL', 'COMMENT', 'DLABEL'] + list(reserved.values())

tokens = ['SEMICOLON', 'ID', 'COMMA', 'DLABEL', 'EQUALS', 'LABEL', 'STRING', 'LEQ', 'LESSER', 'GEQ', 'GREATER', 'NEQ', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'NUM', 'LPAREN', 'RPAREN'] + list(reserved.values())

'''
List of tokens:

(Reserved Tokens)

BEGIN 		-> begin 	-> r'begin'  
END 		-> end		-> r'end'
VAR 		-> var		-> r'var'
PROC 		-> proc		-> r'proc'
INOUT 		-> inout	-> r'\inout'
IN 			-> in		-> r'\in'
OUT 		-> out		-> r'\out'
RETURN 		-> return	-> r'\return'
EXIT 		-> exit		-> r'\exit'
IF 			-> if		-> if
GOTO 		-> goto		-> 
READ 		-> read		-> 
PRINTLN 	-> println 	->
PRINT 		-> print 	->
CALL 		-> call		-> 


(Other Tokens)

SEMICOLON 	-> ;		-> r'\;'
ID 			-> id		-> r'[a-zA-Z][a-zA-Z_0-9]*'
COMMA 		-> ,		-> r'\,'
DLABEL 		-> dlabel	-> r'[a-zA-Z][a-zA-Z_0-9]*:'
EQUALS 		-> = 		-> r'\='
LABEL 		-> label	-> 
STRING 		-> string	-> r'\".*\"'
LEQ 		-> <=		-> 
LESSER 		-> <
GEQ 		-> >=
GREATER 	-> >
NEQ 		-> <>
PLUS 		-> +
MINUS 		-> -
MULTIPLY 	-> *
DIVIDE 		-> /
NUM 		-> num
LPARAN 		-> (
RPARAN 		-> )
'''

# ========== Regular expression rules for simple tokens ==========
t_PLUS      = r'\+'
t_MINUS     = r'\-'
t_MULTIPLY  = r'\*'
t_DIVIDE    = r'\/'
t_EQUALS    = r'\='
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_SEMICOLON = r'\;'
t_COMMA     = r'\,'
t_LEQ       = r'\<\='
t_LESSER    = r'\<'
t_GEQ       = r'\>\='
t_GREATER   = r'\>'
t_NEQ       = r'\<\>'

# ========== Regular expression for tokens to be ignored ==========

# ---------------------------------------------------------------


# ========== Regular expression rules with some action code ==========
def t_STRING(t):
    r'\".*\"'
    t.value = (t.value)[1:-1] # removing the double quotes
    return t
    
def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_DLABEL(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*.:'
    t.value = t.value[:-1]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    reserved_token = reserved.get(t.value)
    if(reserved_token):             # if t.value is a reserved token
        t.type = reserved_token
    elif(t.value in set(labels)):   # if t.value is a label
        t.type = 'LABEL'
    else:                      
        t.type = 'ID'
    return t

def t_newline(t):   # to keep track of line numbers
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore            = ' \t'     # tabs
t_ignore_COMMENT    = r'\%.*'   # comments

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)






# ======================= End of Token Definitions ======================= 

# ==========================================
# Building the lexer and start analysing
# ==========================================


# Build the lexer
lexer = lex.lex()

# Testing (you can use triple quotes as a string)
data = ''' var a,b;
var c;
% following procedure ensures that x<= y on return
proc order(inout x, inout y)
var t;
if x < y goto done;
t= x+0;
x = y+0;
y = t+0;
done:
return;
begin
print "enter two numbers ";
println;
read a ;
read b ;
call order(a,b);
%now a <= b
c=b/a ;
c = c*a ;
c = b - c ;
print "absolute mod is " ;
print c;
println ;
exit ;
end
'''


# data = "print \"enter two numbers\";"
def get_labels(data):
    for s in data:
        if(s[-1] == ':'):
            labels.append(s[:-1])

get_labels(data.split())
# Give the lexer some input
lexer.input(data)

# # Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)     # Prints in the following format: TYPE OF TOKEN + VALUE + LINE NUMBER + LINE POSITION



# ======================= End of Lexical Analysis  ======================= 

# ==========================================
# Building the parser
# ==========================================

# Get the token map from the lexer.  
# from calclex import tokens (UNCOMMENT THIS LINE ONLY IF YOUR LEXER IS IN A DIFFERENT FILE)

# Get the token map from the lexer.  This is required.