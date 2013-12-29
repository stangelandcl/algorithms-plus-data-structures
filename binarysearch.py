# if key is found. return position
# if key is not found return complement of position to insert key at
# so return value < 0 = not found, >= 0 = found
def binary_search(items, key):
        low = 0
        high = len(items) -1
        while low <= high:
                mid = low + (high - low) / 2
                x = items[mid]
                if x < key:   low = mid + 1
                elif x > key: high = mid -1
                else:         return mid
        return ~low


import unittest

class Test(unittest.TestCase):
        def test(self):
                count = 1000
                items = [x*2 for x in xrange(count)]
                
                for i in xrange(count):
                        x = items[i]
                        self.assertEqual(i, binary_search(items,x))
                
                for i in xrange(count):
                        x = items[i] + 1
                        y = binary_search(items, x)
                        self.assertGreater(0, y)
                        self.assertEqual(i+1, ~y)

if __name__=="__main__":
        unittest.main()
