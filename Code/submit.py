#! python
import csv, csvconvert

class Execute():
    def __init__(self, parent):
        self.files = parent.input.getFiles()
        self.location = parent.output.getLocation()
        self.index = 0

    def __call__(self):
        for file in self.files:
            csvconvert.start(file, self.location)
            self.index = self.index + 1
            yield self.index
