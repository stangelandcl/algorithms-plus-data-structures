# Treap: a balanced binary search tree
# it is an especially simple binary search tree and uses a random priority number for each
# node to aid in the balancing


from random import random, seed

class Node:
        def __init__(self, item, priority):
                self.item = item
                self.priority = priority
                self.left = None
                self.right = None

class Treap:
        def __init__(self):
                self.root = None
                self.count = 0

        def add(self, item):
                self.root = self._add(self.root, item)
                
        def _add(self, node, item):
                if not node:
                        self.count+=1
                        return Node(item, random())
                
                if item < node.item:
                        node.left = self._add(node.left, item)
                        if node.left.priority > node.priority:
                                temp = node.left
                                node.left = temp.right
                                temp.right = node
                                node = temp
                elif item > node.item:
                        node.right = self._add(node.right, item)
                        if node.priority < node.right.priority:
                                temp = node.right
                                node.right = temp.left
                                temp.left = node
                                node = temp
                else: 
                        node.item = item
                        self.count += 1
                return node

        def remove(self, item):
                self.root = self._remove(self.root, item)
        
        def _remove(self, node, item):
                if not node: return None
                
                if item < node.item:
                        node.left = self._remove(node.left, item)
                        return node
                if item > node.item:
                        node.right = self._remove(node.right, item)
                        return node
                
                if node.left:
                        if node.right:
                                node = self._reorder(node, node.left, node.right)
                        else:   
                                node = node.left
                else:
                        node = node.right
                self.count -= 1
                return node

        def _reorder(self, node, left, right):
                if not left: return right
                if not right: return left
                if left.priority > right.priority:
                        left.right = self._reorder(left.right, left.right, right)
                        return left
                else:
                        right.left = self._reorder(right.left, left, right.left)
                        return right

        def get(self, item):
                return self._get(self.root, item)
                
        def _get(self, node, item):
                if not node: return None
                if item < node.item: return self._get(node.left, item)
                if item > node.item: return self._get(node.right, item)
                return node.item

        def clear(self):
                self.root = None
                self.count = 0

        def items(self):
                for x in self._items(self.root):
                        yield x
        
        def _items(self, node):
                if not node: return
                for x in self._items(node.left):
                        yield x
                yield node.item
                for x in self._items(node.right):
                        yield x
                

import unittest
class Test(unittest.TestCase):
        def test(self):
                seed(1)
                count = 1000
                treap = Treap()        
                self.assertEqual(treap.count, 0)
                
                print "generating random data"
                items = list(set(random() for x in xrange(count*2)))[:count]
                
                print "testing insert"
                i=0
                for x in items:
                        treap.add(x)
                        i+=1
                        self.assertEqual(i, treap.count)
                        for j in xrange(i):
                                self.assertEqual(items[j], treap.get(items[j]), "i=" + str(i) + " j=" + str(j))                
                self.assertEqual(count, treap.count)
                
                print "testing order"
                ti = list(treap.items())
                self.assertEqual(count, len(ti))
                for i in xrange(1, count):
                        self.assertGreater(ti[i], ti[i-1])
                
                print "testing remove"
                i=0
                for x in items:
                        treap.remove(x)
                        count-=1
                        i+=1
                        self.assertEqual(count, treap.count)
                        for j in xrange(i):
                                self.assertFalse(treap.get(items[j]))

                treap.clear()
                self.assertEqual(0, treap.count)
                        
                        

        
if __name__=="__main__":
        unittest.main()
