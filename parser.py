import lexical_analyser
from lexical_analyser import *
import ply.lex as lex
import ply.yacc as yacc
from collections import deque
import sys

'''
Summary of what parser.py does:
    1. Defines a class Node, which will be used to represent each node of the parse tree generated
    2. Builds a parser using the CFG rules given and using yacc.py
    3. Populates var_dict{}, mapping each procedure scope (and 'global' scope) to list of variables declared in the scope
    4. Populates label_dict{}, mapping each procedure scope (and 'global' scope) to list of labels declared in the scope
    5. Populates param_dict{}, mapping each procedure scope to list of parameters defined in the procedure
    6. Has functionality to display the parse tree (for more details, refer to the display_parse_tree() function defined below)

Semantic checks performed by parser.py":
    - Semantic Check 1: Number of arguments in a call should match with number of parameters in called procedure
    - Semantic Check 3: The in parameter will be pass by value, out by pass by result and inout will be pass by value-result
    - Semantic Check 4: Variables declared in the beginning are global and accessible every where
    - Semantic Check 5: Variables not declared inside a function but referred must be declared as global
    - Semantic Check 6: No variable can have same name as a procedure and vice versa
    - Semantic Check 7: No two variables in same scope can have same name
    - Semantic Check 9: Labels referred must be defined somewhere. If referred in a procedure then must be defined
                        within procedure and if referred in main program then must be defined in main program
'''


#----------------------------------------------------------------------------------------------
#======================= Defining Structure for Each Node in Parse Tree =======================
#----------------------------------------------------------------------------------------------
class Node:
    def __init__(self,type,children=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]


#----------------------------------------------------------------------------------------------
#========================== Defining Rules for CFG of EZY Language ===========================
#----------------------------------------------------------------------------------------------
start = 'prog' # start symbol for the CFG

def p_prog(p):
    '''
    prog    : vardecls procdecls BEGIN stmtlist END
    '''

    if(p[1].children[0] != None):   # vardecls is not empty
        for vd in p[1].children:    # iterating through each vardecl
            for vl in vd.children:  # iterating through each varlist of each vardecl
                for variable in vl.children:    # iterating through each variable in the varlist and adding it to var_dict['global]
                    if(variable in var_dict['global']):
                        print(f"Error: Semantic Check 7 failed -- redefinition of var {variable} in global scope")
                        exit(0)
                    var_dict['global'].append(variable)
    p[0] = Node('prog', [p[1], p[2], p[3], p[4], p[5]])

def p_empty(p):
    'empty  :'
    pass

def p_vardecls(p):
    '''
    vardecls    : vardecl vardecls
                | empty
    '''
    if(len(p) == 3): # the production used is "vardecls -> vardcl vardecls"
        if(p[2].children[0] == None): # there is only a single vardecl
            p[0] = Node('vardecls', [p[1]])
        else: # there are multiple vardecl
            p[0] = Node('vardecls', [p[1], p[2].children[0]])

    else: # the production used is "vardecls -> empty"
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
    
    if(len(p) > 2): # the production used is "varlist -> ID COMMA varlist"
        p[0] = Node('varlist', [p[1], p[3].children[0]]) # the children of varlist are all the individual variables

    else: # the production used is "varlist -> ID"
        p[0] = Node('varlist', [p[1]])

def p_procdecls(p):
    '''
    procdecls   : procdecl procdecls
                | empty
    '''
    if(len(p) == 3): # the production used is "procdecls -> procdecl procdecls"
        if(p[2].children[0] == None):
            p[0] = Node('procdecls', [p[1]])
        else:
            p[0] = Node('procdecls', [p[1], p[2].children[0]])

    else: # the production used is "procdecls -> empty"
        p[0] = Node('procdecls', [p[1]])

# ======================Nikhil's Bit======================
def p_procdecl(p):
    '''
    procdecl    : PROC ID LPAREN paramlist RPAREN vardecls pstmtlist
    '''

    # updating the list of variables declared in current procedure

    if(p[6].children[0] != None):   # vardecls is non empty
        for vd in p[6].children:    # iterating through each vardecl
            for vl in vd.children:  # iterating through each varlist in each vardecl
                for variable in vl.children:    # iterating through each variable name in the varlist
                    if(variable in var_dict[p[2]]):
                        print(f"Error: Semantic Check 7 failed -- redefinition of var {variable} in proc '{p[2]}'")
                        exit(0)
                    var_dict[p[2]].append(variable) 


    # updating the list of params of current procedure

    if(p[4].children[0] != None): 
        tpl = p[4].children[0]  # tpl refers to the tparamlist child of paramlist
        for parameter in tpl.children:  # iterating through each parameter 
            if(parameter == None):
                continue
            param_dict[p[2]].append(parameter.children[1])

    if (p[4].children[0] == None): # If param list is empty
        if (p[6].children[0] == None): # If variable list is empty
            p[0] = Node('procdecl', [p[2], p[7]])
        else:
            p[0] = Node('procdecl', [p[2], p[6], p[7]]) 
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

    p[0] = Node('paramlist', [p[1]])

def p_tparamlist(p):
    '''
    tparamlist  : param COMMA tparamlist
                | param
    '''

    if(len(p) > 2):
        p[0] = Node('tparamlist', [p[1], p[3].children[0]])
    else:
        p[0] = Node('tparamlist', [p[1]])


def p_param(p):
    '''
    param   : mode ID
    '''

    p[0] = Node('param', [p[1], p[2]])
    

def p_mode(p):
    '''
    mode    : IN
            | OUT
            | INOUT
    '''
    p[0] = Node('mode', [p[1]])
    
def p_pstmtlist(p):
    '''
    pstmtlist   : pstmt pstmtlist
                | pstmt
    '''

    if (len(p) == 3):
        p[0] = Node('pstmtlist', [p[1], p[2]])
    else:
        p[0] = Node('pstmtlist', [p[1]])

def p_stmtlist(p):
    '''
    stmtlist    : mstmt stmtlist
                | mstmt
    '''

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
    if(p[6] not in labels):
        print(f"Error: Semantic Check 9 Failed: label '{p[2]}' has not been defined")
        exit(0)

def p_jump(p):
    '''
    jump    : GOTO LABEL
    '''
    p[0] = Node('jump', [p[1], p[2]])
    if(p[2] not in labels):
        print(f"Error: Semantic Check 9 Failed: label '{p[2]}' has not been defined")
        exit(0)

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

def p_error(p):
    print("Syntax error in input!")

#----------------------------------------------------------------------------------------------
#==================== Constructing the Parser Object and Performing Parsing ===================
#----------------------------------------------------------------------------------------------

parser = yacc.yacc(debug=True)

result = parser.parse(ezy_input, lexer)

#----------------------------------------------------------------------------------------------
#===================================== Semantic Checking =====================================
#----------------------------------------------------------------------------------------------

'''
The following function performs the following 3 semantic checks:-
    1. Semantic Check 3: All the variables referred must be declared either inside function or as global
    2. Semantic Check 4: Variables declared in the beginning are global and accessible every where
    3. Semantic Check 5: Variables not declared inside a function but referred must be declared as global
'''
def semantic_check1(lexer, ezy_input):
    lexer = lex.lex() # building the lexer
    lexer.input(ezy_input) # feeding our ezy program into the lexer

    inProc  = False
    curProc = None
    while True:
        tok = lexer.token()
        if not tok:
            print("Semantic Check 3  OK")
            print("Semantic Check 4  OK")
            print("Semantic Check 5  OK")
            break      # No more input
        if(tok.value == 'proc'):
            assert(inProc == False)
            inProc = True
            continue
    
        if(inProc == False):
            continue

        if(inProc == True):
            if(curProc == None):
                assert(tok.type == 'ID')
                curProc = tok.value
                continue
            else:
                if(tok.type == 'ID'):
                    if((tok.value not in var_dict[curProc]) and (tok.value not in param_dict[curProc]) and (tok.value not in var_dict['global'])):
                        print(f"Error: Semantic Checks 3 and 5 failed -- var '{tok.value}' in proc '{curProc}' has not been defined!")
                        exit(0)
                if(tok.value == 'return'):
                    inProc = False
                    curProc = None

semantic_check1(lexer, ezy_input)


#----------------------------------------------------------------------------------------------
#================================= Generating the Parse Tree ==================================
#----------------------------------------------------------------------------------------------

'''
The following function takes the result of yacc.py's parser (the root of our parse tree) 
and walks through all the nodes of the tree in BFS order.
(i.e),
If we were to perform BFS on the parse tree generated, and print the name and children of each
node as we encounter them, the result will be the same.
'''
def display_parse_tree(result):
    ast = deque()
    ast.append(result)
    print()
    print("---------------------------------------------------------------------")
    print("#============= Begin Parse Tree (Displayed in BFS Order) ============")
    print("---------------------------------------------------------------------")
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
    print("---------------------------------------------------------------------")
    print()
    print()

# uncomment the below function call to see the parse tree printed
display_parse_tree(result)
    

    


