# A Mini Compiler for a mock language 'EZY'
An attempt at creating a full mini-compiler as a final project for the course Programming Language Design & Implementation (Monsoon 2021)

Team Members: [Nikhil Bhave](https://github.com/nikhilbhave9),  [Nishant Mahesh](https://github.com/nishant-mahesh)

Primary Language of Development: **Python 3**

Primary Dependencies: **PLY module**

## Specifications 
An EZY program consists of: <b>main program</b> and <b>other procedures</b> (no nested procedures, but recursive calls are permitted) 

- All variables and computations are of integer type
- Each variable must be declared upfront before it is used. 
- Procedures can have their local variables and can access the global variables. No procedure can access the local variable
of other procedure
- If same variable is declared as local and global, then access is meant to the local
variable 
- In EZY, every statement is terminated by a semicolon (;)
- A line starting with % is taken as a comment and is to be ignored for execution

## Expected Input (A Sample Program)
```
%this program calculates absolute mod of two given number, say x and y, defined as follows
% divide the larger number with smaller one and remainder is the result
var a,b;
var c;
% following procedure ensures that x<= y on return
proc order(inout x, inout y)
var t;
if x < y  goto done;
t= x+0;
x = y+0;
y = t+0;
done:
return;
begin
print “enter two numbers “;
println;
read a ;
read b ;
call order(a,b);
%now a <= b
c=b/a ;
c = c*a ;
c = b – c ;
print “absolute mod is “ ;
print c;
println ;
exit ;
end

```
## Expected Output (in Assembly-like code)

```
LPUT “enter two numbers”
GET $0
GET $1
MOV A,I
ADI  6
PUSH A
PUSH $0
PUSH $1
CALL _order
MOV $0,%2
MOV $1,%3
DIV $1,$0
MOV $2, A
MUL $2, $0
MOV $2, A
SUB $1, $2
MOV $2,A
SPUT “absolute mod  is ”
PUT $2
LPUT 
STOP
_order:
MOVE A, S
ADI 1
MOVE S,A
CMP %-2, %-1
JLT done
ADD %-2,0
MOV %0, A
ADD %-1,0
MOV %-2,A
ADD %0, 0
MOV %-1,A
done:
MOV A,S
SBI 3
MOV S,A
RET

```

## Grammar of EZY 

```
<prog> := <vardecls> <procdecls> begin <stmtlist> end
<vardecls> := <vardecl> <verdecls> | 
<vardecl> := var <varlist> ;
<varlist> := id , <varlist> | id
<procdecls> := <procdecl> <procdecls> |
<procdecl> := proc id(<paramlist>) <vardecls> <pstmtlist>
<paramlist> := <tparamlist> | 
<tparamlist> := <param> , <tparamlist> | <param>
<param> := <mode> id
<mode> := in | out | inout
<pstmtlist> := <pstmt> <pstmtlist> | <pstmt>
<stmtlist> := <mstmt> <stmtlist> | <mstmt>
<pstmt> := dlabel | <stmt> ; | return ;
<mstmt> := dlabel | <stmt> ;
<stmt> :=  <assign> | <condjump> | <jump> | <readstmt> | <printstmt>  | <callstmt> 
                                  | exit 
<assign> := id = <opd> <arithop> <opd> 
<condjump> : = if id cmpop id goto label
<jump> :=  goto label
<readstmt := read id
<printstmt> := print <printarg> | println 
<printarg> := id | string 
<callstmt> := call id(<arglist>)
<arglist> := <targlist> |
<targlist> :=  id , <targlist> | id
<cmpop> := < | > | <= | >= | = | <>

<arithop> := + | - | * | / 
<opd> :=  id | num

```

## Implementation 
### Lexical Analysis
In order to eliminate ambiguity during lexical analysis, we implement two procedures: (1) Maximal
Munching and (2) Ordering of token definitions 

Maximal munching is automatically implemented by the Ply module. However, the programmer
has to manually decide the appropriate ordering of tokens.

Order of token definitions
- We started by defining a dictionary of reserved keywords that will act as the terminals in
our context-free grammar. This included keywords like begin, end, if, then, exit, etc.
- Then, we made a list of tokens that included all possible terminals like semicolons, nums,
ids, etc.
- We also declared an empty list of labels (more on this later)
- Then, we started defining the regular expressions for the above tokens in the following
order:
1. Simple tokens like +, -, /, *, (, )
2. Strings (enclosed in double-quotes)
3. Numbers (aka, integers)
4. DLabels (characterized by the fact that they end with semi-colons)
5. IDs
6. Newline
7. Comments (which are ignored)
8. Error handling for illegal characters
IDs were defined in such a way that, first, the regular expression checks if it matches the
definition of an ID. Then, it checks if the ID does not match a reserved keyword by checking the
keyword dictionary. If it does match, instead of returning an ID, it sends back that reserved
keyword as the token value. Finally, it also checks if the current ID matches any previous known
label by referencing the labels list.
The labels list itself is filled using a function that goes over the entire code, locates labels by
looking for the “:” symbol and adding them to the above-mentioned list. This function is defined
after the regular expressions but is called just before the lexer is passed the input data. There is
also a check-in place to see if the label is not part of a string

### Parsing
We used the YACC module within Python in order to parse the token sequence received from our
lexer. For the sake of keeping our code organized, we’ve separated the lexer and the parser into
two files called lexical_analyser.py and parser.py respectively.

We created a class called Node that consists of value and children attributes. Then, we
implemented the grammar rules using a function for each non-terminal production. Within each
function, we described the production rule and we also added additional code to help us build
the parse tree, as well as with catching syntax errors and performing semantic analysis.

We’ve defined a function named display_parse_tree(result) that takes in the Node object
corresponding to the root of the parse tree, and prints the non-terminal (or terminal)
corresponding to each node, along with its list of children (if any). It prints this list in the BFS order
of iterating through the parse tree nodes.

### Symbol Tree 
Instead of using a large, singular symbol table for all our IDs and labels, we used separated
symbol tables for variables, labels and parameters.

We have a set of dictionaries that acts as our symbol table. For example, for the first dict, the key
is the name of the procedure and the value is the list of variables. For the second and third dicts,
the keys will remain the same but the values will be a list of labels and a list of parameters
corresponding to the procedures respectively.

We have made a common class that acts as a template for all the procedures that we encounter.
Every time we encounter a new procedure, we instantiate an object of the above-mentioned
class and we fill it up with the list of variables, labels and parameters from our dictionaries and
then assign values to those with respect to the current call of the procedure.

### Semantic Checking
**Number of arguments in a call should match with number of parameters in called procedure**

This semantic check will be included in the lexical analyser, under the get_procs function. Every
time a new procedure is encountered during the pre-processing stage of the lexer, the get_procs
function will store: (name of proc, num of params) in a list called procs.
The other half of this semantic check will be implemented by a function called check_calls. This
function gets the number of parameters of a function from the procs list. Once we get the name
of the procedure, we check the procs list and cross-reference the number of parameters to see if
it matches. Otherwise, it will raise an error.

**The in parameter will be pass by value, out by pass by result and inout will be pass by
value-result**

(Not implemented)

<b> All the variables referred must be declared either inside function or as global

Variables declared in the beginning are global and accessible every where

Variables not declared inside a function but referred must be declared as global
</b>

Semantic checks #3, #4 and #5 are implemented using symbol table

**No variable can have same name as a procedure and vice versa**

For this check, we have defined a function called idenVarProcs (stands for “Identical Variable &
Procedures”) that iterates through the dictionary of procedures and the dictionary of variables to
see if there are any identical identifiers. In case there are any matches, it raises an error.

**No two variables in same scope can have same name**

In this case, we are considering procs and scopes equivalent for the sake of semantic checking.
To supplement this, we have, in our procs list, “global” as an element which refers to global
scope.

Now, when we’re adding variables to our var_dict, in the prog and the procdecl grammar
production, we’ve implemented the check to see if the variable that we’re about to add already
exists in the dict for key: current procedure. In that case, we flag it as an error.

**No two procedures can have same name**

This semantic check is also done in the get_procs functions

<b> Labels referred must be defined somewhere. If referred in a procedure then it must be defined within procedure and if referred in main program then must be defined in main program </b>

This check has been implemented in the parser under the condjump grammar production

**No label can be defined more than once. In particular, same label can not be used in main program and inside a procedure.**

This check has already been implemented and we’ve mentioned this above, in the Lexical
Analysis section.

### Code Generation 

Ideally, we would've used an a Java-based runtime machine called "EVM" to produce assembly code, however we have not implemented that.

