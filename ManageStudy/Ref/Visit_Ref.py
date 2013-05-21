class Visit_Ref(object):

    def __init__(self, subid=None, visid=None, BirthDate=None, Gender=None, VisitDateTime=None, exclude=None, Performance=None):
        self.subid = subid
        self.visid = visid
        self.BirthDate = BirthDate
        self.VisitDateTime = VisitDateTime
        self.Gender = Gender
        self.Performance = Performance
        self.exclude = exclude

    def merge_both(self, other_visit_ref):
        self.BirthDate = self.test_merge_item(self.BirthDate, other_visit_ref.BirthDate)
        other_visit_ref.BirthDate = self.BirthDate
        self.Gender = self.test_merge_item(self.Gender, other_visit_ref.Gender)
        other_visit_ref.Gender = self.Gender


    @staticmethod
    def overwrite_merge_item(item, other_item):
        'merge items, overwriting when available'
        if other_item == None:
            return item
        else:
            return other_item


    @staticmethod
    def test_merge_item(item, other_item):
        'merge items if equal, or if one is None, else error'
        if item == other_item:
            return item
        elif item == None:
                return other_item
        elif other_item == None:
            return item
        else:
            print "Error in test_merge_item, items not equal and not null"
            raise AttributeError

    def __str__(self):
        subid = self.subid if self.subid != None else ''
        visid = self.visid if self.visid != None else ''
        BirthYear = self.BirthDate.strftime('%Y') if self.BirthDate != None else ''
        VisitDateTime = self.VisitDateTime.strftime('%m/%d/%Y') if self.VisitDateTime != None else ''
        Gender = self.Gender if self.Gender != None else ''
        exclude = 'Y' if self.exclude else 'N'
        Performance = self.Performance if self.Performance != None else ''
        return "subid:{0} visid:{1}  RefBirthYear:{2} Gender:{3} RefVisitDate:{4}  Exclude: {5} Performance: {6}".format(subid, visid, BirthYear, Gender, VisitDateTime, exclude, Performance)

