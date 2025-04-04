import pandas as pd
import numpy as np
import streamlit as st
from sklearn.decomposition import PCA
import umap
from umap import UMAP
import plotly.express as px
import plotly.graph_objects as go
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from Biopython_Entrez import *
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multitest import multipletests
import os
import kaleido

# Load raw data
data_path = 'mesh_terms_matrix_5yrs_and_keywords.xlsx'
raw_data = pd.read_excel(data_path, index_col='Faculty_Full_Name')
raw_data.reset_index(inplace=True)

# Extract numeric data and faculty column
numeric_data = raw_data.drop(columns=['Faculty_Full_Name'])
faculty_column = pd.read_excel(data_path, usecols=['Faculty_Full_Name'])

# Clean column names
raw_data.columns = raw_data.columns.str.replace(
    ' ', '_').str.replace('-', '_').str.replace(',', '_')

# PCA
pca = PCA()
pca_result = pca.fit_transform(numeric_data)
st.subheader("PCA Explained Variance") # Add subheader for clarity
# Write description for Explained Variance Plot using st.write()
st.write("""
**Plot Description:** This plot shows the cumulative percentage of variance captured by the principal components (PCs). The x-axis represents the number of PCs included, and the y-axis shows the total variance explained. It helps determine how many PCs are needed to retain a significant amount of information.
""")

# Visualize explained variance
explained_variance_ratio = pca.explained_variance_ratio_
plt.figure()
plt.plot(np.cumsum(explained_variance_ratio))
plt.xlabel('Number of Components')
plt.ylabel('Variance (%)')
plt.title('Explained Variance')
st.pyplot(plt.gcf())

# PCA scatter plot
st.subheader("PCA Scatter Plot (PC1 vs PC2)") # Add subheader
# Write description for PCA Scatter Plot using st.write()
st.write("""
**Plot Description:** This scatter plot displays the data projected onto the first two principal components (PC1 and PC2). Each point represents a faculty member. Reveals primary axes of variation based on PCA reduction.
""")
pca_df = pd.DataFrame(pca_result, columns=[
                      f'PC{i+1}' for i in range(pca_result.shape[1])])
fig = px.scatter(pca_df, x='PC1', y='PC2')
st.plotly_chart(fig)

# UMAP 2D
st.subheader("UMAP 2D Projection (on Raw Data)") # Add subheader
# Write description for UMAP 2D Plot using st.write()
st.write("""
**Plot Description:** Shows a 2D UMAP representation of the original high-dimensional data. Aims to preserve local and global structure. Hover shows faculty name and top 3 MeSH terms (if available).
""")
umap_2d_result = UMAP().fit_transform(numeric_data)
umap_2d_df = pd.DataFrame(umap_2d_result, columns=["umap_1", "umap_2"])
umap_2d_df['Faculty_Full_Name'] = raw_data['Faculty_Full_Name']

top_mesh_terms = []
# Use the full name column here.
for faculty_full_name in umap_2d_df['Faculty_Full_Name']:
    faculty_terms = combined_faculty_df[combined_faculty_df['Faculty_Full_Name'] ==
                                        faculty_full_name]['Combined_Mesh_Terms'].iloc[0]  # use the full name here.
    counter = Counter(str(faculty_terms).split("; "))
    top_items = [item[0] for item in counter.most_common(3)]
    top_mesh_terms.append("; ".join(top_items))

umap_2d_df['Top_Mesh_Terms'] = top_mesh_terms

fig = px.scatter(umap_2d_df, x="umap_1", y="umap_2", title="UMAP", hover_name="Faculty_Full_Name", hover_data={
                 "umap_1": False, "umap_2": False, "Top_Mesh_Terms": True}, width=800, height=800, color_discrete_sequence=['#fecc07'])

fig.update_layout(plot_bgcolor='#255799', title={
    'text': "UMAP",
    'font': {'size': 30},
})
fig.update_xaxes(title_text="")
fig.update_yaxes(title_text="")
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
st.plotly_chart(fig)

# # UMAP 3D
# umap_3d_result = UMAP(n_components=2).fit_transform(numeric_data)
# umap_3d_df = pd.DataFrame(umap_3d_result, columns=["umap_x", "umap_y"])
# fig = go.Figure(data=[go.Scatter3d(x=umap_3d_df["umap_x"], y=umap_3d_df["umap_y"], mode='markers')])
# st.plotly_chart(fig)

# t-SNE
st.subheader("t-SNE 2D Projection (on Raw Data)") # Add subheader
# Write description for t-SNE Plot using st.write()
st.write("""
**Plot Description:** Presents a 2D t-SNE embedding of the original data. Focuses on local similarities. Hover shows faculty name and top 3 MeSH terms (if available).
""")
tsne = TSNE(n_components=2, perplexity=25)
tsne_result = tsne.fit_transform(numeric_data)
tsne_df = pd.DataFrame(tsne_result, columns=["tsne_1", "tsne_2"])
tsne_df['Faculty_Full_Name'] = raw_data['Faculty_Full_Name']
tsne_df['Top_Mesh_Terms'] = top_mesh_terms
fig = px.scatter(tsne_df, x="tsne_1", y="tsne_2", title="t-SNE", hover_name="Faculty_Full_Name", hover_data={
                 "tsne_1": False, "tsne_2": False, "Top_Mesh_Terms": True}, width=800, height=800, color_discrete_sequence=['#fecc07'])
fig.update_layout(plot_bgcolor='#255799', title={
    'text': "t-SNE",
    'font': {'size': 30},
})
fig.update_xaxes(title_text="")
fig.update_yaxes(title_text="")
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
st.plotly_chart(fig)

# UMAP on PCA components
st.subheader("UMAP on PCA Components")
num_pca_components = 2
pca_scores = pca_result[:, :num_pca_components]
umap_pca_result = UMAP().fit_transform(pca_scores)
umap_pca_df = pd.DataFrame(umap_pca_result, columns=["umap_1", "umap_2"])
umap_pca_df['Faculty_Full_Name'] = raw_data['Faculty_Full_Name']
umap_pca_df["Top_Mesh_Terms"] = top_mesh_terms
st.write(f"""
**Plot Description:** Displays the UMAP projection applied *after* PCA reduction (using first {num_pca_components} components). Visualizes structure found by UMAP within the principal component space. Hover shows faculty/terms.
""")
fig = px.scatter(umap_pca_df, 
                 x="umap_1", 
                 y="umap_2", 
                 title="UMAP on PCA Components", 
                 hover_name="Faculty_Full_Name", 
                 hover_data={"umap_1": False, "umap_2": False, "Top_Mesh_Terms": True}, 
                 width=800, 
                 height=800,
                 color="Faculty_Full_Name")
fig.update_layout(plot_bgcolor='#255799', title={
    'text': "UMAP on PCA Components",
    'font': {'size': 30},
})
fig.update_xaxes(title_text="")
fig.update_yaxes(title_text="")
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
st.plotly_chart(fig)

# UMAP on varying PCA components (1 component)
st.subheader("UMAP on Varying PCA Dimensions") 
for num_components in range(1, 31):
    pca_scores = pca_result[:, :num_components]
    umap_result = UMAP().fit_transform(pca_scores)
    st.write(f"""
    **Plot Description (UMAP with {num_components} PCA Components):** Shows UMAP projection based on the first {num_components} principal components. Observe structure changes as more components are included. Hover shows faculty/terms.
    """)
    umap_df_pca_var = pd.DataFrame(umap_result, columns=["umap_1", "umap_2"])
    umap_df_pca_var['Faculty_Full_Name'] = raw_data['Faculty_Full_Name']
    umap_df_pca_var['Top_Mesh_Terms'] = top_mesh_terms
    fig = px.scatter(umap_df_pca_var, x="umap_1", y="umap_2", title=f"UMAP with {num_components} PCA Components", hover_name="Faculty_Full_Name", hover_data={
                     "umap_1": False, "umap_2": False, "Top_Mesh_Terms": True}, width=800, height=800, color_discrete_sequence=['#fecc07'])
    fig.update_layout(plot_bgcolor='#255799', title={
        'text': f"UMAP with {num_components} PCA Components",
        'font': {'size': 30},
    })
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    st.plotly_chart(fig)

# DBSCAN clustering
st.subheader("UMAP with DBSCAN Clustering")
knn = NearestNeighbors(n_neighbors=8)
knn.fit(pca_scores)
distances, indices = knn.kneighbors(pca_scores)
dbscan = DBSCAN(eps=0.05, min_samples=2).fit(pca_scores)
umap_pca_df['cluster'] = dbscan.labels_
st.write(f"""
**Plot Description:** Shows UMAP projection (based on first {num_pca_components} PCA components). Points colored by DBSCAN clusters (eps={dbscan.eps}, min_samples={dbscan.min_samples}) found using the {num_pca_components} PCA components. Noise points often label -1. Hover shows faculty/terms/cluster. *(Note: Fixed color means all clusters appear yellow).*
""")
fig = px.scatter(umap_pca_df, x="umap_1", y="umap_2", color='cluster', title="UMAP with Clusters", hover_name="Faculty_Full_Name", hover_data={
                 "umap_1": False, "umap_2": False, "Top_Mesh_Terms": True}, width=800, height=800, color_discrete_sequence=['#fecc07'])
fig.update_layout(
    # This sets the color of the plotting area (inside the axes)
    plot_bgcolor='black',
    paper_bgcolor='black',
    title={
        'text': "UMAP with Clusters",
        'font': {'size': 30},
    })
fig.update_xaxes(title_text="")
fig.update_yaxes(title_text="")
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
st.plotly_chart(fig)

# K-means clustering
st.subheader("UMAP with K-means Clustering (K=12)")
kmeans = KMeans(n_clusters=12, random_state=123).fit(pca_scores)
umap_pca_df['cluster'] = kmeans.labels_
st.write(f"""
**Plot Description:** Shows UMAP projection (based on first {num_pca_components} PCA components). Points colored by K-means clusters (K=12) found using the {num_pca_components} PCA components. Hover shows faculty/terms/cluster. *(Note: Fixed color means all clusters appear yellow).*
""")
fig = px.scatter(umap_pca_df, x="umap_1", y="umap_2", color='cluster', title="UMAP with K-means Clusters", hover_name="Faculty_Full_Name",
                 hover_data={"umap_1": False, "umap_2": False, "Top_Mesh_Terms": True}, width=800, height=800, color_discrete_sequence=['#fecc07'])
fig.update_layout(
    # This sets the color of the plotting area (inside the axes)
    plot_bgcolor='black',
    paper_bgcolor='black',     # This sets the color of the entire figure background
    title={
        'text': "UMAP with K-means Clusters",
        'font': {'size': 30},
    })
fig.update_xaxes(title_text="")
fig.update_yaxes(title_text="")
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
st.plotly_chart(fig)

# Silhouette score for optimal K


# def calculate_silhouette_score(data, k):
#     # Make sure only numeric columns are used
#     numeric_data = data.select_dtypes(include=['float64', 'float32', 'int64', 'int32'])
    
#     print(f"Using columns for clustering: {numeric_data.columns.tolist()}")
    
#     kmeans = KMeans(n_clusters=k, random_state=123).fit(numeric_data)
#     labels = kmeans.labels_
#     return silhouette_score(numeric_data, labels)


# k_values = range(2, 21)
# umap_pca_no_faculty = umap_pca_df.drop(columns=['Faculty_Full_Name', 'Top_Mesh_Terms'])
# silhouette_values = [calculate_silhouette_score(umap_pca_no_faculty, k) for k in k_values]

# plt.figure()
# plt.plot(k_values, silhouette_values, 'b*-')
# plt.xlabel('Number of clusters K')
# plt.ylabel('Average Silhouette Width')
# plt.title('Silhouette Score for Different K')
# st.pyplot(plt)

# # ANOVA and feature significance
# filtered_data = pd.DataFrame(numeric_data)
# filtered_data['cluster'] = kmeans.labels_
# filtered_data.columns = filtered_data.columns.str.replace(
#     ' ', '_').str.replace(',', '_').str.replace('-', '_')
# feature_names = filtered_data.columns[:-1]


# def calculate_anova_pvalue(feature, data):
#     model = ols(f"{feature} ~ C(cluster)", data=data).fit()
#     anova_table = sm.stats.anova_lm(model, typ=2)
#     return anova_table["PR(>F)"][0]


# p_values = {feature: calculate_anova_pvalue(
#     feature, filtered_data) for feature in feature_names}
# _, p_adjusted, _, _ = multipletests(list(p_values.values()), method='fdr_bh')
# significant_features = [feature for feature, pval in zip(
#     feature_names, p_adjusted) if pval < 0.05]
# print("Significant features:", significant_features)

# Final UMAP with K-means clusters
st.subheader("Final UMAP Visualization (K=12, Black)") # Add subheader
# Write description for Final UMAP Plot using st.write()
st.write(f"""
**Plot Description:** Another view of UMAP (based on {num_pca_components} PCA components) colored by the K=12 K-means clusters. Hover shows faculty/terms/cluster. *(Note: Fixed BLACK color means all clusters appear black).*
""")
umap_pca_df['Faculty_Full_Name'] = raw_data['Faculty_Full_Name']
fig = px.scatter(umap_pca_df, x="umap_1", y="umap_2", color='cluster', title="UMAP with K-means Clusters", hover_name="Faculty_Full_Name",
                 hover_data={"umap_1": False, "umap_2": False, "Top_Mesh_Terms": True}, width=800, height=800, color_discrete_sequence=['#000000'])
fig.update_layout(
    # This sets the color of the plotting area (inside the axes)
    plot_bgcolor='black',
    paper_bgcolor='black',     # This sets the color of the entire figure background
    title={
        'text': "UMAP with K-means Clusters",
        'font': {'size': 30},
    })
fig.update_xaxes(title_text="")
fig.update_yaxes(title_text="")
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
st.plotly_chart(fig, key="final_umap_cluster_plot")

# Save outputs
# output_path = 'faculty-mapped-mesh-terms'
# significant_features_path = os.path.join(output_path, "Significant_terms_per_cluster.csv")
# professors_clusters_path = os.path.join(output_path, "Professors_in_clusters.csv")

# umap_pca_df_grouped = umap_pca_df.drop(columns=['umap_1', 'umap_2'])
# umap_pca_df_grouped = umap_pca_df_grouped.groupby('cluster')['Faculty_Full_Name'].apply(list).reset_index()
# umap_pca_df_grouped.to_csv(professors_clusters_path, index=True)

# significant_df = pd.DataFrame({
#     'Feature': significant_features,
#     'P-Value Adjusted': p_adjusted[:len(significant_features)]
# })
# uncomment when not running streamlit
# significant_df.to_csv(significant_features_path, index=True)
