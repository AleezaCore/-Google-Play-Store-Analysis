
import plotly.io as pio

pio.renderers.default = "browser"

import pandas as pd
import plotly.express as px

pd.options.display.float_format = '{:,.2f}'.format

df_apps = pd.read_csv('apps.csv')

print(df_apps.shape)
print(df_apps.columns.tolist())
print(df_apps.sample(5))


df_apps = df_apps.drop(['Last_Updated', 'Android_Ver'], axis=1)


print(df_apps[df_apps.Rating.isna()].shape)

df_apps_clean = df_apps.dropna().copy()
print(df_apps_clean.shape)       # expect (9367, 10)


duplicated_rows = df_apps_clean[df_apps_clean.duplicated()]
print(duplicated_rows.shape)     # expect 476 rows
print(df_apps_clean[df_apps_clean.App == 'Instagram'])

df_apps_clean = df_apps_clean.drop_duplicates(subset=['App', 'Type', 'Price'])
print(df_apps_clean.shape)       # expect (8199, 10)

print(df_apps_clean.sort_values('Rating', ascending=False).head())
print(df_apps_clean.sort_values('Size_MBs', ascending=False).head())   # 100 MB cap
print(df_apps_clean.sort_values('Reviews', ascending=False).head(50))  # no paid apps

ratings = df_apps_clean.Content_Rating.value_counts()

fig = px.pie(values=ratings.values,
             names=ratings.index,
             title='Content Rating')
fig.update_traces(textposition='outside', textinfo='percent+label')
fig.show()

fig = px.pie(values=ratings.values,
             names=ratings.index,
             title='Content Rating',
             hole=0.6)
fig.update_traces(textposition='inside', textfont_size=15, textinfo='percent')
fig.show()


# ---------------------------------------------------------------
# 5. NUMERIC CONVERSIONS (lesson 563)
# ---------------------------------------------------------------
print(df_apps_clean.Installs.dtype)   # object (text)

# Installs: remove commas, convert
df_apps_clean['Installs'] = df_apps_clean.Installs.astype(str).str.replace(',', '', regex=False)
df_apps_clean['Installs'] = pd.to_numeric(df_apps_clean.Installs)
print(df_apps_clean[['App', 'Installs']].groupby('Installs').count())

# Price: remove $, convert
df_apps_clean['Price'] = df_apps_clean.Price.astype(str).str.replace('$', '', regex=False)
df_apps_clean['Price'] = pd.to_numeric(df_apps_clean.Price)
print(df_apps_clean.sort_values('Price', ascending=False).head(20))  # "I am Rich" apps

# Remove the junk apps
df_apps_clean = df_apps_clean[df_apps_clean['Price'] < 250]
print(df_apps_clean.sort_values('Price', ascending=False).head(5))

# Revenue estimate (price x installs)
df_apps_clean['Revenue_Estimate'] = df_apps_clean.Installs.mul(df_apps_clean.Price)
print(df_apps_clean.sort_values('Revenue_Estimate', ascending=False)[:10])


# ---------------------------------------------------------------
# 6. COMPETITIVE + POPULAR CATEGORIES (lesson 564)
# ---------------------------------------------------------------
print(df_apps_clean.Category.nunique())   # 33

# Most competitive: number of apps per category
top10_category = df_apps_clean.Category.value_counts()[:10]
bar = px.bar(x=top10_category.index,
             y=top10_category.values,
             title='Top 10 Categories by Number of Apps')
bar.update_layout(xaxis_title='Category', yaxis_title='Number of Apps')
bar.show()

# Most popular: total installs per category
category_installs = df_apps_clean.groupby('Category').agg({'Installs': 'sum'})
category_installs = category_installs.sort_values('Installs', ascending=True)

h_bar = px.bar(x=category_installs.Installs,
               y=category_installs.index,
               orientation='h',
               title='Category Popularity')
h_bar.update_layout(xaxis_title='Number of Downloads', yaxis_title='Category')
h_bar.show()

# Concentration: apps vs installs per category
cat_number = df_apps_clean.groupby('Category').agg({'App': 'count'})
cat_merged_df = pd.merge(cat_number, category_installs, on='Category', how='inner')
print(f'The dimensions of the DataFrame are: {cat_merged_df.shape}')

scatter = px.scatter(cat_merged_df,
                     x='App',
                     y='Installs',
                     title='Category Concentration',
                     size='App',
                     hover_name=cat_merged_df.index,
                     color='Installs')
scatter.update_layout(xaxis_title='Number of Apps (Lower=More Concentrated)',
                      yaxis_title='Installs',
                      yaxis=dict(type='log'))
scatter.show()


# ---------------------------------------------------------------
# 7. NESTED GENRE DATA WITH .stack() (lesson 565)
# ---------------------------------------------------------------
print(df_apps_clean.Genres.nunique())     # 114 (inflated by nested values)

stack = df_apps_clean.Genres.str.split(';', expand=True).stack()
print(f'We now have a single column with shape: {stack.shape}')
num_genres = stack.value_counts()
print(f'Number of genres: {len(num_genres)}')   # 53

bar = px.bar(x=num_genres.index[:15],
             y=num_genres.values[:15],
             title='Top Genres',
             hover_name=num_genres.index[:15],
             color=num_genres.values[:15],
             color_continuous_scale='Agsunset')
bar.update_layout(xaxis_title='Genre',
                  yaxis_title='Number of Apps',
                  coloraxis_showscale=False)
bar.show()


# ---------------------------------------------------------------
# 8. FREE VS PAID: GROUPED BARS + BOX PLOTS (lesson 566)
# ---------------------------------------------------------------
print(df_apps_clean.Type.value_counts())

df_free_vs_paid = df_apps_clean.groupby(['Category', 'Type'], as_index=False).agg({'App': 'count'})
print(df_free_vs_paid.head())

g_bar = px.bar(df_free_vs_paid,
               x='Category',
               y='App',
               title='Free vs Paid Apps by Category',
               color='Type',
               barmode='group')
g_bar.update_layout(xaxis_title='Category',
                    yaxis_title='Number of Apps',
                    xaxis={'categoryorder': 'total descending'},
                    yaxis=dict(type='log'))
g_bar.show()

# Installs: free vs paid
box = px.box(df_apps_clean,
             y='Installs',
             x='Type',
             color='Type',
             notched=True,
             points='all',
             title='How Many Downloads are Paid Apps Giving Up?')
box.update_layout(yaxis=dict(type='log'))
box.show()

# Revenue by category (paid apps only)
df_paid_apps = df_apps_clean[df_apps_clean['Type'] == 'Paid']

box = px.box(df_paid_apps,
             x='Category',
             y='Revenue_Estimate',
             title='How Much Can Paid Apps Earn?')
box.update_layout(xaxis_title='Category',
                  yaxis_title='Paid App Ballpark Revenue',
                  xaxis={'categoryorder': 'min ascending'},
                  yaxis=dict(type='log'))
box.show()

# Pricing by category
print(f'Median price of a paid app: ${df_paid_apps.Price.median()}')   # 2.99

box = px.box(df_paid_apps,
             x='Category',
             y='Price',
             title='Price per Category')
box.update_layout(xaxis_title='Category',
                  yaxis_title='Paid App Price',
                  xaxis={'categoryorder': 'max descending'},
                  yaxis=dict(type='log'))
box.show()