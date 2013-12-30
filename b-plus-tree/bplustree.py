# B+ Tree:
# internal nodes hold lists of keys and nodes
# leaf nodes hold lists of keys and values

import sys
sys.path.append("..") # for binarysearch module

from binarysearch import binary_search
from operator import indexOf

NodeSize = 128
MinNodeSize = NodeSize / 2

def type_check(x, t):
        if not isinstance(x, t):
                raise Exception("Expected type: " + str(t.__name__) + " got " + str(type(x)))

def same_type_check(a, b):
        if a.__class__.__name__ != b.__class__.__name__:
                raise Exception("left is " + a.__class__.__name__ + " while right is " +
                                b.__class__.__name__)

def iter_len(a):
        return sum(1 for _ in a)

class Node(object):
        def __init__(self):
                self.keys = []
                self.values = []
        @property
        def is_full(self):     return len(self.keys) == NodeSize
        @property
        def is_empty(self):    return len(self.keys) == 0
        @property
        def count(self):       return len(self.keys)
        @property
        def is_internal(self): return isinstance(self, Internal)
        @property
        def is_leaf(self):     return isinstance(self, Leaf)

        def split(self):
                right        = self.new()
                half         = NodeSize/2
                right.keys   = self.keys[half:NodeSize]
                right.values = self.values[half:NodeSize]
                self.keys    = self.keys[:half]
                self.values  = self.values[:half]
                return right

        def take_left(self):
                half = max((self.count - MinNodeSize)/2, 1)
                keys = self.keys[:half]
                values = self.values[:half]
                self.keys = self.keys[half:]
                self.values= self.values[half:]
                return (keys, values)

        def take_right(self):
                half = max((self.count - MinNodeSize)/2, 1)
                keys = self.keys[-half:]
                values = self.values[-half:]
                self.keys = self.keys[:-half]
                self.values = self.values[:-half]
                return (keys, values)

        def add_from_right(self, node):
                self.add_left(*node.take_right())

        def add_from_left(self,node):
                self.add_right(*node.take_left())

        def add_left(self, keys, values):
                self.keys = keys + self.keys
                self.values = values + self.values
        def add_right(self, keys, values):
                self.keys += keys
                self.values += values

        def add(self, key, value):
                i = binary_search(self.keys, key)
                if i >= 0:
                        self.values[i] = value
                        return True

                if len(self.keys) == NodeSize:
                        return False
                i = ~i

                self.keys.insert(i, key)
                self.values.insert(i, value)
                return True

        def get(self, key):
                i = binary_search(self.keys, key)
                if i >= 0:
                        return self.values[i]
                return None

        def items(self):
                for i in xrange(self.count):
                        yield (self.keys[i], self.values[i])

class Leaf(Node):
        def __init__(self):
                Node.__init__(self)
        def new(self):
                return Leaf()
        def remove(self, key):
                i = binary_search(self.keys, key)
                if i < 0:
                        return False
                del self.keys[i]
                del self.values[i]
                return True


class Internal(Node):
        def __init__(self):
                Node.__init__(self)
        def new(self):
                return Internal()
        def get_node(self, key):
                i = binary_search(self.keys, key)
                if i < 0:
                        i = ~i
                        if i > 0: i-= 1
                return (i, self.values[i])

        def update(self, index, node):
                self.keys[index] = node.keys[0]

        def update_node(self, index, key):
                if key < self.keys[index]:
                        self.keys[index] = key

        def remove_at(self, index):
                del self.keys[index]
                del self.values[index]

        def add_node(self, node):
                self.add(node.keys[0], node)
#                for x in self.values:
#                        same_type_check(node, x)

        def left_of(self, i):
                i -= 1
                if i < 0: return None
                return self.values[i]

        def right_of(self, i):
                i += 1
                if i >= self.count: return None
                return self.values[i]

        def replace(self, index, node):
                self.keys[index]   = node.keys[0]
                self.values[index] = node


class BTree:
        def __init__(self):
                self.root = None
                self.count = 0

        def add(self, key, value):
                if not self.root:
                        self._add_root(key, value)
                        return
                if isinstance(self.root, Leaf):
                        self._add_root_leaf(key, value)
                        return
                self._add_root_internal(key, value)

        def _add_root(self, key, value):
                self.root = Leaf()
                self.root.add(key, value)

        def _add_root_leaf(self, key, value):
                if self.root.add(key, value): return
                self._split_root()
                self.add(key, value)

        def _split_root(self):
                left = self.root
                right = self.root.split()
                self.root = Internal()
                self.root.add_node(left)
                self.root.add_node(right)

        def _add_root_internal(self, key, value):
                parent = self._add_internal(None, self.root, key ,value)
                if parent: self.root = parent

        def _add_internal(self, parent, node, key, value):
                if node.is_full:
                        if not parent:
                                parent = Internal()
                                parent.add_node(node)
                        parent.add_node(node.split())
                        node = parent

                next_index, next_node = node.get_node(key)
                node.update_node(next_index, key)
                if next_node.is_internal:
                        node = self._add_internal(node, next_node, key, value)
                else:
                        if next_node.add(key, value): return parent
                        node.add_node(next_node.split())
                        parent = self._add_internal(parent, node, key, value)
                return parent

        def remove(self, key):
                if not self.root: return
                if self.root.is_leaf:
                        self._remove_root_leaf(key)
                else:
                        self._remove_root_internal(key)

        def _remove_root_leaf(self, key):
                if self.root.remove(key) and self.root.is_empty:
                        self.root = None

        def _remove_root_internal(self, key):
                nodes = self.move_to(key)
                leaf = nodes[-1][1]
                if not leaf.remove(key):
                        return
                if not leaf.is_empty:
                        self._update_parents(nodes)
                #if not self._rebalance(nodes):
                #        return
                self.root = nodes[0][1]

        def _update_parents(self, nodes):
                for x in xrange(len(nodes)-1):
                        index, parent =nodes[-(x+2)]
                        _, child = nodes[-(x + 1)]
                        parent.update(index, child)


        def _rebalance(self, nodes):
                if len(nodes) < 2:
                        return

                left  = None
                right = None
                leaf  = nodes[-1][1]
                if leaf.count >= MinNodeSize:
                        return

                left_nodes = self._left_child(nodes)
                if left_nodes:
                        left = left_nodes[-1][1]
                        if left and left.count > MinNodeSize:
                                same_type_check(left, leaf)

                                leaf.add_from_right(left)
                                self._update_parents(nodes)
                                return
                right_nodes = self._right_child(nodes)
                if right_nodes:
                        right = right_nodes[-1][1]
                        if right and right.count > MinNodeSize:
                                same_type_check(right, leaf)

                                leaf.add_from_left(right)
                                self._update_parents(right_nodes)
                                return

                if left:
#                        print "in left"
                        same_type_check(left, leaf)

                        left.add_right(leaf.keys, leaf.values)
                        child_index, parent = nodes[-2]
                        parent.remove_at(child_index)
                        self._rebalance(nodes[:-1])
                        return
                if right:
 #                       print "in right"
                        same_type_check(right, leaf)

                        right.add_left(leaf.keys, leaf.values)
                        self._update_parents(right_nodes)
                        child_index, parent = nodes[-2]
                        parent.remove_at(child_index)
                        self._rebalance(nodes[:-1])
                        return

                nodes[-2] = (0, leaf)
                self._rebalance(nodes[:-2])


        def get(self, key):
                if not self.root:
                        return None
                return self._get(self.root, key)

        def _get(self, node, key):
                if node.is_leaf:
                        return node.get(key)
                index, next_node = node.get_node(key)
                return self._get(next_node, key)

        def _left_child(self, nodes):
                if len(nodes) < 2: return None
                index, node = nodes[-1]
                i = len(nodes) - 2
                while i >= 0:
                        index2, parent = nodes[i]
                        index2-=1
                        if index2 >= 0: break
                        i-= 1
                if i < 0: return None
                left_path = nodes[:i]
                while len(left_path) < len(nodes):
                        left_path.append((index2, parent))
                        if parent.is_leaf: break
                        parent = parent.values[index2]
                        index2 = parent.count -1 # right most
                return left_path

        def _right_child(self, nodes):
                if len(nodes) < 2: return None
                index, onde = nodes[-1]
                i = len(nodes)-2
                while i>=0:
                        index2, parent = nodes[i]
                        index2+= 1
                        if index2 < parent.count: break
                        i -= 1
                if i < 0: return None
                right_path = nodes[:i]
                while len(right_path) < len(nodes):
                        right_path.append((index2, parent))
                        if parent.is_leaf: break
                        parent = parent.values[index2]
                        index2 = 0 # left most
                return right_path

        def move_to(self, key):
                nodes = []
                if not self.root:
                        return nodes
                self._move_to(nodes, key, self.root)
                return nodes

        def _move_to(self, nodes, key, node):
                if node.is_internal:
                        next_index, next_node = node.get_node(key)
                        nodes.append((next_index, node))
                        self._move_to(nodes, key, next_node)
                else:
                        i = binary_search(node.keys, key)
                        nodes.append((i, node))

        def items(self):
                if self.root:
                        for x in self._items(self.root):
                                yield x

        def _items(self, node):
                if node.is_leaf:
                        for x in node.items():
                                yield x
                else:
                        for x in node.items():
                                for item in self._items(x[1]):
                                        yield item;


import unittest
from random import random, seed, randint
#import cProfile
#import pstats


class Test(unittest.TestCase):
        def _assert_order(self, x):
                i = None
                for x2 in x:
                        if i:
                                self.assertGreater(x2, i)
                        i = x2

        # def setUp(self):
        #         self.pr = cProfile.Profile()
        #         self.pr.enable()

        # def tearDown(self):
        #         p = pstats.Stats(self.pr)
        #         p.strip_dirs()
        #         p.sort_stats('cumtime')
        #         p.print_stats()

        def test(self):
                seed_value = randint(0, sys.maxint)
                print "testing with random.seed=", seed_value
                seed(seed_value)

                count = 1000000
                items = list(set(random() for x in xrange(count*2)))[:count] # unique random values

                tree = BTree()
                for x in items:
                        tree.add(x, x)

                self._assert_order(tree.items())

                for item in items:
                        x = tree.get(item)
                        self.assertEqual(item, x)

                for item in items:
                        #print count
                        #self._assert_order(tree.items())
                        #if count <= 90082:
                        #self.assertEqual(count, iter_len(tree.items()))
                        tree.remove(item)
                        count -= 1

                for x in items:
                        tree.add(x, x)

                count = len(items)
                items.sort()
                for item in items:
                        tree.remove(item)
                        count -= 1


                self.assertEqual(0, iter_len(tree.items()))

if __name__=="__main__":
        unittest.main()
