from __future__ import annotations

from tree.node import Node


class NaiveBST:
    """Unbalanced binary search tree (deliberate naive baseline).

    Implements the same insert/delete/search interface as AVLTree, but
    performs no rebalancing. Under sorted insertion order the tree
    degenerates into a linked list, so all operations are implemented
    iteratively to avoid exceeding Python's recursion limit.
    """

    def __init__(self):
        self.root: Node | None = None

    def insert(self, key: int) -> None:
        """Insert a key into the tree (duplicates are ignored)."""

        if self.root is None:
            self.root = Node(key)
            return

        current = self.root

        while True:
            if key < current.key:
                if current.left is None:
                    current.left = Node(key)
                    return
                current = current.left
            elif key > current.key:
                if current.right is None:
                    current.right = Node(key)
                    return
                current = current.right
            else:
                # Ignore duplicate keys
                return

    def delete(self, key: int) -> None:
        """Delete a key from the tree (missing keys are ignored)."""

        parent: Node | None = None
        current = self.root

        while current is not None and current.key != key:
            parent = current
            current = current.left if key < current.key else current.right

        if current is None:
            return

        # Node with two children: replace with in-order successor
        if current.left is not None and current.right is not None:
            succ_parent = current
            succ = current.right

            while succ.left is not None:
                succ_parent = succ
                succ = succ.left

            current.key = succ.key

            # Now remove the successor node (has no left child)
            parent = succ_parent
            current = succ

        # Node with at most one child
        child = current.left if current.left is not None else current.right

        if parent is None:
            self.root = child
        elif parent.left is current:
            parent.left = child
        else:
            parent.right = child

    def search(self, key: int) -> bool:
        """Search for a key in the tree."""

        current = self.root

        while current is not None:
            if key == current.key:
                return True
            current = current.left if key < current.key else current.right

        return False
