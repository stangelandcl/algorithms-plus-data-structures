# B+ Tree:
# internal nodes hold lists of keys and nodes
# leaf nodes hold lists of keys and values

import sys
sys.path.append("..") # for binarysearch module

from binarysearch import binary_search
from operator import indexOf

NodeSize = 128
MinNodeSize = NodeSize / 2

class Node:
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
                items = []
                print "h=",half, " k=",len(self.keys), " c=",self.count
                for i in xrange(half):
                        items.append((self.keys[i], self.values[i]))
                c = self.count
                self.keys = self.keys[c - half:]
                self.values= self.values[c-half:]
                return items

        def take_right(self):
                half = max((self.count - MinNodeSize)/2, 1)
                items = []
                for i in xrange(half):
                        x = self.count - half + i
                        items.append((self.keys[x], self.values[x]))
                c = self.count
                self.keys = self.keys[:half]
                self.values = self.values[:half]
                return items

        def add_from_right(self, node):
                self.add_range(self.take_right())

        def add_from_left(self,node):
                self.add_range(self.take_left())

        def add_range(self, items):
                for k,v in items:
                        self.add(k,v)

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
        def new(self):         return Leaf()


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
        def new(self):         return Internal()
        
        def get_node(self, key):
                i = binary_search(self.keys, key)
                if i < 0:
                        i = ~i
                        if i > 0: i-= 1
                return (i, self.values[i])

        def update(self, index, node):
                print "i=",index, " k=",len(self.keys), " n=", len(node.keys)
                self.keys[index] = node.keys[0]

        def update_node(self, index, key):
                if key < self.keys[index]:
                        self.keys[index] = key

        def remove_at(self, index):
                del self.keys[index]
                del self.values[index]

        def add_node(self, node):
                self.add(node.keys[0], node)

        def left_of(self, i):
                i -= 1
                if i < 0: return None
                return self.values[i]
        
        def right_of(self, i):
                i += 1
                if i >= self.count: return None
                return self.values[i]


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
                                parent.add(node)
                        parent.add(node.split())
                        node = parent
                
                next_index, next_node = node.get_node(key)
                node.update_node(next_index, key)
                if next_node.is_internal:
                        node = self.add_internal(node, next_node, key, value)
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
                next_index, next_node = self.root.get_node(key)
                rebalanced, new_parent = self._remove(self.root, next_index, next_node, key)
                if rebalanced and new_parent:
                        self.root = remove.new_parent
        
        def _remove(self, parent, child_index, child_node, key):
                if child_node.is_leaf:
                        if not child_node.remove(key):
                                return (None,None)
                        parent.update(child_index, child_node)
                        return self._rebalance(parent, child_index, child_node)

                grand_child_index, grand_child_node = child_node.get_node(key)
                rebalanced, new_parent = self._remove(child_node, grand_child_index, grand_child_node, key)
                parent.update(child_index, child_node)                

                if rebalanced:
                        if new_parent:
                                parent.replace(child_index, grand_child_node)
                                child_node = grand_child_node
                        return self._rebalance(parent, child_index, child_node)

                return (None,None)

        def _rebalance(self, parent, child_index, child_node):
                if child_node.count >= MinNodeSize:
                        return (None, None)
                
                left = parent.left_of(child_index)
                if left and left.count > MinNodeSize:
                        child_node.add_from_right(left)
                        parent.update(child_index, child_node)
                        return (None, None)

                right = parent.right_of(child_index)
                if right and right.count > MinNodeSize:
                        child_node.add_from_left(right)
                        parent.update(child_index+1, right)
                        return (None, None)
                
                if left:
                        left.add_range(child_node.items())
                        parent.update(child_index-1, left)
                        parent.remove_at(child_index)
                        return (True, None)
                
                if right:
                        right.add_range(child_node.items())
                        parent.update(child_index+1, right)
                        parent.remove_at(child_index)
                        return (True, None)
                return (True, child_node)                        
        
        def get(self, key):
                if not self.root:
                        return None
                return self._get(self.root, key)
        
        def _get(self, node, key):
                if node.is_leaf:
                        return node.get(key)
                index, next_node = node.get_node(key)
                return self._get(next_node, key)
        
        def move_to(self, key):
                nodes = []
                if not self.root:
                        return nodes
                self._move_to(nodes, key, node)
                return nodes

        def _move_to(self, nodes, keys, node):
                if not node.is_internal:
                        next_index, next_node = node.get_node(key)
                        nodes.append((next_index, node))
                        self._move_to(nodes, key, next_node)
                        return
                
                i = binary_search(node.keys, key)
                if i < 0: i = ~i
                nodes.append((i, node))

        def items(self):
                if self.root:
                        for x in self._items(self.root):
                                yield x
                else:
                        return
        def _items(self, node):
                if node.is_leaf:
                        for x in node.items():
                                yield x
                else:
                        for x in node.items():
                                for item in self._items(x[1]):
                                        yield item;


import unittest
from random import random

class Test(unittest.TestCase):
        def test(self):
                count = 1000
                items = list(set(random() for x in xrange(count*2)))[:count]
                
                tree = BTree()
                for x in items:
                        tree.add(x, x)

                values = [k for k,v in tree.items()]
                sorted = list(items)
                sorted.sort()
                
                for i in xrange(len(values)):
                        self.assertEqual(sorted[i], values[i])
                
                for item in items:
                        x = tree.get(item)
                        self.assertEqual(item, x)
                        
                for item in items:
                        tree.remove(item)

                self.assertEqual(0, len(list(tree.items())))

if __name__=="__main__":
        unittest.main()
