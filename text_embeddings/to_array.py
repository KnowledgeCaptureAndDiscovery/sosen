from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

file = args.file

with open(file, "r") as in_file:
    stripped_lines = (line.rstrip('\n') for line in in_file)
    lines = [line for line in stripped_lines if len(line) > 1]
    print(" ".join(lines))