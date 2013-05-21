class Bad_Column_Entry_Exception(Exception):
    def __init__(self, entry, column, why=''):
        self.entry = entry
        self.column = column
        self.why = why
    def __str__(self):
        infostring = 'Column {0.column} with entry "{0.entry}" is not allowed because: {0.why}'.format(self)
        return infostring
