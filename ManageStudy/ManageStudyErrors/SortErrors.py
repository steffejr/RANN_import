class CreateSeriesError(Exception):
    def __init__(self, source, description='CreateSeriesError'):
        self.source = source
        self.description = description
    def __str__(self):
        infostring = '{0}: cannot create series:\n{1}\n'.format(self.description, self.source)
        return infostring

class MergeSeriesError(Exception):
    def __init__(self, source, dest, description='MergeSeriesError'):
        self.source = source
        self.dest = dest
        self.description = description
    def __str__(self):
        infostring = '%s: cannot merge series:\n%s\nand\n%s\n' % (self.description, self.source, self.dest)
        return infostring

class FindUnsortedSeriesError(Exception):
    def __init__(self, source, dest, description=''):
        self.source = source
        self.dest = dest
        self.description = description
    def __str__(self):
        infostring = '%s: found series with same IDs but not identical: \n%s\nand\n%s\n' % (self.description, self.source, self.dest)
        return infostring

class FindcheeSeriesError(Exception):
    def __init__(self, source, dest, description=''):
        self.source = source
        self.dest = dest
        self.description = description
    def __str__(self):
        infostring = '%s: found series with same IDs but not identical: \n%s\nand\n%s\n' % (self.description, self.source, self.dest)
        return infostring
