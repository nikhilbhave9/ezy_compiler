import lexical_analyser
from lexical_analyser import tokens
from lexical_analyser import lexer
from lexical_analyser import procs
from lexical_analyser import sy_dict
from lexical_analyser import var_dict
from lexical_analyser import label_dict
from lexical_analyser import labels
import ply.lex as lex
import ply.yacc as yacc
from collections import deque
import sys

# Code for dynamically creating new classes 
class BaseClass(object):
    def __init__(self, classtype):
        self._type = classtype

def ClassGenerator(name, argnames, BaseClass=BaseClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in argnames:
                raise TypeError("Argument %s not valid for %s" 
                    % (key, self.__class__.__name__))
            setattr(self, key, value)
        BaseClass.__init__(self, name[:-len("Class")])
    newclass = type(name, (BaseClass,),{"__init__": __init__})
    return newclass


class Node:
    def __init__(self,type,children=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]

curScope = 'global'

start = 'prog'



curLabels = []
curVars = []

def p_prog(p):
    '''
    prog    : vardecls procdecls BEGIN stmtlist END
    '''
    global curScope
    global curVars
    p[0] = Node('prog', [p[1], p[2], p[3], p[4], p[5]])

def p_empty(p):
    'empty  :'
    pass

def p_vardecls(p):
    '''
    vardecls    : vardecl vardecls
                | empty
    '''

    global curScope
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

    global curScope
    p[0] = Node('vardecl', [p[2]])

def p_varlist(p):
    '''
    varlist : ID COMMA varlist
            | ID
    '''

    global curScope
    global curVars
    curVars.append(p[1])
    
    if(len(p) > 2):
        p[0] = Node('varlist', [p[1], p[3].children[0]])
    else:
        p[0] = Node('varlist', [p[1]])

def p_procdecls(p):
    '''
    procdecls   : procdecl procdecls
                | empty
    '''
    global curScope
    if(len(p) == 3):
        if(p[2].children[0] == None):
            p[0] = Node('procdecls', [p[1]])
        else:
            p[0] = Node('procdecls', [p[1], p[2].children[0]])
    else:
        p[0] = Node('procdecls', [p[1]])

# ======================Nikhil's Bit======================
def p_procdecl(p):
    '''
    procdecl    : PROC ID LPAREN paramlist RPAREN vardecls pstmtlist
    '''
    global curScope
    global curVars
    global curLabels

    sy_dict[p[2]] = ClassGenerator(p[2], "variables labels".split())
    var_dict[p[2]] = curVars
    label_dict[p[2]] = curLabels

    curVars = []
    curLabels = []
    assert(curScope == 'global')

    curScope = p[2]

    

    if (p[4].children[0] == None): # If param list is empty
        if (p[6].children[0] == None): # If variable list is empty
            p[0] = Node('procdecl', [p[2], p[7]])
        else:
            p[0] = Node('procdecl', [p[2], p[6], p[7]]) # (p[6][0]?)
    else: # If param list is non-empty
        if (p[6].children[0] == None): # If variable list is empty
            p[0] = Node('procdecl', [p[2], p[4], p[7]])
        else: 
            p[0] = Node('procdecl', [p[2], p[4], p[6], p[7]])


def p_paramlist(p):
    '''
    paramlist   : tparamlist
                | empty
    '''
    global curScope

    

    # assert(curScope != 'global')
    p[0] = Node('paramlist', [p[1]])

def p_tparamlist(p):
    '''
    tparamlist  : param COMMA tparamlist
                | param
    '''
    global curScope
    # assert(curScope != 'global')

    if (len(p) == 4):
        p[0] = Node('tparamlist', [p[1], p[3]])
        
    else:
        p[0] = Node('tparamlist', [p[1]])

def p_param(p):
    '''
    param   : mode ID
    '''
    global curScope
    # assert(curScope != 'global')


    p[0] = Node('param', [p[1], p[2]])
    # sy_dict[curScope].variables.append(p[2])

def p_mode(p):
    '''
    mode    : IN
            | OUT
            | INOUT
    '''
    global curScope
    # assert(curScope != 'global')

    p[0] = Node('mode', [p[1]])
    
def p_pstmtlist(p):
    '''
    pstmtlist   : pstmt pstmtlist
                | pstmt
    '''
    global curScope
    # assert(curScope != 'global')

    if (len(p) == 3):
        p[0] = Node('pstmtlist', [p[1], p[2]])
    else:
        p[0] = Node('pstmtlist', [p[1]])

def p_stmtlist(p):
    '''
    stmtlist    : mstmt stmtlist
                | mstmt
    '''
    global curScope

    if (len(p) > 2):
        p[0] = Node('stmtlist', [p[1], p[2]])
    else:
        p[0] = Node('stmtlist', [p[1]])

def p_pstmt(p):
    '''
    pstmt   : DLABEL
            | stmt SEMICOLON
            | RETURN SEMICOLON
    '''
    global curScope
    # assert(curScope != 'global')

    if(p[1] in labels):
        sy_dict[curScope].labels.append(p[1])
    elif(p[1] == 'return'):
        curScope = 'global'
    p[0] = Node('pstmt', [p[1]])

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

    p[0] = Node('stmt', [p[1]])

def p_assign(p):
    '''
    assign  : ID EQUALS opd arithop opd
    '''
    p[0] = Node('assign', [p[1], p[3], p[4], p[5]])

def p_condjump(p):
    '''
    condjump    : IF ID cmpop ID GOTO LABEL
    '''
    p[0] = Node('condjump', [p[2], p[3], p[4], p[6]])

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

# data = ''' var a,b;
# var c;
# % following procedure ensures that x<= y on return
# proc order(inout x, inout y)
# var t;
# if x < y goto done;
# t= x+0;
# x = y+0;
# y = t+0;
# done:
# return;
# begin
# print "enter two numbers ";
# println;
# read a ;
# read b ;
# call order(a,b);
# %now a <= b
# c=b/a ;
# c = c*a ;
# c = b - c ;
# print "absolute mod is " ;
# print c;
# println ;
# exit ;
# end
# '''

data2 = '''proc order(inout x, inout y)
var t;
t=0+1;
return;
proc order2(inout x, inout y)
var a, b;
a=0+1;
b = 3+2;
return;
begin
print"hi";
end
'''
res = parser.parse(data2, lexer)
# print(res)

ast = deque()

ast.append(res)

def generate_parse_tree(ast):
    while(ast):
        root = ast.popleft()
        print(root.type, ': ', end = "")
        for child in root.children:
            if(not child):
                print(None, end = " ")
                # print(top.type, None)
                continue
            if(type(child) != Node):
                print(child, end=" ")
                # print(top.type, child)
            else:
                print(child.type, end = " ")
                # print(top.type, child.type)
                ast.append(child)
        print()
# generate_parse_tree(ast)

    



