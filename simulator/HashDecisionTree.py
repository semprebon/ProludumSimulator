# Represents a binary decision tree

#                 staggered?
#                 /     \
#            Yes /       \ No
#               /         \
#    many_attackers?     BasicAttack
#       /      \
#  Yes /        \ No
#     /          \
# Defend   DefensiveAttack
#
# Each branch node represents a test of the current situation, with subnodes
# representing what to do for true and false results.
#
# In yaml form, the tree should be easily interpreted, so the following
# structure is used: { test: { True: node, False: node } }
#
# However, we also need to have a form that can be easily manpulated by the genetic
# algorithm - i.e., a breadth-first array
#
#      0              1               2          3         4
# [ staggered?, many_attackers?, BasicAttack, Defend, DefensiveAttack ]
#
# In this case for a branch node i, the True node is at 2i+1, and the false node at 2i+2
#
# TODO: store strings seperately and use indexes in tree for more compact storage
from simulator.decision_tree import DecisionTree


class HashDecisionTree(DecisionTree):

    # initialize a tree from a copy of its internal representation
    def __init__(self, tests, decisions, data):
        self.root_node = data
        self.tests = tests
        self.decisions = decisions

    @classmethod
    def branch_node(cls, value, true_subtree, false_subtree):
        return { value: { True: true_subtree, False: false_subtree } }

    @classmethod
    def leaf_node(cls, value):
        return value

    def root(self):
        return self.root_node

    def is_branch(self, node):
        return isinstance(node, dict)

    def is_leaf(self, node):
        return not self.is_branch(node)

    def test(self, node, inputs):
        return inputs[self.data(node)]

    def true_node(self, node):
        return node[self.data(node)][True]

    def false_node(self, node):
        return node[self.data(node)][False]

    def data(self, node):
        if self.is_branch(node):
            return list(node.keys())[0]
        else:
            return node

    def replace_subnode(self, node, old_node, new_node):
        if self.true_node(node) == old_node:
            node[True] = new_node
        if self.false_node(node) == old_node:
            node[False] = new_node

    def replace_node(self, old_node, new_node):
        if self.root == old_node:
            self.root = new_node
        self.breadth_first_traverse(branch_visitor=lambda node: self.replace_subnode(node, old_node, new_node))

    def replace_node_data(self, node, new_data):
        if self.is_leaf_node(node):
            self.replace_node(node, new_data)
        else:
            node[new_data] = node[self.data(node)]
            del node[self.data(node)]
