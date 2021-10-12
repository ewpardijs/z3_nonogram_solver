from z3 import *
import pandas as pd
import xml.etree.ElementTree as ET

class Nonogram():
    def __init__(self,  column_blocks, row_blocks, title="", author=""):
        self.title = title
        self.author = author
        self.CB = column_blocks
        self.RB = row_blocks
        self.cols = len(column_blocks)
        self.rows = len(row_blocks)

    def solve(self):
        self.s = Solver()
        self.set_variables()
        self.add_constraints()
        if self.s.check():
            return (True, self.evaluate_grid())
        else:
            return (False, None)


    def set_variables(self):
        self.C = [[Bool("C_%d_%d" % (r, c)) for c in range(self.cols)] for r in range(self.rows)]
        self.RS = [[Int("RS_%d_%d" % (r, b)) for b in range(len(self.RB[r]))] for r in range(self.rows)]
        self.CS = [[Int("CS_%d_%d" % (c, b)) for b in range(len(self.CB[c]))] for c in range(self.cols)]

    def add_constraints(self):
        for r in range(self.rows):
            for b in range(len(self.RB[r])):
                self.s.add(self.RS[r][b] >= 0)
                self.s.add(self.RS[r][b] <= self.cols - self.RB[r][b])  # Block is within the boundaries
                if (b > 0):
                    self.s.add(self.RS[r][b] > self.RS[r][b - 1] + self.RB[r][
                    b - 1])  # Block is at least one space after the previous block
            for c in range(self.cols):
                # Cell within a block <==> Cell is filled
                self.s.add(
                    self.C[r][c] == Or([And(self.RS[r][b] <= c, c < self.RS[r][b] + self.RB[r][b]) for b in range(len(self.RB[r]))]))

        for c in range(self.cols):
             for b in range(len(self.CB[c])):
                self.s.add(self.CS[c][b] >= 0)
                self.s.add(self.CS[c][b] <= self.rows - self.CB[c][b])
                if (b > 0):
                    self.s.add(self.CS[c][b] > self.CS[c][b - 1] + self.CB[c][b - 1])
             for r in range(self.rows):
                self.s.add(
                    self.C[r][c] == Or([And(self.CS[c][b] <= r, r < self.CS[c][b] + self.CB[c][b]) for b in range(len(self.CB[c]))]))

    def evaluate_grid(self):
        m = self.s.model()
        return pd.DataFrame.from_records(self.C).applymap(lambda x: bool(m.evaluate(x)))

def parse_from_xml(path):
    puzzle = ET.parse(path).getroot().find('puzzle')
    for x in puzzle.findall('clues'):
        if x.attrib['type'] == 'columns':
            CB = [[int(block.text) for block in line.findall('count')] for line in x.findall('line')]
        elif x.attrib['type'] == 'rows':
            RB = [[int(block.text) for block in line.findall('count')] for line in x.findall('line')]
    title = puzzle.find('title').text
    author = puzzle.find('author').text
    return Nonogram(column_blocks=CB, row_blocks=RB, title=title, author=author)

def process_blocks(f):
    b = []
    for line in f:
        if (not line[0].isdigit()):
            return b, line
        if line == "0\n":
            b.append([])
        else:
            b.append([int(x) for x in line.rstrip('\n').split(',')])

def parse_from_non(path):
    non = {}
    with open(path) as f:
        line = f.readline()
        while line:
            if line == 'columns\n':
                non['c'], line = process_blocks(f)
                continue
            if line == 'rows\n':
                non['r'], line = process_blocks(f)
                continue
            else:
                try:
                    k, v = line.split(" ", 1)
                    non[k] = v.rstrip("\n")
                except ValueError:
                    pass
            line = f.readline()
    return Nonogram(column_blocks=non['c'], row_blocks=non['r'], title=non.get('title'), author=non.get('by'))

def parse_nonogram(path):
    _, ext = os.path.splitext(path)
    if (ext == '.xml'):
        return parse_from_xml(path)
    if (ext == '.non'):
        return parse_from_non(path)