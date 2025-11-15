 # backend/app/core/hash_table.py
class HashTable:
    def __init__(self, size=1000):
        self.size = size
        self.table = [[] for _ in range(size)]
        self.count = 0
    
    def _hash(self, key):
        return hash(key) % self.size
    
    def insert(self, key, value):
        index = self._hash(key)
        bucket = self.table[index]
        
        # Check if key already exists, update if it does
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        # Key doesn't exist, add new entry
        bucket.append((key, value))
        self.count += 1
    
    def get(self, key):
        index = self._hash(key)
        bucket = self.table[index]
        
        for k, v in bucket:
            if k == key:
                return v
        return None
    
    def delete(self, key):
        index = self._hash(key)
        bucket = self.table[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.count -= 1
                return True
        return False
    
    def __contains__(self, key):
        return self.get(key) is not None
    
    def __len__(self):
        return self.count
    
    def keys(self):
        all_keys = []
        for bucket in self.table:
            for key, value in bucket:
                all_keys.append(key)
        return all_keys
    