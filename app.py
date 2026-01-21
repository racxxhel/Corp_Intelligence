from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import numpy as np

app = Flask(__name__)

CLUSTER_METADATA = {
    0: {
        "name": "Small Service Providers",
        "summary": "Established small to mid-sized service firms relying on human expertise.",
        "key_traits": ["Service-driven revenue", "Moderate team sizes", "Regional focus"],
    },
    1: {
        "name": "Lean & IP-Driven Firms",
        "summary": "High-revenue companies operating with extremely small teams.",
        "key_traits": ["High rev/employee", "Expertise-driven", "Owner-led"],
    },
    2: {
        "name": "Scaling Professional Firms",
        "summary": "Growth-stage service companies expanding teams and market reach.",
        "key_traits": ["Growing headcount", "Structured ops", "Balanced ratios"],
    },
    3: {
        "name": "Industrial & Infrastructure",
        "summary": "Large, asset-heavy firms operating in manufacturing and utilities.",
        "key_traits": ["Capital-intensive", "Large workforce", "Complex ops"],
    },
    "micro": {
        "name": "Micro & Low-Activity",
        "summary": "Very small firms with limited economic footprint.",
        "key_traits": ["Minimal revenue", "Small teams", "Early-stage"],
    }
}

try:
    with open("data/clustered_companies.pkl", "rb") as f:
        df = pickle.load(f)
    print("Data Loaded Successfully!")
    
    # Ensure numeric columns are actually numeric
    cols_to_numeric = ['Revenue (USD)', 'Employees Total', 'IT spend', 'Year Found']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Pre-calculate Cluster Averages for the Graph
    cluster_stats = df.groupby('Cluster')[['Revenue (USD)', 'IT spend']].mean().to_dict(orient='index')

except Exception as e:
    print(f"Error loading data: {e}")
    df = pd.DataFrame()
    cluster_stats = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search")
def search():
    """Autofill: Finds companies matching the typed query (Partial Match)"""
    query = request.args.get('q', '').lower()
    if not query or df.empty: return jsonify([])
    
    mask = df['Company Sites'].astype(str).str.lower().str.contains(query)
    candidates = df[mask]['Company Sites'].unique().tolist() 
    candidates.sort(key=lambda x: 0 if x.lower().startswith(query) else 1) #prioritise those that start with query first 
    return jsonify(candidates[:6])

@app.route("/api/get_company")
def get_company():
    """Returns Full Data for One Company"""
    name = request.args.get('name')
    if df.empty: return jsonify({"error": "No data loaded"})

    try:
        # Find exact match
        row = df[df['Company Sites'] == name].iloc[0]
        
        # Get Age
        age = row.get('Year Found', 'Unreported')

        # Get Cluster Context
        cid = row.get('Cluster', 0)
        stats = cluster_stats.get(cid, {})

        # Find Nearest Neighbors (Same Cluster, Similar Revenue)
        cluster_peers = df[df['Cluster'] == cid].copy()
        cluster_peers['diff'] = abs(cluster_peers['Revenue (USD)'] - row['Revenue (USD)'])
        
        # Get top 5 neighbors (excluding itself)
        neighbors = cluster_peers.sort_values('diff').head(6)
        neighbors = neighbors[neighbors['Company Sites'] != name].head(5)
        
        neighbor_list = neighbors[['Company Sites', 'Revenue (USD)']].to_dict(orient='records')

        response = {
            "name": row['Company Sites'],
            "city": row.get('City', '-'),
            "country": row.get('Country', '-'),
            
            # The 5 KPIs
            "revenue": float(row.get('Revenue (USD)', 'Unreported')),
            "employees": "Unreported" if row.get('Employees Total') == 0 else int(row.get('Employees Total')),
            "age": age,
            "it_spend": float(row.get('IT spend', 0)),
            "sic": row.get('SIC Description', 'Unknown'),

            # Cluster Context for AI/Graph
            "cluster_id": int(cid),
            "cluster_avg_rev": float(stats.get('Revenue (USD)', 0)),
            "cluster_avg_it": float(stats.get('IT spend', 0)),
            
            # Neighbors Table
            "neighbors": neighbor_list
        }
        return jsonify(response)

    except IndexError:
        return jsonify({"error": "Company not found"})

if __name__ == "__main__":
    app.run(debug=True)