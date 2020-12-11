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

class DecisionTree:

    @classmethod
    def branch_node(cls, true_subtree, false_subtree):
        raise NotImplementedError

    @classmethod
    def leaf_node(cls, value):
        raise NotImplementedError

    def root(self):
        raise NotImplementedError

    def is_branch(self, node):
        raise NotImplementedError

    def is_leaf(self, node):
        raise NotImplementedError

    def test(self, node, inputs):
        raise NotImplementedError

    def true_node(self, node):
        raise NotImplementedError

    def false_node(self, node):
        raise NotImplementedError

    def data(self, node):
        raise NotImplementedError

    def replace_node(self, node, new_node):
        raise NotImplementedError

    def replace_node_data(self, node, new_data):
        raise NotImplementedError

    @classmethod
    def from_yaml_data_(cls, data):
        ''' In yaml form, the tree should be easily interpreted, so the following
        structure is used: { test: { True: node, False: node } } '''

        if isinstance(data, str):
            return cls.leaf_node(str)
        else:
            test = data.keys[0]
            return cls.branch_node(test,
                                        cls.from_yaml_data(data[test][True]),
                                        cls.from_yaml_data(data[test][False]))

    # Make a decision from a set of inputs.
    # The inputs are in the form of a dict, with an entry for each
    # possible attribute, where the key is the attribute name and the value is
    # True or False
    def decide(self, inputs):
        node = self.root()
        while self.is_branch(node):
            if self.test(node, inputs):
                node = self.true_node(node)
            else:
                node = self.false_node(node)
        return self.data(node)

    def _breadth_first_traverse(self, node, branch_visitor=None, leaf_visitor=None):
        if self.is_leaf(node):
            if leaf_visitor != None:
                leaf_visitor.visit(self.data(node))
        else:
            if branch_visitor != None:
                branch_visitor.visit(self.data(node))
                self._breadth_first_traverse(self.true_node(node), branch_visitor, leaf_visitor)
                self._breadth_first_traverse(self.false_node(node), branch_visitor, leaf_visitor)

    def breadth_first_traverse(self, node_visitor=None, leaf_visitor=None):
        self._breadth_first_traverse(self.root(), node_visitor, leaf_visitor)

    class Counter:
        def __init__(self):
            self.count = 0
        def visit(self, obj):
            self.count += 1

    def size(self):
        counter = self.Counter()
        self.breadth_first_traverse(counter, counter)
        return counter.count

    def branch_count(self):
        counter = self.Counter()
        self.breadth_first_traverse(counter, None)
        return counter.count

    def leaf_count(self):
        counter = self.Counter()
        self.breadth_first_traverse(None, counter)
        return counter.count

