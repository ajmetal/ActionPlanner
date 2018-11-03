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
        return 'State' + str(dict(item for item in self.items() if item[1] > 0))


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

    delta = {}
    if "Produces" in rule.keys():
        delta["Produces"] = rule["Produces"]
    if "Consumes" in rule.keys():
        delta["Consumes"] = rule["Consumes"]

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()
        #next_state = State({key: value for key, value in state.items()})
        if rule.get('Consumes'):
            for key, value in delta["Consumes"].items():
                next_state[key] -= value

        for key, value in delta["Produces"].items():
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
            try: #not sure if we need this try except block
                if not state[key] >= value:
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

def heuristic(state, diff, action):
    #print(state, action)
    for key, value in diff.items():
        if value > 0:
            if key in list(goal_components.keys()):
                if isinstance(goal_components[key], bool) and state[key] > 1:
                    #print("returning inf", key, state[key], state)
                    return inf
            else:
                return inf
                #all_actions.remove(action)
                #print(key, "not in goal")
                
    #print("return 0 for state, ", state)
    return 0

def search(graph, state, is_goal, limit, heuristic, goal):
    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state

    # The priority queue
    #cost, state, name of action
    queue = [(0, state, "No Action", )]

    # The dictionary that will be returned with the costs
    distances = {}
    distances[state] = 0

    # The dictionary that will store the backpointers
    backpointers = {}
    backpointers[state] = None

    visited = set(state)

    #how many required actions were taken
    length = 0
    current_state = state
    while queue and time() - start_time < limit:
       # print("in loop")
        current_dist, current_state, current_action = heappop(queue)
        #print(current_state, current_dist)
        #print(queue)
        #print([i[0] for i in queue])
        # Check if current node is the destination
        if is_goal(current_state):
            #print("reached goal")
            # List containing all cells from initial_position to destination
            plan = [(current_state, current_action, current_dist, length)]

            # Go backwards from destination until the source using backpointers
            # and add all the nodes in the shortest path into a list

            current_back_node = backpointers[current_state]
            while current_back_node is not None:
                plan.append(current_back_node)
                current_back_node = backpointers[current_back_node[0]]

            return plan[::-1]

        length += 1

        # Calculate cost from current note to all the adjacent ones
        for action, next_state, cost in graph(current_state):
            #print(name)
            plancost = current_dist + cost
            # If the cost is new
            #if next_state not in distances or plancost < distances[next_state] and next_state not in visited:
            diff = { k : next_state[k] - current_state[k] for k in next_state }
            h = heuristic(next_state, diff, action)
            if next_state not in distances or plancost + h < distances[next_state] and next_state:
                #print(next_state, current_state)
                distances[next_state] = plancost
                #visited.add(next_state)
                backpointers[next_state] = (current_state, action, plancost, length)
                #
                #print(diff)
                #
                
                if h != inf:
                    heappush(queue, (plancost + h, next_state, action))

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    print('the state is: ', current_state)
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

    #print(Crafting['Initial'], Crafting['Goal'], len(Crafting['Initial']), len(Crafting['Goal']))

    # Build rules
    item_cost_map = {}
    all_recipes = []
    master_actions = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        master_actions.append(name)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)
        key = list(rule['Produces'])[0]
        item_cost_map[key] = rule.get('Consumes')
        if item_cost_map[key] != None and rule.get('Requires') != None:
            item_cost_map[key].update(rule.get('Requires'))
        elif rule.get('Requires') != None:
            item_cost_map[key] = rule.get('Requires')
    #print("Item cost map:", item_cost_map)
    #print("All recipes: ", all_recipes)
    #print(Crafting['Initial'])
    for i in range(len(Crafting['Initial'])):
        starting_state = State({key: 0 for key in Crafting['Items']})
        all_actions = master_actions.copy()
        goal = Crafting['Goal'][i]
        is_goal = make_goal_checker(Crafting['Goal'][i])
        starting_state.update(Crafting['Initial'][i])
        #print(state)

        goal_components = {}

        item_list = []

        for item in goal:
            item_list.append((item, goal[item]))

        #print(item_list)

        while len(item_list) != 0:
            item, num = item_list.pop()

            if item + " for " in list(Crafting['Recipes'].keys()) or " in " + item in list(Crafting['Recipes'].keys()):
                goal_components[item] = 1
            else:
                if goal_components.get(num):
                    goal_components[item] += num
                else:
                    goal_components[item] = num

            for action in Crafting['Recipes']:

                if Crafting['Recipes'][action]['Produces'].get(item):
                    if Crafting['Recipes'][action].get('Consumes'):
                        for k, v in Crafting['Recipes'][action]['Consumes'].items():
                            item_list.append((k, v))

                    if Crafting['Recipes'][action].get('Requires'):
                        for k, v in Crafting['Recipes'][action]['Requires'].items():
                            if goal_components.get(k) == None or goal_components[k] == 0:
                                item_list.append((k, v))

        print("\nGOAL COMPONENTS: ", goal_components, '\n')

        # Search for a solution
        print('\ngoal, start ', goal, starting_state)
        resulting_plan = search(graph, starting_state, is_goal, 30, heuristic, Crafting['Goal'][i])
        if resulting_plan:
            state = resulting_plan[0][0]
            action = resulting_plan[0][1]
            cost = resulting_plan[0][2]
            length = resulting_plan[0][3]
            
            print('end state: ', state)
            print("action: ", action)
            print('cost: ', cost)
            print('len: ', length)
