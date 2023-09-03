import copy
import heapq
class OSPF_Router:
    def __init__(self, num_router):
        self.rcv_buffer = {}
        self.fwd_buffer = {}
        self.link_state = []
        self.rcv_from_router = [False for i in range(num_router)]
        
class RIP_Router:
    def __init__(self, num_router):
        self.link_state = []
        self.old_link_state = []
        self.rcv_buffer = {}

def run_ospf(link_cost: list) -> tuple[list, list]:
    n = len(link_cost)  # number of nodes
    routers = [OSPF_Router(n) for i in range(n)]
    for i in range(n):
        routers[i].rcv_from_router[i] = True
        routers[i].link_state = copy.deepcopy(link_cost[i])
    # first iter
    do_iter = False
    logs = []  # initialize messages
    #! send my link state to my neighbor
    for src in range(n):
        neighbors = [neighbor for neighbor, cost in enumerate(link_cost[src]) if (cost != 999 and neighbor != src)]
        for neighbor in neighbors:
            routers[neighbor].rcv_buffer[src] = link_cost[src]
            routers[neighbor].rcv_from_router[src] = True
            logs.append((src, src, neighbor))
    #! move buffer and examine if all routers get link_state info from others
    for i in range(n):
        routers[i].fwd_buffer.clear()
        routers[i].fwd_buffer = copy.deepcopy(routers[i].rcv_buffer)
        # print("router", i, " rcv_buffer", routers[i].rcv_buffer, " fwd_buffer", routers[i].fwd_buffer)
        routers[i].rcv_buffer.clear()
        # print("router", i, " rcv_buffer", routers[i].rcv_buffer, " fwd_buffer", routers[i].fwd_buffer)
        if not all(routers[i].rcv_from_router):
            do_iter = True
    #do iter until all(routers[i].rcv_from_all)
    while (do_iter):
        do_iter = False
        #! send my link state to my neighbor if it does not receive my link_state info yet
        for src in range(n):
            neighbors = [neighbor for neighbor, cost in enumerate(link_cost[src]) if (cost != 999 and neighbor != src)]
            for buf_data in routers[src].fwd_buffer:
                # print("src:", src, " here!! ", buf_data)
                for neighbor in neighbors:
                    if not routers[neighbor].rcv_from_router[buf_data]:
                        routers[neighbor].rcv_buffer[buf_data] = link_cost[buf_data]
                        routers[neighbor].rcv_from_router[buf_data] = True
                        logs.append((src, buf_data, neighbor))
        #! move buffer and examine if all routers get link_state info from others
        for i in range(n):
            routers[i].fwd_buffer.clear()
            routers[i].fwd_buffer = copy.deepcopy(routers[i].rcv_buffer)
            # print("router", i, " rcv_buffer", routers[i].rcv_buffer, " fwd_buffer", routers[i].fwd_buffer)
            routers[i].rcv_buffer.clear()
            # print("router", i, " rcv_buffer", routers[i].rcv_buffer, " fwd_buffer", routers[i].fwd_buffer)
            if not all(routers[i].rcv_from_router):
                # print("router", i, "still has false......")
                do_iter = True
        if not do_iter:
            break
    path_cost = []
    for i in range(n):
        path_cost.append(routers[i].link_state)
    #! do shortest path calculation
    #? Dijastra
    all_min_path = []
    for src in range(n):
        min_path = [float('inf')] * n
        min_path[src] = 0
        heap = [(0, src)]
        visited = set()
        while heap:
            cost, router = heapq.heappop(heap) 
            visited.add(router)
            for neighbor in range(len(path_cost[router])):
                cost = path_cost[router][neighbor]
                if (cost != 999) and (neighbor not in visited):
                    new_cost = min_path[router] + cost
                    if new_cost < min_path[neighbor]:
                        min_path[neighbor] = new_cost
                        heapq.heappush(heap, (new_cost, neighbor))
        all_min_path.append(min_path)
    return_tuple = (all_min_path, logs)
    #? Bellman-Ford
    # for src in range(n):
    #     for j in range(n-1):
    #         for node in range(n):
    #             for neighbor in range(len(path_cost[node])):        
    #                 cost = path_cost[node][neighbor]
    #                 # print("Router:", node, " src:", src, " neighbor:", neighbor, " neighbor state:", neighbor_state)
    #                 # for dst in range(len(neighbor_state)):
    #                 #     cost = neighbor_state[dst]
    #                 if path_cost[src][neighbor] > path_cost[src][node] + cost:
    #                     # print(routers[node].link_state[neighbor], routers[node].link_state[src],cost)
    #                     # print("update!")
    #                     path_cost[src][neighbor] = path_cost[src][node] + cost
    # return_tuple = (path_cost, logs)
    return return_tuple

def run_rip(link_cost: list) -> tuple[list, list]:
    n = len(link_cost)  # number of nodes
    routers = [RIP_Router(n) for i in range(n)]
    for i in range(n):
        routers[i].link_state = copy.deepcopy(link_cost[i])
    
    do_iter = False
    logs = []  # initialize messages
    #! send my link state to my neighbor
    for src in range(n):
        neighbors = [neighbor for neighbor, cost in enumerate(link_cost[src]) if (cost != 999 and neighbor != src)]
        for neighbor in neighbors:
            routers[neighbor].rcv_buffer[src] = link_cost[src]
            logs.append((src, neighbor))
    #! copy all routers' link_state to old_link_state
    for i in range(n):
        routers[i].old_link_state.clear()
        routers[i].old_link_state = copy.deepcopy(routers[i].link_state)
    #! do shortest path calculation
    for node in range(n):
        for neighbor, neighbor_state in routers[node].rcv_buffer.items():
            # print("Router:", node, " src:", src, " neighbor:", neighbor, " neighbor state:", neighbor_state)
            for dst in range(len(neighbor_state)):
                cost = neighbor_state[dst]
                if routers[node].link_state[dst] > routers[node].link_state[neighbor] + cost:
                    # print(routers[node].link_state[neighbor], routers[node].link_state[src],cost)
                    # print("update src:", node, " neighbor:", neighbor, " dst:", dst)
                    routers[node].link_state[dst] = routers[node].link_state[neighbor] + cost
    #! examine if all routers' link_state change or not
    for i in range(n):
        if routers[i].old_link_state != routers[i].link_state:
            do_iter = True
    #! clear buffer
    for i in range(n):
        routers[i].rcv_buffer.clear()        

    while (do_iter):
        do_iter = False
        # for i in range(n):
            # print(routers[i].old_link_state, routers[i].link_state)
        #! send my link state to my neighbor if my link_state change
        for src in range(n):
            neighbors = [neighbor for neighbor, cost in enumerate(link_cost[src]) if (cost != 999 and neighbor != src)]
            for neighbor in neighbors:
                if (routers[src].link_state != routers[src].old_link_state):
                    routers[neighbor].rcv_buffer[src] = copy.deepcopy(routers[src].link_state)
                    logs.append((src, neighbor))
        #! copy all routers' link_state to old_link_state
        for i in range(n):
            routers[i].old_link_state.clear()
            routers[i].old_link_state = copy.deepcopy(routers[i].link_state)
        #! do shortest path calculation
        for node in range(n):
            for neighbor, neighbor_state in routers[node].rcv_buffer.items():
                for dst in range(len(neighbor_state)):
                    cost = neighbor_state[dst]
                    if routers[node].link_state[dst] > routers[node].link_state[neighbor] + cost:
                        # print(routers[node].link_state[neighbor], routers[node].link_state[src],cost)
                        # print("update src:", node, " neighbor:", neighbor, " dst:", dst)
                        routers[node].link_state[dst] = routers[node].link_state[neighbor] + cost
        #! examine if all routers' link_state change or not
        for i in range(n):
            if routers[i].old_link_state != routers[i].link_state:
                do_iter = True
        #! clear buffer
        for i in range(n):
            routers[i].rcv_buffer.clear()
    path_cost = []
    for i in range(n):
        path_cost.append(routers[i].link_state)
    return_tuple = (path_cost, logs)
    return return_tuple

def main():
    testdata = [
            [
                [0, 4, 1, 999], 
                [4, 0, 2, 999], 
                [1, 2, 0, 3], 
                [999, 999, 3, 0]
            ],
            [
                [  0,   2,   5,   1, 999, 999],
                [  2,   0,   3,   2, 999, 999],
                [  5,   3,   0,   3,   1,   5],
                [  1,   2,   3,   0,   1, 999],
                [999, 999,   1,   1,   0,   2],
                [999, 999,   5, 999,   2,   0]
            ]
        ]
    for i in range(len(testdata)):
        print("========== testdata", i,"==========")
        ans_ospf = run_ospf(testdata[i])
        print("---ospf---")
        print(ans_ospf)
        ans_rip = run_rip(testdata[i])
        print("---rip---")
        print(ans_rip)

if __name__ == '__main__':
    main()