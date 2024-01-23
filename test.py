import multiprocessing
from multiprocessing import Manager


class ParentClass:
    def __init__(self, parentStuffList_X):
        self.parentStuffList = parentStuffList_X


class CallingClass(ParentClass):
    def __init__(self):
        ParentClass.__init__(self, ["foo", "bar", "oh dear!"])
        try:
            manager = getattr(type(self), "manager")
        except AttributeError:
            manager = type(self).manager = Manager()
        self._whole_hashmap = manager.dict()

    def parallelMethod(self, stuffPassed):
        # let's explore the data in the parent
        # is the parent list different for every process?
        print(str(id(self.parentStuffList)))

    def doTheHardWork(self):
        stuffToPassList = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
        ]  # not bothered by you, yet!

        pool = multiprocessing.Pool(4)
        for _ in pool.starmap(self.parallelMethod, stuffToPassList):
            pass


if __name__ == "__main__":
    callingClass = CallingClass()

    # Call this multiple times
    for i in range(3):
        callingClass.doTheHardWork()
        print("..............................")
