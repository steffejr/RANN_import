import os
import sys
import numpy
from xml.dom import minidom

class TemplateElement(object):
    def __init__(self,inputNode,parentElement=None,DEBUG=False):
        self.type = inputNode.getAttribute("type")
        self.fixed = inputNode.getAttribute("fixed")
        self.pattern = inputNode.getAttribute("pattern")
        self.label = inputNode.getAttribute("label")
        self.countable = numpy.int32(inputNode.getAttribute("countable"))
        self.parent = parentElement
        
        if(self.parent):
            self.fullpattern = os.path.join(self.parent.fullpattern[:-1],inputNode.getAttribute("pattern")[1:]) # make sure to strip extra ^'s and $'s
        else:
            self.fullpattern = self.pattern

        self.childlist = []
        self.children = {}
        self.level = 0 if self.parent==None else self.parent.level + 1
        
        self.csvchildrowtrack = 0
        if(numpy.int32(inputNode.getAttribute("csvrowtrack"))==1 and self.level > -1):
            self.parent.csvchildrowtrack = 1

        self.csvcolumntrack = numpy.int32(inputNode.getAttribute("csvcolumntrack"))
        
        if(self.type == "folder" or self.label=="root"):
            childNodes = [n for n in inputNode.childNodes if not isinstance(n, minidom.Text)]
            for node in childNodes:
                newElement = TemplateElement(node,self)
                self.childlist.append(newElement)
                self.children[newElement.label] = newElement
        
    def prettyPrint(self):
        string = ""
        for i in range(self.level):
            string = string + "\t"
        
        string = string + self.label + " {" + self.pattern + "}" + " {level " + str(self.level) + "}"  
        print string
        
        for child in self.childlist:
            child.prettyPrint()