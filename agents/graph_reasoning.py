import networkx as nx
from node2vec import Node2Vec
from sklearn.cluster import KMeans
import community

def analyze_graph(G):
    analysis = {}

    # Centrality measures
    analysis['centrality'] = {
        'degree_centrality': nx.degree_centrality(G),
        'betweenness_centrality': nx.betweenness_centrality(G),
        'pagerank': nx.pagerank(G)
    }

    # Community detection using Louvain method
    partition = community.best_partition(G)
    analysis['communities'] = partition

    # Node embeddings using Node2Vec
    node2vec = Node2Vec(G, dimensions=64, walk_length=30, num_walks=200, workers=4)
    model = node2vec.fit(window=10, min_count=1)
    
    # Cluster embeddings
    embeddings = [model.wv[node] for node in G.nodes()]
    kmeans = KMeans(n_clusters=min(5, len(G.nodes())), random_state=42)
    clusters = kmeans.fit_predict(embeddings)
    analysis['clusters'] = dict(zip(G.nodes(), clusters))

    # Link prediction
    analysis['link_predictions'] = []
    for u, v in nx.non_edges(G):
        jaccard = list(nx.jaccard_coefficient(G, [(u, v)]))[0][2]
        adamic_adar = list(nx.adamic_adar_index(G, [(u, v)]))[0][2]
        preferential_attachment = list(nx.preferential_attachment(G, [(u, v)]))[0][2]
        score = jaccard + adamic_adar + preferential_attachment
        analysis['link_predictions'].append((u, v, score))
    analysis['link_predictions'].sort(key=lambda x: x[2], reverse=True)

    return analysis
