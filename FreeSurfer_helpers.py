import os
import sys

def fsID_from_visit(visit):
    subid = visit.subject.subid
    visid = visit.visid

    subid_int = int(subid.replace("P",""))
    visid_int = int(visid.replace("S",""))
    fsID = "{0}_{1}_RANN".format(str(subid_int),str(visid_int))

    return fsID
