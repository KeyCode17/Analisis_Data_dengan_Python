# Import Library
import os
import numpy as np
import pandas as pd 
import seaborn as sns
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt
from scipy.stats import shapiro
from MyModule import AnalyzeData
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import ConnectionPatch

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]

Acc_all_df = pd.read_csv(os.path.abspath("dataset/Acc_AllData.csv"))
Not_Acc_all_df = pd.read_csv(os.path.abspath("dataset/NotAcc_AllData.csv"))

Acc_all_df.sort_values(by="order_approved_at", inplace=True)
Acc_all_df.reset_index(inplace=True)

Not_Acc_all_df.sort_values(by="order_approved_at", inplace=True)
Not_Acc_all_df.reset_index(inplace=True)



for col in datetime_cols:
    Acc_all_df[col] = pd.to_datetime(Acc_all_df[col])
    Not_Acc_all_df[col] = pd.to_datetime(Not_Acc_all_df[col])

Acc_min_date = Acc_all_df["order_approved_at"].min()
Acc_max_date = Acc_all_df["order_approved_at"].max()

Not_Acc_min_date = Not_Acc_all_df["order_approved_at"].min()
Not_Acc_max_date = Not_Acc_all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Mochammad Daffa Putra Karyudi")

    # Image
    st.image(Image.open(os.path.abspath("e-commerce.png")), output_format="PNG")

    # Date Range
    start_date, end_date = st.date_input(
        label="Pilih jangka waktu",
        value=[Acc_min_date, Acc_max_date],
        min_value=Acc_min_date,
        max_value=Acc_max_date
    )

df_Acc = Acc_all_df[(Acc_all_df["order_approved_at"] >= str(start_date)) & 
                 (Acc_all_df["order_approved_at"] <= str(end_date))]

df_NotAcc = Not_Acc_all_df[(Not_Acc_all_df["order_approved_at"] >= str(start_date)) & 
                 (Not_Acc_all_df["order_approved_at"] <= str(end_date))]

# Create an instance of AnalyzeData
analyzer_Acc = AnalyzeData(df_Acc)

# Call the numunique method on the instance
Acc_Uniqe_ID = analyzer_Acc.numunique()

# Create an instance of AnalyzeData
analyzer_NotAcc = AnalyzeData(df_NotAcc)

# Call the numunique method on the instance
NotAcc_Uniqe_ID = analyzer_NotAcc.numunique()

# Call data method on the instance
data, data_SP = analyzer_Acc.data()

# Membuat Array Data yang Digunakan untuk data_frames
data_frames = [analyzer_Acc.grouped()]

grouped = analyzer_Acc.ACC_data2019()

# Title
st.title("E-Commerce Dashboard")

# Header
st.header("Perbandingan Penjualan")

# Pie Chart Perbandingan Penjualan
sizes = [Acc_Uniqe_ID, NotAcc_Uniqe_ID]
labels = 'Sells Accepted', 'Sells Declined'
colors = ['#66b3ff', '#ff9999']  
explode = (0.1, 0.2)  

fig, ax = plt.subplots()
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, 
                                   explode=explode, shadow=True, startangle=0,
                                   pctdistance=0.85, wedgeprops={'width': 1}) 

ax.axis('equal') 

ax.legend(loc='best', labels=labels)

st.pyplot(fig)



# SubTitle
st.header('Distribusi data dari Tipe Pembayaran')
tab1, tab2 = st.tabs(["Daerah Terbanyak", "Tipe Pembayaran"])

with tab1:
	st.subheader('Distribusi Customers dengan Daerah Terbanyak')
	# make figure and assign axis objects
	fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 5))
	fig.subplots_adjust(wspace=0)

	explode = explode = [0.1 if i == 0 else 0 for i in range(len(data))]

	# pie chart parameters
	overall_ratios = data.values
	labels = data.index.get_level_values('customer_state')

	# rotate so that first wedge is split by the x-axis
	wedges, *_ = ax1.pie(overall_ratios, autopct='%1.1f%%', startangle=260,
	                     labels=labels, explode=explode, wedgeprops=dict(edgecolor='white') ,textprops={'fontsize': 10})

	# bar chart parameters
	age_ratios = data_SP.values / data_SP.sum() * 100
	age_labels = data_SP.index.get_level_values('payment_type')
	bottom = 1
	width = .2

	# Adding from the top matches the legend.
	for j, (height, label) in enumerate(reversed([*zip(age_ratios, age_labels)])):
	    bottom -= height
	    bc = ax2.bar(0, height, width, bottom=bottom, label=label, color='#c2c2f0',
	                alpha=0.1 + 0.25 * j)
	    if height > 15:
	        ax2.bar_label(bc, labels=[f"{height:1.1f}%"], label_type='center')

	ax2.legend()
	ax2.axis('off')
	ax2.set_xlim(- 2.5 * width, 2.5 * width)

	# use ConnectionPatch to draw lines between the two plots
	theta1, theta2 = wedges[0].theta1, wedges[0].theta2
	center, r = wedges[0].center, wedges[0].r
	bar_height = 100

	# draw top connecting line
	x = r * np.cos(np.pi / 180 * theta2) + center[0]
	y = r * np.sin(np.pi / 180 * theta2) + center[1]
	con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax2.transData,
	                      xyB=(x, y), coordsB=ax1.transData)
	con.set_color([0, 0, 0])
	con.set_linewidth(4)
	ax2.add_artist(con)

	# draw bottom connecting line
	x = r * np.cos(np.pi / 180 * theta1) + center[0]
	y = r * np.sin(np.pi / 180 * theta1) + center[1]
	con = ConnectionPatch(xyA=(-width / 2, bottom), coordsA=ax2.transData,
	                      xyB=(x, y), coordsB=ax1.transData)
	con.set_color([0, 0, 0])
	ax2.add_artist(con)
	con.set_linewidth(4)

	st.pyplot(fig)

with tab2:
	st.subheader('Distribusi dengan Pembagian Tipe Pembayaran')

	# Extract payment types and their counts
	counts = data_SP.values

	# Custom colors for the slices
	colors = ['#c2c2f0', '#99ff99', '#66b3ff', '#ff9999']
	labels = data_SP.index.get_level_values('payment_type')
	# Explode values to separate slices
	explode = (0.05, 0, 0.1, 0.15)

	# Create a pie chart
	plt.figure(figsize=(8, 8))  # Set the figure size
	plt.pie(counts,radius=0.8,labeldistance=1, pctdistance=0.8, labels=labels,
	    autopct='%1.1f%%', explode=explode, startangle=20, colors=colors, shadow=True, textprops={'fontsize': 15})

	# Add a legend with custom colors
	plt.legend(labels=labels, loc='upper right', bbox_to_anchor=(1, 0, 0.5, 1), prop={'size': 12})

	# Equal aspect ratio ensures that pie is drawn as a circle
	plt.axis('equal')

	# Display the chart
	st.pyplot(plt)

st.header('Test Distribusi Data Secara Normal dan Tidak Normal')
# Set alpha
alpha = 0.05

# String Komentar Data
normal = 'Data terdistribusi secara normal '
notnormal = 'Data terdistribusi secara tidak normal'

# Loop Start
for i, df in enumerate(data_frames):
    f, axes = plt.subplots(1, 2, figsize=(15, 15))
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=1, wspace=0.4, hspace=0.4)

    # Histogram
    # Seller State
    seller_state = sns.histplot(df.iloc[:, 1], ax=axes[0], kde=True, color='blue')
    seller_state.set(xlim=(0.0, 1.0))
    seller_state.set_xticks(np.arange(0.0, 1.1, 0.3))
    seller_state.set_xlabel('Seller State')
    stat, p_value = shapiro(df.iloc[:, 1])
    if p_value > alpha:
        seller_state.set_title(f'p-value: {p_value:.4f} \n' + normal)
    else:
        seller_state.set_title(f'p-value: {p_value:.4f} \n' + notnormal)

    # Ponsel
    customer_state = sns.histplot(df.iloc[:, 2], ax=axes[1], kde=True, color='green')
    customer_state.set_xlabel('Customer State')
    customer_state.set(xlim=seller_state.get_xlim())
    customer_state.set_xticks(seller_state.get_xticks())
    stat, p_value = shapiro(df.iloc[:, 2])
    if p_value > alpha:
        customer_state.set_title(f'p-value: {p_value:.4f} \n' + normal)
    else:
        customer_state.set_title(f'p-value: {p_value:.4f} \n' + notnormal)

# Display the chart
st.pyplot(plt)

# Korelasi Daerah Penjualan dan Pembeli
st.header("Korelasi Daerah Penjualan dan Pembeli")

# Membuat Array untuk Xbar Variable dan Ybar Variable
column_labels = ['Seller State', 'Customer State']

# Loop Start
for i, df in enumerate(data_frames):
    # Membuat subplots
    f, axes = plt.subplots(1, 3, figsize=(14, 6), gridspec_kw={'width_ratios': [1, 0.05, 1]})

    # Pearson correlation
    correlation_pearson = df.iloc[:,1:].corr(method='pearson')
    pearson_heatmap = sns.heatmap(correlation_pearson,
                                  cmap='coolwarm',
                                  annot=True,
                                  fmt='.3g',
                                  ax=axes[0],
                                  vmax=1,
                                  vmin=0.939,
                                  cbar=False)
    pearson_heatmap.set_title("Korelasi Pearson")
    pearson_heatmap.set_xticklabels(column_labels, rotation=45, ha='right')
    pearson_heatmap.set_yticklabels(column_labels, rotation=0)

    # Spearman correlation
    correlation_spearman = df.iloc[:,1:].corr(method='spearman')
    sns.heatmap(correlation_spearman,
                cmap='coolwarm',
                annot=True,
                fmt='.3g',
                ax=axes[2],
                vmin=0.939,
                vmax=1,
                cbar=True,
                cbar_ax=axes[1])
    axes[2].set_title("Korelasi Spearman")
    axes[2].set_xticklabels(column_labels, rotation=45, ha='right')
    axes[2].set_yticklabels(column_labels, rotation=0)
    axes[2].yaxis.tick_right()
    axes[2].yaxis.set_label_position('right')

st.pyplot(plt)

# Tren Penjualan
st.header('Tren penjualan produk berdasarkan produk kategori (Penjualan > 300)')

df_reset = grouped.reset_index()

# Filter rows where count is more than 300
filtered_df = df_reset[df_reset['Count'] > 300]

# Filter months from January to May
months_to_include = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']
filtered_df = filtered_df[filtered_df['Purchase Timestamp'].isin(months_to_include)]

# Get product categories that had sales in each month
product_categories_to_include = filtered_df.groupby('Product Category').filter(lambda x: len(x) == len(months_to_include))['Product Category'].unique()

# Filter the DataFrame to include only selected product categories
filtered_df = filtered_df[filtered_df['Product Category'].isin(product_categories_to_include)]

# Pivot the filtered DataFrame to create the appropriate format for the line graph
pivot_df = filtered_df.pivot_table(index='Purchase Timestamp', columns='Product Category', values='Count', aggfunc='sum')

# Set a seaborn style for better aesthetics
sns.set(style="whitegrid")

# Plotting the line graph with seaborn settings and custom x-axis order
plt.figure(figsize=(12, 6))
sns.lineplot(data=pivot_df, markers=True, dashes=False, hue_order=product_categories_to_include)
plt.xlabel('Purchase Timestamp')
plt.ylabel('Count')
plt.legend(title='Product Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)  # Rotating x-axis labels for better visibility
plt.xticks(ticks=range(len(months_to_include)), labels=months_to_include)  # Setting custom x-axis order
plt.tight_layout()
st.pyplot(plt)

# Geolokasi
st.header('Geolokasi dari tiap customer yang mendaftar')

customer = pd.read_csv(os.path.abspath("dataset/customers_dataset.csv"))
geolocation = pd.read_csv(os.path.abspath("dataset/geolocation_dataset.csv"))

location = pd.merge(
    left=customer,
    right=geolocation,
    left_on=["customer_zip_code_prefix", "customer_city", "customer_state"],
    right_on=["geolocation_zip_code_prefix", "geolocation_city", "geolocation_state"],
    how="inner"
)

plt.figure(figsize=(12, 9))

# Create a Basemap of Brazil
map = Basemap(projection='merc', llcrnrlat=-35, urcrnrlat=6, llcrnrlon=-75, urcrnrlon=-35, resolution='i')

# Create a scatter plot of customer geolocation data with smaller dots
x, y = map(location['geolocation_lng'].values, location['geolocation_lat'].values)
map.scatter(x, y, marker='o', color='blue', alpha=0.6, zorder=5, s=1)  # Adjust the 's' parameter for smaller dots

# Draw coastlines and country boundaries
map.drawcoastlines()
map.drawcountries()

st.pyplot(plt)