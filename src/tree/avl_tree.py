from __future__ import annotations

from tree.node import Node


class AVLTree:
    """Augmented AVL Tree."""

    def __init__(self):
        self.root: Node | None = None

    def insert(self, key: int) -> None:
        """Insert a key into the AVL tree."""

        self.root = self._insert(self.root, key)

    def delete(self, key: int) -> None:
        """Delete a key from the AVL tree."""

        self.root = self._delete(self.root, key)

    def search(self, key: int) -> bool:
        """Search for a key in the AVL tree."""

        return self._search(self.root, key)

    def select(self, index: int) -> int | None:
        """Return the index-th smallest key."""

        node = self._select(self.root, index)

        return None if node is None else node.key

    def range_agg(self, start: int, end: int) -> int:
        """Return the number of keys in the interval [start, end]."""

        if start > end:
            return 0

        return self.rank(end + 1) - self.rank(start)
    
    def inorder(self) -> list[int]:
        """Return the keys in sorted order."""

        result: list[int] = []

        def traverse(node: Node | None) -> None:
            if node is None:
                return

            traverse(node.left)
            result.append(node.key)
            traverse(node.right)

        traverse(self.root)

        return result

    def rank(self, key: int) -> int:
        """Return the rank of a key."""

        return self._rank(self.root, key)

    def _insert(self, node: Node | None, key: int) -> Node:
        """Insert a key into a subtree."""

        if node is None:
            return Node(key)

        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            # Ignore duplicate keys
            return node

        self._update(node)

        return self._rebalance(node)

    def _delete(self, node: Node | None, key: int) -> Node | None:
        """Delete a key from a subtree."""

        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key)

        elif key > node.key:
            node.right = self._delete(node.right, key)

        else:
            # Node with only one child or no child
            if node.left is None:
                return node.right

            if node.right is None:
                return node.left

            # Node with two children
            successor = self._min_value_node(node.right)

            node.key = successor.key

            node.right = self._delete(
                node.right,
                successor.key,
            )

        self._update(node)

        return self._rebalance(node)

    def _search(self, node: Node | None, key: int) -> bool:
        """Search for a key in a subtree."""

        if node is None:
            return False

        if key == node.key:
            return True

        if key < node.key:
            return self._search(node.left, key)

        return self._search(node.right, key)

    def _rebalance(self, node: Node) -> Node:
        """Rebalance an AVL subtree."""

        balance = self._balance_factor(node)

        # Left heavy
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right heavy
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rotate_left(self, node: Node) -> Node:
        """Perform a left rotation."""

        new_root = node.right
        transferred_subtree = new_root.left

        new_root.left = node
        node.right = transferred_subtree

        self._update(node)
        self._update(new_root)

        return new_root

    def _rotate_right(self, node: Node) -> Node:
        """Perform a right rotation."""

        new_root = node.left
        transferred_subtree = new_root.right

        new_root.right = node
        node.left = transferred_subtree

        self._update(node)
        self._update(new_root)

        return new_root

    def _update(self, node: Node) -> None:
        """Update all augmented information stored in a node."""

        node.height = 1 + max(
            self._height(node.left),
            self._height(node.right),
        )

        node.size = (
            1
            + self._size(node.left)
            + self._size(node.right)
        )

        # Group 7: range_agg is based on counting.
        # The aggregate stores the number of nodes in the subtree.
        node.aggregate = node.size

    def _balance_factor(self, node: Node) -> int:
        """Return the AVL balance factor."""

        return (
            self._height(node.left)
            - self._height(node.right)
        )

    def _height(self, node: Node | None) -> int:
        """Return the height of a node."""
        return 0 if node is None else node.height

    def _size(self, node: Node | None) -> int:
        """Return the size of a subtree."""
        return 0 if node is None else node.size
    
    def _min_value_node(self, node: Node) -> Node:
        """Return the node with the smallest key in a subtree."""

        current = node

        while current.left is not None:
            current = current.left

        return current
    
    def _rank(self, node: Node | None, key: int) -> int:
        """Return the number of keys smaller than the given key."""

        if node is None:
            return 0

        if key <= node.key:
            return self._rank(node.left, key)

        return (
            self._size(node.left)
            + 1
            + self._rank(node.right, key)
        )
    
    def _select(self, node: Node | None, index: int) -> Node | None:
        """Return the node containing the index-th smallest key."""

        if node is None:
            return None

        left_size = self._size(node.left)

        if index < left_size:
            return self._select(node.left, index)

        if index > left_size:
            return self._select(
                node.right,
                index - left_size - 1,
            )

        return node

