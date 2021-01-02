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

def resource_name(path):
    import string
    return os.path.splitext(os.path.basename(path))[0].rstrip(string.digits)

load_data_cache = {}

def load_data(files, filter=None, root=__file__, directory="data"):
    """Read YAML file and return list containing the data"""
    import yaml
    files = resolve_resources(files, root=root, directory=directory, ext="yaml")
    records = []
    for yamlfile in files:
        res_name = resource_name(yamlfile)
        item = load_data_cache.get(res_name, None)
        if item == None:
            with open(yamlfile) as file:
                item = yaml.safe_load(file)
                load_data_cache[res_name] = item
        records.append(item)

    if filter != None:
        records = [ item for item in records if filter(item) ]

    return records
