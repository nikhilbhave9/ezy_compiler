import ply.lex as lex   #  Lex = Lexer-generator 
import ply.yacc as yacc #  Yacc = Parser-generator
import sys

'''
Summary of what lexical_analyser.py does:
    1. Determines the input of the compiler (i.e), the ezy program to be compiled (see ezy_input)
       Note: To see the result of the tokenisation, call tokenise() function defined towards the end of file

    2. Defines a list of tokens using the grammar provided, and performs tokenisation using lex.py

    3. Does some pre-processing of the input ezy program to obtain:-
        a. A list of all labels defined in the program
        b. A list of names of all procedures defined in the program, along with the number of parameters in the function

Semantic checks performed by lexical_analyser.py:
    - Semantic Check 8 : No two procedures can have same name
    - Semantic Check 10: No label can be defined more than once. In particular, same label can not be used in main
program and inside a procedure.
'''

#----------------------------------------------------------------------------------------------
#==================== Ezy Program Input Used For Lexical Analysis & Parsing ===================
#----------------------------------------------------------------------------------------------

ezy_input = ''' 
var a,b;
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


#----------------------------------------------------------------------------------------------
#==================== Declaring List of Tokens, Labels and Procedure Names ====================
#----------------------------------------------------------------------------------------------

# List of reserved tokens
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

# Declaring the list of all tokens
tokens = ['SEMICOLON', 'ID', 'COMMA', 'DLABEL', 'EQUALS', 'LABEL', 'STRING', 'LEQ', 'LESSER', 'GEQ', 'GREATER', 'NEQ', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'NUM', 'LPAREN', 'RPAREN'] + list(reserved.values())

# Stores the list of all labels that have been declared in the ezy program 
# (using the get_labels() function defined below)
labels = [] 

# Stores the list of names of all procs that have been declared in the ezy program 
# (using the get_procs() function defined below)
# the list is initialised with 'global' which refers to the global scope
procs = [['global', 0]]


#----------------------------------------------------------------------------------------------
# =============== Pre-processing the EZY Program to Store List of Labels, Procs ===============
#----------------------------------------------------------------------------------------------

# function that goes through the ezy input program and updates the list of labels
def get_labels(data):
    inPrintStmt = False # flag that tells if current word in ezy input is within a print statement
    for s in data:

        # checking for double quotes to identify the start of a print statement
        if(s[0] == "\"" and inPrintStmt == False):
            inPrintStmt = True # if print statement is entered, set the inPrintStmt flag to True
            continue

        # checking if we have reached the end of a print statement
        elif(s[-1] == "\"" and inPrintStmt == True):
            inPrintStmt = False # if print statement is ending, set the inPrintStmt flag to False
            continue

        # do nothing if s is within a print statement
        if(inPrintStmt):
            continue

        # if we're not in a print statement
        else:
            if(s[-1] == ':'): # checking if last character is a colon => we've encountered a label definition
                if(s[:-1] in labels): # Semantic Check: ensuring the encountered label has not been previously defined
                    print(f"Error: Semantic Check 10 failed -- redefinition of label '{s[:-1]}' ")
                    exit(0)
                else:
                    labels.append(s[:-1]) # update the list of labels

    print("Semantic Check 10 OK")


# function that goes through the ezy input program and updates the list of procedure names
def get_procs(data):
    inPrintStmt = False # flag that tells if current word in ezy input is within a print statement
    isProc = False      # flag that tells if current word in ezy input is within a proc's definition
    procAdded = False   # flag that tells if the proc name has been added to the proc list but we're still within the function declaration
    stringBuf = ""
    for s in data:
        # checking if we're within a print statement
        if(s[0] == "\"" and inPrintStmt == False):
            inPrintStmt = True
            continue
        elif(s[-1] == "\"" and inPrintStmt == True):
            inPrintStmt = False
            continue
        
        if(inPrintStmt):
            continue
        # if we're not within a print statement
        else:
            if s == 'proc':
                isProc = True
            else:
                if isProc == True: 
                    stringBuf += s
                    if s[-1] == ')':
                        isProc = False
                        proc_name = stringBuf.split('(')[0]
                        for proc in procs:
                            if(proc[0] == proc_name):
                                print(f"Error: Semantic check 8 failed -- redefinition of procedure '{proc_name}'")
                                exit(0)
                        procs.append([proc_name, len(stringBuf.split(','))])
                        stringBuf = ""                


    print("Semantic Check 8  OK")                



get_labels(ezy_input.split())   # updating the labels list
get_procs(ezy_input.split())    # updating the procs list


# (the below dictionaries will be used later on during parsing for building the symbol table for each scope)

var_dict = {key[0]: [] for key in procs}   # initialising the variable dictionary for each process scope
label_dict = {key[0]: [] for key in procs} # initialising the labels dictionary for each process scope
param_dict = {key[0]: [] for key in procs} # initialising the params dictionary for each process scope



#----------------------------------------------------------------------------------------------
# ===================== Defining Regular Expression Rules for Each Token ======================
#----------------------------------------------------------------------------------------------

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


def t_STRING(t):
    r'\".*\"'
    t.value = (t.value)[1:-1] # removing the double quotes
    return t
    
def t_NUM(t):
    r'\d+'
    t.value = int(t.value) # storing value as an int
    return t

def t_DLABEL(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*.:'
    t.value = t.value[:-1] # removing the colon at the end of label name
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    reserved_token = reserved.get(t.value)
    if(reserved_token):             # if t.value is in the list of reserved tokens
        t.type = reserved_token
    elif(t.value in set(labels)):   # if t.value is in the list labels 
        t.type = 'LABEL'
    else:                           # else, t.value is simply of type ID
        t.type = 'ID'               
    return t

def t_newline(t):   # to keep track of line numbers
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore            = ' \t'     # to ignore tabs
t_ignore_COMMENT    = r'\%.*'   # to ignore comments


def t_error(t):     # for error handling
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)



#----------------------------------------------------------------------------------------------
# ===================== Building The Lexer and Performing Lexical Analysis ====================
#----------------------------------------------------------------------------------------------

lexer = lex.lex() # building the lexer

lexer.input(ezy_input) # feeding our ezy program into the lexer

def tokenize(lexer):
    print()
    print("---------------------------------------------------------------------")
    print("================ Begin Tokenised Output (Type, Lexeme) ==============")
    print("---------------------------------------------------------------------")
    ctr = 1
    while True:
        tok = lexer.token()
        if not tok:
            print("---------------------------------------------------------------------")
            print()
            print()
            break      # No more input

        print(f'{ctr}. ({tok.type}, \'{tok.value}\')')
        ctr += 1

# uncomment below function call to see the tokenisation take place
tokenize(lexer) 








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