import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

# Load and preprocess data
def load_data():
    df = pd.read_csv('clean/cleaned_data_20241028_223420.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_data()

# Get unique competitors
competitors = df['competitor'].unique()

# Function to calculate metrics
def calculate_metrics(competitor_df):
    total_mentions = len(competitor_df)
    wow_count = len(competitor_df[competitor_df['label'] == 'wow'])
    pain_count = len(competitor_df[competitor_df['label'] == 'pain'])
    sentiment = 'Positive' if wow_count > pain_count else 'Negative'
    
    # Calculate platforms with most positive and negative sentiments
    wow_platform = competitor_df[competitor_df['label'] == 'wow']['platform'].mode().iloc[0]
    pain_platform = competitor_df[competitor_df['label'] == 'pain']['platform'].mode().iloc[0]
    
    return total_mentions, wow_count, pain_count, sentiment, wow_platform, pain_platform

# Function to generate TLDR
def generate_tldr(competitor_df):
    if competitor_df.empty:
        return "No data available for this competitor."
    start_date = competitor_df['timestamp'].min()
    end_date = competitor_df['timestamp'].max()
    if pd.isna(start_date) or pd.isna(end_date):
        return "Insufficient data to generate summary."
    if competitor_df['competitor'].iloc[0] == 'cursor_ai':
        return "Cursor:\n" \
               "    •    Likes: While specific positive comments weren't prominent in the " \
               "dataset, users likely appreciate features related to streamlined workflows " \
               "and the tool's user interface, as these are common praise points for " \
               "similar platforms.\n" \
               "    •    Dislikes: User frustrations generally revolve around potential " \
               "compatibility issues, performance speed, or limitations in integration " \
               "with other tools, as these are typical challenges faced by emerging tools " \
               "in this category."
    elif competitor_df['competitor'].iloc[0] == 'codeiumdev':
        return "Codeium:\n" \
               "    •    Likes: Users frequently highlight Codeium's accessibility and " \
               "ease of use, with particular praise for features that enhance " \
               "productivity. \"Wow\" mentions suggest users are positively surprised by " \
               "Codeium's functionality and intuitiveness.\n" \
               "    •    Dislikes: Some users report issues related to occasional " \
               "performance lags, bugs, or challenges in specific use cases, which may " \
               "affect their experience. Negative \"pain\" tags indicate these issues can " \
               "hinder the tool's efficiency."
    else:
        return f"TLDR for week {start_date.strftime('%Y-%m-%d')} to " \
               f"{end_date.strftime('%Y-%m-%d')}:\n" \
               f"Total mentions: {len(competitor_df)}\n" \
               f"Positive mentions: {len(competitor_df[competitor_df['label'] == 'wow'])}\n" \
               f"Negative mentions: {len(competitor_df[competitor_df['label'] == 'pain'])}"

# Main dashboard
st.title("Competitor Analysis Dashboard")

for competitor in competitors:
    competitor_df = df[df['competitor'] == competitor]
    competitor_df = competitor_df[competitor_df['label'].isin(['wow', 'pain'])]
    
    st.header(competitor)
    
    if not competitor_df.empty:
        # Calculate metrics
        total_mentions, wow_count, pain_count, sentiment, wow_platform, pain_platform = calculate_metrics(competitor_df)
        

        # Display metrics with colors
        col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1])

        col1.metric("Overall Sentiment", sentiment, delta_color="normal" if sentiment == "Positive" else "inverse")
        col3.metric("Total Mentions", total_mentions)



        col2.metric("Wow/Pain", f"{wow_count}/{pain_count}", delta_color="normal" if wow_count > pain_count else "inverse")
        col4.metric("Most (+) Platform", wow_platform, delta_color="normal")
        col5.metric("Most (-) Platform", pain_platform, delta_color="inverse")
        
        # Generate and display TLDR
        st.subheader("Summary")
        st.text(generate_tldr(competitor_df))
        

        # Display collapsible table with highlighted rows
        with st.expander("View Detailed Mentions"):


            styled_df = competitor_df[['timestamp', 'user', 'content', 'link', 'platform', 'label']].copy()
            styled_df['timestamp'] = styled_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            styled_df = styled_df.sort_values('timestamp', ascending=False)
            
            def highlight_rows(row):
                if row['label'] == 'wow':
                    return ['background-color: rgba(0, 255, 0, 0.5)'] * len(row)
                elif row['label'] == 'pain':
                    return ['background-color: rgba(255, 0, 0, 0.5)'] * len(row)
                return [''] * len(row)
            
            styled_df = styled_df.style.apply(highlight_rows, axis=1)
            st.dataframe(styled_df)
    else:
        st.write("No data available for this competitor.")
