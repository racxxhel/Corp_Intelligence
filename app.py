from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import numpy as np
import requests 
import os
from huggingface_hub import InferenceClient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "frontend", "static"),
    template_folder=os.path.join(BASE_DIR, "frontend", "templates")
)

CLUSTER_METADATA = {
    0: {
        "name": "General B2B Services",
        "summary": "The core service sector comprising advertising, IT, and accounting firms with steady, moderate revenue.",
        "key_traits": ["Standard B2B", "Moderate Revenue", "Human-Capital Centric"],
    },
    1: {
        "name": "Infrastructure & Communications",
        "summary": "Niche service firms focused specifically on cable TV, telegraph, and specialized communication infrastructure.",
        "key_traits": ["Communications Focus", "Specialized Tech", "Infrastructure-Heavy"],
    },
    2: {
        "name": "High-Efficiency Consultancies",
        "summary": "Elite firms or asset-holding companies generating high revenue ($10M+) with very small, expert teams (~7 employees).",
        "key_traits": ["High Revenue per Employee", "Lean Operations", "Asset-Light"],
    },
    3: {
        "name": "High-Operation Service Firms",
        "summary": "Traditional labor-intensive companies requiring larger workforces (~25 employees) to meet the $10M revenue mark.",
        "key_traits": ["Labor-Intensive", "Scaling Workforce", "Operational Complexity"],
    },
    4: {
        "name": "Industrial & Heavy Construction",
        "summary": "Large-scale manufacturing and heavy construction companies. The primary industrial segment of the market.",
        "key_traits": ["Manufacturing", "Large Capital Assets", "Heavy Industry"],
    },
    "micro": {
        "name": "Retail & Low-Activity",
        "summary": "Low-revenue retail businesses and data outliers that represent minimal commercial activity.",
        "key_traits": ["Low Revenue", "Small Retail", "Minimal Infrastructure"],
    }
}

try:

    with open("data/clustered_companies.pkl", "rb") as f:
        df = pickle.load(f)
        print(df.columns.tolist())

    # for col in df.columns:
        # df[col] = df[col].astype(object)
    
    # Clean the column names (remove any hidden space)
    df.columns = df.columns.str.strip()
    
    # Fix String and Object types to remove trailing whitespace 
    for col in df.columns:
        if df[col].dtype.name in ["string", "object", "category"]:
            # Convert to  string and strip gap
            df[col] = df[col].astype(str).str.strip()

    # Handle missing values
    df = df.fillna("N/A")
    df = df.astype(object)

    # Ensure numeric columns are actually numeric
    cols_to_numeric = ['Revenue (USD)', 'Employees Total', 'IT spend', 'Year Found', 'Corporate Family Members', 'hybrid_Cluster']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Pre-calculate Cluster Averages for the Graph
    if 'hybrid_Cluster' in df.columns:
        cluster_stats = df.groupby('hybrid_Cluster')[['Revenue (USD)', 'IT spend', 'Employees Total', 
        'Corporate Family Members']].mean().to_dict(orient='index')

    else:
        cluster_stats = {}

    print("Data Loaded and Cleaned Successfully!")

    
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
    name = request.args.get('name')
    if df.empty:
        return jsonify({"error": "No data loaded"})

    try:
        row = df[df['Company Sites'] == name].iloc[0]

        # ---------- Year Founded ----------
        year_founded = row.get('Year Found')
        if pd.isna(year_founded) or year_founded == 0:
            age = "Unreported"
        else:
            age = int(year_founded)

        # ---------- Company Description ----------
        raw_desc = row.get('Company Description')
        comp_desc = (
            raw_desc
            if pd.notna(raw_desc) and str(raw_desc).strip() != ""
            else "No description available for this company."
        )

        # ---------- Cluster ----------
        cid = row.get('hybrid_Cluster', 0)
        stats = cluster_stats.get(cid, {})

        # ---------- Neighbors ----------
        cluster_peers = df[df['hybrid_Cluster'] == cid].copy()
        cluster_peers['diff'] = abs(
            cluster_peers['Revenue (USD)'] - row['Revenue (USD)']
        )

        neighbors = (
            cluster_peers
            .sort_values('diff')
            .query("`Company Sites` != @name")
            .head(5)
        )

        neighbor_list = [
            {
                "name": str(n['Company Sites']),
                "revenue": float(n['Revenue (USD)'])
            }
            for _, n in neighbors.iterrows()
        ]

        # ---------- Response ----------
        response = {
            "name": str(row['Company Sites']),
            "city": str(row.get('City', '-')),
            "country": str(row.get('Country', '-')),
            "comp_desc": comp_desc,

            "revenue": float(row.get('Revenue (USD)', 0)),
            "employees": (
                "Unreported"
                if int(row.get('Employees Total', 0)) == 0
                else int(row.get('Employees Total'))
            ),
            "age": age,
            "it_spend": float(row.get('IT spend', 0)),
            "sic": str(row.get('SIC Description', 'Unknown')),
            "corp_family": int(row.get('Corporate Family Members', 0)),

            "cluster_id": int(cid),
            "cluster_avg_rev": float(stats.get('Revenue (USD)', 0)),
            "cluster_avg_it": float(stats.get('IT spend', 0)),

            "neighbors": neighbor_list
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



HF_TOKEN = "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"
client = InferenceClient(api_key=HF_TOKEN)

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message")
        context = data.get("context", {}) 

        # Create a summary of all clusters

        # In the try-except block at the top of app.py
        if 'hybrid_Cluster' in df.columns:
            cluster_stats = df.groupby('hybrid_Cluster')[['Revenue (USD)', 'IT spend', 'Employees Total', 'Corporate Family Members']].mean().to_dict(orient='index')
        
        # 2. Get the most common industry for each cluster
        top_industries = df.groupby('hybrid_Cluster')['SIC_2digit_Description'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else "General Services").to_dict()
        
        # 3. Add industry to stats
        for cid in cluster_stats:
            cluster_stats[cid]['top_industry'] = top_industries.get(cid, "General Services")

        all_clusters_summary = ""
        for cid_key, info in CLUSTER_METADATA.items():
            # Get stats if they exist in your cluster_stats dictionary
            stats = cluster_stats.get(cid_key, {})
            avg_rev = f"${stats.get('Revenue (USD)', 0):,.0f}"
            avg_it = f"${stats.get('IT spend', 0):,.0f}"
            avg_emp = round(stats.get('Employees Total', 0), 1)
            avg_fam = round(stats.get('Corporate Family Members', 0), 1)
            
            all_clusters_summary += f"""
            CLUSTER {cid_key} ({info['name']}):
            - Profile: {info['summary']}
            - Avg Revenue: {avg_rev}
            - Avg IT Spend: {avg_it}
            - Avg Team Size: {avg_emp} employees
            - Avg Corp Family: {avg_fam} members
            - Traits: {", ".join(info['key_traits'])}
            - Top Industry: {stats.get('top_industry', 'Various')}
            """
            
        # 2. Content Grounding
        system_instruction = f"""
        You are an expert sales analyst. You have access to data for a specific company and the broader market segmentation (Clusters).
        
        DATA COMPARISON RULES:
        - Compare the 'Target Company' against the 'Market Segmentation Data'.
        - Can look at 'IT spend' vs 'Revenue' to determine if they are over or under-investing.
        - Look at 'Corporate Family Members' to see if they are part of a large enterprise or a standalone firm.
        - If the company is a 'Branch' or 'Subsidiary' (from Entity Type), mention how that affects their decision-making.

        RULES:
        - NEVER use asterisks (**), hashtags (#), or dashes (-) for bullet points in any circumstance.
        - DO NOT use any Markdown symbols whatsoever.
        - Use only standard capitalization and line breaks for structure.
        - If the 'Description' is missing or "N/A", use the 'SIC Industry' (Standard Industrial Classification) to explain what the company does.
        If BOTH are missing, use the 'Name' but state clearly that you are making an educated guess based on the title.
        - If asked to compare, look at the traits and averages of both clusters.
        - If the description is missing, state that you are analyzing based on name and stats only.


        MARKET SEGMENTATION DATA (All Clusters):
        {all_clusters_summary}

        TARGET COMPANY DATA:

        - Name: {context.get('name', 'N/A')}
        - Year Founded: {context.get('age', 'N/A')}
        - Company Description: {context.get('description', 'N/A')}
        - SIC Industry Category: {context.get('sic', 'N/A')}
        - Revenue: ${context.get('revenue', 0):,.0f}
        - Employees: {context.get('employees', 'N/A')}
        - IT Spend: ${context.get('it_spend', 0):,.0f}
        - Current Cluster: {context.get('cluster_id', 'N/A')}
        - Corporate Family Size: {context.get('corp_family', 'N/A')}

        
        Output Format:
        1. Observed Trend: (Analysis of the question)

        2. Data-Driven Explanation: (Use specific stats from any cluster mentioned)

        3. Limitations: (Missing info)
        """

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct:fastest",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            max_tokens=450 
        )

        return jsonify({"response": response.choices[0].message.content})

    except Exception as e:
        print(f"Backend Error: {e}")
        return jsonify({"response": "Error. Please try again."})

if __name__ == "__main__":
    app.run(debug=True)