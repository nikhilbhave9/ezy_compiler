import lexical_analyser
from lexical_analyser import tokens
from lexical_analyser import lexer
import ply.lex as lex
import ply.yacc as yacc
import sys

# Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)     # Prints in the following format: TYPE OF TOKEN + VALUE + LINE NUMBER + LINE POSITION

start = 'prog'

def p_prog(p):
    '''
    prog    : vardecls procdecls BEGIN stmtlist END
    '''

def p_empty(p):
    'empty  :'
    pass

def p_vardecls(p):
    '''
    vardecls    : vardecl vardecls
                | empty
    '''

def p_vardecl(p):
    '''
    vardecl : VAR varlist SEMICOLON
    '''

def p_varlist(p):
    '''
    varlist : ID COMMA varlist
            | ID
    '''

def p_procdecls(p):
    '''
    procdecls   : procdecl procdecls
                | empty
    '''

def p_procdel(p):
    '''
    procdecl    : PROC ID LPAREN paramlist RPAREN vardecls pstmtlist
    '''

def p_paramlist(p):
    '''
    paramlist   : tparamlist
                | empty
    '''

def p_tparamlist(p):
    '''
    tparamlist  : param COMMA tparamlist
                | param
    '''

def p_param(p):
    '''
    param   : mode ID
    '''

def p_mode(p):
    '''
    mode    : IN
            | OUT
            | INOUT
    '''
    
def p_pstmtlist(p):
    '''
    pstmtlist   : pstmt pstmtlist
                | pstmt
    '''

def p_stmtlist(p):
    '''
    stmtlist    : mstmt stmtlist
                | mstmt
    '''

def p_pstmt(p):
    '''
    pstmt   : DLABEL
            | stmt SEMICOLON
            | RETURN SEMICOLON
    '''

def p_mstmt(p):
    '''
    mstmt   : DLABEL
            | stmt SEMICOLON
    '''

def p_stmt(p):
    '''
    stmt    : assign
            | condjump
            | jump
            | readstmt
            | printstmt
            | callstmt
            | EXIT
    '''

def p_assign(p):
    '''
    assign  : ID EQUALS opd arithop opd
    '''

def p_condjump(p):
    '''
    condjump    : IF ID cmpop ID GOTO LABEL
    '''

def p_jump(p):
    '''
    jump    : GOTO LABEL
    '''

def p_readstmt(p):
    '''
    readstmt    : READ ID
    '''

def p_printstmt(p):
    '''
    printstmt   : PRINT printarg
                | PRINTLN
    '''

def p_printarg(p):
    '''
    printarg    : ID
                | STRING
    '''

def p_callstmt(p):
    '''
    callstmt    : CALL ID LPAREN arglist RPAREN
    '''

def p_arglist(p):
    '''
    arglist : targlist
            | empty
    '''

def p_targlist(p):
    '''
    targlist    : ID COMMA targlist
                | ID
    '''

def p_cmpop(p):
    '''
    cmpop   : LESSER
            | GREATER
            | LEQ
            | GEQ
            | EQUALS
            | NEQ
    '''

def p_airthop(p):
    '''
    arithop : PLUS
            | MINUS
            | MULTIPLY
            | DIVIDE
    '''

def p_opd(p):
    '''
    opd : ID
        | NUM
    '''

def p_error(p):
    print("Syntax error in input!")

parser = yacc.yacc(debug=True)

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

data2 = '''var a, b;
begin
print "hello world ";
end
'''
res = parser.parse(data2, lexer)
print(res)
# while True:
#     try:
#        s = input()
#     except EOFError:
#        break
#     if not s: continue
#     result = parser.parse(s, lexer)
#     print(result)