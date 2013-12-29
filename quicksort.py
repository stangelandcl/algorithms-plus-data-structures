# quicksort: a fast in place sorting algorithm

def swap(items, left, right):
        temp         = items[left]
        items[left]  = items[right]
        items[right] = temp

def partition(items, left, right, pivot):
        v = items[pivot]
        swap(items, pivot, right)
        s = left
        for i in xrange(left, right):
                if items[i] <= v:
                        swap(items, i, s)
                        s+=1
        swap(items, s, right)
        return s
                

def median(left, right):
        mid = left + (right - left) / 2
        if left < mid:
                if mid < right: return mid
                else:           return right
        elif right < mid:
                if mid < left:  return mid
                else:           return left
        elif left < right:      return left
        else:                   return right

# left and right are inclusive
def sort_range(items, left, right):
        if left >= right: return
        mid = median(left, right)
        pivot = partition(items, left, right, mid)
        sort_range(items, left, pivot-1)
        sort_range(items, pivot+1, right)

def quicksort(items):
        if len(items) < 2: return
        sort_range(items, 0, len(items)-1)


import unittest
from random import random

class Test(unittest.TestCase):
        def test(self):
                count = 10000
                items = [random() for x in xrange(count)]
                quicksort(items)
                for i in xrange(1, count):
                        self.assertLessEqual(items[i-1], items[i])

if __name__=="__main__":
        unittest.main()
