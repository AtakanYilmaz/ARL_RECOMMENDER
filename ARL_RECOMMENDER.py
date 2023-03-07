
############################################
# Data Pre-processing
############################################

import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 500)
pd.set_option("display.expand_frame_repr", False)
from mlxtend.frequent_patterns import apriori, association_rules

# Veri'nin Okunması

df_ = pd.read_excel("Hafta_03/Ders Öncesi Notlar/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.info()
df.head()

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

def retail_data_prep(dataframe):
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    return dataframe

df = retail_data_prep(df)

############################################
# Preparing the ARL Data Structure  (Invoice-Product Matrix)
############################################

df_de = df[df["Country"] == "Germany"]

# df_de.groupby(["Invoice", "Description"]).agg({"Quantity" : "sum"}).head(20)
#
# df_de.groupby(["Invoice", "Description"]).agg({"Quantity" : "sum"}).unstack().iloc[0:5, 0:5]
#
# df_de.groupby(["Invoice", "Description"]).agg({"Quantity" : "sum"}).unstack().fillna(0).iloc[0:5, 0:5]
#
# df_de.groupby(["Invoice", "Description"]).agg({"Quantity" : "sum"}).unstack().fillna(0).applymap(
#     lambda x: 1 if x > 0 else 0).iloc[0:5, 0:5]

def create_invoice_product_df(dataframe, id=False):
    if id:
        return dataframe.groupby(["Invoice", "StockCode"])["Quantity"].sum().unstack().fillna(0).applymap(
            lambda x: 1 if x > 0 else 0)
    else:
        return dataframe.groupby(["Invoice", "Description"])["Quantity"].sum().unstack().fillna(0).applymap(
            lambda x: 1 if x > 0 else 0)


de_inv_pro_df = create_invoice_product_df(df_de)
de_inv_pro_df.head()

de_inv_pro_df = create_invoice_product_df(df_de, id=True)

def check_id(dataframe, stock_code):
    product_name = dataframe[dataframe["StockCode"] == stock_code][["Description"]].values[0].tolist()
    print(product_name)

check_id(df_de,84945)

############################################
# Making Association Rules
############################################

frequent_itemsets = apriori(de_inv_pro_df, min_support=0.01, use_colnames=True)
frequent_itemsets.sort_values("support", ascending=False).head(50)

rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
rules.sort_values("support", ascending=False).head()

rules.sort_values("lift", ascending=False).head(50)

# Task 3: What are the names of the products whose IDs are given?
# User 1 product id: 21987
# User 2 product id: 23235
# User 3 product id: 22747

check_id(df_de, 21987) # PACK OF 6 SKULL PAPER CUPS

check_id(df_de, 23235) # STORAGE TIN VINTAGE LEAF

check_id(df_de, 22747) # POPPY'S PLAYHOUSE BATHROOM


############################################
# Preparing the Script of the Study
############################################

# import pandas as pd
#
# pd.set_option('display.max_columns', None)
# from mlxtend.frequent_patterns import apriori, association_rules

# def create_invoice_product_df(dataframe, id=False):
#     if id:
#         return dataframe.groupby(['Invoice', "StockCode"])['Quantity'].sum().unstack().fillna(0). \
#             applymap(lambda x: 1 if x > 0 else 0)
#     else:
#         return dataframe.groupby(['Invoice', 'Description'])['Quantity'].sum().unstack().fillna(0). \
#             applymap(lambda x: 1 if x > 0 else 0)

# def check_id(dataframe, stock_code):
#     product_name = dataframe[dataframe["StockCode"] == stock_code][["Description"]].values[0].tolist()
#     print(product_name)

def create_rules(dataframe, id=True, country="Germany"):
    dataframe = dataframe[dataframe["Country"] == country]
    dataframe = create_invoice_product_df(dataframe, id)
    frequent_itemsets = apriori(dataframe, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
    return rules

df_ = pd.read_excel("Hafta_03/Ders Öncesi Notlar/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

df = retail_data_prep(df)
rules_de = create_rules(df)
sorted_rules_de = rules_de.sort_values("lift", ascending=False)

product_id = 21987

recommendation_list = []

for i, product in enumerate(sorted_rules_de["antecedents"]):
    for j in list(product):
        if j == product_id:
            recommendation_list.append(list(sorted_rules_de.iloc[i]["consequents"])[0])

recommendation_list[0:3]

check_id(df, recommendation_list[0])

def arl_recommender(rules_df, product_id, rec_count=1):

    sorted_rules = rules_df.sort_values("lift", ascending=False)

    recommendation_list = []

    for i, product in sorted_rules["antecedents"].items():
        for j in list(product):
            if j == product_id:
                recommendation_list.append(list(sorted_rules.iloc[i]["consequents"]))

    recommendation_list = list({item for item_list in recommendation_list for item in item_list})

    return recommendation_list[:rec_count]

# User product ids: 21987, 23235, 22747

  # MISSION 4: Make a product recommendation for the users in the cart.

product_ids = [21987, 23235, 22747]

arl_recommender(rules_de, 21987, 1) # 21671 = RED SPOT CERAMIC DRAWER KNOB'
check_id(df, 21671)
arl_recommender(rules_de, 23235, 1) #21915 = RED  HARMONICA IN BOX
check_id(df, 21915)
arl_recommender(rules_de, 22747, 1) #22423 = REGENCY CAKESTAND 3 TIER
check_id(df, 22423)
