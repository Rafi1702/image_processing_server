import os
import json
import aiofiles

class HistoryDataSource:
    def __init__(self):
        self.file = os.path.join(os.path.dirname(__file__), 'history.json')
        self.images: list[str] = []

    async def read_file(self):
        
        if not os.path.exists(self.file):
            self.images = []
            return

        async with aiofiles.open(self.file, mode='r') as f:
            content = await f.read()
            self.images = json.loads(content)
        
        if len(self.images) > 0:
            desktop_path = os.path.expanduser("~/Desktop")
            self.images = [os.path.join(desktop_path, img) for img in self.images]

    async def write_file(self):
        async with aiofiles.open(self.file, mode='w') as f:
            await f.write(json.dumps(self.images))

history_data_source = HistoryDataSource()
        