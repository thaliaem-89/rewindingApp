# streamlit_app.py

import streamlit as st
from st_supabase_connection import SupabaseConnection
from graphviz import Digraph

# Function to create a flow diagram for a given variant
def create_variant_diagram(variant_text):
    steps = variant_text.split(',')
    dot = Digraph()
    for i, step in enumerate(steps):
        dot.node(str(i), step)
        if i > 0:
            dot.edge(str(i-1), str(i))
    return dot

# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

# Perform query.
rows = conn.query("*", table="all_variants", ttl="10m").execute()

# Filter the data to find Variant rank 1 for each machine
variant_rank_1 = {}
for row in rows.data:
    if row['Variant Rank'] == 1:
        variant_rank_1[row['machine']] = row['Variant']

# Displaying diagrams for each machine's Variant rank 1
for machine, variant in variant_rank_1.items():
    st.header(f'Variant Rank 1 Flow Diagram for {machine}')
    diagram = create_variant_diagram(variant)
    st.graphviz_chart(str(diagram))