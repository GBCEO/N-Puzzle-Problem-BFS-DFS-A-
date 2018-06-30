#!/usr/bin/python3


import time
import sys
from queue import Queue as Q
import math
import resource
import queue as q

MAX = 10000000
nodes_expanded = 0
running_time = 0.0
goal_state = None
max_depth = -1




class PuzzleState(object):

    def __str__(self):
        return "Puzzle" + ' ' + str(id(self))

    def __init__(self,config,parent=None,rm='',action='',cost=0):
        if not is_perfect_square(len(config)):
            raise Exception("Puzzle config not correct")
        self.n =  len(config)
        self.m = math.sqrt(self.n)
        self.parent = parent
        self.action = action
        self.cost = cost 
        self.total_cost = int(0)
        self.dimension = self.n
        self.config = config
        self.children = list()
        self.restricted_move = rm
        self.allowed_moves = set()

        for i,item in enumerate(self.config):
            if item == 0:
                self.blank_row = i//self.m
                self.blank_col = i%self.m

    def __lt__(self, other):
        return self.total_cost < other.total_cost
    
                    
    def display(self):
        print(self)
        for i in range(int(self.m)):
            line = ''
            for j in range(int(self.m)):
                line+= ' ' + str(self.config[int(i*self.m+j)])
            print(line)
            print("----")


    def move_left(self):
        if self.blank_col == 0:
            return None
        new_config = list(self.config)
        blank_pos = int(self.blank_row * self.m + self.blank_col)
        target_pos = int(self.blank_row * self.m + self.blank_col - 1)

        new_config[target_pos],new_config[blank_pos] = self.config[blank_pos],self.config[target_pos]
        return PuzzleState(new_config,parent=self,rm='Right',action='Left',cost=self.cost+1)


    def move_right(self):
        if self.blank_col == self.m-1:
            return None
        new_config = list(self.config)
        blank_pos = int(self.blank_row * self.m + self.blank_col)
        target_pos = int(self.blank_row * self.m + self.blank_col + 1)

        new_config[target_pos],new_config[blank_pos] = self.config[blank_pos],self.config[target_pos]
        return PuzzleState(new_config,parent=self,rm='Left',action='Right',cost=self.cost+1)

    def move_up(self):
        if self.blank_row == 0:
            return None
        new_config = list(self.config)
        blank_pos = int(self.blank_row * self.m + self.blank_col)
        target_pos = int((self.blank_row -1) * self.m + self.blank_col)

        new_config[target_pos],new_config[blank_pos] = self.config[blank_pos],self.config[target_pos]
        return PuzzleState(new_config,parent=self,rm='Down',action='Up',cost=self.cost+1)

    def move_down(self):
        if self.blank_row == self.m-1:
            return None
        new_config = list(self.config)
        blank_pos = int(self.blank_row * self.m + self.blank_col)
        target_pos = int((self.blank_row+1) * self.m + self.blank_col)
        new_config[target_pos],new_config[blank_pos] = self.config[blank_pos],self.config[target_pos]
        return PuzzleState(new_config,parent=self,rm='Up',action='Down',cost=self.cost+1)

    def expand(self):
        moves = ['Up','Down','Left','Right']
        if self.restricted_move is not '':
            moves.remove(self.restricted_move)
        #print(moves)
        for move in moves:
            if move == 'Left':
                left_child = self.move_left()
                if left_child is not None:
                    self.children.append(left_child)

            if move == 'Right':
                right_child = self.move_right()
                if right_child is not None:
                    self.children.append(right_child)

            if move == 'Up':
                up_child = self.move_up()
                if up_child is not None:
                    self.children.append(up_child)

            if move == 'Down':
                down_child = self.move_down()
                if down_child is not None:
                    self.children.append(down_child)

#-------CODE-------

def is_perfect_square(num):
    if (math.sqrt(num) - int(math.sqrt(num))):
        return False
    return True

def write_output(running_time):
    global goal_state
    global nodes_expanded
    global max_depth
    path_to_goal,search_depth = find_path(goal_state)
    cost_of_path = goal_state.cost
    max_search_depth = max_depth
    max_ram_usage = 0
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    ram_size = rusage.ru_maxrss/(1024.0*1024.0)
    
    o_file = open("output.txt","w")
    
    o_file.write("path_to_goal: {}\n".format(path_to_goal))
    o_file.write("cost_of_path: {}\n".format(cost_of_path))
    o_file.write("nodes_expanded: {}\n".format(nodes_expanded))
    o_file.write("search_depth: {}\n".format(search_depth))
    o_file.write("max_search_depth: {}\n".format(max_search_depth))
    o_file.write("running_time: {}\n".format(running_time))
    o_file.write("max_ram_usage: {}\n".format(ram_size))
    o_file.close()

def find_path(state):
    path = []
    depth = 0
    parent = state.parent
    while (parent is not None):
        path.append(state.action)
        state=parent
        depth+=1
        parent = parent.parent
    path.reverse()
    return path,depth

#To test goal state Passing PuzzleState Object
def test_goal(state):
    goal_state = [x for x in range(len(state.config))]
    if goal_state == state.config:
        return True
    return False

def calculate_total_cost(state):
    c_config = tuple([x for x in range(0,int(state.n))])
    h = 0
    for i in range(int(state.n)):
        h+=calculate_manhattan_distance(i,state.config[i],int(state.m))
        
    return int(state.cost+h)



def calculate_manhattan_distance(idx,value,m):
    c_config = tuple([x for x in range(0,m*m)])
    c_idx = c_config.index(value)
    
    c_row = int(c_idx//m)
    c_col = int(c_idx%m)
    
    row = int(idx//m)
    col = int(idx%m)
    
    man_dis = abs(c_row-row) + abs(c_col-col)
    return man_dis

def bfs(initial_state):
    frontier = Q(maxsize=MAX)
    f_list = set()
    f_list.add(tuple(initial_state.config))
    explored = set()
    frontier.put(initial_state)

    while not frontier.empty():
        state = frontier.get()
        f_list.remove(tuple(state.config))
        if test_goal(state):
            global goal_state
            goal_state = state
            break
        state.expand()
        global nodes_expanded
        nodes_expanded+=1
        explored.add(tuple(state.config))
                     
        for child in state.children:
            if (tuple(child.config) not in explored) and (tuple(child.config) not in f_list):
                global max_depth
                if child.cost >= max_depth:
                    max_depth = child.cost
                frontier.put(child)
                f_list.add(tuple(child.config))



def dfs(initial_state):
    frontier = [initial_state]
    f_list = set()
    f_list.add(tuple(initial_state.config))
    explored = set()
    while frontier:
        state = frontier.pop()
        f_list.remove(tuple(state.config))
        if test_goal(state):
            global goal_state
            goal_state = state
            break
            
        state.expand()
        global nodes_expanded
        nodes_expanded+=1
        explored.add(tuple(state.config))
        
        c_list = reversed(state.children)
        for child in c_list:
            if (tuple(child.config) not in explored) and (tuple(child.config) not in f_list):
                frontier.append(child)
                f_list.add(tuple(child.config))
                explored.add(tuple(child.config))
                global max_depth
                if child.cost >= max_depth:
                    max_depth = child.cost
                
    
    
    


def a_star(initial_state):
    frontier = q.PriorityQueue()
    explored = set()
    initial_state.total_cost = calculate_total_cost(initial_state)
    frontier.put(initial_state)
    f_list = set()
    f_list.add(tuple(initial_state.config))
    while not frontier.empty():
        state = frontier.get()
        f_list.remove(tuple(state.config))
        
        if test_goal(state):
            global goal_state
            goal_state = state
            break
            
        state.expand()
        global nodes_expanded
        nodes_expanded+=1
        explored.add(tuple(state.config))
        
        for child in state.children:
            if (tuple(child.config) not in explored) and (tuple(child.config) not in f_list):
                child.total_cost = int(calculate_total_cost(child)) 
                frontier.put(child)
                f_list.add(tuple(child.config))
                global max_depth
                if child.cost >= max_depth:
                    max_depth = child.cost



def main():
    method = sys.argv[1].lower()
    config = list(map(int,sys.argv[2].split(',')))

    hard_config = PuzzleState(config)
    t0 = time.clock()
    if method == 'bfs':
        bfs(hard_config)
    elif method == 'dfs':
        dfs(hard_config)
    elif method == 'ast':
        a_star(hard_config)
    else:
        print("Warning:Enter Valid Search Method!")
        exit()
        
    t1 = time.clock()
    write_output(t1-t0)



if __name__ == "__main__":
    main()
    

