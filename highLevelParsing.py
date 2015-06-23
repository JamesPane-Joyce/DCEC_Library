import prototypes
import cleaning
import random

class Token:
    def __init__(self,funcname,args):
        self.funcName = funcname
        self.args = args
        self.depth = ""
        self.width = ""
        self.Sexpression = ""
        self.Fexpression = ""
    def depthOf(self):
        if self.depth != "":
            return self.depth
        temp = []
        for arg in self.args:
            if isinstance(arg,Token):
                temp.append(arg)
        if len(temp) == 0:
            self.depth = 1
        else:
            self.depth = 1+max([x.depthOf() for x in temp]) 
        return self.depth
    def widthOf(self):
        if self.width != "":
            return self.width
        temp = 0
        for arg in self.args:
            if isinstance(arg,str):
                temp += 1
            else:
                temp += arg.widthOf()
        self.width = temp
        return self.width
    def createSExpression(self):
        if not self.Sexpression == "":
            return self.Sexpression
        self.Sexpression = "("+self.funcName+" "
        for arg in self.args:
            if isinstance(arg,str):
                self.Sexpression += arg+" "
            else:
                arg.createSExpression()
                self.Sexpression += arg.Sexpression+" "
        self.Sexpression = self.Sexpression.strip()
        self.Sexpression += ")"
        return self.Sexpression
    def createFExpression(self):
        if not self.Fexpression == "":
            return self.Fexpression
        self.Fexpression = self.funcName+"("
        for arg in self.args:
            if isinstance(arg,str):
                self.Fexpression += arg+","
            else:
                arg.createFExpression()
                self.Fexpression += arg.Fexpression+","
        self.Fexpression = self.Fexpression.strip(",")
        self.Fexpression += ")"
        return self.Fexpression 
    def printTree(self):
        self.createSExpression()
        self.createFExpression()
        print self.Fexpression

def removeComments(expression):
    index = expression.find(";")
    if index != -1:
        expression = expression[:index]
    if len(expression) == 0:
        expression = ""
    return expression
    
def functorizeSymbols(expression):
    '''
    This function replaces all symbols with the appropreate internal funciton name.
    Some symbols are left untouched, these symbols have multiple interpretations in the DCEC syntax.
    For example, the symbol * can represent both multiplication and the self operator.
    '''
    symbols = ["^","*","/","+","<->","->","-","&","|","~",">=","==","<=","===","=",">","<",]
    symbolMap = {
        "^": "exponent",
        "*": "*",
        "/": "divide",
        "+": "add",
        "-": "-",
        "&": "&",
        "|": "|",
        "~": "not",
        "->": "implies",
        "<->": "ifAndOnlyIf",
        ">": "greater",
        "<": "less",
        ">=": "greaterOrEqual",
        "<=": "lessOrEqual",
        "=": "equals",
        "==": "equals",
        "===": "tautology",
    }
    returner = expression
    for symbol in symbols:
        returner = returner.replace(symbol," "+symbolMap[symbol]+" ")
    returner = returner.replace("( ","(")
    return returner

def replaceSynonyms(args):
    '''
    These are some common spelling errors that users demand the parser takes
    care of, even though it increases "shot-in-foot" syndrome.
    '''
    synonymMap = {
        "ifAndOnlyIf": "iff",
        "if": "implies",
        "Time": "Moment",
        "forall": "forAll",
        "Forall": "forAll",
        "ForAll": "forAll",
        "Exists": "exists",
    }
    for arg in range(0,len(args)):
        if args[arg] in synonymMap.keys():
            print "WARNING: replaced the common mispelling "+args[arg]+" with the correct name of "+synonymMap[args[arg]]
            args[arg] = synonymMap[args[arg]]
    return

def prefixLogicalFunctions(args,addAtomics):
    '''
    This function turns infix notation into prefix notation. It assumes standard
    logical order of operations.
    '''
    logicKeywords = ["not","and","or","xor","implies","iff"]
    #Checks for infix notation
    if len(args) < 3:
        return args    
    #Checks for infix notation. Order of operations is only needed in infix notation.
    if not args[-2] in logicKeywords:
        return args
    #This is a very common error. Order of operations really fucks with the parser, especially because it needs to interpret both S and F notations. Because of this, operations are read left-to-right throughout the parser.
    for arg in range(0,len(args)):
        if args[arg] == "not" and arg+2 < len(args) and not args[arg+1] in logicKeywords:
            print "WARNING: ambiguous not statement. This parser assumes standard order of logical operations. Please use prefix notation or parentheses to resolve this ambiguity."
    for word in logicKeywords:
        index = 0
        while word in args:
            index = args.index(word)
            if word == "not":
                newToken = Token(word,[args[index+1]])
                #Assign sorts to the atomics used
                if args[index+1] in addAtomics.keys():
                    addAtomics[args[index+1]].append("Boolean")
                else:
                    addAtomics[args[index+1]] = ["Boolean"]
                #Replace infix notation with tokenized representation
                args = args[:index+1]+args[index+2:]
                args[index] = newToken
                break
            in1 = index-1
            in2 = index+1
            #If the thing is actually prefix anyway > twitch <
            if in1 < 0:
                break
            #Tucks the arithmetic expression into a token
            newToken = Token(word,[args[in1],args[in2]])
            #Assign sorts to the atomics used
            if args[in1] in addAtomics.keys():
                addAtomics[args[in1]].append("Boolean")
            else:
                addAtomics[args[in1]] = ["Boolean"]
            if args[in2] in addAtomics.keys():
                addAtomics[args[in2]].append("Boolean")
            else:
                addAtomics[args[in2]] = ["Boolean"]
            #Replace the args used in the token with the token
            args = args[:in1]+args[in2:]
            args[in1] = newToken
    return args

def prefixEMDAS(args,addAtomics):
    """
    This function turns infix notation into a tokenized prefix notation using the standard PEMDAS order of operations.
    """
    arithmeticKeywords = ["negate","exponent","multiply","divide","add","sub"]
    #Checks for infix notation
    if len(args) < 3:
        return args
    #Checks for infix notation. PEMDAS is only needed in infix notation.
    elif not args[-2] in arithmeticKeywords:
        return args
    else:
        pass
    for word in arithmeticKeywords:
        while word in args:
                index = args.index(word)
                if word == "negate":
                    newToken = Token(word,[args[index+1]])
                    #Assign sorts to the atomics used
                    if args[index+1] in addAtomics.keys():
                        addAtomics[args[index+1]].append("Numeric")
                    else:
                        addAtomics[args[index+1]] = ["Numeric"]
                    #Replace infix notation with tokenized representation
                    args = args[:index+1]+args[index+2:]
                    args[index] = newToken
                    continue
                in1 = index-1   
                in2 = index+1
                #If it mixes both forms > twitch <
                if in1 < 0:
                    break
                #Tucks the arithmetic expression into a token
                newToken = Token(word,[args[in1],args[in2]])
                #Assign sorts to the atomics used
                if args[in1] in addAtomics.keys():
                    addAtomics[args[in1]].append("Numeric")
                else:
                    addAtomics[args[in1]] = ["Numeric"]
                if args[in2] in addAtomics.keys():
                    addAtomics[args[in2]].append("Numeric")
                else:
                    addAtomics[args[in2]] = ["Numeric"]
                #Replace the args used in the token with the token
                args = args[:in1]+args[in2:]
                args[in1] = newToken
    return args
            

def assignTypes(args,namespace,addAtomics,addFunctions):
    '''
    This function assigns sorts to atomics, tokens, and inline defined functions based
    on the sorts keywords.
    '''
    #Add the types to the namespace
    for arg in range(0,len(args)):
        if args[arg] in namespace.sorts.keys():
            if arg+1 == len(args):
                print "ERROR: Cannot find something to attach the sort \""+args[arg]+"\". Cannot overload sorts."
                return False
            elif args[arg+1] in namespace.sorts.keys() or args[arg+1] in namespace.functions.keys():
                print "ERROR: Cannot assign inline types to basicTypes, keywords, or function names"
                return False
            elif isinstance(args[arg+1],Token):
                name = args[arg+1].funcName
                inargs = []
                for x in args[arg+1].args:
                    if x in namespace.atomics.keys():
                        inargs.append(namespace.atomics[x])
                    elif x in addAtomics.keys():
                        inargs.append(addAtomics[x][0])
                    else:
                        print "ERROR: token \""+str(x)+"\" has an unknown type. Please type it."
                        return False
                if name in addFunctions.keys():
                    for item in addFunctions[name]:
                        if inargs == item[1]:
                            if item[0] == "?":
                                item[0] = args[arg]
                            elif item[0] == args[arg]:
                                continue
                            else:
                                print "ERROR: A function cannot have two different returntypes"
                                return False
                        else:
                            newItem = [name,inargs]
                            if name in addFunctions.keys():
                                addFunctions[name].append(newItem)
                            else:
                                addFunctions[name] = [newItem]
            else:
                addAtomics[args[arg+1]] = [args[arg]]
    #Remove the types from the expression 
    counter = 0
    while counter != len(args):
        if args[counter] in namespace.sorts.keys():
            args.pop(counter)
            continue
        else:
            counter += 1
    return True

def distinguishFunctions(args,namespace,addAtomics,addFunctions):
    '''
    Because several symbols in the DCEC syntax can mean more than one thing, this 
    function tires to resolve that ambiguity by looking at various sorts.
    Hopefully, users do not use these symbols and instead use the unambiguous names
    instead.
    '''
    if len(args) == 1:
        return True
    for arg in range(0,len(args)):
        if args[arg] == "*":
            ### CAN ADD HEURISTIC THAT SELF HAS ONE ARG AND MULTIPLY HAS 2 HERE ###
            if arg == 0:
                args[arg] = "multiply"
            elif args[arg-1] == "self":
                args[arg] = args[arg-1]
                args[arg-1] = "self"
            elif args[arg-1] in namespace.atomics.keys():
                if namespace.atomics[args[arg-1]] == "Agent":
                    args[arg] = args[arg-1]
                    args[arg-1] = "self"
                elif namespace.atomics[args[arg-1]] == "Numeric":
                    args[arg] = "multiply"
                else:
                    print "ERROR: keyword * does not take atomic arguments of type: "+namespace.atomics[args[arg-1]]
                    return False
            elif args[arg-1] in addAtomics.keys():
                if addAtomics[args[arg-1]][0] == "Agent":
                    args[arg] = args[arg-1]
                    args[arg-1] = "self"
                elif addAtomics[args[arg-1]][0] == "Numeric":
                    args[arg] = "multiply"
                else:
                    print "ERROR: keyword * does not take atomic arguments of type: "+addAtomics[args[arg-1]][0]
                    return False
            else:
                print "ERROR: ambiguous keyword * can be either self or multiply, please set the types of your atomics and use parentheses."
                return False
        if args[arg] == "-":
            if arg == 0:
                args[arg] = "negate"
            elif args[arg-1] in namespace.atomics.keys():
                if namespace.atomics[args[arg-1]] != "Numeric":
                    args[arg] = "negate"
                elif len(args) > arg+1 and args[arg+1] in namespace.atomics.keys():
                    if namespace.atomics[args[arg+1]] != "Numeric":
                        print "ERROR: - keyword does not take "+namespace.atomics[args[arg+1]]+" arguments."
                        return False
                    else:
                        args[arg] = "sub"
            elif args[arg-1] in addAtomics.keys():
                if addAtomics[args[arg-1]][0] != "Numeric":
                    args[arg] = "negate"
                elif len(args) > arg+1 and args[arg+1] in addAtomics.keys():
                    if addAtomics[args[arg+1]][0] != "Numeric":
                        print "ERROR: - keyword does not take "+addAtomics[args[arg+1]][0]+" arguments."
                        return False
                    else:
                        args[arg] = "sub"                
            elif args[arg-1] in namespace.functions.keys():
                args[arg] = "negate"
            elif args[arg-1] in addFunctions.keys():
                args[arg] = "negate"
            else:
                print "ERROR: keyword - can be either sub or negate, please add types, or use the sub or negate keywords"
                return False
        if args[arg] == "&":
            if arg+1<len(args) and args[arg+1] in namespace.atomics.keys():
                if namespace.atomics[args[arg+1]] == "Boolean":
                    args[arg] = "and"
                elif namespace.atomics[args[arg+1]] == "Set":
                    args[arg] = "union"
                else:   
                    print "ERROR: keyword & does not take "+namespace.atomics[args[arg+1]]+" arguments"
                    return False
            elif arg+1<len(args) and args[arg+1] in addAtomics.keys():
                if addAtomics[args[arg+1]][0] == "Boolean":
                    args[arg] = "and"
                elif addAtomics[args[arg+1]][0] == "Set":
                    args[arg] = "union"
                else:   
                    print "ERROR: keyword & does not take "+addAtomics[args[arg+1]][0]+" arguments"
                    return False
            else:
                print "ERROR: keyword & can be either union or and, please add types, or use the and or union keyword."
                return False
        if args[arg] == "|":
            if arg+1<len(args) and args[arg+1] in namespace.atomics.keys():
                if namespace.atomics[args[arg+1]] == "Boolean":
                    args[arg] = "or"
                elif namespace.atomics[args[arg+1]] == "Set":
                    args[arg] = "intersection"
                else:   
                    print "ERROR: keyword | does not take "+namespace.atomics[args[arg+1]]+" arguments"
                    return False
            elif arg+1<len(args) and args[arg+1] in addAtomics.keys():
                if addAtomics[args[arg+1]][0] == "Boolean":
                    args[arg] = "or"
                elif addAtomics[args[arg+1]][0] == "Set":
                    args[arg] = "intersection"
                else:
                    print "ERROR: keyword | does not take "+addAtomics[args[arg+1]][0]+" arguments"
                    return False
            else:
                print "ERROR: keyword | can be either union or and, please add types, or use the or or intersect keyword."
                return False
    return True

def checkPrenex(args,addQuants):
    for arg in args:
        if arg in addQuants.keys() and not 'QUANT' in arg:
            print "WARNING: not using prenex form. This may cause an error if improperly handled. Use prenex form and make sure that your quantifiers are unique."

def nextInternal(namespace):
    if not "TEMP" in namespace.quantMap.keys():
        namespace.quantMap["TEMP"] = 0
        nextnumber = 0
    else:
        nextnumber = namespace.quantMap["TEMP"]
        namespace.quantMap["TEMP"] += 1
    nextinternal = 'QUANT'+str(nextnumber)
    if nextinternal in namespace.atomics:
        return nextInternal(namespace)
    else:
        return nextinternal

def popQuantifiers(args,highlevel,sublevel,namespace,quantifiers,addQuants,addAtomics,addFunctions):
    '''
    This function removes all quantifiers from the statement, and replaces quantified variables
    with thier internal representations. These representations are then stored in the namespace atomics map.
    '''
    removelist = []
    place = 0
    for arg in range(0,len(args)):
        #Replace quants with internal representations
        if args[arg] in addQuants.keys():
            args[arg] = addQuants[args[arg]]
        #Hey look here is a quantifier
        if args[arg] in ["forAll","exists"]:
            #Move to the next argument
            arg += 1
            #Check for args in parens
            if args[arg] == "":
                removelist.append(arg-1)
                removelist.append(arg)
                newArgs = highlevel[sublevel[0][0]:sublevel[0][1]][1:-1].split(",")
                place += 1
                interned = nextInternal(namespace)
                for temp in newArgs:
                    if temp in namespace.sorts.keys():
                        addAtomics[interned] = [temp]
                        continue
                    else:
                        addQuants[interned] = temp
                        addQuants[temp] = interned
                        quantifiers.append(args[arg-1])
                        quantifiers.append(interned)
                        interned = nextInternal(namespace)
            #if the quantifier is written as forAll x forAll y forAll z blah(x,y,z)
            elif isinstance(args[arg],Token) or not "[" in args[arg]:
                removelist.append(arg-1)
                removelist.append(arg)
                interned = nextInternal(namespace)
                if args[arg] in namespace.sorts.keys():
                    addAtomics[interned] = [args[arg]]
                    arg += 1
                    removelist.append(arg)
                addQuants[interned] = args[arg]
                addQuants[args[arg]] = interned
                quantifiers.append(args[arg-1])
                quantifiers.append(interned)
            #If the quantifier is written with a list of symbols ex. forAll [x,y,z] blah(x,y,z)
            else:
                #Store the quant type
                tempQuant = args[arg-1]
                removelist.append(arg-1)
                while True:
                    newArg = args[arg].strip("[").strip("]")
                    args[arg] = args[arg].strip("[")
                    removelist.append(arg)
                    interned = nextInternal(namespace)
                    if newArg in namespace.sorts.keys():
                        addAtomics[interned] = [newArg]
                        arg += 1
                        removelist.append(arg)
                        newArg = args[arg].strip("[").strip("]")
                    addQuants[interned] = newArg
                    addQuants[newArg] = interned
                    quantifiers.append(tempQuant)
                    quantifiers.append(interned)
                    arg += 1
                    if "]" in args[arg-1]:
                        args[arg-1] = args[arg-1].strip("]")
                        break
    #Remove quantifiers from the arguments
    args = [i for j, i in enumerate(args) if j not in removelist]
    return args,place

def assignArgs(funcName,args,namespace,addAtomics,addFunctions):
    '''
    This function attempts to assign sorts to the current function and all of its arguments.
    It also attempts to differentiate between different overloaded functions. 
    '''
    #Fluents are weird, this is as good as it gets
    fluents = ["action","initially","holds","happens","clipped","initiates","terminates","prior","interval","self","payoff"]
    exceptions = []
    #This is more sane. Find the right set of arguments for overloaded functions.
    tempArgs = args
    tempArgs.remove(funcName)
    realTypes = []
    arg = 0
    if funcName in namespace.functions.keys():
        while arg < len(tempArgs) and arg < max([len(x[1]) for x in namespace.functions[funcName]]):
            if tempArgs[arg] in namespace.atomics.keys():
                realTypes.append(namespace.atomics[tempArgs[arg]])
            elif tempArgs[arg] in namespace.functions.keys():
                if tempArgs[arg] in fluents:
                    exceptions.append(len(realTypes))
                newTail,returnType = assignArgs(tempArgs[arg],tempArgs[arg:],namespace,addAtomics,addFunctions)
                realTypes.append(returnType)
                tempArgs = tempArgs[:arg]+newTail
            elif tempArgs[arg] in addAtomics.keys():
                realTypes.append(addAtomics[tempArgs[arg]][0])
            else:
                realTypes.append("?")
            arg += 1
    else:
        while arg < len(tempArgs) and arg < max([len(x[1]) for x in addFunctions[funcName]]):
            if tempArgs[arg] in addAtomics.keys():
                realTypes.append(addAtomics[tempArgs[arg]][0])
            elif tempArgs[arg] in namespace.functions.keys():
                if tempArgs[arg] in fluents:
                    exceptions.append(len(realTypes))
                newTail,returnType = assignArgs(tempArgs[arg],tempArgs[arg:],namespace,addAtomics,addFunctions)
                realTypes.append(returnType)
                tempArgs = tempArgs[:arg]+newTail            
            elif tempArgs[arg] in addFunctions.keys():
                if tempArgs[arg] in fluents:
                    exceptions.append(len(realTypes))
                newTail,returnType = assignArgs(tempArgs[arg],tempArgs[arg:],namespace,addAtomics,addFunctions)
                realTypes.append(returnType)
                tempArgs = tempArgs[:arg]+newTail 
            else:
                realTypes.append("?")
            arg += 1   
    validItems = []
    #Find the right item
    if funcName in namespace.functions.keys():
        for item in namespace.functions[funcName]:
            valid = True
            levels = []
            if not len(item[1]) <= len(realTypes): continue
            for arg in range(0,len(item[1])):
                returnthing = namespace.noConflict(realTypes[arg],item[1][arg],0)
                if returnthing[0]:
                    levels.append(returnthing[1])
                elif item[1][arg] == "Fluent": #Fluents are special, they can take bools, ect.
                    if arg in exceptions:
                        pass
                    else:
                        valid = False
                        break
                else:
                    valid = False
                    break
            if valid:
                validItems.append([item,levels])
    if funcName in addFunctions.keys():
        for item in addFunctions[funcName]:
            valid = True
            levels = []
            if not len(item[1]) <= len(realTypes): continue
            for arg in range(0,len(item[1])):
                returnthing = namespace.noConflict(realTypes[arg],item[1][arg],0)
                if returnthing[0]:
                    levels.append(returnthing[1])
                elif item[1][arg] == "Fluent": #Fluents are special, they can take bools, ect.
                    if arg in exceptions:
                        pass
                    else:
                        valid = False
                        break
                else:
                    valid = False
                    break
            if valid:
                validItems.append([item,levels])
    if len(validItems) > 1:
        #Sort by length first
        sortedItems = sorted(validItems,key=lambda item: len(item[1]),reverse = True)
        if len(sortedItems[0][1]) == len(sortedItems[1][1]):
            sortedItems = sorted(validItems,key=lambda item: sum(item[1]))
            if sum(sortedItems[0][1]) == sum(sortedItems[1][1]):
                print "ERROR: more than one possible interpretation for function \""+funcName+"\". Please type your atomics."
                print "   The interpretations are:"
                for x in sortedItems:
                    print "interpretation: ",x[0]," Constraining factor: ",sum(x[1])
                print "   you gave:"
                print "  ",realTypes
                return False,[]
            else:
                validItems = [sortedItems[0]]
        else:
            validItems = [sortedItems[0]]
    elif len(validItems) == 0:
        print "ERROR: the function named \""+funcName+"\" does not take arguments of the type provided. You cannot overload inline. Use prototypes."
        print "   the possible inputs for \""+funcName+"\" are:"
        #Print the possible interpretations
        if funcName in namespace.functions.keys():
            for x in namespace.functions[funcName]:
                print "  ",x[1]
        if funcName in addFunctions.keys():
            for x in addFunctions[funcName]:
                print "  ",x[1]
        print "   you gave:"
        print "  ",realTypes
        #Throw an error
        return False,[]
    #Assign Types
    validItems = [validItems[0][0]]
    for arg in range(0,len(validItems[0][1])):
        if tempArgs[arg] in addAtomics.keys():
            addAtomics[tempArgs[arg]].append(validItems[0][1][arg])
        else:
            addAtomics[tempArgs[arg]] = [validItems[0][1][arg]]
    #Make a token of the right function
    newToken = Token(funcName,tempArgs[:len(validItems[0][1])])
    addAtomics[newToken] = [validItems[0][0]]
    #Remove used args from list:
    returnArgs = [newToken]
    returnArgs += tempArgs[len(validItems[0][1]):]
    return returnArgs,addAtomics[newToken][0]
            

def TokenTree(expression,namespace,quantifiers,addQuants,addAtomics,addFunctions):
    '''
    This is the meat and potatoes function of the parser. It pulls together all of the
    other utility functions and decides which words are function names, which are
    arguments to the functions, and which are special keywords that define sorts, ect.
    Most of the complexity of the parser comes from dealing with overloaded and inline
    functions. Unfortunately, the users demand these features, so the parser must make
    it easy to shoot oneself in the foot with it.
    '''
    #Strip the outer parens
    temp = expression[1:-1].strip(",")
    #check for an empty string
    if temp == "":
        return temp
    #Find the sub-level tokens at this level of parsing
    level = 0
    highlevel = ""
    sublevel = []
    for index in range(0,len(temp)):
        if temp[index] == "(":
            level += 1
            if(level == 1):
                sublevel.append([index,cleaning.getMatchingCloseParen(temp,index)+1])
            continue
        if temp[index] == ")":
            level -= 1
            continue
        if level == 0:
            highlevel = highlevel + temp[index]
    #These are the function components. One is the function name, the others are its args.
    args = highlevel.split(",")   
    place = 0
    #Fix some common keyword mistakes
    replaceSynonyms(args)
    if isinstance(args,bool):
        return False
    #Rip out quantified statements
    args,offset = popQuantifiers(args,temp,sublevel,namespace,quantifiers,addQuants,addAtomics,addFunctions)
    place += offset
    if isinstance(args,bool):
        return False
    #Tokens can be nested, so this recurses thorough the tree
    for index in range(0,len(args)):
        if args[index] == "":
            args[index] = TokenTree(temp[sublevel[place][0]:sublevel[place][1]],namespace,quantifiers,addQuants,addAtomics,addFunctions)
            if not args[index]:
                return False
            place += 1
    #Assign inline types
    if not assignTypes(args,namespace,addAtomics,addFunctions): return False  
    #Distinguish inbetween ambiguous symbols
    if not distinguishFunctions(args,namespace,addAtomics,addFunctions): return False
    #Check for prenex form
    checkPrenex(args,addQuants)
    #Prefix inline logical functions
    args = prefixLogicalFunctions(args,addAtomics)
    #Prefix inline numeric functions
    args = prefixEMDAS(args,addAtomics)
    #If this is a basic argument, it does not need to be tokenized
    if len(args) == 1: return args[0]
    #Otherwise it does, more than one arg means one is a function name and others are args
    while len(args) > 1:
        #Find the function name. If a function is known this will find it.
        primaryToken = ""
        for arg in args:
            if arg in namespace.functions.keys():
                primaryToken = arg
                break
            elif arg in addFunctions.keys():
                primaryToken = arg
                break
        #If there is no primary token, the first arg is a function (this will only happen in an inline function definition)
        if primaryToken == "":
            primaryToken = args[0]
            #Check if there is no function name. This will happen in postfix notation or if the user is bad. We do not support this
            if isinstance(primaryToken,Token):
                print "ERROR: \""+primaryToken.createSExpression()+"\" is not a valid function name. Postfix notation is not supported when defining inline functions."
                return False
            #Attempt to define the inline function
            subTypes = []
            for arg in args[1:]:
                if arg in namespace.atomics.keys():
                    subTypes.append(namespace.atomics[arg])
                elif arg in addAtomics.keys():
                    subTypes.append(addAtomics[arg][0])
                else:
                    print "ERROR: token \""+str(arg)+"\" is of an unknown type. Please type it."
                    return False
            newToken = Token(primaryToken,args[1:])
            if primaryToken in addFunctions.keys():
                #This is a very common error, but unfortunately cannot be let go without a warning. Inline functions need to be defined outside of the parentheses, but most people are too lazy. However, some people might forget a paren or name or something which would lead to the same syntax as the previous case, but unintentionally. This makes this conditional ambiguous, but because the alternative results in an error, the parser will assume that the user meant for this to happen.
                if primaryToken in addAtomics.keys():
                    addFunctions[primaryToken].append([addAtomics[primaryToken][0],subTypes])
                    print "WARNING: ambiguity in parsing. Assuming that the inline function \""+primaryToken+"\" has returntype of "+addAtomics[primaryToken][0]+". Please place inline return type definitions outside of the function definition, or use prototypes."
                    del addAtomics[primaryToken]
                else:
                    addFunctions[primaryToken].append(["?",subTypes])
            #This is a very common error, but unfortunately cannot be let go without a warning. Inline functions need to be defined outside of the parentheses, but most people are too lazy. However, some people might forget a paren or name or something which would lead to the same syntax as the previous case, but unintentionally. This makes this conditional ambiguous, but because the alternative results in an error, the parser will assume that the user meant for this to happen.
            elif primaryToken in addAtomics.keys():
                addFunctions[primaryToken] = [[addAtomics[primaryToken][0],subTypes]]
                print "WARNING: ambiguity in parsing. Assuming that the inline function \""+primaryToken+"\" has returntype of "+addAtomics[primaryToken][0]+". Please place inline return type definitions outside of the function definition, or use prototypes."
                del addAtomics[primaryToken]
            else:
                addFunctions[primaryToken] = [["?",subTypes]]
            args = [newToken]
        #If a primary function is found, find the arguments and tokenize them
        else:
            returnArgs,validItems = assignArgs(primaryToken,args,namespace,addAtomics,addFunctions)
            if not returnArgs:
                return False
            return returnArgs[0]
    if len(args) == 1:
        return args[0]
    else:
        print "ERROR: Unspecified error, something went wrong"
        return False

def tokenizeQuantifiers(tokenTree,quantifiers):
    '''
    Quantifiers are tokenized last, because they need to be written in prenex form
    to work in the prover.
    '''
    #Going backwards to perserve the order of quantifiers
    place = len(quantifiers)-2
    temp = tokenTree
    while place >= 0:
        temp = Token(quantifiers[place],[quantifiers[place+1],temp])
        place -= 2
    return temp

def tokenizeRandomDCEC(expression,namespace = ""):
    '''
    This function creates a token representation of a random DCEC statement.
    It returns the token as well as sorts of new atomics and functions.
    '''
    #Default DCEC Functions
    if namespace == "":
        namespace = prototypes.NAMESPACE()
        namespace.addBasicDCEC()
    else:
        namespace = namespace
    #Remove Comments
    temp = removeComments(expression)
    #Check for an empty string
    if temp == "()":
        return ("",{},{},{})
    #Check for a parentheses mismatch error
    if not cleaning.checkParens(expression):
        print "ERROR: parentheses mismatch error."
        return (False,False,False,False)
    #Make symbols into functions
    temp = functorizeSymbols(temp)
    #Strip comments
    temp = cleaning.stripComments(temp)
    #Strip whitespace so you can do the rest of the parsing
    temp = cleaning.stripWhiteSpace(temp)
    #Tuck the functions inside thier parentheses
    temp = cleaning.tuckFunctions(temp)
    #Strip whitespace again
    temp = cleaning.stripWhiteSpace(temp)
    #Consolidate Parentheses
    temp = cleaning.consolidateParens(temp)
    quantifiers = []
    #These are the tokens that should be added to the namespace
    addAtomics = {}
    addFunctions = {}
    addQuants = {}
    returnToken = TokenTree(temp,namespace,quantifiers,addQuants,addAtomics,addFunctions)
    #check for errors that occur in the lower level
    if isinstance(returnToken,bool) and returnToken == False:
        return (False,False,False,False)
    #Add quantifiers to the TokenTree
    returnToken = tokenizeQuantifiers(returnToken,quantifiers)
    return (returnToken,addQuants,addAtomics,addFunctions)
        
if __name__ == "__main__":
    '''
    Testing suite.
    '''
    inputin = raw_input("Enter an expression: ")
    #Make symbols into functions
    temp = removeComments(inputin)
    print temp
    temp = functorizeSymbols(temp)
    print temp
    #Strip comments
    temp = cleaning.stripComments(temp)
    print temp
    #Strip whitespace so you can do the rest of the parsing
    temp = cleaning.stripWhiteSpace(temp)
    print temp
    #Tuck the functions inside thier parentheses
    temp = cleaning.tuckFunctions(temp)
    print temp
    #Consolidate Parentheses
    temp = cleaning.consolidateParens(temp)
    print temp
    testNAMESPACE = prototypes.NAMESPACE()
    testNAMESPACE.addBasicDCEC()
    testNAMESPACE.addBasicNumerics()
    testNAMESPACE.addBasicLogic()
    testNAMESPACE.addTextFunction("ActionType heal Agent")
    #testNAMESPACE.addTextFunction("Boolean B Agent Moment Boolean Certainty")
    addQuants = {}
    addAtomics = {}
    addFunctions = {}     
    tree,addQuants,addAtomics,addFunctions = tokenizeRandomDCEC(temp,testNAMESPACE)
    if tree == False:
        pass
    elif isinstance(tree,str):
        print tree
    else:
        tree.printTree()
        print tree.depthOf(),tree.widthOf(),addQuants,addAtomics,addFunctions
