from z3 import *
import pandas as pd
from nonogram import Nonogram, parse_nonogram
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FuncFormatter, NullFormatter
import argparse
import os

parser = argparse.ArgumentParser(description='List the content of a folder')
parser.add_argument('Path', metavar='path', type=str, help='path to puzzle file')
args = parser.parse_args()


def visualize_grid(df, cb, rb):
    na = df.to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(len(cb)/2, len(rb)/2))
    plt.grid(b=True, which='both')

    ax.set_xticks(range(len(cb)))
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.xaxis.set_minor_formatter(FuncFormatter(lambda x, i:  "\n".join([str(n) for n in cb[i]]) if i < len(cb) else ""))
    ax.tick_params(axis='x', labelrotation=90)
    ax.xaxis.label.set_size(40)


    ax.set_yticks(range(len(rb)))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda x, i: " ".join([str(n) for n in rb[::-1][i]]) if i < len(rb) else ""))
    ax.yaxis.set_major_formatter(NullFormatter())
    ax.yaxis.label.set_size(40)


    ax.imshow(na, cmap='GnBu', interpolation='nearest', origin='upper', extent=[0, len(cb), 0, len(rb)], aspect='auto')
    ax.grid(which='minor', color='b', linestyle='-', linewidth=2)

    plt.savefig(os.path.splitext(args.Path)[0]+'.png')

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

if __name__ == '__main__':
    nonogram = parse_nonogram(args.Path)
    res = nonogram.solve()
    if res[0]:
        visualize_grid(res[1], nonogram.CB, nonogram.RB)
    else:
        print("No solution found")
