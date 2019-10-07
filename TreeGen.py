'''  L-System Generator

  inspired by Janne Kaasalainen's work from http://blog.studioe18.com/69/visualizing-l-systems/
  
  This program allows you to generate trees by adjusting the values on the UI which appears when the program run'''  
  
import maya.cmds as cmds
import math as math
import functools


def actionProc(*pArgs):
    '''Starting action'''
    print "Start action" 
   
def cancelProc(*pArgs):
    '''creating the cancel callback function'''
    print "Action is cancelled"
    cmds.deleteUI("myWindowID")

def createUI(pWindowTitle, pApplyCallback):
    ''' Creating the UserInterface

	windowTitle		    : title of the window
	ApplyCallback		: function called when button is pressed, therefore inclusion of functiontools.partial
	'''
   
    windowID = 'myWindowID'

    if cmds.window( windowID, exists=True ):
        cmds.deleteUI( windowID )

    cmds.window( windowID, title=pWindowTitle, sizeable=True, resizeToFitChildren=True)
    cmds.columnLayout( adjustableColumn=True )
    
    #create logo
    logopath = cmds.internalVar(upd=True)+"icons/43.png"
    cmds.image(w=443, h=222, image=logopath)
    cmds.separator( h=10, style='none')    
    cmds.text(label = "TREE GENERATOR") 
    cmds.separator( h=10, style='none') 
    
    #create options for materials
    type = cmds.checkBoxGrp( numberOfCheckBoxes=3, label='Type:   ', labelArray3=['One', 'Two', 'Three'], value1 = True)
    materials = cmds.checkBoxGrp( numberOfCheckBoxes=3, label='Materials For Branches:   ', labelArray3=['Phong', 'Lambert', 'Blinn'], value1 = True)
    materialsleaf = cmds.checkBoxGrp( numberOfCheckBoxes=3, label='Materials For Leafs:   ', labelArray3=['Phong', 'Lambert', 'Blinn'], value1 = True)  
    cmds.separator( h=10, style='none')  
    cmds.text(label = "ADJUST TREE") 
    cmds.separator( h=10, style='none')
     
    #create options for angle rotation, iterations and step length
    rotateAngle = cmds.intSliderGrp(label='RotateAngle:   ', minValue=1, maxValue=50, value=25, field=True)
    iterations = cmds.intSliderGrp(label='Iterations:   ', minValue=1, maxValue=5, value=4, field=True)
    stepLength = cmds.intSliderGrp( label='StepLength:   ', minValue=0, maxValue=5, value=1, field=True )
    
    cmds.separator( h=10, style='none')
    
    #create options to colour branches and leafs
    colourTree = cmds.colorInputWidgetGrp( label='Tree Colour:', rgb=(0.109, 0.056, 0.023), columnAlign=(1, 'center'))
    colourLeaf = cmds.colorInputWidgetGrp( label='Leaf Colour:', rgb=(0.109, 0.382, 0.023), columnAlign=(1, 'center')) 
    cmds.separator( h=10, style='none')
    
    #apply adujustment
    cmds.button(label = "Apply", command = functools.partial(pApplyCallback, iterations, stepLength, rotateAngle, materials, colourTree, colourLeaf, materialsleaf, type))
    
    cmds.separator( h=10, style='none')
    
    #cancel the window
    cmds.button(label = "Cancel", command = cancelProc)
    cmds.showWindow()
    cmds.window(windowID, e =True, width = 400)

#Xiaosong Yang code starts here 
def addRule(ruleDict, replaceStr, newStr ):
	''' add a new rule to the ruleDict

	ruleDict		: the dictionary holding the rules
	replaceStr		: the old character to be replaced
	newStr			: the new string replacing the old one
	'''
	ruleDict[ replaceStr ] = newStr

def iterate(baseString, numIterations, ruleDict):
	''' following the rules, replace old characters with new ones

	baseString		: start string
	numIterations	: how many times the rules will be used
	ruleDict		: the dictionary holding the rules
	return			: return the final expanded string
	'''
	while numIterations > 0:
		replaced = ""
		for i in baseString:
			replaced = replaced + ruleDict.get(i,i)
		baseString = replaced
		numIterations-=1
	return baseString
#Xiaosong Yang code ends here 

def createBranch(startPoint, length, anglex, anglez):
	''' create a cylinder for each branch

	startPoint	: startPoint, base point for the new cylinder
	length		: step size for growing
	angleX		: the rotation angle for branching, used for calculating the axis of the cylinder
	angleZ		: the rotation angle for branching, used for calculating the axis of the cylinder
	return		: return the created object
	'''
#maths implementation to make it 3D: "math.sin(radiansZ), math.cos(radiansZ)*math.cos(radiansX), math.cos(radiansZ)*math.sin(radiansX)"
	
	radiansX = anglex * math.pi /180.0
	radiansZ = anglez * math.pi /180.0
	branch = cmds.polyCylinder(axis=[math.sin(radiansZ), math.cos(radiansZ)*math.cos(radiansX), math.cos(radiansZ)*math.sin(radiansX)], r=length/5.0, height=length)
	cmds.move(startPoint[0] + 0.5*length*math.sin(radiansZ), startPoint[1] + 0.5*length*math.cos(radiansZ)*math.cos(radiansX),startPoint[2]+0.5*length*math.cos(radiansZ)*math.sin(radiansX))
	return branch[0]
	

def calculateVector( length, rotationx, rotationz ):
	'''calculate the vector from the start point to the end point for each branch

	length		: step size for growing
	rotationX	: the rotation angle for branching
	rotationZ	: the rotation angle for branching
	return		: return the vector from start point to end point
	'''
	radiansX = math.pi * rotationx / 180
	radiansZ = math.pi * rotationz / 180
	return [length* math.sin(radiansZ), length* math.cos(radiansZ)*math.cos(radiansX), length*math.cos(radiansZ)*math.sin(radiansX)]	

def createModel( actionString, length, turn):
    '''create the 3D model based on the actionString, following the characters in the string, 
    one by one, grow the branches, and finally group all branches together into one group

      actionString	: instructions on how to construct the model
      length		: step size for growing
      turn			: the rotation angle for branching
      return		: return the group of all the branches
    '''
    inputString = actionString
    index = 0		# Where at the input string we start from
    anglex = 0	
    anglez = 0	# Degrees, nor radians
    currentPoint = [0.0, 0.0, 0.0]	# Start from origin
    coordinateStack = []	# Stack where to store coordinates
    anglexStack = []	
    anglezStack = []		# Stack to store angles
    branchList = []
    leafList = []

    while ( index < len( inputString ) ):
        if inputString[index] == 'F':
            branch = createBranch(currentPoint, length, anglex, anglez)
            branchList.append(branch)
            vector = calculateVector( length, anglex, anglez )
            newPoint = [currentPoint[0] + vector[0], currentPoint[1] + vector[1], currentPoint[2] + vector[2]]
            currentPoint = newPoint	# update the position to go on growing from the new place
        elif inputString[index] == '-':
            anglex = anglex - turn
        elif inputString[index] == '+':
            anglex = anglex + turn
        elif inputString[index] == '|':
            anglez = anglez - turn
        elif inputString[index] == '/':
            anglez = anglez + turn
        elif inputString[index] == 'L':
            leaf = cmds.sphere(r=1)
            cmds.move( newPoint[0], newPoint[1], newPoint[2]) #adjusted currentPoint too newPoint
            leafList.append(leaf[0])          
        elif inputString[index] == 'D':
            leaf = cmds.sphere(r=1.5)
            cmds.move( currentPoint[0], currentPoint[1], currentPoint[2]) #adjusted currentPoint too newPoint
            leafList.append(leaf[0]) 
        elif inputString[index] == 'S':
            leaf = cmds.sphere(r=0.5)
            cmds.move( currentPoint[0], currentPoint[1], currentPoint[2]) #adjusted currentPoint too newPoint
            leafList.append(leaf[0]) 
        elif inputString[index] == '[': # add new branches, save the old position into the stack
            coordinateStack.append( currentPoint )
            anglexStack.append( anglex )
            anglezStack.append( anglez )
        elif inputString[index] == ']': # finish the branches, get back to the root position
            currentPoint = coordinateStack.pop()
            anglex = anglexStack.pop()
            anglez = anglezStack.pop()
        # Move to the next drawing directive
        index = index + 1
    groupName = cmds.group(branchList, n = "tree")
    groupleafName = cmds.group(leafList, n = "leafs")
    return groupName, groupleafName
	
def setMaterial(objName, materialType, colour, leafmodelGroup, colourleaf, materialTypeLeaf):
   '''Assigns a material to the object 'objectName'

   objectName      : is the name of a 3D object in the scene which is the branch
   materialType    : is string that specifies the type of the sufrace shader, 
                     this can be any of Maya's valid surface shaders such as:
                     lambert, blin, phong, etc. 
   colour          : is a 3-tuple of (R,G,B) and (H,S,V) values within the range [0,1]
                     which specify the colour of the material
                     colour=(0.024, 0.369, 0.024)):
   leafmodelGroup  : is the name of a 3D object in the scene which is the leaf
   colourleaf      : is a 3-tuple of (R,G,B) and (H,S,V) values within the range [0,1]
                     which specify the colour of the material
   materialTypeLeaf: is string that specifies the type of the sufrace shader, 
                     this can be any of Maya's valid surface shaders such as:
                     lambert, blin, phong, etc. 
   On Exit         : 'objName' has been assigned a new material according to the 
                     input values of the procedure, and a tuple (of two strings) 
                     which contains the new shading group name, and the new shader
                     name is returned to the caller
	'''

   # branch material and colour
   setName = cmds.sets(name='_MaterialGroup_', renderable=True, empty=True)
   shaderName = cmds.shadingNode(materialType, asShader=True)
   cmds.setAttr(shaderName+'.color', colour[0], colour[1], colour[2], type='double3')
   cmds.surfaceShaderList(shaderName, add=setName)
   cmds.sets(objName, edit=True, forceElement=setName)
   
   # leaf material and colour
   setLeafName = cmds.sets(name='_MaterialLeafGroup_', renderable=True, empty=True)
   shaderLeafName = cmds.shadingNode(materialTypeLeaf, asShader=True)
   cmds.setAttr(shaderLeafName+'.color', colourleaf[0], colourleaf[1], colourleaf[2], type='double3')
   cmds.surfaceShaderList(shaderLeafName, add=setLeafName)
   cmds.sets(leafmodelGroup, edit=True, forceElement=setLeafName)
   
	
def buildTree(piterations,pstepLength,protateAngle, pmaterials, pcolourTree, pcolourLeaf, pmaterialsleaf, ptype, *pargs):
	''' add the rules, initialise the control parameters, such as 
	iteration numbers, branch rotation angle, step size of growing, materials, colour and type'''
	
	#type of tree
	type = cmds.checkBoxGrp(ptype, query=True, valueArray3=True)
	
	#type of material for branch and leaf
	materials = cmds.checkBoxGrp(pmaterials, query=True, valueArray3=True)
	
	print materials
	
	if materials[0]:
	    material = 'phong'
	elif materials[1]:
	    material = 'lambert'
	else:
	    material = 'blinn'
	    	    
	materialsleaf = cmds.checkBoxGrp(pmaterialsleaf, query=True, valueArray3=True)
	
	print materialsleaf
	
	if materialsleaf[0]:
	    materialsleaf = 'phong'
	elif materialsleaf[1]:
	    materialsleaf = 'lambert'
	else:
	    materialsleaf = 'blinn'
	    	        
	#colour adjustments for branch and leaf
	colourTree=[]   
	 
	colourTree = cmds.colorInputWidgetGrp(pcolourTree, query =True, rgbValue = True)
	
	colourLeaf=[]
	
	colourLeaf = cmds.colorInputWidgetGrp(pcolourLeaf, query =True, rgbValue = True)
	
	#query for length, iterations and angle
	stepLength = cmds.intSliderGrp(pstepLength, query=True, value=True)
	rotateAngle = cmds.intSliderGrp(protateAngle, query=True, value=True)
	iterations = cmds.intSliderGrp(piterations, query=True, value=True)
    	
	# clear up the scene
	cmds.select(all=True)
	cmds.delete()
	
	#Lsystems
	type = cmds.checkBoxGrp(ptype, query=True, valueArray3=True)
	
	''' inspired by "http://algorithmicbotany.org/papers/abop/abop-ch1.pdf" '''  
	
	if type[0]:
	    tree = ruleDictionary = {} 
	    ruleDictionary = {}
	    actionString = ""	
	    addRule(ruleDictionary, "X", "F[+FXL][|XL][/XL][-FX]+F[-FX]+L" ) 
	    addRule(ruleDictionary, "F", "FF" )
	elif type [1]:
	    tree = ruleDictionary = {} 
	    actionString = ""	
	    addRule(ruleDictionary, "X", "FF[+XL]FF[-XL]+/XD" )  
	    addRule(ruleDictionary, "F", "FF" )
	else:
	    tree = ruleDictionary = {} 
	    actionString = ""	
	    addRule(ruleDictionary, "X", "F-[[XS]/+XS]+F[+|FXL]-X" )  
	    addRule(ruleDictionary, "F", "FF" )
        
        
   
	''' set growing parameters
	#iterations = 5
	#stepLength = 1
	#rotateAngle = 25 
    '''
	axiom = "X"
	
	# create the action string
	finalString=iterate(axiom, iterations, ruleDictionary)
	
	# create the 3D model
	modelGroup, groupleafName = createModel(finalString, stepLength, rotateAngle)
	
	# set the color to green
	setMaterial(modelGroup, material, colourTree, groupleafName, colourLeaf, materialsleaf)

# main program, start with the function buildTree()
if __name__ == "__main__":
	createUI("tree generator", buildTree)
	

