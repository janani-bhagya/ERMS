# backend/app/core/queue.py
from collections import deque

class PriorityQueue:
    def __init__(self):
        self.queue = deque()
    
    def enqueue(self, item, priority=0):
        self.queue.append((priority, item))
        # Simple implementation - for production use heapq
    
    def dequeue(self):
        if self.is_empty():
            return None
        
        # Find highest priority item
        highest_priority_index = 0
        for i in range(1, len(self.queue)):
            if self.queue[i][0] > self.queue[highest_priority_index][0]:
                highest_priority_index = i
        
        return self.queue[highest_priority_index][1]
    
    def peek(self):
        if self.is_empty():
            return None
        
        highest_priority_index = 0
        for i in range(1, len(self.queue)):
            if self.queue[i][0] > self.queue[highest_priority_index][0]:
                highest_priority_index = i
        
        return self.queue[highest_priority_index][1]
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def size(self):
        return len(self.queue)
