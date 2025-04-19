class Graph:
    def __init__(self, nodes):
        self.nodes = set(nodes)
        self.edges = {node: set() for node in nodes}

    def add_edge(self, u, v):
        self.edges[u].add(v)
        self.edges[v].add(u)

    def __repr__(self):
        return f"Graph(nodes={self.nodes}, edges={self.edges})"
    
def find_subgraphs(graphs):
        subgraphs = []

        for graph in graphs:
            visited = set()

            def dfs(node, component):
                visited.add(node)
                component.add(node)
                for neighbor in graph.edges[node]:
                    if neighbor not in visited:
                        dfs(neighbor, component)

            for node in graph.nodes:
                if node not in visited:
                    component = set()
                    dfs(node, component)
                    subgraphs.append(component)

        return subgraphs