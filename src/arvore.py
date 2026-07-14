"""Module providing a Binary Search Tree (BST) implementation.

This module contains the Node and MeuBST classes used for basic search tree
operations such as insertion, deletion, and search.
"""

class Node:
    """A class representing a node in a Binary Search Tree (BST).

    Attributes:
        key (int): The value stored in the node.
        left (Node): The left child node.
        right (Node): The right child node.
    """

    def __init__(self, key: int):
        """Initializes a Node with a given key.

        Args:
            key (int): The value to store in this node.
        """
        self.key = key
        self.left = None
        self.right = None


class MeuBST:
    """A simple Binary Search Tree (BST) implementation.

    Provides standard operations: insert, delete, and search.
    """

    def __init__(self):
        """Initializes an empty Binary Search Tree."""
        self.root = None

    def insert(self, key: int) -> None:
        """Inserts a new key into the BST.

        Args:
            key (int): The key to insert.
        """
        self.root = self._insert(self.root, key)

    def _insert(self, root: Node, key: int) -> Node:
        if root is None:
            return Node(key)
        if key < root.key:
            root.left = self._insert(root.left, key)
        elif key > root.key:
            root.right = self._insert(root.right, key)
        return root

    def search(self, key: int) -> bool:
        """Searches for a key in the BST.

        Args:
            key (int): The key to search for.

        Returns:
            bool: True if the key is found, False otherwise.
        """
        return self._search(self.root, key)

    def _search(self, root: Node, key: int) -> bool:
        if root is None:
            return False
        if root.key == key:
            return True
        if key < root.key:
            return self._search(root.left, key)
        return self._search(root.right, key)

    def delete(self, key: int) -> None:
        """Deletes a key from the BST.

        Args:
            key (int): The key to delete.
        """
        self.root = self._delete(self.root, key)

    def _delete(self, root: Node, key: int) -> Node:
        if root is None:
            return root
        if key < root.key:
            root.left = self._delete(root.left, key)
        elif key > root.key:
            root.right = self._delete(root.right, key)
        else:
            # Node with only one child or no child
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left

            # Node with two children: Get the inorder successor (smallest in the right subtree)
            temp = self._min_value_node(root.right)
            root.key = temp.key
            root.right = self._delete(root.right, temp.key)
        return root

    def _min_value_node(self, node: Node) -> Node:
        current = node
        while current.left is not None:
            current = current.left
        return current
