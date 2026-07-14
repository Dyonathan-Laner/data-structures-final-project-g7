class Node:
    def __init__(self, key: int):
        self.key = key

        self.left = None
        self.right = None

        self.height = 1

        self.size = 1

        self.aggregate = 1