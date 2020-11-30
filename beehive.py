# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 14:07:52 2020

@author: straw
"""
import pandas as pd
import random
import numpy as np
import copy
from itertools import filterfalse

import matplotlib.pyplot as plt

class Flowerfield:
    def __init__(self):
        self.flowers = self.grow_flowers()
    
    def grow_flowers(self):
        df = pd.read_excel('Champ de pissenlits et de sauge des pres.xlsx')
        subset = df[['x', 'y']]
        flowers = [tuple(x) for x in subset.to_numpy()]
        del df
        return flowers
    
    def display_field(self):
        plt.figure(0)
        plt.scatter(*zip(*self.flowers), c = 'yellow', label='Flowers')
        plt.scatter(500, 500, c = 'red', label ='Hive')
        plt.legend()

class Bee():
    def __init__(self, index):
        self.index = index
        self.genes = self.pollen_gathering()
        self.score = 0
        
    def pollen_gathering(self):
        f = Flowerfield()
        genes = random.sample(f.flowers, 50)
        return genes
        
    def fitness(self):
        score = []
        for i in range(0, len(self.genes)-1):
            T1 = copy.copy(self.genes[i])
            T2 = copy.copy(self.genes[i+1])
            D = abs(T2[0]-T1[0]) + abs(T2[1]-T1[1])
            score.append(D)            
        self.score = sum(score)

class Hive():
    def __init__(self):
        self.bees = [Bee(i) for i in range(100)]
        
    def fitness(self):
        score = []
        for bee in self.bees:
            bee.fitness()
            s = copy.copy(bee.score)
            score.append(s)
        return score
    
    def mean_fitness(self):
        score = self.fitness()
        return np.mean(score)
        
    def ranking(self):
        score = self.fitness()
        return np.argsort(score)
        
    def selection(self, method='rank', n=20):
        if method == 'rank':
            ranking = self.ranking()
            
            best = []
            for bee in self.bees:
                if bee.index in ranking[0:n]:
                    new_bee = copy.copy(bee)
                    best.append(new_bee)
            
            worst = []
            for bee in self.bees:
                if bee.index in ranking[-n:]:
                    new_bee = copy.copy(bee)
                    worst.append(new_bee)
            
            del ranking
            
            return best, worst
            
        if method =='tournament':            
            best_bees = []
            for i in range(n):
                pair_index = random.sample(range(100), 2)
                pair = []
                for bee in self.bees:
                    if bee.index in pair_index:
                        new_bee = copy.copy(bee)
                        pair.append(new_bee)
                best_bee_index = np.argmin([pair[0].score, pair[1].score])
                if best_bee_index == 0:
                    best_bees.append(copy.copy(pair[0]))
                else:
                    best_bees.append(copy.copy(pair[1]))
            
            worst_bees = []
            for i in range(n):
                pair_index = random.sample(range(100), 2)
                pair = []
                for bee in self.bees:
                    if bee.index in pair_index:
                        new_bee = copy.copy(bee)
                        pair.append(new_bee)
                worst_bee_index = np.argmax([pair[0].score, pair[1].score])
                if worst_bee_index == 0:
                    worst_bees.append(copy.copy(pair[0]))
                else:
                    worst_bees.append(copy.copy(pair[1]))
            
            del pair, pair_index
            
            return best_bees, worst_bees
        
        if method =='battleroyale':
            best_bees = []
            worst_bees = []
            for i in range(n):
                group_index = np.random.choice(range(100), 5, replace=False)
                group = [copy.copy(bee) for bee in self.bees if bee.index in group_index]
                winner = group[np.argmin([copy.copy(bee.score) for bee in group])]
                looser = group[np.argmax([copy.copy(bee.score) for bee in group])]
                best_bees.append(winner)
                worst_bees.append(looser)
                del group_index, group, winner, looser

            return best_bees, worst_bees
                    
        if method == 'random':
            pseudo_best_index = random.sample(range(100), n)
            pseudo_worst_index = random.sample([i for i in range(100) if i not in pseudo_best_index], n)
            
            pseudo_best = []
            for bee in self.bees:
                if bee.index in pseudo_best_index:
                    new_bee = copy.copy(bee)
                    pseudo_best.append(new_bee)
            
            pseudo_worst = []
            for bee in self.bees:
                if bee.index in pseudo_worst_index:
                    new_bee = copy.copy(bee)
                    pseudo_worst.append(new_bee)
            
            del pseudo_best_index, pseudo_worst_index
            
            return pseudo_best, pseudo_worst
    
    def cross_over(self, method='rank', n=20):
        f = Flowerfield()
        best, worst = self.selection(method, n)
        children = []
        for p in range(0, len(best), 2):
            P1 = best[p].genes
            P2 = best[p+1].genes

            child1 = P1[0:25]
            for i in range(0, len(P2)):
                if P2[i] not in child1:
                    child1.append(P2[i])
                
            child2 = P2[0:25]
            for i in range(0, len(P1)):
                if P1[i] not in child2:
                    child2.append(P1[i])   

            M1 = list(filterfalse(set(child1).__contains__, f.flowers))
            if len(M1) > 0:
                print('Missing genes for child 1')
                child1 = child1 + M1
                children.append(child1)
            else:
                children.append(child1)
                
            M2 = list(filterfalse(set(child1).__contains__, f.flowers))
            if len(M2) > 0:
                print('Missing genes for child 2')
                child2 = child2 + M2
                children.append(child2)
            else:
                children.append(child2)
            
        for q in range(0, len(worst)):
            worst[q].genes = children[q]

        del children
            
        return worst

    def mutation(self, method='rank', n=20):
        children = self.cross_over()
        length = 5
        for child in children:
            start = random.randint(0, 50-length)
            part = child.genes[start:start+length]
            random.shuffle(part)
            mutant = child.genes[0:start] + part + child.genes[start+length:len(child.genes)]
            child.genes = mutant
        return children
    
    def relay(self, method='rank', n=20, mutate = False):
        if mutate :
            children = self.mutation(method=method, n=n)
            for i in range(0, len(children)):
                for j in range(0, len(self.bees)):
                    if self.bees[j].index == children[i].index:
                        self.bees[j].genes = children[i].genes
        else:
            children = self.cross_over(method=method, n=n)
            for i in range(0, len(children)):
                for j in range(0, len(self.bees)):
                    if self.bees[j].index == children[i].index:
                        self.bees[j].genes = children[i].genes

    def evolution(self, nb_gen=1000):
        i = 0
        M = False
        performance = [self.mean_fitness()]
        while i < nb_gen :
            perf1 = self.mean_fitness() 
            self.relay(method='rank', mutate = M)
            perf2 = self.mean_fitness() 
            performance.append(self.mean_fitness())
            if abs(perf2 - perf1) < (perf2*5)/100:
                M = True
            else:
                M = False
            i = i + 1
        return performance        
    
    def plot_performance(self):
        performance = self.evolution()
        plt.plot(performance)
        plt.xlabel('Generation of bees')
        plt.ylabel('Fitness score')
        plt.title('Fitness score variation for n generations of bees')
    
    def plot_best_bee(self):
        Killer_B = self.bees[self.ranking()[-1]].genes
        plt.plot(*zip(*Killer_B), c='orange', linestyle=':')
        plt.scatter(*zip(*Killer_B), c = 'green', label='Flowers')
        plt.title('Best bee trajectory of last generation')
        
if __name__ == '__main__':
    f = Flowerfield()
    h = Hive()
    plt.figure(1)
    h.plot_performance()
    plt.figure(2)
    h.plot_best_bee()

            
    
    

    