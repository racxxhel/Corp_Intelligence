# Corporate Clustering Prototype: Corp Intelligence

## Project Overview

This project aims to develop a prototype system that helps users derive actionable insights from company-level data by analysing firmographic, operational, and organizational attributes. By leveraging data analytics, machine learning techniques, and large language models (LLMs), the system should generate data-grounded insights and explanations that help users understand how companies operate today and how they compare with similar firms.

The project is organized into three main components:

***Data Cleaning and Clustering*** (`CAT_A_ACC.ipynb`): This Jupyter Notebook provides a detailed, step-by-step documentation of the original development and experimentation process. It involves Exploratory Data Analysis and clustering of the data. 

***Final Model*** (`clustered_companies.pkl`): This pkl file consists of the cleaned company data with its respective cluster. This pkl file will be further used for our interactive web application.

***Interactive Web Application***: A web app built with Flask that allows user to find out more details on their interested company and discover the scope and usefulness of the data.

## Setup and Installation
Follow these steps to set up the local environment to run the experiment and reproduce the results.

**1. Create a virtual environment named 'venv'**
```bash
python -m venv venv
```

To activate it
* On macOS/Linux:
```bash
source venv/bin/activate
```
* On Windows (Command Prompt):
```bash
.\venv\Scripts\activate
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

## How to Run:

There are two main components to this project: reproducing the experiments and running the web app.

**1. Reproducing the Results**

You may reproduce the results of our notebook and clustering by simply running the whole `CAT_A_ACC.ipynb` file. Do remember to include your raw file`champions_group_data.csv`.

**2. Running the Flask Web App**

Users are able to access the application via https://sds-datathon-26.onrender.com/. 
The web interface is deployed on Render (free version). Please be aware that the site may take up to 10 minutes to load after 15 minutes of inactivity as the server reboots. To run the application locally instead, follow the steps below.

## Results:

The primary value of this dataset lies in its multidimensionality, combining financial metrics with semantic descriptions. Our analysis proved that while traditional numerical clustering provides a baseline, the true "signal" is found in the intersection of firmographics and industry context.

**Modelling**

We used mainly 3 methods of clustering: K-Means Clustering, Hierarchical Clustering, Hybrid Semantic-Numeric Clustering. 

The Hybrid Semantic-Numeric Clustering approach was selected as the final model for the following reason: 

1. Unlike K-Means, which relied too heavily on financial metrics (such as revenue, employees), this model integrates Natural Language Processing (NLP). By using text embeddings of business descriptions, the model takes into account what a company does, not just based on numerical metrics. 

2. Hierarchical Clustering proved too sensitive to outliers, creating clusters of just one company. The Hybrid model solved this by implementing a rule-based filter to separate "Micro" businesses (revenue > $50k) from active ones, ensuring that data noise didn't skew the results for established firms. 

3. This model successfully separated "Hard Industries" (Manufacturing/Electronics) from "Soft Industries" (Consulting/Services), which the other models struggled to do clearly.

**Key Discoveries**

There were 6 clusters identified in total. 

Cluster 0 represents the core "General Services" sector, containing the bulk of standard B2B companies in advertising, IT, and accounting with moderate revenue.
Cluster 1 appears to be a niche subset of this group, likely separated by the text analysis because these firms focus specifically on infrastructure and communications, as evidenced by the unique presence of cable TV and telegraph services in their top categories.
Cluster 2 and Cluster 3 demonstrate a powerful distinction in business models. Both groups earn roughly $10 million in revenue, but Cluster 2 is an "High-Efficiency" group that achieves this with only 7 employees, likely representing asset-holding firms or elite consultancies. In contrast, Cluster 3 is a "High-Operation" group that requires 25 employees to generate the same amount of money, indicating a more traditional, labor-intensive workforce.
Cluster 4 is the standout success of this method, clearly isolating the big Industrial companies in manufacturing and heavy construction.
Finally, the Micro Cluster captures the low-revenue retail businesses and data noise, ensuring they do not skew the statistics of the active commercial groups.

To validate the high-dimensional clusters visually, we applied t-SNE (t-Distributed Stochastic Neighbor Embedding). The resulting visualization confirmed clear spatial separation, particularly highlighting the distinct isolation of the 'Hard Industries' (Cluster 4) from the 'Service' clusters.

## Conclusion:
Through this prototype, we have proved that this dataset is valuable in identifying high-revenue, low-headcount targets for B2B services, sector differentiation and strategic segmentation. 
By moving beyond simple filters and adopting a Hybrid Semantic-Numeric clustering approach, we have successfully mapped the complex intricacies of the commercial landscape. By incorporating an interface and LLM, the insights gained from clustering are more readable to users and  transform the raw statistical outputs into natural language business intelligence. Through bridging the gap between data analytics and intuitive user interaction, the system allows non-technical stakeholders to query the market as if they were speaking to a specialized consultant.
