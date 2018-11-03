import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf


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
    
    print(all_recipes)
    del all_recipes["craft wooden_pickaxe at bench"]
    print(all_recipes)