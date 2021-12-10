import lexical_analyser
from lexical_analyser import tokens
from lexical_analyser import lexer
import ply.lex as lex
import ply.yacc as yacc
from collections import deque
import sys

# Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)     # Prints in the following format: TYPE OF TOKEN + VALUE + LINE NUMBER + LINE POSITION

class Node:
    def __init__(self,type,children=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]

start = 'prog'

def p_prog(p):
    '''
    prog    : vardecls procdecls BEGIN stmtlist END
    '''
    p[0] = Node('prog', [p[1], p[2], p[3], p[4], p[5]])

def p_empty(p):
    'empty  :'
    pass

def p_vardecls(p):
    '''
    vardecls    : vardecl vardecls
                | empty
    '''
    if(len(p) == 3):
        if(p[2].children[0] == None):
            p[0] = Node('vardecls', [p[1]])
        else:
            p[0] = Node('vardecls', [p[1], p[2].children[0]])
    else:
        p[0] = Node('vardecls', [p[1]])

def p_vardecl(p):
    '''
    vardecl : VAR varlist SEMICOLON
    '''
    p[0] = Node('vardecl', [p[2]])

def p_varlist(p):
    '''
    varlist : ID COMMA varlist
            | ID
    '''
    if(len(p) > 2):
        p[0] = Node('varlist', [p[1], p[3].children[0]])
    else:
        p[0] = Node('varlist', [p[1]])

def p_procdecls(p):
    '''
    procdecls   : procdecl procdecls
                | empty
    '''
    if(len(p) == 3):
        if(p[2].children[0] == None):
            p[0] = Node('procdecls', [p[1]])
        else:
            p[0] = Node('procdecls', [p[1], p[2].children[0]])
    else:
        p[0] = Node('procdecls', [p[1]])

# ======================Nikhil's Bit======================
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
    if(len(p) > 2):
        p[0] = Node('stmtlist', [p[1], p[2]])
    else:
        p[0] = Node('stmtlist', [p[1]])

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
    p[0] = Node('mstmt', [p[1]])

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
    if(p[1]):
        p[0] = Node('stmt', [p[1]])

    # p[0] = Node('stmt', [p[1]])

def p_assign(p):
    '''
    assign  : ID EQUALS opd arithop opd
    '''

def p_condjump(p):
    '''
    condjump    : IF ID cmpop ID GOTO LABEL
    '''

# ======================End Nikhil's Bit======================

# # ======================Nishant's Bit======================

def p_jump(p):
    '''
    jump    : GOTO LABEL
    '''
    p[0] = Node('jump', [p[1], p[2]])

def p_readstmt(p):
    '''
    readstmt    : READ ID
    '''
    p[0] = Node('readstmt', [p[1], p[2]])

def p_printstmt(p):
    '''
    printstmt   : PRINT printarg
                | PRINTLN
    '''
    if(len(p) == 3):
        p[0] = Node('printstmt',[p[1], p[2]])
    else:
        p[0] = Node('printstmt', [p[1]])

def p_printarg(p):
    '''
    printarg    : ID
                | STRING
    '''
    p[0] = Node('printarg', [p[1]])

def p_callstmt(p):
    '''
    callstmt    : CALL ID LPAREN arglist RPAREN
    '''
    p[0] = Node('callstmt', [p[1], p[2], p[4]])

def p_arglist(p):
    '''
    arglist : targlist
            | empty
    '''
    p[0]  = Node('arglist', [p[1]])

def p_targlist(p):
    '''
    targlist    : ID COMMA targlist
                | ID
    '''
    if(len(p) == 4):
        p[0] = Node('targlist', [p[1], p[3].children[0]])
    else:
        p[0] = Node('targlist', [p[1]])

def p_cmpop(p):
    '''
    cmpop   : LESSER
            | GREATER
            | LEQ
            | GEQ
            | EQUALS
            | NEQ
    '''
    p[0] = Node('cmpop', [p[1]])
def p_airthop(p):
    '''
    arithop : PLUS
            | MINUS
            | MULTIPLY
            | DIVIDE
    '''
    p[0] = Node('arithop', [p[1]])


def p_opd(p):
    '''
    opd : ID
        | NUM
    '''
    p[0] = Node('opd', [p[1]])
# ======================End Nishant's Bit======================
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
a = 3 + 3;
print a;
end
'''
res = parser.parse(data2, lexer)
# print(res)

ast = deque()

ast.append(res)

while(ast):
    root = ast.popleft()
    print(root.type, ': ', end = "")
    for child in root.children:
        if(not child):
            print(None, end = " ")
            # print(top.type, None)
            continue
        if(type(child) == str):
            print(child, end=" ")
            # print(top.type, child)
        else:
            print(child.type, end = " ")
            # print(top.type, child.type)
            ast.append(child)
    # stack.reverse()
    print()



# while True:
#     try:
#        s = input()
#     except EOFError:
#        break
#     if not s: continue
#     result = parser.parse(s, lexer)
#     print(result)

# ('prog', ('vardecls', ('vardecl', ('varlist', 'a')), ('vardecls', None)), None, 'begin', ('stmtlist', ('mstmt', ('stmt', None)), ('stmtlist', ('mstmt', ('stmt', ('printstmt', 'print', ('printarg', 'a')))))), 'end')