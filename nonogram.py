import os
import xml.etree.ElementTree as ET
from z3 import *
import pandas as pd

class Nonogram():

     def __parse(self, path):
         _, ext = os.path.splitext(path)
         if(ext == '.xml'):
             self.__parse_from_xml(path)

     def __parse_from_xml(self, path):
         puzzle = ET.parse(path).getroot().find('puzzle')
         for x in puzzle.findall('clues'):
             if x.attrib['type'] == 'columns':
                 self.CB = [[int(block.text) for block in line.findall('count')] for line in x.findall('line')]
             elif x.attrib['type'] == 'rows':
                 self.RB = [[int(block.text) for block in line.findall('count')] for line in x.findall('line')]
         self.title = puzzle.find('title').text
         self.author = puzzle.find('author').text
         self.authorid = puzzle.find('authorid').text
         self.id = puzzle.find('id').text
         self.description = puzzle.find('description').text
         self.note = puzzle.find('note').text
         self.cols = len(self.CB)
         self.rows = len(self.RB)

     def __init__(self, path):
         self.__parse(path)

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