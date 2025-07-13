import os

data_dir = "./data/eur-lexsum/processed-data"
summary_prefix = "val-oracle_summaries_batch_"
labels_prefix = "val-oracle_labels_batch_"
output_summary = "val-oracle_summaries_merged.txt"
output_labels = "val-oracle_labels_merged.txt"

batch_files = [f for f in os.listdir(data_dir) if f.startswith(summary_prefix)]
batch_numbers = sorted(
    [int(f[len(summary_prefix):-4]) for f in batch_files]
)

# Open output files
with open(os.path.join(data_dir, output_summary), "w", encoding="utf-8") as out_sum, 
     open(os.path.join(data_dir, output_labels), "w", encoding="utf-8") as out_lab:

    for batch_num in batch_numbers:
        sum_file = os.path.join(data_dir, f"{summary_prefix}{batch_num}.txt")
        lab_file = os.path.join(data_dir, f"{labels_prefix}{batch_num}.txt")

        with open(sum_file, encoding="utf-8") as f_sum:
            out_sum.write(f_sum.read())
            if not f_sum.read().endswith("\n"):
                out_sum.write("\n")

        with open(lab_file, encoding="utf-8") as f_lab:
            out_lab.write(f_lab.read())
            if not f_lab.read().endswith("\n"):
                out_lab.write("\n")

print(f"Merged {len(batch_numbers)} batches into:")
print(f"- {output_summary}")
print(f"- {output_labels}")
