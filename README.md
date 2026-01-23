# Corporate Clustering Prototype: IntelCorp Intelligence

## Project Overview

This project aims to develop a prototype system that helps users derive actionable insights from company-level data by analysing firmographic, operational, and organizational attributes. By leveraging data analytics, machine learning techniques, and large language models (LLMs), the system should generate data-grounded insights and explanations that help users understand how companies operate today and how they compare with similar firms.

The project is organized into three main components:

***Data Cleaning and Clustering*** (`CAT_A_ACC.ipynb`): This Jupyter Notebook provides a detailed, step-by-step documentation of the original development and experimentation process. It involves Exploratory Data Analysis and clustering of the data. 

***Final Model*** (`clustered_companies.pkl`): This pkl file consists of the cleaned company data with its respective cluster. This pkl file will be further used for our interactive web application (`app.py`)

***Interactive Web Application*** (`app.py`): A web app built with Flask that allows user to find out more details on their interested company and discover the scope and usefulness of the data.

## Project Structure
```plaintext
.
├── app.py                     # Backend script for the Flask web application.
├── requirements.txt           # A list of required Python packages.
├── .gitignore                 # Specifies files for Git to ignore.
├── frontend/                  # Contains all frontend files for the web app.
│   ├── static/
│   │   └── script.js
│   │   └── styles.css
│   └── templates/
│       └── index.html
├── data/                   
│   └── clustered_companies.pkl #pkl file with the cleaned company data and its respective clusters
│   └── champions_group_data.csvl #raw file (I BELIEVE WE HAVE TO REMOVE)
├── src/     
│   └── CAT_A_ACC.ipynb # Python notebook which consists of the whole process of cleaning and clustering
└── README.md                  # This README file.
```

## Setup and Installation
Follow these steps to set up the local environment to run the web application.

**1. Clone the Repository**
```bash
git clone https://github.com/racxxhel/SDS_Datathon-26.git

cd Coporate Clustering Prototype: IntelCorp Intelligence
```
**2. Create a virtual environment named 'venv'**
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

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Create a Hugging Face Token**

A token is needed to access the Large Lanuage Model through an API, which is used for our chatbot.

1. Log in to huggingface.co. Go to Settings (click your profile picture) > Access Tokens.
2. Click Create new token. Give it a name (e.g., "ClusteringProject") and set the type to Read.
3. Copy the string (starts with hf_...). You will not be able to see this token anymore. 
4. Create a file in the root folder exactly named .env and add the line as below: 

```python
HF_TOKEN=hf_your_actual_token_string_here
```

## How to Run:

There are two main components to this project: reproducing the experiments and running the web app.

**1. Reproducing the Results**

You may reproduce the results of our notebook and clustering by simply running the whole `CAT_A_ACC.ipynb` file.

**2. Running the Flask Web App**

The Flask app allows you to interactively test and compare the two fine-tuned models.

Run the app from your terminal: 
```bash
python app.py
```

## Results:


## Conclusion:
