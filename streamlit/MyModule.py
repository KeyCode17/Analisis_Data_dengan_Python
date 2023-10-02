import pandas as pd 

class AnalyzeData:
	def __init__(self, df):
		self.df = df

	def numunique(self):
		num = self.df["order_id"].drop_duplicates(keep='first').nunique()
		return num

	def data(self):
		data = self.df.groupby("customer_state")["order_id"].count().sort_values(ascending=False).head(5)
		data_SP = self.df[(self.df['customer_state'] == 'SP') & (self.df['payment_sequential'] == 1)] \
    		.groupby(["customer_state", "payment_type"])["order_id"].count().sort_values(ascending=False)
		return data, data_SP

	def grouped(self):
		# Create grouped_data for data_comb1
		grouped_data = self.df.drop_duplicates(subset=['order_id'], keep='first').groupby("seller_state")["seller_state"].count().reset_index(name='count_sell').sort_values(by='count_sell', ascending=False)

		# Create a new DataFrame from the grouped data
		grouped_df = pd.DataFrame(grouped_data)

		# Concatenate grouped data to Acc_AllData
		data_comb1 = pd.concat([grouped_df], ignore_index=True)

		# Create grouped_data for data_comb2
		grouped_data = self.df.drop_duplicates(subset=['order_id'], keep='first').groupby(["customer_state"])["customer_state"].count().reset_index(name='count_cust').sort_values(by='count_cust', ascending=False)

		# Create a new DataFrame from the grouped data
		grouped_df = pd.DataFrame(grouped_data)

		# Concatenate grouped data to Acc_AllData
		data_comb2 = pd.concat([grouped_df], ignore_index=True)

		# Merge Data for data_comb
		data_comb = pd.merge(left=data_comb2, right=data_comb1, how="outer", left_on="customer_state", right_on="seller_state")

		# Change the column name at index 0
		data_comb.rename(columns={'customer_state': 'State'}, inplace=True)

		# Remove the column at index 2 also fill Null with 0
		data_comb = data_comb.drop(columns=['seller_state'], axis=1).fillna(0)

		# Normalisasi Data
		def minmax_scaler(df, columns):
		
		  scaled_df = pd.DataFrame()
		  for column in columns:
		    min_value = df[column].min()
		    max_value = df[column].max()
		    scaled_column = (df[column] - min_value) / (max_value - min_value)
		    scaled_df[column] = scaled_column
		  return scaled_df
		
		data_comb[['count_cust', 'count_sell']] = minmax_scaler(data_comb, ['count_cust', 'count_sell'])
		return data_comb

	def ACC_data2018(self):
		ACC_data2018 = self.df[(self.df['order_purchase_timestamp'].dt.year == 2018)].drop_duplicates(subset=['order_id','product_category_name_english'], keep='first')
		ACC_data2018.rename(columns={'order_purchase_timestamp': 'Purchase Timestamp'}, inplace=True)
		ACC_data2018.rename(columns={'product_category_name_english': 'Product Category'}, inplace=True)
		grouped = ACC_data2018.groupby([ACC_data2018['Purchase Timestamp'].dt.month,'Product Category']).count()
		# Define a dictionary to map month numbers to month names
		month_map = {
		    1: 'January',
		    2: 'February',
		    3: 'March',
		    4: 'April',
		    5: 'May',
		    6: 'June',
		    7: 'July',
		    8: 'August',
		    9: 'September',
		    10: 'October',
		    11: 'November',
		    12: 'December'
		}

		# Map month numbers to month names in the MultiIndex level and assign it back to the DataFrame
		new_index = grouped.index.set_levels(grouped.index.levels[0].map(month_map), level=0)

		# Update the MultiIndex of the DataFrame
		grouped.set_index(new_index, inplace=True)

		grouped.rename(columns={'order_purchase_timestamp': 'Purchase Timestamp'}, inplace=True)
		grouped.rename(columns={'product_category_name_english': 'Product Category'}, inplace=True)

		# Print the updated DataFrame
		grouped = grouped['order_id'].reset_index(name='Count').set_index(['Purchase Timestamp', 'Product Category'])
		return grouped

