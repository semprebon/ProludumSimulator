import os


def resource_path(filename, root=None, directory="resources", ext=None):
    """Returns the full pathname of the specified file in a resource directory"""
    root = __file__ if root == None else root
    root = os.path.dirname(root) if not os.path.isdir(root) else root

    while root != os.path.dirname(root):
        path = os.path.join(root, directory, filename)
        if os.path.isfile(path):
            return os.path.abspath(path)
        if ext is not None:
            path = f"{path}.{ext}"
        if os.path.isfile(path):
            return os.path.abspath(path)
        root = os.path.dirname(root)
    raise FileNotFoundError(f"Resource not found: {filename}")

def resolve_resources(filenames, root=None, directory="resources", ext=None):
    filenames = [filenames] if isinstance(filenames, str) else filenames

    return [resource_path(f, root=root, directory=directory, ext=ext) for f in filenames]


def load_data(files, filter=None, root=__file__, directory="data"):
    """Read YAML file and return list containing the data"""
    import yaml
    files = resolve_resources(files, root=root, directory=directory, ext="yaml")
    records = []
    for yamlfile in files:
        with open(yamlfile) as file:
            items = yaml.safe_load(file)
            items = [items] if isinstance(items, dict) else items
            records += items

    if filter != None:
        records = [ item for item in records if filter(item) ]

    return records
