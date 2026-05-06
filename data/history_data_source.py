import os
import json

class HistoryDataSource:
    def __init__(self):
        self.file = os.path.join(os.path.dirname(__file__), 'history.json')
        self.images: list[str] = []
        self.read_file()
        
    def read_file(self):
        with open(self.file, 'r') as f:
            self.images = json.load(f)
        
        if(len(self.images) > 0):
            self.images = list(map(lambda x: os.path.join(os.path.expanduser("~/Desktop"), x), self.images))

        
 
    def write_file(self):
        with open(self.file, 'w') as f:
            json.dump(self.images, f)

history_data_source = HistoryDataSource()
        