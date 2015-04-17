import cleaning

class NAMESPACE:
    def __init__(self):
        self.functions = {}
        self.atomics = {}
        self.sorts = {}
    def addCodeSort(self,name,inheritance = None):
        if inheritance == None: inheritance = []
        if not (isinstance(name,str) and isinstance(inheritance,list)):
            print "ERROR: function addCodeSort takes arguments of the form, string, list of strings"
            return False
        for thing in inheritance:
            if not thing in self.sorts.keys():
                print "ERROR: sort "+thing+" is not previously defined"
                return False
        if name in self.sorts.keys():
            return True
        self.sorts[name] = inheritance
        return True
    def addTextSort(self,expression):
        temp = expression.replace("("," ")
        temp = temp.replace(")"," ")
        temp = cleaning.stripWhiteSpace(temp)
        temp = temp.replace("`","")
        args = temp.split(",")
        if len(args) == 2:
            self.addCodeSort(args[1])
        elif len(args) > 2:
            self.addCodeSort(args[1],args[2:])
        else:
            print "ERROR: Cannot define the sort"
            return False
    def findAtomicType(self,name):
        if name in self.atomics.keys():
            return self.atomics[name]
    def addCodeFunction(self,name,returnType,argsTypes):
        item = [returnType,argsTypes]
        if name in self.functions.keys():
            if item in self.functions[name]:
                pass
            else:
                self.functions[name].append(item)
        else:
            self.functions[name] = [item]
        return True
    def addTextFunction(self,expression):
        temp = expression.replace("("," ")
        temp = temp.replace(")"," ")
        temp = cleaning.stripWhiteSpace(temp)
        temp = temp.replace("`","")
        args = temp.split(",")
        if args[0].lower() == "typedef":
            return self.addTextSort(expression)
        elif len(args) == 2:
            return self.addTextAtomic(expression)
        returnType = ""
        funcName = ""
        funcArgs = []
        #Find the return type
        if args[0] in self.sorts.keys():
            returnType = args[0]
            args.remove(args[0])
        #Find the function name
        for arg in args:
            if not arg in self.sorts.keys():
                funcName = arg
                args.remove(arg)
                break
        #Find the function args
        for arg in args:
            if arg in self.sorts.keys():
                funcArgs.append(arg)
        #Error Checking
        if returnType == "" or funcName == "" or funcArgs == []:
            print "ERROR: The function prototype was not formatted correctly."
            return False
        #Add the function
        return self.addCodeFunction(funcName,returnType,funcArgs)
    def addCodeAtomic(self,name,Type):
        atomic = Type
        if name in self.atomics.keys():
            if atomic in self.atomics[name]:
                return True
            else:
                print "ERROR: item "+name+" was previously defined as an "+self.atomics[name]+", you cannot overload atomics."
                return False
        else:
            self.atomics[name] = atomic
        return True
    def addTextAtomic(self,expression):
        temp = expression.replace("("," ")
        temp = temp.replace(")"," ")
        temp = cleaning.stripWhiteSpace(temp)
        temp = temp.replace("`","")
        args = temp.split(",")
        returnType = ""
        funcName = ""        
        #Find the return type
        for arg in args:
            if arg in self.sorts.keys():
                returnType = arg
                args.remove(arg)
                break
        #Find the function name
        for arg in args:
            if not arg in self.sorts.keys():
                funcName = arg
                args.remove(arg)
                break
        return self.addCodeAtomic(funcName,returnType)
    def addBasicDCEC(self):
        #The Basic DCEC Sorts
        self.addCodeSort("Object")
        self.addCodeSort("Agent",["Object"])
        self.addCodeSort("Self",["Object","Agent"])
        self.addCodeSort("ActionType",["Object"])
        self.addCodeSort("Event",["Object"])
        self.addCodeSort("Action",["Object","Event"])
        self.addCodeSort("Moment",["Object"])
        self.addCodeSort("Boolean",["Object"])
        self.addCodeSort("Fluent",["Object"])
        self.addCodeSort("Numeric",["Object"])
        self.addCodeSort("Set",["Object"])
        #The Basic DCEC Modal Functions
        self.addCodeFunction("C","Boolean",["Moment","Boolean"])
        self.addCodeFunction("B","Boolean",["Agent","Moment","Boolean"])
        self.addCodeFunction("K","Boolean",["Agent","Moment","Boolean"])
        self.addCodeFunction("P","Boolean",["Agent","Moment","Boolean"])
        self.addCodeFunction("I","Boolean",["Agent","Moment","Boolean"])
        self.addCodeFunction("D","Boolean",["Agent","Moment","Boolean"])
        self.addCodeFunction("S","Boolean",["Agent","Agent","Moment","Boolean"])
        self.addCodeFunction("O","Boolean",["Agent","Moment","Boolean","Boolean"])
        #Fluent Functions
        self.addCodeFunction("action","Action",["Agent","ActionType"])
        self.addCodeFunction("initially","Boolean",["Fluent"])
        self.addCodeFunction("holds","Boolean",["Event","Moment"])
        self.addCodeFunction("happens","Boolean",["Event","Moment"])
        self.addCodeFunction("clipped","Boolean",["Moment","Fluent","Moment"])
        self.addCodeFunction("initiates","Boolean",["Event","Fluent","Moment"])
        self.addCodeFunction("terminates","Boolean",["Event","Fluent","Moment"])
        self.addCodeFunction("prior","Boolean",["Moment","Moment"])
        self.addCodeFunction("interval","Fluent",["Moment","Boolean"])
        self.addCodeFunction("self","Self",["Agent"])
        self.addCodeFunction("payoff","Numeric",["Agent","ActionType","Moment"])
        #Logical Functions
        self.addCodeFunction("implies","Boolean",["Boolean","Boolean"])
        self.addCodeFunction("iff","Boolean",["Boolean","Boolean"])
        self.addCodeFunction("not","Boolean",["Boolean"])
        self.addCodeFunction("and","Boolean",["Boolean","Boolean"])
        #Time Functions
        self.addCodeFunction("lessOrEqual","Boolean",["Moment","Moment"])
    def addBasicLogic(self):
        #Logical Functions
        self.addCodeFunction("or","Boolean",["Boolean","Boolean"])
        self.addCodeFunction("xor","Boolean",["Boolean","Boolean"])
    def addBasicNumerics(self):
        #Numerical Functions
        self.addCodeFunction("negate","Numeric",["Numeric"])
        self.addCodeFunction("add","Numeric",["Numeric","Numeric"])
        self.addCodeFunction("sub","Numeric",["Numeric","Numeric"])
        self.addCodeFunction("multiply","Numeric",["Numeric","Numeric"])
        self.addCodeFunction("divide","Numeric",["Numeric","Numeric"])
        self.addCodeFunction("exponent","Numeric",["Numeric","Numeric"])
        #Comparison Functions
        self.addCodeFunction("greater","Boolean",["Numeric","Numeric"])
        self.addCodeFunction("greaterOrEqual","Boolean",["Numeric","Numeric"])
        self.addCodeFunction("less","Boolean",["Numeric","Numeric"])
        self.addCodeFunction("lessOrEqual","Boolean",["Numeric","Numeric"])
        self.addCodeFunction("equals","Boolean",["Numeric","Numeric"])        
    def noConflict(self,type1,type2):
        if type1 == "?":
            return True
        elif type1 == type2:
            return True
        elif type2 in self.sorts[type1]:
            return True
        return False
    def printNAMESPACE(self):
        for item in self.sorts.keys():
            print item,self.sorts[item]
        for item in self.functions:
            print item,self.functions[item]
        for item in self.atomics:
            print item,self.atomics[item]
        


if __name__ == "__main__":
    this = NAMESPACE()
    expression = raw_input("Enter Prototype: ")
    this.addTextFunction(expression)
    this.addBasicDCEC()
    this.printNAMESPACE()