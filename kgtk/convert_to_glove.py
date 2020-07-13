import sys
in_file = sys.argv[1]
out_file = sys.argv[2]

vec_size = 0
line_count = 0

with open(in_file, "r") as in_file:
    with open(out_file, "w") as out_file:
        for line in in_file:
            row = line.split("\t")
            if len(row) == 3 and row[1] == "text_embedding":
                line_count += 1

                row_id = row[0]
                vector = row[2].split(",")

                if vec_size == 0:
                    vec_size = len(vector)

                reformat_vector = ['{:.3f}'.format(float(x)) for x in vector]
                full_row = f"{row_id} {' '.join(reformat_vector)}\n"

                out_file.write(full_row)

print(f"{line_count} {vec_size}")