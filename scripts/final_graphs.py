from igraph import *
import re
from collections import Counter
import os
import  pandas as pd


def clean_script(name, directory):
	script_object = open(directory + name, "r")
	script = script_object.read()

	script = re.split("INT\.|EXT\.", script)

	counters = []

	for item in script:
		c = Counter(
			word.lower() 
			for word in re.findall(r'\b[^\W\d_]+\b', item))
		counters.append(c)

	return counters


# creates a list of characters appearing in each scene based
# on a script and list of characters
def parse_script(script, characters):
	connections = []
	for scene in script:
		edges = []
		for char in characters:
			if char in scene.keys():
				edges.append(char)
		connections.append(edges)

	return connections


# build the graph based on characters appearing in scenes together
def convert_to_graph(connections, g):
	for scene in connections:
		# add an edge between every character that appears in the scene
		while (len(scene) > 1):
			# character at the top of the list
			cur = scene.pop()
			for char in scene:
				# get edge id for (current character and each of the others)
				eid = g.get_eid(cur, char, error=False)
				# if edge already exists increment by 1
				if eid >= 0:
					g.es[eid]["weight"] += 1
				# otherwise create it
				else:
					g.add_edge(cur, char, weight=1)

	return g


def get_meta(directory):
	names = dict()
	for file in os.listdir(directory):
		if file.endswith(".txt"):
			df = pd.read_csv(directory+file)
			names[file] = df
	return names


# prints name of character with the highest betweenness in the graph
def find_betweenness(g):
	for edge in g.es:
		cur = edge['weight']
		edge['weight'] = 1/cur

	vbs = g.betweenness(directed=False, weights=g.es['weight'])
	max_vb = max(vbs)

	betw = [g.vs[idx]['name'] for idx, eb in enumerate(ebs) if eb == max_eb]

	print(betw)


# takes input as a parsed script and list of characters and
# writes it out as a graph
def write_graph(script, meta, name, out):
	# isolate characters from each parsed scene
	characters = [name.strip().lower() for name in meta['Name']]
	
	connections = parse_script(script, characters)
	# initialize graph using names from character set
	g = Graph()
	g.add_vertices(len(characters))
	g.vs['name'] = characters

	# create graph object using helper method
	g = convert_to_graph(connections, g)

	g.vs['quality'] = list(meta['Quality'])
	g.vs['object'] = list(meta['Object'])
	g.vs['role'] = list(meta['Role'])

	# visual styles
	color_dict = ({"Victim": "blue", "Perpetrator": "red",\
					 "Rescuer": "green", "Neutral": "grey"})
	visual_style = {}
	visual_style["edge_width"] = [weight for weight in g.es["weight"]]
	visual_style["vertex_label"] = g.vs["name"]
	visual_style["margin"] = 80
	visual_style["bbox"] = (1000,1000)
	visual_style["vertex_size"] = 60
	visual_style["autocurve"] = True

	visual_style["vertex_color"] = [color_dict[role] for role in g.vs["role"]]

	# write graph
	plot(g, out+name+".png", **visual_style)


def main():
	# directory of scripts
	directory = "DIRECTORY_FOR_SCRIPTS"
	
	# output directory for completed graphs
	out = "DIRECTORY_FOR_GRAPH_OUTPUT"

	meta_dir = "DIRECOTRY_FOR_METADATA"

	# titles of scripts to be parsed
	titles = ['it_follows.txt', 'get_out.txt', 'halloween.txt', 'scream.txt', 'the_shining.txt']

	meta = get_meta(meta_dir)

	# convert each script into a counter object broken up by scene
	# i.e. each scene is a dict counting the occurences of each word
	for name in titles:
		script = clean_script(name, directory)
		title = name.split(".")[0]
		write_graph(script, meta[name], title, out)

	print("Done.")



if __name__ == '__main__':
	main()
