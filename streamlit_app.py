# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

import requests
import pandas 



# Write directly to the app
st.title(f"Custom Smoothie Order :balloon: {st.__version__}")
st.write(
  """Customize your smoothie
  """
)

name_on_order = st.text_input("Smoothie Name:")
st.write("The name of Smoothie is", name_on_order)

cnx = st.connection("snowflake")
session=cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

ingredients_list = st.multiselect('Choose up to 5 ingredients',my_dataframe,max_selections = 5)

time_to_insert = st.button('Submit Order')
if ingredients_list:
    st.write(ingredients_list)
    st.text(ingredients_list)

    ingredients_string =''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen +' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' nutrition info')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)      
        st.write(ingredients_string)
        my_insert_stmt = """ insert into smoothies.public.orders(ingredients,NAME_ON_ORDER)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie ' + name_on_order + ' is ordered!', icon="✅")
