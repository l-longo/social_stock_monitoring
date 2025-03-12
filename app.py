import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import os

# Get current working directory
path_saved = os.getcwd() + '/saved_df_update/'

# Streamlit app title
st.title("Financial Data and Network Analysis")

# Select ticker
ticker = st.selectbox("Select a ticker:", ['amc', 'gme', 'tsla'])

# Select parameters I and network_days
I = st.number_input("Select I:", value=30, step=5)
network_days = st.number_input("Select network_days:", value=20, step=5)

# Load financial data
df_financial = pd.read_excel(f'{path_saved}financial_{ticker}_{I}_{network_days}.xlsx')
df = pd.read_excel(f'{path_saved}df_{ticker}_{I}_{network_days}.xlsx', index_col=0)

# Load alternative dates
file_path_alter_dates = f'{path_saved}alert_dates_{ticker}_{I}_{network_days}.txt'
with open(file_path_alter_dates, "r") as f:
    alter_dates_nvda = [line.strip() for line in f]

# Rename and convert Date column
df_financial.rename(columns={"Unnamed: 0": "Date"}, inplace=True)
df_financial["Date"] = pd.to_datetime(df_financial["Date"])
df_financial.set_index("Date", inplace=True)

# Convert alert dates to datetime
alter_dates_nvda = pd.to_datetime(alter_dates_nvda, errors="coerce")

# Plot the Close column
st.subheader(f"{ticker.upper()} Close Price with Highlighted Dates")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_financial["Close"]["2024":].diff(), label="Close Price", color="blue")

for date in alter_dates_nvda:
    ax.axvline(date, color="red", linestyle="--", alpha=0.7)
    ax.axvspan(date, date + pd.Timedelta(days=20), color="gray", alpha=0.3)

ax.set_xlabel("Date")
ax.set_ylabel("Close Price")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Network graph selection
show_network = st.checkbox("Show Network Graph")

if show_network:
    df['author_y'] = df['author_y'].ffill()
    df.index = pd.to_datetime(df.index).date
    unique_dates = sorted(df.index.unique())
    selected_date = st.selectbox("Select Date:", unique_dates)
    
    df_day = df.loc[df.index == selected_date]
    title_body_dict = df_day.groupby('author_y')['author_x'].apply(list).to_dict()

    G = nx.Graph()
    for title, bodies in title_body_dict.items():
        G.add_node(title, type='title')
        for body in bodies:
            G.add_node(body, type='body')
            G.add_edge(title, body)

    node_colors = ['lightblue' if G.nodes[node]['type'] == 'title' else 'lightgreen' for node in G.nodes]
    
    st.subheader(f"Title-Body Network Graph for {selected_date}")
    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color=node_colors, edge_color='gray', font_size=8, ax=ax)
    st.pyplot(fig)
