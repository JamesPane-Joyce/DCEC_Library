def tuckFunctions(expression):
    """
    This function returns a string with all function calls of the form B(args)
    transformed into calls of the form (`B` args). This makes it easier to keep
    tokens on the same level.
    """
    firstParen = 0
    newIndex = 0
    adder = ""
    temp = ""
    #Find the parentheses
    while(firstParen < len(expression)):
        firstParen = expression.find("(",firstParen)
        if(firstParen == -1): break
        if (not(expression[firstParen-1] in [","," ","(",")"])):
            funcStart = firstParen-1
            while funcStart >= 0:
                if expression[funcStart] == "," or expression[funcStart] == "(":
                    funcStart += 1
                    break
                funcStart -= 1
            if(funcStart == -1): funcStart = 0
            funcname = expression[funcStart:firstParen]
            if funcname in ["not","negate"]:  
                adder = expression[newIndex:funcStart]+"("+funcname+",("
                closeParenPlace = getMatchingCloseParen(expression,funcStart+len(funcname))
                expression = expression[:funcStart]+expression[funcStart:closeParenPlace]+"))"+expression[closeParenPlace+1:]
                temp += adder
                newIndex += len(adder)-2
            else:
                adder = expression[newIndex:funcStart]+"("+funcname+","
                temp += adder
                newIndex += len(adder)-1
        firstParen += 1
    returner = temp + expression[newIndex:]
    returner = returner.replace("``","`")
    returner = returner.replace(",,",",")
    returner = returner.replace("`"," ")
    return returner

def stripWhiteSpace(expression):
    """
    This function strips any uneccesary whitespace from an expression. It also
    does some cleaning for different syntax. It then transforms all arguments
    seperated by whitespace or commas into arguments seperated by commas.
    Note- Commas are treated as whitespace
    """
    #Strip the whitespace around the function
    temp = expression.strip()
    #[ Have special notation, they are bracket-ish
    temp = temp.replace("["," [")
    temp = temp.replace("]","] ")
    #Treat commas and spaces identically
    temp = temp.replace(","," ")
    #Strip whitespace
    while True:
        lengthpre = len(temp)
        temp = temp.replace("  "," ")
        temp = temp.replace("( ","(")
        temp = temp.replace(" )",")")
        lengthpost = len(temp)
        if lengthpre == lengthpost:
            break
    #Find any touching parens, they should have a space between them
    temp = temp.replace(")(",") (")
    
    #I prefer to work with commas. Makes it less confusing.
    temp = temp.replace(" ",",")
    return temp

def stripComments(expression):
    place = expression.find("#")
    if place == -1:
        return expression
    else:
        return expression[:place]

def consolidateParens(expression):
    """
    Returns a string identical to the input except all superfluous parens are
    removed. It will also put parens around the outside of the expression, if it
    does not already have them. It will not detect a paren mismatch error.
    """
    temp = "("+expression+")"
    #list of indexes to delete
    deletelist = []
    #location of first paren
    firstParenA = 0
    #looks through entire expression
    while(firstParenA < len(temp)):
        #Find every occurance of a "(("
        firstParenA = temp.find("((",firstParenA)
        firstParenB = firstParenA+1
        if(firstParenA == -1): break
        #Get the matching close parens.
        secondParenA = getMatchingCloseParen(temp,firstParenA)
        secondParenB = getMatchingCloseParen(temp,firstParenB)
        #If both the open parens and the close parens match one set of parens is uneccesary, so delete them
        if(secondParenA == secondParenB+1):
            deletelist.append(firstParenA)
            deletelist.append(secondParenA)
        firstParenA += 1
    #Make the string to return    
    returner = ""
    for x in range(0,len(temp)):
        if x in deletelist: continue
        returner += temp[x]
    #Returns it
    return returner

def checkParens(expression):
    """
    This function checks to see if the expression has the right number of parentheses.
    It returns true if there are an equal amount of left and right parentheses, and false if there are not.
    """
    return expression.count("(") == expression.count(")")

def getMatchingCloseParen(inputStr,openParenIndex=0):
    parenCounter=1
    currentIndex=openParenIndex
    if currentIndex==-1:
        return False
    while parenCounter>0:
        closeIndex=inputStr.find(")",currentIndex+1)
        openIndex=inputStr.find("(",currentIndex+1)
        if (openIndex<closeIndex or closeIndex==-1) and openIndex!=-1:
            currentIndex=openIndex
            parenCounter+=1
        elif(closeIndex<openIndex or openIndex==-1) and closeIndex!=-1:
            currentIndex=closeIndex
            parenCounter-=1
        else:
            return False
    return currentIndex