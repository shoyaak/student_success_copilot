import heapq
from planner.node import Node


def astar(planner):

    start_state = planner.get_initial_state()
    start_node = Node(start_state)

    frontier = []
    heapq.heappush(frontier, (start_node.f, start_node))

    visited = set()

    nodes_expanded = 0

    while frontier:

        _, node = heapq.heappop(frontier)

        nodes_expanded += 1

        if node.state.is_goal():
            return node, nodes_expanded

        visited.add(node.state.key())

        actions = planner.get_actions(node.state)

        for action in actions:

            new_state = planner.apply_action(node.state, action)

            if new_state.key() in visited:
                continue

            g = planner.compute_cost(new_state)
            h = planner.heuristic(new_state)

            child = Node(new_state, node, action, g, h)

            heapq.heappush(frontier, (child.f, child))

    return None, nodes_expanded