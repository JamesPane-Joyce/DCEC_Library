import highLevelParsing #This imports prototypes,utility, and cleaning too
import prototypes       #But just to make the code nice, import them again
import pickle           #Pickle module for saving

class DCECContainer:
    def __init__(self):
        self.namespace = prototypes.NAMESPACE()
        self.statements = []
        self.checkMap = {}
        
    def save(self,filename):
        namespaceOut = open(filename+".namespace","w")
        statementsOut = open(filename+".statements","w")
        pickle.dump(self.namespace,namespaceOut)
        pickle.dump(self.checkMap,statementsOut)
    
    def load(self,filename):
        nameIn = open(filename+".namespace","r")
        stateIn = open(filename+".statements","r")
        namespaceIn = pickle.load(nameIn)
        statementsIn = pickle.load(stateIn)
        if isinstance(namespaceIn,prototypes.NAMESPACE):
            self.namespace = namespaceIn
        else:
            return False
        if isinstance(statementsIn,dict):
            self.statements = statementsIn.keys()
            self.checkMap = statementsIn
    
    def printStatement(self,statement,expressionType = "S"):
        if isinstance(statement,str):
            return statement
        place = 0
        if expressionType == "S":
            temp = statement.createSExpression()
        elif expressionType == "F":
            temp = statement.createFExpression()
        else:
            print "ERROR: invalid notation type"
            return False
        for quant in self.namespace.quantMap.keys():
            if 'QUANT' in quant:
                temp = temp.replace(quant,self.namespace.quantMap[quant])
        return temp
    
    def addStatement(self,statement):
        addAtomics = {}
        addFunctions = {}
        addQuants = {}
        addee = statement
        if isinstance(addee,str):
            addee,addQuants,addAtomics,addFunctions = highLevelParsing.tokenizeRandomDCEC(addee,self.namespace)
            if isinstance(addee,bool) and not addee:
                print "ERROR: the statement "+str(statement)+" was not correctly formed."
                return False
            elif addee == "":
                return True
        elif isinstance(addee,highLevelParsing.Token):
            pass
        else:
            print "ERROR: the input "+str(statement)+" was not of the correct type."
            return False
        for atomic in addAtomics.keys():
            if isinstance(atomic,highLevelParsing.Token): continue #Tokens are not currently stored
            for potentialtype in range(0,len(addAtomics[atomic])):
                if not self.namespace.noConflict(addAtomics[atomic][0],addAtomics[atomic][potentialtype],0)[0]:
                    print "ERROR: The atomic "+atomic+" cannot be both "+addAtomics[atomic][potentialtype]+" and "+addAtomics[atomic][0]+". (This is caused by assigning different sorts to two atomics inline. Did you rely on the parser for sorting?)"
                    return False
        for function in addFunctions.keys():
            for item in addFunctions[function]:
                if item[0] == "?":
                    print "ERROR: please define the returntype of the inline function "+function
                    return False
                else:
                    self.namespace.addCodeFunction(function,item[0],item[1])         
        for atomic in addAtomics.keys():
            if isinstance(atomic,highLevelParsing.Token): continue #Tokens are not currently stored
            elif atomic in self.namespace.atomics.keys():
                if not self.namespace.noConflict(self.namespace.atomics[atomic],addAtomics[atomic][0],0)[0]:
                    print "ERROR: The atomic "+atomic+" cannot be both "+addAtomics[atomic][0]+" and "+self.namespace.atomics[atomic]+"."
                    return False
            else:
                self.namespace.addCodeAtomic(atomic,addAtomics[atomic][0])    
        for quant in addQuants.keys():
            if 'QUANT' in quant:
                self.namespace.quantMap[quant] = addQuants[quant]
        self.statements.append(addee)
        if not isinstance(addee,str):
            self.checkMap[addee.createSExpression()] = addee
        else:
            self.checkMap[addee] = addee
        return True


    def sortOf(self,statement):
        if isinstance(statement,str):
            return self.namespace.atomics.get(statement)
        if statement == None:
            return None
        if not statement.funcName in self.namespace.functions.keys():           
            return None
        tmpFunc = statement.funcName
        tmpArgs = statement.args
        tmpTypes = []
        for arg in tmpArgs:
            tmpTypes.append(self.sortOf(arg))
        for x in self.namespace.functions[tmpFunc]:
            if len(x[1]) != len(tmpTypes): continue
            else:
                returner = True
                for r in range(0,len(x[1])):
                    if not tmpTypes[r] == None and self.namespace.noConflict(tmpTypes[r],x[1][r],0)[0]:
                        continue
                    else:
                        returner = False
                        break
                if returner:
                    return x[0]
                else:
                    continue
        return None

    def sortsOfParams(self,statement):
        sorts=[]
        if isinstance(statement,str):
            return sorts
        if statement == None:
            return None
        if not statement.funcName in self.namespace.functions.keys():
            return None
        tmpFunc = statement.funcName
        tmpArgs = statement.args
        tmpTypes = []
        for arg in tmpArgs:
            tmpTypes.append(self.sortOf(arg))
        for x in self.namespace.functions[tmpFunc]:
            if len(x[1]) != len(tmpTypes): continue
            else:
                returner = True
                for r in range(0,len(x[1])):
                    if not tmpTypes[r] == None and self.namespace.noConflict(tmpTypes[r],x[1][r],0)[0]:
                        continue
                    else:
                        returner = False
                        break
                if returner:
                    return x[1]
                else:
                    continue
        return None

    
    def stupidSortDefine(self,sort,oldContainer):
        if sort in self.namespace.sorts.keys():
            return
        else:
            for x in oldContainer.namespace.sorts[sort]:
                self.stupidSortDefine(x,oldContainer)
            self.namespace.addCodeSort(sort,oldContainer.namespace.sorts[sort])
    
    #TODO replace with iterator
    def stupidLoop(self,token,functions,atomics,oldContainer):
        if isinstance(token,str):
            if oldContainer.sortOf(token)==None:
                self.stupidSortDefine(atomics[token][0],oldContainer)
                self.namespace.addCodeAtomic(token,atomics[token][0])
            else:
                self.stupidSortDefine(oldContainer.sortOf(token),oldContainer)
                self.namespace.addCodeAtomic(token,oldContainer.sortOf(token))
        else:
            if token.funcName in ["forAll","exists"]:
                pass
            elif oldContainer.sortOf(token)==None:
                argTypes = []
                for arg in token.args:
                    argTypes.append(atomics[arg][0])
                if token in atomics.keys():
                    self.stupidSortDefine(atomics[token][0],oldContainer)
                    for arg in argTypes:
                        self.stupidSortDefine(arg,oldContainer)
                    poss = []
                    map = {}
                    for x in oldContainer.namespace.functions[token.funcName]:
                        deep = 0
                        compat,depth = oldContainer.namespace.noConflict(x[0],atomics[token][0],0)
                        if not compat:
                            continue
                        else:
                            deep += depth
                        args = [atomics[arg][0] for arg in token.args]
                        if len(args) != len(x[1]):
                            continue
                        for y in range(0,len(x[1])):
                            compat,depth = oldContainer.namespace.noConflict(args[y],x[1][y],0)
                            deep += depth
                        poss.append(deep)
                        map[deep] = x
                    final = map[min(poss)]
                    self.namespace.addCodeFunction(token.funcName,final[0],final[1])
                else:
                    #This should never happen, but if it does make a new function
                    for x in functions[token.funcName]:
                        self.stupidSortDefine(x[0],oldContainer)
                        for y in x[1]:
                            self.stupidSortDefine(y,oldContainer)
                        self.namespace.addCodeFunction(token.funcName,x[0],x[1])
            else:
                self.stupidSortDefine(oldContainer.sortOf(token),oldContainer)
                for x in oldContainer.sortsOfParams(token):
                    self.stupidSortDefine(x,oldContainer)
                self.namespace.addCodeFunction(token.funcName,oldContainer.sortOf(token),oldContainer.sortsOfParams(token))
            for arg in token.args:
                self.stupidLoop(arg,functions,atomics,oldContainer)


    def tokenize(self,statement):
        if not isinstance(statement,str):
            return False
        dcecContainer=DCECContainer()
        stuff=highLevelParsing.tokenizeRandomDCEC(statement,self.namespace)
        if isinstance(stuff[0],bool) and not stuff[0]:
            return False
        elif stuff[0] == "":
            return True
        dcecContainer.stupidLoop(stuff[0],stuff[3],stuff[2],self)
        dcecContainer.addStatement(statement)
        return dcecContainer

if __name__ == "__main__":
    test = DCECContainer()
    test.namespace.addBasicDCEC()
    test.namespace.addBasicLogic()
    test.namespace.addTextFunction("ActionType heal Agent")
    #test.namespace.addTextFunction("Agent james")
    #test.namespace.addTextFunction("Boolean hello Object")
    #test.namespace.addTextFunction("Boolean equals Object Object")
    #test.namespace.addTextAtomic("Boolean earth")
    #test.namespace.addTextSort(raw_input("Enter a sort: "))
    #test.namespace.addTextSort(raw_input("Enter a sort: "))
    #test.namespace.addTextSort(raw_input("Enter a sort: "))
    #test.tokenize(raw_input("Enter an expression: "))
    test.addStatement(raw_input("Enter an expression: "))
    new = test.tokenize(raw_input("Enter an expression: "))
    #print new.statements[0].createSExpression(),new.namespace.atomics
    #test.save("TEST")
    print test.statements,test.namespace.atomics,test.namespace.functions
    print new.statements,new.namespace.atomics,new.namespace.functions
    #new.load("TEST")
    #print len(test.statements)
    for x in test.statements:
        #print test.printStatement(x)
        pass
    #print test.namespace.atomics
    #print test.namespace.functions
    #print test.namespace.sorts
    if len(test.statements) > 0:
        #print test.sortsOfParams(test.statements[0])
        #print test.sortOf(test.statements[0])
        pass