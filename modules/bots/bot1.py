import heapq as PriorityQueue;
from ..ship.utilities import get_open_neighbours;

class Bot1:
    def __init__(self):
        self.prev={};
        self.start=(None, None)
        self.end=(None, None)
        path=[];
    
    def set_path(self):
        path=[];
        curr= tuple(self.end);
        while curr is not None:
            path.append((curr));
            curr=self.prev[tuple(curr)];
        path.reverse();
        self.path=path;

    def move_and_get_position(self):
        return self.path.pop(0)
        # for node in self.path:
        #     yield (node[0],node[1]);
    
    def execute_strategy(self,maze,start,end):
        print(f"start and end : {start},{end}")
        fringe=[(0,start)];
        self.start=start
        self.end=end
        PriorityQueue.heapify(fringe);
        totalCosts={start:0}
        prev={start:None}
        while bool(fringe):
            # print(f"in while {fringe}")
            curr=PriorityQueue.heappop(fringe)[1]
            if curr == end:
                self.prev=prev
                return True,prev,totalCosts;
            # print(f"Fringe->{curr}:{fringe}")
            # print(f"Neighbours of curr {curr}->{get_open_neighbours(maze,curr[0],curr[1])[1]}")
            for child in get_open_neighbours(maze,curr[0],curr[1])[1]:
                # print(f"processing child: {child}")
                cost = totalCosts[tuple(curr)] + 1;
                if tuple(child) not in totalCosts:
                    prev[tuple(child)]=curr;
                    totalCosts[tuple(child)]=cost;
                    # print(f"Adding {child} to the fringe")
                    PriorityQueue.heappush(fringe,(cost,child));
                if cost < totalCosts[tuple(child)] :
                    prev[tuple(child)]=curr;
                    totalCosts[tuple(child)]=cost;
                    #replace item in fringe
                    print(f"Updating {child} to the fringe")
                    fringe= list(filter(lambda x: x[1]!=child[1],fringe))
                    PriorityQueue.heappush(fringe,(cost,child));
        self.prev=prev;
        print('failed')
        return False,prev,totalCosts;