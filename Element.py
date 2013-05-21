import os
import sys
import re # use regular expressions to match expected patterns with actual files
import numpy
import copy
from TemplateElement import TemplateElement

class Element(object):
    def __init__(self,path,template,parentElement=None):
        self.path = path # this is a string
        self.name = os.path.split(path)[1] # only the file/directory name, without the path
        self.template = template # this is an object of type "TemplateElement"        
        self.parent = parentElement        

        # lists and directories
        self.dirlist = [] # this is a list of direct children returned by os.listdir
        self.dirrellist = [] # this is a filtered version of self.dirlist, containing only elements that have corresponding entries in the template xml
        self.dirreldict = {} # relevant items that we care about - dictionary
        
        self.templatelist = template.childlist # this is a list of expected children as specified in the template xml
        self.templatedict = {} # this is a dictionary in which the key is the label from each template element, and the value is TRUE or FALSE based on whether that element actually exists        
        self.fulltemplatelist = [] # this is a list of tuples containing entries from self.templatedict for ALL children of the current node, whether direct or indirect
        
        self.level = 0 if self.parent==None else self.parent.level + 1
        
        self.csvchildrowtrack = template.csvchildrowtrack # if this variable is 1, then we need to loop over the child elements of this element for the rows of the csv
        self.csvcolumntrack = template.csvcolumntrack # if this variable is 1, then this element will constitute a column in the csv
        
        # only populate dirlist if the element is a folder
        if(os.path.isdir(self.path)):
            self.dirlist = os.listdir(path)
        
        # loop through list of expected children
        for templatechild in self.templatelist:
            pattern = templatechild.pattern
            x = re.compile(pattern)
            
            # initialize dictionary entry
            self.templatedict[templatechild.label] = (False, templatechild)
            
            # check whether the current template child exists by looping through the items that actually do exist
            for item in self.dirlist:
                if(x.search(item)):
                    self.templatedict[templatechild.label] = (True, templatechild)
                    
                    itempath = os.path.join(self.path,item)
                    newElement = Element(itempath,templatechild,self)
                    
                    self.dirrellist.append(newElement)
                    self.dirreldict[item] = newElement
                    
                    if(templatechild.countable > 0):
                        break
        
        #self.getFullTemplateList()
    
    def getFullTemplateList(self):
        outputlist = self.templatedict.items() # first add the direct children
        
        for templatechild in self.templatelist:
            outputlist.extend(templatechild.getFullTemplateList())
            
        return outputlist
        
        return outputlist