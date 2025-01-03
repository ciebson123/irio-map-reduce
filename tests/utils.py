import os
from collections import defaultdict
from pathlib import Path


def count_words(input_dir: Path):
    word_counts = defaultdict(int)
    for input_file in os.listdir(input_dir):
        if not input_file.startswith('.'):
            with open(input_dir / input_file, 'r') as f:
                for line in f:
                    for word in line.strip().split():
                        word_counts[word] += 1
    return word_counts

def read_mapreduce_outputs(output_dir: Path):
    word_counts = defaultdict(int)
    for output_file in os.listdir(output_dir):
        if not output_file.startswith('.'):
            with open(output_dir / output_file, 'r') as f:
                for line in f:
                    kval = line.strip().split()
                    word_counts[kval[0]] += int(kval[1])
    return word_counts