from simulator.decision_tree import DecisionTree

# The binary tree here is stored in an array where, for parent node stored at
# n, the True and False nodes are stored at 2n+1 and 2n+2. Not all spaces in
# the tree are used, and each tree will need space = d^2-1 where d = max depth
class EvolutionaryDecisionTree(DecisionTree):
    def __init__(self, tests, decisions, data=[]):
        self.tree_data = data
        self.tests = tests
        self.decisions = decisions

    @classmethod
    def tree_size_to_depth(cls, size):
        depth = 0
        while size > 1:
            size = size / 2
            depth = depth + 1
        return depth

    @classmethod
    def tree_depth_to_size(cls, depth):
        return 2^depth - 1

    @classmethod
    def branch_node(cls, value, true_subtree, false_subtree):
        max_len = max(len(true_subtree), len(false_subtree))
        data = [value] + 2*max_len * [None]
        cls.place_tree(data, 1, true_subtree, 0)
        cls.place_tree(data, 2, false_subtree, 0)

        return data

    @classmethod
    def place_tree(cls, dest, dest_offset, src, src_offset):
        dest[dest_offset] = src[src_offset]
        if src_offset*2+2 < len(src):
            cls.place_tree(dest, dest_offset*2+1, src, src_offset*2+1)
            cls.place_tree(dest, dest_offset*2+2, src, src_offset*2+2)

    @classmethod
    def leaf_node(cls, value):
        return [value]

    def root(self):
        return 0

    def is_branch(self, node):
        return self.tree_data[node] in self.tests

    def is_leaf(self, node):
        return self.tree_data[node] in self.decisions

    def test(self, node, inputs):
        return inputs[self.tree_data[node]]

    def true_node(self, node):
        return 2*node+1

    def false_node(self, node):
        return 2*node+2

    def data(self, node):
        return self.tree_data[node]

    def node_depth(self, node):
        node_depth = 0
        while node > 1:
            node = node / 2
            node_depth = node_depth + 1
        return node_depth

    def depth(self):
        return self.node_depth(len(self.tree_data - 1))

    def resize(self, depth):
        new_size = self.tree_depth_to_size(depth)
        if new_size > len(self.tree_data):
            self.tree_data = self.tree_data + (new_size - len(self.tree_data)) * [None]

    def replace_node(self, node, new_node):
        new_depth = self.node_depth(node) + new_node.depth()
        if new_depth > self.depth():
            self.resize(new_depth)
        self.place_tree(self.tree_data, node, new_node.data, 0)

    def replace_node_data(self, node, new_data):
        self.tree_data[node] = new_data

