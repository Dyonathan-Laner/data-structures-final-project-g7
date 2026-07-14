"""Unit tests for the augmented AVL Tree implementation.

This module validates the correctness of the AVLTree class, including basic BST
operations (insert, delete, search), self-balancing properties (height-balance,
rotations), augmented properties (size, aggregate), and order-statistics
queries (rank, select, range_agg).
"""

import pytest
from tree.avl_tree import AVLTree
from tree.node import Node


def get_balance(node: Node | None) -> int:
    """Helper function to calculate the balance factor of a node.

    Args:
        node (Node | None): The node to evaluate.

    Returns:
        int: The balance factor (height of left subtree - height of right subtree).
    """
    if node is None:
        return 0
    left_height = node.left.height if node.left else 0
    right_height = node.right.height if node.right else 0
    return left_height - right_height


def verify_avl_invariants(node: Node | None) -> None:
    """Helper function to recursively verify AVL tree and augmented invariants.

    Invariants checked:
        1. BST property: left child key < node key < right child key.
        2. Height property: node.height = 1 + max(left height, right height).
        3. Balance factor property: -1 <= balance factor <= 1.
        4. Size property: node.size = 1 + left size + right size.
        5. Aggregate property: node.aggregate = node.size (Group 7 count aggregation).

    Args:
        node (Node | None): The node to start validation from.
    """
    if node is None:
        return

    # 1. BST property
    if node.left:
        assert node.left.key < node.key, f"BST property violated: Left key {node.left.key} >= parent key {node.key}"
    if node.right:
        assert node.right.key > node.key, f"BST property violated: Right key {node.right.key} <= parent key {node.key}"

    # Recursively check subtrees
    verify_avl_invariants(node.left)
    verify_avl_invariants(node.right)

    # 2. Height property
    left_height = node.left.height if node.left else 0
    right_height = node.right.height if node.right else 0
    expected_height = 1 + max(left_height, right_height)
    assert node.height == expected_height, f"Height mismatch at key {node.key}: got {node.height}, expected {expected_height}"

    # 3. Balance factor
    balance = get_balance(node)
    assert -1 <= balance <= 1, f"Balance factor violated at key {node.key}: balance is {balance}"

    # 4. Size property
    left_size = node.left.size if node.left else 0
    right_size = node.right.size if node.right else 0
    expected_size = 1 + left_size + right_size
    assert node.size == expected_size, f"Size mismatch at key {node.key}: got {node.size}, expected {expected_size}"

    # 5. Aggregate property (Group 7: range_agg count = size)
    assert node.aggregate == node.size, f"Aggregate mismatch at key {node.key}: got {node.aggregate}, expected {node.size}"


def test_empty_tree() -> None:
    """Tests operations on an empty AVL tree."""
    tree = AVLTree()
    assert tree.root is None
    assert tree.search(10) is False
    assert tree.rank(10) == 0
    assert tree.select(0) is None
    assert tree.range_agg(1, 10) == 0
    assert tree.inorder() == []


def test_insert_basic() -> None:
    """Tests basic insertion and presence search in the AVL tree."""
    tree = AVLTree()
    keys = [10, 20, 5, 15, 3]

    for key in keys:
        tree.insert(key)
        assert tree.search(key) is True

    assert tree.inorder() == sorted(keys)
    verify_avl_invariants(tree.root)


def test_insert_duplicate() -> None:
    """Tests that inserting duplicate keys is ignored and does not alter size."""
    tree = AVLTree()
    tree.insert(10)
    tree.insert(10)  # Duplicate
    tree.insert(20)

    assert tree.inorder() == [10, 20]
    assert tree.root.size == 2
    verify_avl_invariants(tree.root)


def test_rotations() -> None:
    """Tests the trigger and correctness of AVL rotations."""
    # Test Left Rotation (LL Case - inserting larger values sequentially)
    tree_left = AVLTree()
    tree_left.insert(10)
    tree_left.insert(20)
    tree_left.insert(30)  # Should trigger left rotation on 10
    assert tree_left.root.key == 20
    assert tree_left.root.left.key == 10
    assert tree_left.root.right.key == 30
    verify_avl_invariants(tree_left.root)

    # Test Right Rotation (RR Case - inserting smaller values sequentially)
    tree_right = AVLTree()
    tree_right.insert(30)
    tree_right.insert(20)
    tree_right.insert(10)  # Should trigger right rotation on 30
    assert tree_right.root.key == 20
    assert tree_right.root.left.key == 10
    assert tree_right.root.right.key == 30
    verify_avl_invariants(tree_right.root)

    # Test Left-Right Rotation (LR Case)
    tree_lr = AVLTree()
    tree_lr.insert(30)
    tree_lr.insert(10)
    tree_lr.insert(20)  # Should trigger LR rotation
    assert tree_lr.root.key == 20
    assert tree_lr.root.left.key == 10
    assert tree_lr.root.right.key == 30
    verify_avl_invariants(tree_lr.root)

    # Test Right-Left Rotation (RL Case)
    tree_rl = AVLTree()
    tree_rl.insert(10)
    tree_rl.insert(30)
    tree_rl.insert(20)  # Should trigger RL rotation
    assert tree_rl.root.key == 20
    assert tree_rl.root.left.key == 10
    assert tree_rl.root.right.key == 30
    verify_avl_invariants(tree_rl.root)


def test_delete_leaf() -> None:
    """Tests deletion of a leaf node."""
    tree = AVLTree()
    for key in [20, 10, 30]:
        tree.insert(key)

    tree.delete(10)  # Delete leaf node
    assert tree.search(10) is False
    assert tree.inorder() == [20, 30]
    verify_avl_invariants(tree.root)


def test_delete_one_child() -> None:
    """Tests deletion of a node with exactly one child."""
    tree = AVLTree()
    for key in [20, 10, 30, 5]:
        tree.insert(key)

    tree.delete(10)  # Node 10 has single left child 5
    assert tree.search(10) is False
    assert tree.inorder() == [5, 20, 30]
    verify_avl_invariants(tree.root)


def test_delete_two_children() -> None:
    """Tests deletion of a node with two children."""
    tree = AVLTree()
    for key in [20, 10, 30, 5, 15]:
        tree.insert(key)

    tree.delete(10)  # Node 10 has two children (5 and 15)
    assert tree.search(10) is False
    assert tree.inorder() == [5, 15, 20, 30]
    verify_avl_invariants(tree.root)


def test_delete_non_existent() -> None:
    """Tests that deleting a non-existent key changes nothing."""
    tree = AVLTree()
    keys = [10, 20, 30]
    for key in keys:
        tree.insert(key)

    tree.delete(15)  # Key 15 does not exist
    assert tree.inorder() == keys
    verify_avl_invariants(tree.root)


def test_rank() -> None:
    """Tests the rank(key) operation (number of keys smaller than key)."""
    tree = AVLTree()
    keys = [10, 20, 30, 40, 50]
    for key in keys:
        tree.insert(key)

    # Test keys present in the tree
    assert tree.rank(10) == 0
    assert tree.rank(20) == 1
    assert tree.rank(30) == 2
    assert tree.rank(40) == 3
    assert tree.rank(50) == 4

    # Test keys absent but within range
    assert tree.rank(15) == 1
    assert tree.rank(25) == 2
    assert tree.rank(35) == 3
    assert tree.rank(45) == 4

    # Test keys outside the range
    assert tree.rank(5) == 0
    assert tree.rank(100) == 5


def test_select() -> None:
    """Tests the select(index) operation (find the i-th smallest key)."""
    tree = AVLTree()
    keys = [10, 30, 20, 50, 40]
    for key in keys:
        tree.insert(key)

    # Valid indices (sorted order: [10, 20, 30, 40, 50])
    assert tree.select(0) == 10
    assert tree.select(1) == 20
    assert tree.select(2) == 30
    assert tree.select(3) == 40
    assert tree.select(4) == 50

    # Invalid indices
    assert tree.select(-1) is None
    assert tree.select(5) is None
    assert tree.select(100) is None


def test_range_agg() -> None:
    """Tests the range_agg(start, end) operation (count in the range [start, end])."""
    tree = AVLTree()
    keys = [10, 20, 30, 40, 50]
    for key in keys:
        tree.insert(key)

    # Range covering all keys
    assert tree.range_agg(10, 50) == 5
    assert tree.range_agg(5, 55) == 5

    # Range covering subsets of keys
    assert tree.range_agg(15, 45) == 3  # [20, 30, 40]
    assert tree.range_agg(20, 40) == 3  # [20, 30, 40]
    assert tree.range_agg(10, 10) == 1  # [10]
    assert tree.range_agg(25, 25) == 0  # empty range

    # Invalid ranges (start > end)
    assert tree.range_agg(40, 20) == 0

    # Range fully outside the tree
    assert tree.range_agg(60, 100) == 0
    assert tree.range_agg(1, 5) == 0


def test_large_random_operations() -> None:
    """Tests tree correctness under a large set of randomized operations."""
    import random
    random.seed(42)

    tree = AVLTree()
    inserted = set()

    # Perform 1000 insertions
    for _ in range(1000):
        key = random.randint(1, 10000)
        tree.insert(key)
        inserted.add(key)

    assert tree.inorder() == sorted(list(inserted))
    verify_avl_invariants(tree.root)

    # Perform 500 searches
    for _ in range(500):
        key = random.randint(1, 10000)
        assert tree.search(key) == (key in inserted)

    # Verify rank, select and range_agg correctness against baseline sorted list
    sorted_keys = sorted(list(inserted))
    for _ in range(100):
        key = random.randint(0, 11000)
        
        # Rank baseline check
        expected_rank = sum(1 for k in sorted_keys if k < key)
        assert tree.rank(key) == expected_rank

        # Select baseline check
        idx = random.randint(-10, len(sorted_keys) + 10)
        expected_select = sorted_keys[idx] if 0 <= idx < len(sorted_keys) else None
        assert tree.select(idx) == expected_select

        # Range aggregate baseline check (count elements in [start, end])
        start = random.randint(0, 10000)
        end = start + random.randint(0, 1000)
        expected_count = sum(1 for k in sorted_keys if start <= k <= end)
        assert tree.range_agg(start, end) == expected_count

    # Perform 500 deletions
    keys_to_delete = random.sample(list(inserted), min(500, len(inserted)))
    for key in keys_to_delete:
        tree.delete(key)
        inserted.remove(key)
        assert tree.search(key) is False

    assert tree.inorder() == sorted(list(inserted))
    verify_avl_invariants(tree.root)
