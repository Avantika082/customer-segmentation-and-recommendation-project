import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


# Load Data
customers_df = pd.read_csv('../Dataset/Customers.csv')
products_df = pd.read_csv('../Dataset/Products.csv')
transactions_df = pd.read_csv('../Dataset/Transactions.csv')


# Build customer product interaction
def product_user_interaction():
    interaction = transactions_df.groupby(['customer_id','product_id']).size().unstack(fill_value=0)
    return interaction


# Get the customer cluster
def get_customer_cluster(customer_id):
    customer_cluster = customers_df[customers_df['customer_id'] == customer_id]
    if not customer_cluster.empty:
        return customer_cluster.iloc[0]['Cluster']
    return None


# Build feature matrix for product description
def product_feature_matrix():

    products_df['combined'] = (products_df['category'].astype(str) + ' ' +
    products_df['brand'].astype(str) + ' ' +
    products_df['style'].astype(str) + ' ' +
    products_df['season'].astype(str) + ' ' +
    products_df['price'].astype(str)  
    )

    vectorizer = TfidfVectorizer()
    prod_feature_matrix = vectorizer.fit_transform(products_df['combined'])
    return  prod_feature_matrix

# Collaborative recommendation using cosine similarity

def collaborative_recommendation(customer_id , top_n=10):
    customer_cluster = get_customer_cluster(customer_id)
    if customer_cluster is None:
        return pd.DataFrame()
    
    cluster_users = customers_df[customers_df['Cluster']== customer_cluster]['customer_id'].tolist()
    interaction_matrix = product_user_interaction()
    common_users = [users for users in cluster_users if users in interaction_matrix.index]

    if customer_id not in interaction_matrix.index:
        return pd.DataFrame()
    
    cluster_matrix = interaction_matrix.loc[common_users]

    similarities = cosine_similarity([interaction_matrix.loc[customer_id]] , cluster_matrix)[0]

    similar_users = pd.Series(similarities , index=cluster_matrix.index)
    top_users = similar_users.sort_values(ascending=False)[1:11]

    # aggregate top products from similar users
    recommended_product_ids = (
        interaction_matrix.loc[top_users.index].sum().sort_values(ascending=False).head(top_n).index.tolist()

    )

    return products_df[products_df['product_id'].isin(recommended_product_ids)]


# Content based filtering using cosine similarity

def content_based_recommendation(customer_id , top_n=10):

    customer_products = transactions_df[transactions_df['customer_id'] == customer_id]['product_id'].unique()
    if len(customer_products) == 0:
        return pd.DataFrame()
    
    Tfidfmatrix = product_feature_matrix()
    product_indices = products_df[products_df['product_id'].isin(customer_products)].index


    customer_profile = np.asarray(Tfidfmatrix[product_indices].mean(axis=0)).reshape(1,-1)

    similarity_scores = cosine_similarity(customer_profile,Tfidfmatrix)[0]
    Top_product_indices = similarity_scores.argsort()[::-1]

    recommendations =[]
    for idx in Top_product_indices:
        product_index = products_df.iloc[idx]['product_id']
        if product_index not in customer_products:
            recommendations.append(product_index)
        if len(recommendations)>= top_n:
            break

    return products_df[products_df['product_id'].isin(recommendations)]


# Include both the recommendation to build hybrid recommendation filter
def hybrid_recommendation(customer_id , top_n=10):
    collab_df = collaborative_recommendation(customer_id, top_n=top_n)
    content_df = content_based_recommendation(customer_id,top_n=top_n)

    combined_df = pd.concat([collab_df,content_df])
    #combined_df = combined_df.drop_duplicates('product_id')


    return combined_df.head(top_n)


interactions = product_user_interaction()
cluster = get_customer_cluster(5)
idfmat = product_feature_matrix()
collab_recommendation = collaborative_recommendation(5,10)
cont_rec = content_based_recommendation(5,10)
hyb_rec = hybrid_recommendation(5,10)

'''print(interactions)
print(cluster)
print(idfmat)
print(collab_recommendation)
print(cont_rec)
print(hyb_rec)'''

