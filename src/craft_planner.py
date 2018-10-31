import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf

#test comment from Samuel

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])

def clamp(n, smallest=-inf, largest=inf): return max(smallest, min(n, largest))

class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    requirements = {}
    #{"Requires": rule["Requires"], "Consumes": rule["Consumes"]
    if "Requires" in rule.keys():
        requirements["Requires"] = rule["Requires"]
    if "Consumes" in rule.keys():
        requirements["Consumes"] = rule["Consumes"]

    #TODO if we're running out of time, try writing multiple check functions 
    # that only look at relevant fields ie: dont look at Requires if there are none

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        if "Requires" in requirements.keys():
            for key, value in requirements["Requires"].items():
                if state[key] == 0:
                    return False
        if "Consumes" in requirements.keys():
            for key, value in requirements["Consumes"].items():
                if not state[key] == value:
                    return False
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    change = {}
    if "Produces" in rule.keys():
        change["Produces"] = rule["Produces"]
    if "Consumes" in rule.keys():
        change["Consumes"] = rule["Consumes"]

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()
        if "Consumes" in rule.keys():
            for key, value in change["Consumes"].items():
                next_state[key] -= value

        for key, value in change["Produces"].items():
            next_state[key] += value

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        #print("checking goal: ", goal)
        #print("against state: ", state)
        for key, value in goal.items():
            try:
                if not state[key] == value:
                    return False
            except KeyError:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    #global all_recipes
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state):
    # Implement your heuristic here!
    return 0

def search(graph, state, is_goal, limit, heuristic):
    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state

    # The priority queue
    queue = [(0, state, "No Action")]

    # The dictionary that will be returned with the costs
    distances = {}
    distances[state] = 0

    # The dictionary that will store the backpointers
    backpointers = {}
    backpointers[state] = None

    while queue and time() - start_time < limit:
       # print("in loop")
        current_dist, current_state, current_action = heappop(queue)

        # Check if current node is the destination
        if is_goal(current_state):
            #print("reached goal")
            # List containing all cells from initial_position to destination
            plan = [(current_state, current_action)]

            # Go backwards from destination until the source using backpointers
            # and add all the nodes in the shortest path into a list

            current_back_node = backpointers[current_state]
            while current_back_node is not None:
                plan.append(current_back_node)
                current_back_node = backpointers[current_back_node[0]]

            return plan[::-1]

        # Calculate cost from current note to all the adjacent ones
        for name, next_state, cost in graph(current_state):
            #print(name, cost)
            plancost = current_dist + cost

            # If the cost is new
            if next_state not in distances or plancost < distances[next_state]:
                distances[next_state] = plancost
                backpointers[next_state] = (current_state, name)
                heappush(queue, (plancost, next_state, name))

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Initialize first state from initial inventory
    
    print(Crafting['Initial'])
    for i in range(len(Crafting['Initial'])):
        state = State({key: 0 for key in Crafting['Items']})
         # Create a function which checks for the goal
        is_goal = make_goal_checker(Crafting['Goal'][i])
        #print(i)
        #print(Crafting['Initial'][i])
        #print(Crafting['Goal'][i])
        state.update(Crafting['Initial'][i])
        #print(state)

        # Search for a solution
        resulting_plan = search(graph, state, is_goal, 30, heuristic)

        if resulting_plan:
            # Print resulting plan
            #print("plan: ", resulting_plan)
            for state, action in resulting_plan:
                print('\t',state)
                print(action)
