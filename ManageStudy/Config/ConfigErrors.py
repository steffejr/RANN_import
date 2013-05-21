class MissingIndexError(Exception):
    def __init__(self, index, description='MissingIndexError'):
        self.index = index
        self.description = description
    def __str__(self):
        infostring = 'Path for Index %s specified in main.cfg not in main.cfg:\n' % (self.index, self.value)
        return infostring

class BadIndexPathError(Exception):
    def __init__(self, index, value, description='BadIndexPathError'):
        self.index = index
        self.value = value
        self.description = description
    def __str__(self):
        infostring = 'Bad Path: Index %s with value %s specified in main.cfg could not be located:\n' % (self.index, self.value)
        return infostring
