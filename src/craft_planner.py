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
    

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        #print(requirements, state)
        if "Requires" in requirements.keys():
            for key, value in requirements["Requires"].items():
                if state[key] == 0:
                    return False
        if "Consumes" in requirements.keys():
            for key, value in requirements["Consumes"].items():
                if state[key] < value:
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
            #if key in goal_components:
            #    goal_components[key] -= value

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
    
    valid_recipes = []
    for r in all_recipes:
        #print('recipe', r)
        if r.check(state):
            valid_recipes.append((r.name, r.effect(state), r.cost))
    #print(valid_recipes[0][0])
    return valid_recipes


def heuristic(state):

    for key, value in state.items():
        if key not in goal_components:
            return inf
        elif value > goal_components[key]:
            return inf
    print("return 0 for state, ", state)
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
        #print(current_state)

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
            #print(name)
            plancost = current_dist + cost

            # If the cost is new
            if next_state not in distances or plancost < distances[next_state]:
                #print(next_state, current_state)
                distances[next_state] = plancost
                backpointers[next_state] = (current_state, name)
                #diff = { k : next_state[k] - current_state[k] for k in next_state }
                #print(diff)
                #
                heappush(queue, (plancost + heuristic(next_state), next_state, name))

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None
#"coal":['iron_pickaxe', 'stone_pickaxe', 'wood_pickaxe'], "ore":['iron_pickaxe', 'stone_pickaxe'],
#parts = { "bench": ['plank', 'wood'], "wooden_pickaxe": ['bench', 'plank', 'stick', 'wood'], "stone_pickaxe":['bench', 'cobble','stick','wood'], "iron_pickaxe":['bench', 'planks', 'wood', 'ingot', 'stick', 'furnace', 'coal','ore'], "wooden_axe":['bench', 'plank','wood','stick'],"stone_axe":['bench','cobble','stick','wood','stone_pickaxe','wood_pickaxe','iron_pickaxe']"iron_axe":,['bench', 'plank','wood','ingot','stick','furnace','coal','ore'] ]}

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
    item_cost_map = {}
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)
        key = list(rule['Produces'])[0]
        item_cost_map[key] = rule.get('Consumes')
        if item_cost_map[key] != None and rule.get('Requires') != None:
            item_cost_map[key].update(rule.get('Requires'))
        elif rule.get('Requires') != None:
            item_cost_map[key] = rule.get('Requires')
    print("Item cost map:", item_cost_map)

    #print(Crafting['Initial'])
    for i in range(len(Crafting['Initial'])):
        state = State({key: 0 for key in Crafting['Items']})

        goal = Crafting['Goal'][i]
        is_goal = make_goal_checker(Crafting['Goal'][i])
        state.update(Crafting['Initial'][i])
        #print(state)

        goal_components = {}
    
        #tools = ['bench', 'wooden_pickaxe', 'wooden_axe', 'stone_axe', 'stone_pickaxe', 'iron_pickaxe', 'iron_axe', 'furnace']

        requirements = []

        for item in goal:
            requirements.append((item, goal[item]))

        print(requirements)

        while len(requirements) != 0:
            item, num = requirements.pop()

            if item + " for " in list(Crafting['Recipes'].keys()) or " in " + item in list(Crafting['Recipes'].keys()):
                goal_components[item] = 1
            else:
                if goal_components.get(num) != None:
                    goal_components[item] += num
                else:
                    goal_components[item] = num

            for action in Crafting['Recipes']:

                if item in Crafting['Recipes'][action]['Produces']:
                    if 'Consumes' in Crafting['Recipes'][action]:
                        for consumable in Crafting['Recipes'][action]['Consumes']:
                            requirements.append((consumable, Crafting['Recipes'][action]['Consumes'][consumable]))
                    if 'Requires' in Crafting['Recipes'][action]:
                        for requireable in Crafting['Recipes'][action]['Requires']:
                            if goal_components.get(requireable) == None or goal_components[requireable] == 0:
                                requirements.append((requireable, 1))
        print("GOAL COMPONENTS: ", goal_components)

        # Search for a solution
        resulting_plan = search(graph, state, is_goal, 30, heuristic)

        if resulting_plan:
            # Print resulting plan
            #print("plan: ", resulting_plan)
            for state, action in resulting_plan:
                print('\t',state)
                print(action)
