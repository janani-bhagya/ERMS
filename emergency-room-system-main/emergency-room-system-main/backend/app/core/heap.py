# backend/app/core/heap.py
class MaxHeap:
    def __init__(self):
        self.heap = []
    
    def _parent(self, index):
        return (index - 1) // 2
    
    def _left_child(self, index):
        return 2 * index + 1
    
    def _right_child(self, index):
        return 2 * index + 2
    
    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def _heapify_up(self, index):
        while index > 0:
            parent = self._parent(index)
            if self.heap[index][0] > self.heap[parent][0]:
                self._swap(index, parent)
                index = parent
            else:
                break
    
    def _heapify_down(self, index):
        size = len(self.heap)
        while True:
            left = self._left_child(index)
            right = self._right_child(index)
            largest = index
            
            if left < size and self.heap[left][0] > self.heap[largest][0]:
                largest = left
            if right < size and self.heap[right][0] > self.heap[largest][0]:
                largest = right
            
            if largest != index:
                self._swap(index, largest)
                index = largest
            else:
                break
    
    def push(self, priority, patient_id, clinical_data):
        element = (priority, patient_id, clinical_data)
        self.heap.append(element)
        self._heapify_up(len(self.heap) - 1)
    
    def pop(self):
        if not self.heap:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root
    
    def peek(self):
        return self.heap[0] if self.heap else None
    
    def is_empty(self):
        return len(self.heap) == 0
    
    def size(self):
        return len(self.heap)
    
    def update_priority(self, patient_id, new_priority, new_clinical_data=None):
        for i, (priority, p_id, clinical_data) in enumerate(self.heap):
            if p_id == patient_id:
                self.heap[i] = (new_priority, patient_id, 
                               new_clinical_data if new_clinical_data else clinical_data)
                # Re-heapify both directions to maintain heap property
                self._heapify_up(i)
                self._heapify_down(i)
                return True
        return False
    