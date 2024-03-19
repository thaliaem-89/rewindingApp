# streamlit_app.py

import streamlit as st
from st_supabase_connection import SupabaseConnection

# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

# Perform query.
rows = conn.query("*", table="all_variants", ttl="10m").execute()
st.write(rows)

# Print results.
for row in rows.data:
    st.write(f" machine {row['machine']} has a variant :{row['variant']}:")