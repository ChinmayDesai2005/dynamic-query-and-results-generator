import streamlit as st
import helper_functions
import os
import pandas as pd
import function_calling
import matplotlib

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'path/to/credentials.json'


# Application begins here
prompt = st.text_input(label="Prompt", placeholder="Enter a prompt")
gemini = helper_functions.GeminiChat()

if prompt:
    # spin_loader
    with st.spinner('Generating query'):
    # ask gemini for query
        response = function_calling.userPromptToFunctionCall(prompt)
        print(type(response))
        match response:
            case pd.DataFrame():
                print("dataframe")
                st.dataframe(response)
            case matplotlib.figure.Figure():
                print("figure")
                st.pyplot(response)

# DONE
# TODO Before sending a query, add to the prompt so that only the columns we need will be returned in the dataframe in a very specific order, so that we can directly use it.
# TODO Clean up code into functions.