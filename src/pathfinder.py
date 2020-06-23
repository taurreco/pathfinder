import pygame

# Global constants
NODE_SIZE = 25
BLACK = (0, 0, 0)
WHITE = (250, 250, 250)
YELLOW = (245, 245, 70)
GREEN = (115, 255, 125)
BLUE = (125, 115, 200)
SCREEN_SIZE = (800, 600)

# Setting up the pygame window
pygame.init()
pygame.display.set_caption("Pathfinder")
icon = pygame.image.load("blue-square-16.png")
pygame.display.set_icon(icon)
pygame.display.set_mode(SCREEN_SIZE)


def draw_screen(source, target, walls, path, visited):
    """This function serves to draw each component of the program on the screen

       In times where the screen must be drawn, such as in the game loop, this function
       will be called.  It takes in the information that the screen must display, and
       carries out the appropriate checks to draw them in the right place.

       Args:
            source (Node): The source node.
            target (Node): The target node.
            walls (list of Node): The wall nodes.
            visited (list of Node):  The nodes that were marked by the
                algorithm as visited.
            path (list of Node):  The nodes within the shortest path
                between the source and target node.

    """
    screen = pygame.display.get_surface()
    w, h = screen.get_size()

    for x in range(int(w / NODE_SIZE)):  # This will loop for how many times the node size will fit into the width
        for y in range(int(h / NODE_SIZE)):  # This will loop for how many times the node size will fit into the height

            node = Node((x, y))
            rect = pygame.Rect(x * NODE_SIZE, y * NODE_SIZE, NODE_SIZE - 1, NODE_SIZE - 1)

            pygame.draw.rect(screen, BLACK, (x * NODE_SIZE, y * NODE_SIZE, NODE_SIZE, NODE_SIZE))
            pygame.draw.rect(screen, WHITE, rect)

            # If the node is a wall
            if node in walls:
                pygame.draw.rect(screen, BLACK, rect)
            # If the node is visited
            if node in visited:
                pygame.draw.rect(screen, BLUE, rect)
            # If the node is in the path
            if node in path:
                pygame.draw.rect(screen, GREEN, rect)
            # If the node is either the source or target
            if source == node or target == node:
                pygame.draw.rect(screen, YELLOW, rect)

    pygame.display.update()


class Node(object):
    """This is an immutable class that represents a node.

        The Node class is made immutable so that different instances of Node with the
        same name will be considered the same.  The name is dependent entirely on the position
        given to the Node.  Its x coordinate becomes the first character in the name, and its
        y coordinate becomes the third character in the name, with a comma separating them.
        Therefore, two nodes with the same position will have the same name, and when accessed
        in a dict as a key there is no difference between the two-- they would return the same value.

        Attributes:
            pos (pair of int): This is a tuple used to store
                the x and y values of the Node.
            _name (str): This is the string which identifies each Node.

    """

    def __init__(self, pos=(0, 0)):
        self.pos = pos
        self._name = self.name(pos)

    def __eq__(self, other):
        return self._name == other

    def __hash__(self):
        return hash(self._name)

    def __str__(self):
        return self._name

    def name(self, pos):
        x, y = pos
        return str(x) + "," + str(y)


class Graph(object):
    """Instances of the Graph class hold node information and compute the least cost path between two nodes.

    A dictionary structure is used to hold the node information, with each key representing
    a node on the graph and each value a list of nodes that neighbor the key.  This class
    controls which of its nodes are considered walls.  Walls are nodes whose edges weigh
    infinity, and are checked in the shortest path algorithm.

    Attributes:
        nodes (dict of Node: list of Node): This is a structure used
            to represent every node in the graph.
        walls (list of Node): This is a list of every node in the
            graph that is a wall.

    """

    def __init__(self, nodes={}, walls=[]):
        """Here the Graph can be initialized with the nodes and the walls, or left empty"""
        self.nodes = nodes
        self.walls = walls

    def add_wall(self, wall_node):
        """This method allows additions to the list of walls after initialization of the Graph"""
        self.walls.append(wall_node)

    def find_shortest_path(self, source, target):
        """This method uses dijkstra's algorithm to generate the least cost path between two nodes.

            Here, the algorithm first marks every node as unvisited, then sets the distance of every node
            to the source as infinity.  The previous node of each node is set to None-- this means that
            the node before the considered node in a path to the source node is unknown.  Then, the distance
            to the source node is set to zero.

            Until the algorithm marks the target node as visited
            it will do the following: 1) find the node with the shortest distance to the source and
            mark it as curr. 2) For each neighbor of curr check its distance to source with the curr
            distance to source plus its edge weight to the neighbor (a weight of one by default, but
            infinity if the neighbor is a wall).  If the calculated distance is shorter, reassign the
            neighbor's distance to source and mark the previous node of neighbor as curr.  3) Repeat
            the process.

                Args:
                    source (Node): The source node.
                    target (Node): The target node.

                Returns:
                    visited (list of Node): The nodes that were marked by the
                        algorithm as visited.
                    path (list of Node): The nodes within the shortest path
                        between the source and target node.

        """
        # Initialize variables used in the algorithm
        dist = {}
        prev = {}
        unvisited = []
        visited = []
        path = []
        infinity = float('inf')
        # A boolean that determines whether the visited nodes are updated in real time or not
        visualize = False

        # Set the dist, and prev values for each node with the default values
        # Add every node to unvisited
        for node in self.nodes.keys():
            unvisited.append(node)
            dist[node] = infinity
            prev[node] = None
        # Set the distance of the source to the source as zero
        dist[source] = 0
        curr = None

        # Execute this loop until the target is found
        while target in unvisited:
            min = infinity
            # Find the smallest distance of nodes (in unvisited) from the source
            for node in unvisited:
                if dist[node] < min:
                    min = dist[node]
            # Find the first node in unvisited with the same distance as min, set it to curr and add to visited
            for node in unvisited:
                if dist[node] == min:
                    curr = node
                    visited.append(curr)
                    unvisited.remove(curr)
                    break
            # Re-draw the screen if the program is set to do so
            if visualize:
                draw_screen(source, target, self.walls, path, visited)

            # Loop through the neighbors of curr and calculate a new distance based on the distance of the current
            # node to the source plus the edge weight between curr and the neighbor
            for neighbor in self.nodes[curr]:
                # If the neighbor is a wall, the edge connecting to curr is considered infinite
                if neighbor in self.walls:
                    alt = infinity + dist[curr]
                else:
                    alt = 1 + dist[curr]  # The edge between curr and neighbor is one by default
                # If the recalculated distance from the neighbor to the source is shorter than its current distance
                if alt < dist[neighbor]:
                    dist[neighbor] = alt  # Re-assign the distance
                    prev[neighbor] = curr  # Make the node before the neighbor curr

        # Using prev, trace back from the target a shortest path to source
        path = self.trace_back(prev, target)

        return path, visited

    def trace_back(self, prev, target):
        """Follows the previous nodes down the line from source to target in order to generate a path.

            Args:
                prev (dict of Node: Node): A dictionary of nodes whose values
                    are the nodes before them in a path to the source.
                target (Node): The target node.

            Returns:
                path (list of Node): The nodes within the shortest path
                        between the source and target node.

        """
        path = [target]  # Target is the first node added to the path
        while prev[target] is not None:  # So long as target is not the source
            # (source is the only node which should not have a value for prev)
            path.append(prev[target]) # Add the previous node to path
            target = prev[target] # Set the target to the node just added to path
        path.reverse() # Reverse the path so that it goes from source to target

        return path


class Game:
    """The Game class builds and handles the program

        This class creates the nodes dict to generate a graph that corresponds to the graphic
        on screen.  It will also handle the events and inputs of the user to draw walls, establish
        which nodes are the source and target, and run the path-finding algorithm.

    """

    def __init__(self):
        self.run()

    def run(self):
        """This method handles the user events and draws the screen until the user closes the window."""
        # Initialize variables
        graph = Graph(self.generate_nodes()) # Create the graph
        source = None
        target = None
        visited = []
        path = []

        while True:
            for event in pygame.event.get():
                mpos = pygame.mouse.get_pos()
                # Get the x and y coords of the node that the mouse is hovering over
                x = int(mpos[0] / NODE_SIZE)
                y = int(mpos[1] / NODE_SIZE)
                node = Node((x, y))

                # Exit the program if the user closes the window
                if event.type == pygame.QUIT:
                    return
                # Put a source node at the node where the user left-clicks,
                # and a target at the position of the right-click
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        source = node
                    if event.button == 3:
                        target = node
                # If the user presses the 'w' key, add a wall at the node where the mouse is
                if pygame.key.get_pressed()[pygame.K_w]:
                    graph.add_wall(node)
                # If the user presses enter, run the shortest path algorithm from the graph
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        path, visited = graph.find_shortest_path(source, target)

            # Re-draw the screen
            draw_screen(source, target, graph.walls, path, visited)

    def generate_nodes(self):
        """This method creates nodes that correspond to every point in a matrix defined by the screen and node size.

            Returns:
                nodes (dict of Node: list of Node): This is a structure used
                    to represent every node in the graph.
                    
        """
        # Initializing the variables used to check for and return the nodes dict
        w, h = pygame.display.get_surface().get_size()
        nodes = {}

        # Loops through every node in the graph
        for x in range(int(w / NODE_SIZE)):  # This will loop for how many times the node size will fit into the width
            for y in range(int(h / NODE_SIZE)):  # This for how many times the node size will fit into the height
                # Creates the node that corresponds to the position on the graph, and adds it and its neighbors to
                # the nodes dict
                node = Node((x, y))
                nodes[node] = self.get_neighbors(node)

        return nodes

    def get_neighbors(self, node):
        """This method takes in a node and returns its neighbors based on its position in the graph.

            Args:
                node: Any node.

            Returns:
                neighbors (list of Node): The list of neighbor
                    nodes which become the values in a dict of nodes.
                    
        """
        # Initializing the variables used to check for and return neighbors
        x, y = node.pos
        w, h = pygame.display.get_surface().get_size()
        neighbors = []

        # Checks for a neighbor to the left
        if x > 0:
            neighbor_left = Node((x - 1, y))
            neighbors.append(neighbor_left)
        # Checks for a neighbor to the right
        if x < int(w / NODE_SIZE) - 1:
            neighbor_right = Node((x + 1, y))
            neighbors.append(neighbor_right)
        # Checks for a neighbor above
        if y > 0:
            neighbor_up = Node((x, y - 1))
            neighbors.append(neighbor_up)
        # Checks for a neighbor below
        if y < int(h / NODE_SIZE) - 1:
            neighbor_down = Node((x, y + 1))
            neighbors.append(neighbor_down)

        return neighbors


Game()
