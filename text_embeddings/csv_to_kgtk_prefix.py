import sys

assert(len(sys.argv) == 2)
file = sys.argv[1]

with open(file, "r") as in_file:
    print("node1\tlabel\tnode2")
    for line in in_file:
        line_split = line.split(",")
        if len(line_split) == 2:
            prefix, value = line_split
            print(f"{prefix}\tprefix_expansion\t{value}")