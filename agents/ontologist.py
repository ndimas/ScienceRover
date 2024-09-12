from .shared import make_api_call
from .graph_reasoning import analyze_graph
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_concepts(text):
    doc = nlp(text)
    return [chunk.text for chunk in doc.noun_chunks]

def analyze(graph):
    graph_analysis = analyze_graph(graph)
    
    # Prepare the analysis results for the prompt
    centrality_info = "Top 5 nodes by PageRank: " + ", ".join(sorted(graph_analysis['centrality']['pagerank'], key=graph_analysis['centrality']['pagerank'].get, reverse=True)[:5])
    community_info = f"Number of communities detected: {len(graph_analysis['communities'])}"
    cluster_info = f"Number of clusters: {len(set(graph_analysis['clusters'].values()))}"
    link_prediction_info = "Top 3 predicted links: " + ", ".join([f"({u}, {v})" for u, v, _ in graph_analysis['link_predictions'][:3]])
    
    prompt = f"""Analyze the following graph and provide insights about the relationships between concepts, taking into account the advanced graph analysis results:

Graph edges: {graph.edges()}

Graph Analysis Results:
1. {centrality_info}
2. {community_info}
3. {cluster_info}
4. {link_prediction_info}

Based on these results, provide a detailed analysis of the relationships between concepts, identifying key nodes, potential clusters of related concepts, and possible missing links between concepts. Consider the community structure and the node embeddings to identify overarching themes or research areas."""

    return make_api_call(prompt)
