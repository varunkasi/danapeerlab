import objc


def __len__(self):
    return self.length()

def __getitem__(self, idx):
    if isinstance(idx, slice):
        raise ValueError(idx)
    return self.indexAtPosition_(idx)

def __add__(self, value):
    return self.indexPathByAddingIndex_(value)


objc.addConvenienceForSelector(b'length', [
    ('__len__', __len__),
])
objc.addConvenienceForSelector(b'indexAtPosition:', [
    ('__getitem__', __getitem__),
])
objc.addConvenienceForSelector(b'indexPathByAddingIndex:', [
    ('__add__', __add__),
])
