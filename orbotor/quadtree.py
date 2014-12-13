class QuadTreeObject():
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.r = 0
    
class QuadTreeBounds():
    
    def __init__(self, obj=None, x1=0, y1=0, x2=0, y2=0):
        if obj is not None:
            self.get_from_object(obj)
        else:
            self.x1 = x1
            self.x2 = x2
            self.y1 = y1
            self.y2 = y2
        
    def get_width(self):
        return self.x2-self.x1
    
    def get_height(self):
        return self.y2-self.y1
    
    def get_from_object(self, obj):
        self.x1 = obj.x-obj.r
        self.x2 = obj.x+obj.r
        self.y1 = obj.y-obj.r
        self.y2 = obj.y+obj.r
        
    def get_from_planet(self, pl):
        self.x1 = pl.x-pl.r2*2
        self.x2 = pl.x+pl.r2*2
        self.y1 = pl.y-pl.r2*2
        self.y2 = pl.y+pl.r2*2

class QuadTree():
    
    def __init__(self, level, bounds):
        self.max_objects = 20
        self.max_levels = 6
        self.level = level
        self.objects = []
        self.nodes = []
        self.bounds = bounds
        self.calculate_points()
        
    def calculate_points(self):
        self.subwidth = int(self.bounds.get_width()/2)
        self.subheight = int(self.bounds.get_height()/2)
        self.x1 = self.bounds.x1
        self.y1 = self.bounds.y1
        self.x2 = self.bounds.x2
        self.y2 = self.bounds.y2
        
    def clear(self):
        self.objects = []
        self.nodes = []
        
    def split(self):
        if len(self.nodes) == 0:
            self.nodes = [QuadTree(self.level+1, QuadTreeBounds(obj=None, x1=self.x1, y1=self.y1, x2=self.subwidth, y2=self.subheight)),
                        QuadTree(self.level+1, QuadTreeBounds(obj=None, x1=self.subwidth, y1=self.y1, x2=self.x2, y2=self.subheight)),
                        QuadTree(self.level+1, QuadTreeBounds(obj=None, x1=self.x1, y1=self.subheight, x2=self.subwidth, y2=self.y2)),
                        QuadTree(self.level+1, QuadTreeBounds(obj=None, x1=self.subwidth, y1=self.subheight, x2=self.x2, y2=self.y2))]
        
    def is_obj_in_me(self, objb):
        return objb.x1 >= self.x1 and objb.y1 >= self.y1 and objb.x2 <= self.x2 and objb.y2 <= self.y2
        
    def findAppropriateNode(self, obj):
        objb = QuadTreeBounds(obj=obj)
        
        if not self.is_obj_in_me(objb):
            return -1
        
        if objb.y2 < self.subheight+self.y1:
            if objb.x2 < self.subwidth+self.x1:
                return 0
            elif objb.x1 > self.subwidth+self.x1:
                return 1
        elif objb.y1 >= self.subheight+self.y1:
            if obj.x < self.subwidth+self.x1:
                return 2
            else:
                return 3
            
        return -1
            
    def insert(self, obj):
        if len(self.nodes) > 0:
            index = self.findAppropriateNode(obj)
            if index != -1:
                self.nodes[index].insert(obj)
        else:
            self.objects.append(obj)
            if len(self.objects) > self.max_objects and self.level < self.max_levels:
                self.split()
                for obj2 in self.objects:
                    index = self.findAppropriateNode(obj2)
                    if index != -1:
                        self.nodes[index].insert(obj2)
                        self.objects.remove(obj2)
                        
    def reinsertlist(self, l):
        self.clear()
        for obj in l:
            self.insert(obj)
                        
    def retrieve(self, obj):
        result = []
        index = self.findAppropriateNode(obj)
        if index != -1 and len(self.nodes) > 0:
            result += self.nodes[index].retrieve(obj)
        result += self.objects
        return result