from collections import deque
from planner.node import Node


def bfs(planner):

    start_state = planner.get_initial_state()
    start_node = Node(start_state)

    frontier = deque([start_node])
    visited = set()

    nodes_expanded = 0

    while frontier:

        node = frontier.popleft()
        nodes_expanded += 1

        if node.state.is_goal():
            return node, nodes_expanded

        visited.add(node.state.key())

        actions = planner.get_actions(node.state)

        for action in actions:

            new_state = planner.apply_action(node.state, action)

            if new_state.key() in visited:
                continue

            cost = planner.compute_cost(new_state)

            child = Node(new_state, node, action, cost)

            frontier.append(child)

    return None, nodes_expanded