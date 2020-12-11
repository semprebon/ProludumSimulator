# Takes a decision tree where each non-terminal node is a hash of the form
# { tag:  name, True: node, False: node }, and converts it into a genetic string
# represented as an array of numbers
class DecisionTreeCoder():

    def __init__(self, domain):
        self.domain = domain

    def translate_tag(self, tag):
        return self.domain.index(tag)

    def translate_node(self, node):
        if isinstance(node, str):
            return self.translate_tag(node, self.domain)
        else:
            return self.translate_tag(node['tag'], self.domain)

    def encode(self, node):
        gene = []
        if isinstance(node, str):
            gene.append(self.translate(node, self.domain))
        else:
            gene.append(self.translate(node['tag'], self.domain))
            gene.append(self.translate(node[False], self.domain))
            gene.append(self.translate(node[True], self.domain))


        gene.append()