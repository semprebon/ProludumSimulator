import ast

with open("../data/situations.dat", "w") as out:
    with open("../simulation.log") as log:
        for line in log:
            situaton = ast.literal_eval(line.split(";", 2)[1])
            out.write(f"{situaton}\n")


