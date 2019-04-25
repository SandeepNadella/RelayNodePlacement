
# coding: utf-8

# In[5]:

#$ pip install networkx

#Recommend running the program in jupyter notebook since it's developed in that.
#Install jupyter notebook $pip install jupyter

#importing graphviz for fixed graph layout. graphviz should be installed using homebrew.
#$brew install graphviz 
#$pip install pygraphviz

#To run over terminal: $ python3 relay_node_placement.py (Not Recommended since graph UI may not be appealing!)
import sys

import matplotlib.pyplot as plt
import networkx as nx
import random
import math
import itertools as it

from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms import approximation as apxalgo

print("Enter the values or leave blank for default values. Pay attention to the console logs.")
#set range R
R = float(input("Enter maximum Range R(must be number):") or "5")
#set max budget B1 for BCRP-MNCC
B1 = float(input("Enter maximum Budget B1(must be number):") or "5")

#set max distance between two sensor nodes
maxdist = float(input("Enter max distance between two sensor nodes(must be number):") or "50")

print('Algorithm 4: Heuristic for solving BCRP-MNCC problem with the given number of sensor nodes')
print("Range R: ",R)
print("Budget B1: ",B1)
print("Maximum distance between two sensor nodes: ",maxdist)

#creating the sensor node graph with random edges
N= random.randint(3,int(input("Enter maximum number of nodes to generate(must be number):") or "5"))
G= nx.complete_graph(N)
nx.set_node_attributes(G, True, name='sensornode')


for (a,b) in G.edges():
    G.edges[a,b]['length'] = random.randint(1,maxdist)
    G.edges[a,b]['weight'] = 0 if (math.ceil(G.edges[a,b]['length']/R)-1)<0 else (math.ceil(G.edges[a,b]['length']/R)-1)

print('Initial Graph G')
print('Edges: ')
print(G.edges(data=True))
print('Nodes: ')
print(G.nodes(data=True))

n = len(G)
#creating the source sensor node graph with fixed edges
# G = nx.cycle_graph(5)
# G.add_edge(0,1,weight=2)
# G.add_edge(0,3,weight=3)
# G.add_edge(0,4,weight=3)
# G.add_edge(1,2,weight=3)
# G.add_edge(2,3,weight=5)
# G.add_edge(3,4,weight=2)
G.pos = graphviz_layout(G)

#sensor nodes are represented by green and relay nodes by red
print("Green nodes indicate Sensor nodes and Red nodes indicate Relay nodes")
colorvalues = ['green' if node[1].get('sensornode') else 'red' for node in G.nodes(data=True)]

#ploting the source sensor node graph G
plt.figure(figsize=(20,14))
plt.title("Sensor Node Graph G")
pos=G.pos
edge_labels=nx.get_edge_attributes(G,'length')
nx.draw_networkx_edge_labels(G,pos,edge_labels, font_size=18, font_color='black', font_family='sans-serif', font_weight='bold')
nx.draw_networkx(G,pos,with_labels=True,node_size=1000, node_color=colorvalues, font_size=18, font_color='white', font_family='sans-serif', font_weight='bold')
plt.show()


#Algorithm 4
#computing the minimum spanning tree(MST) based on edge length i.e distance between points
Tp = nx.minimum_spanning_tree(G,weight='length', algorithm='prim')
Tp.pos = graphviz_layout(G)

#sad that python doesn't provide do while
weightsum =0
for edge in Tp.edges(data=True):
    weightsum = weightsum+edge[2].get('weight')

print(weightsum, ' Relay nodes needed')
if weightsum>B1:
    print('Budget constraint violated!')
else:
    print('Budget constraint NOT violated!')
    

#plotting the forest Tp
plt.clf
plt.figure(figsize=(20,14))
plt.title("Initial MST Tp")
pos=Tp.pos
colorvalues = ['green' if node[1].get('sensornode') else 'red' for node in Tp.nodes(data=True)]
edge_labels=nx.get_edge_attributes(Tp,'length')
nx.draw_networkx_edge_labels(Tp,pos,edge_labels, font_size=18, font_color='black', font_family='sans-serif', font_weight='bold')
nx.draw_networkx(Tp,pos,with_labels=True,node_size=1000, node_color=colorvalues, font_size=18, font_color='white', font_family='sans-serif', font_weight='bold')
plt.show()

prunecount=0
while weightsum>B1:
    maxweightedge = None
    maxweight = 0
    for edge in Tp.edges(data=True):
        if edge[2].get('weight')>maxweight:
            maxweightedge = edge
            maxweight = edge[2].get('weight')
    Tp.remove_edge(maxweightedge[0],maxweightedge[1])
    prunecount+=1
    
    #plotting the forest Tp after each prune
    plt.clf
    plt.figure(figsize=(20,14))
    plt.title("Forest Tp after pruning "+str(prunecount)+" times")
    pos=Tp.pos
    colorvalues = ['green' if node[1].get('sensornode') else 'red' for node in Tp.nodes(data=True)]
    edge_labels=nx.get_edge_attributes(Tp,'length')
    nx.draw_networkx_edge_labels(Tp,pos,edge_labels, font_size=18, font_color='black', font_family='sans-serif', font_weight='bold')
    nx.draw_networkx(Tp,pos,with_labels=True,node_size=1000, node_color=colorvalues, font_size=18, font_color='white', font_family='sans-serif', font_weight='bold')
    plt.show()
    
    weightsum =0
    for edge in Tp.edges(data=True):
        weightsum = weightsum+edge[2].get('weight')


# In[6]:


# add relay nodes for visualization purpose
Tpp = Tp.copy()
lastnodenumber = len(Tp.nodes()) - 1
for edge in Tpp.edges(data=True):
    sensornodelist = list(range(1, edge[2].get("weight") + 1))
    sensornodelist = [x + lastnodenumber for x in sensornodelist]
    if len(sensornodelist) != 0:
        lastnodenumber = max(sensornodelist)
        for i in sensornodelist:
            Tp.add_node(i, sensornode=False)
        Tp.add_path(
            [edge[0]] + sensornodelist + [edge[1]],
            length=round((edge[2].get("length") / (edge[2].get("weight") + 1)), 1),
        )
        Tp.remove_edge(edge[0], edge[1])

Tp.pos = graphviz_layout(Tp)

print("Final forest with sensor and relay nodes(if any)")
print("Edges: ")
print(Tp.edges(data=True))
print("Nodes: ")
print(Tp.nodes(data=True))

# plotting the final forest Tp
plt.clf
plt.figure(figsize=(20, 14))
plt.title("Final forest Tp")
pos = Tp.pos
colorvalues = [
    "green" if node[1].get("sensornode") else "red" for node in Tp.nodes(data=True)
]
edge_labels = nx.get_edge_attributes(Tp, "length")
nx.draw_networkx_edge_labels(
    Tp,
    pos,
    edge_labels,
    font_size=18,
    font_color="black",
    font_family="sans-serif",
    font_weight="bold",
)
nx.draw_networkx(
    Tp,
    pos,
    with_labels=True,
    node_size=1000,
    node_color=colorvalues,
    font_size=18,
    font_color="white",
    font_family="sans-serif",
    font_weight="bold",
)

plt.show()


# In[8]:


print(
    "Algorithm 5: Heuristic for solving BCRP-MLCC problem with the given number of sensor nodes"
)

B2 = float(input("Enter maximum Budget B2(must be number):") or B1)
print("Budget B2: ", B2)

# ploting the source sensor node graph G
plt.clf
plt.figure(figsize=(20, 14))
plt.title("Initial Sensor Node Graph G")
pos = G.pos
colorvalues = [
    "green" if node[1].get("sensornode") else "red" for node in G.nodes(data=True)
]
edge_labels = nx.get_edge_attributes(G, "length")
nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels,
    font_size=18,
    font_color="black",
    font_family="sans-serif",
    font_weight="bold",
)
nx.draw_networkx(
    G,
    pos,
    with_labels=True,
    node_size=1000,
    node_color=colorvalues,
    font_size=18,
    font_color="white",
    font_family="sans-serif",
    font_weight="bold",
)
plt.show()

Tp = None


def powerset(itr):
    s = list(itr)
    return it.chain.from_iterable(
        it.combinations(s, r) for r in range(len(s) + 1, 1, -1)
    )


print("Initial Graph G")
print("Edges: ")
print(G.edges(data=True))
print("Nodes: ")
print(G.nodes(data=True))

print("Range of k: " + str(list(powerset(list(range(n - 1, -1, -1))))))
sol_found = False
for k in list(powerset(list(range(n - 1, -1, -1)))):
    Gp = G.copy()
    print("Terminal nodes: " + str(list(k)))
    for node in G.nodes(data=True):
        if node[0] not in list(k):
            Gp.remove_node(node[0])

    Tp = apxalgo.steiner_tree(Gp, list(k), weight="length")
    print("Tp nodes: ")
    print(Tp.nodes(data=True))
    print("Tp edges: ")
    print(Tp.edges(data=True))
    Tp.pos = G.pos
    # plotting the steiner tree Tp
    plt.clf
    plt.figure(figsize=(20, 14))
    plt.title("Steiner tree Tp")
    pos = Tp.pos
    colorvalues = [
        "green" if node[1].get("sensornode") else "red" for node in Tp.nodes(data=True)
    ]
    edge_labels = nx.get_edge_attributes(Tp, "length")
    nx.draw_networkx_edge_labels(
        Tp,
        pos,
        edge_labels,
        font_size=18,
        font_color="black",
        font_family="sans-serif",
        font_weight="bold",
    )
    nx.draw_networkx(
        Tp,
        pos,
        with_labels=True,
        node_size=1000,
        node_color=colorvalues,
        font_size=18,
        font_color="white",
        font_family="sans-serif",
        font_weight="bold",
    )
    plt.show()
    for (a, b) in Tp.edges():
        Tp.edges[a, b]["weight"] = (
            0
            if (math.ceil(Tp.edges[a, b]["length"] / R) - 1) < 0
            else (math.ceil(Tp.edges[a, b]["length"] / R) - 1)
        )

    weightsum = 0
    for edge in Tp.edges(data=True):
        weightsum = weightsum + edge[2].get("weight")

    print("Sum of weights: " + str(weightsum))
    if weightsum <= B2:
        print("Solution to BCRP-MLCC")
        # plotting the steiner tree Tp
        plt.clf
        plt.figure(figsize=(20, 14))
        plt.title("Tree Tp, solution to BCRP-MLCC")
        pos = Tp.pos
        colorvalues = [
            "green" if node[1].get("sensornode") else "red"
            for node in Tp.nodes(data=True)
        ]
        edge_labels = nx.get_edge_attributes(Tp, "length")
        nx.draw_networkx_edge_labels(
            Tp,
            pos,
            edge_labels,
            font_size=18,
            font_color="black",
            font_family="sans-serif",
            font_weight="bold",
        )
        nx.draw_networkx(
            Tp,
            pos,
            with_labels=True,
            node_size=1000,
            node_color=colorvalues,
            font_size=18,
            font_color="white",
            font_family="sans-serif",
            font_weight="bold",
        )
        plt.show()
        sol_found = True
        break

if sol_found == False:
    print("Returning arbitrary terminal point as solution")
    Tp = G.subgraph([0])
    Tp.pos = G.pos
    # plotting the forest Tp
    plt.clf
    plt.figure(figsize=(20, 14))
    plt.title("Tree Tp, solution to BCRP-MLCC")
    pos = Tp.pos
    colorvalues = [
        "green" if node[1].get("sensornode") else "red" for node in Tp.nodes(data=True)
    ]
    edge_labels = nx.get_edge_attributes(Tp, "length")
    nx.draw_networkx_edge_labels(
        Tp,
        pos,
        edge_labels,
        font_size=18,
        font_color="black",
        font_family="sans-serif",
        font_weight="bold",
    )
    nx.draw_networkx(
        Tp,
        pos,
        with_labels=True,
        node_size=1000,
        node_color=colorvalues,
        font_size=18,
        font_color="white",
        font_family="sans-serif",
        font_weight="bold",
    )
    plt.show()

