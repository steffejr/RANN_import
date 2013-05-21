import Visit
import os.path
import warnings
import string

class Subject(object):

    def __init__(self, index, subid):
        self.index = index
        self.subid = subid
        self.path = os.path.join(self.index.path, subid)
        self.visitlist = []
        self.visits = {}
        if not os.path.exists(self.path):
            os.makedirs(self.path, 0775)
        self.findvisits()

    def findvisits(self):
        
        'Returns a list of visit objects at the subject dir'

        try:
            visitFiles = os.listdir(self.path)
        except:
            warnings.warn("\nCould not list files in: " + self.path)
            return

        for visitFile in visitFiles:
            fulldir = os.path.join(self.path, visitFile)
            if (not os.path.isdir(fulldir)):
                continue
            m = self.index.config.__visitfolderREC__.match(visitFile)
            if m:
                newvisit = Visit.Visit(self, m.group(0))
            else:
                raise Exception('could not parse ' + fulldir + '\n with regex\n' + self.index.config.__visitfolderRE__ + '\n Should it be in this directory?\n')
            self.visitlist.append(newvisit)
            self.visits[newvisit.visid] = newvisit

    def add_visit(self, visid, warn=False):
        m = self.index.config.__visitfolderREC__.match(visid)
        if not m:
            warnings.warn('Did not create visit with visid ' + visid + '\n::visit Regex did not match.\n' + 'Regex:: ' + self.index.config.__visitfolderRE__)
            return False
        if (visid not in self.visits):
            newvisit = Visit.Visit(self, visid)
            self.visitlist.append(newvisit)
            self.visits[newvisit.visid] = newvisit
            return True
        elif warn == True:
            warnings.warn('Did not create visit with visid ' + visid + '::Already Exists.')
            return False


    def __str__(self):
        outstring = 'Subject: {}\n\t'.format(self.subid)
        visit_text = '\n\t'.join([x.__str__().replace('\n', '\n\t') for x in self.visitlist])
        return outstring + visit_text

    def __str_concise__(self):
        outstring = 'Subject: {}\n\t'.format(self.subid)
        visit_text = '\n\t'.join([x.__str_concise__().replace('\n', '\n\t') for x in self.visitlist])
        return outstring + visit_text


