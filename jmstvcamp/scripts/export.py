#!/usr/bin/env python
import pymongo
import sys
import os.path
import xlwt
from jmstvcamp import scripting


class Exporter(object):

    def __init__(self):
        self.app = scripting.get_app()
        self.settings = self.app.settings
        self.users = self.settings.users
        self.filename = sys.argv[2]

    def export(self):
        """export names"""
        people = self.users.get_attend("yes")

        wb = xlwt.Workbook()
        ws = wb.add_sheet('Teilnehmer')
        i=0
        for row in people:
            ws.write(i,0,row['name'])
            ws.write(i,1,row.get('organization',''))
            i = i +1

        wb.save(self.filename)

if __name__=="__main__":
    exporter = Exporter()
    exporter.export()



