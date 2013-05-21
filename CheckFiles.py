import os
import sys
import csv

from TemplateElement import TemplateElement
from Element import Element
from xml.dom import minidom
   
xmldoc = minidom.parse("/share/studies/RANN/Config/checkfiles2.xml")
basedirectory = xmldoc.getElementsByTagName("filestructure")[0].getAttribute("pattern")[1:-1]
template = TemplateElement(xmldoc.firstChild.getElementsByTagName("filestructure")[0])
elem = Element(basedirectory,template)
