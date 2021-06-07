import pandas as pd
from customer_segmentation_toolkit.analyse_customers import (
    add_customer_clusters_info,
    analyse_customers_pca,
    build_transactions_per_user,
    compute_customer_clusters,
    convert_customers_df_to_np,
)
from customer_segmentation_toolkit.analyse_purchases import (
    add_purchase_clusters_info,
    build_keywords_matrix,
    build_product_list,
    compute_purchase_clusters,
)
from customer_segmentation_toolkit.clean_rows import clean_data_rows


def transform(no_live_data: pd.DataFrame) -> pd.DataFrame:  # type: ignore
    """
    Transforms taken from the Customer segmentation toolkit:
      https://github.com/artemlops/customer-segmentation-toolkit/
      (see index.ipynb)

    In general, it uses PCA to compute clusters of products
    (using keywords in Descriptions) and of customers, and
    returns a copy data frame.
    """

    df = no_live_data.copy()

    N_PURCHASE_CLUSTERS = 5
    N_CUSTOMER_CLUSTERS = 11
    THRESHOLD = [0, 1, 2, 3, 5, 10]

    # Clean bad data entries
    df_cleaned = clean_data_rows(df)

    # Analysing purchases
    list_products = build_product_list(df_cleaned)
    matrix = build_keywords_matrix(df_cleaned, list_products, THRESHOLD)
    clusters = compute_purchase_clusters(matrix, N_PURCHASE_CLUSTERS)

    df_with_clusters = add_purchase_clusters_info(
        df_cleaned, clusters, N_PURCHASE_CLUSTERS
    )

    # Analysing customers
    # NOTE: here we do different from the original notebook:
    #  we don't split train-test here, we'll do it later
    basket_price = df_with_clusters
    transactions_per_user = build_transactions_per_user(
        basket_price, n_purchase_clusters=N_PURCHASE_CLUSTERS
    )
    matrix = convert_customers_df_to_np(transactions_per_user, N_PURCHASE_CLUSTERS)
    scaled_matrix, pca = analyse_customers_pca(matrix)
    clusters_clients = compute_customer_clusters(scaled_matrix, N_CUSTOMER_CLUSTERS)

    merged_df = add_customer_clusters_info(transactions_per_user, clusters_clients)

    # done
    return merged_df
