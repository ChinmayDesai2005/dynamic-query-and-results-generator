import vertexai
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)
import matplotlib.pyplot as plt
import pandas as pd
from vertexai.preview.generative_models import ToolConfig
import os
import helper_functions
import streamlit as st
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'path/to/credentials.json'

def generatePieChart(parameters):

    # Call getResultsFromQuery and remove redundancy
    dataDesc = parameters['dataDescription']
    dataDesc += ".\nGenerate the query so that the output can be shown on a pie chart and has only 2 columns the first one being labels and second one the numbers for the pie chart sections.\n"
    df = getResultsFromQuery({'query': dataDesc})
    st.write(df)

    #Convert data into a pie chart
    fig, ax = plt.subplots()
    ax.pie(df.iloc[:, 1].values, labels=df.iloc[:, 0].values)

    return fig

def getResultsFromQuery(parameters):

    dataDesc = parameters['query']
    gemini = helper_functions.GeminiChat()
    response = gemini.convertToQuery(dataDesc)
    st.write(response.text)
    try:
        df = helper_functions.query_bigquery(response.text.replace('```', '').replace("sql", ''))

    except Exception as e:
        st.error("We encountered an error. Please wait!")
        response = gemini.askGeminiChat(f"The query you provided had a syntax error. Error: {e}. Please provide a correct query. Only return SQL Query and nothing more.")
        st.write("New Query")
        st.write(response.text)
        df = helper_functions.query_bigquery(response.text.replace('```', '').replace("sql", ''))

    return df

def generateLineChart(parameters):
    # Call getResultsFromQuery and remove redundancy
    dataDesc = parameters['dataDescription']
    gemini = helper_functions.GeminiChat()
    response = gemini.convertToQuery(dataDesc)
    print(response.text)
    st.write(response.text.replace('```', '').replace("```sql", ''))
    df = helper_functions.query_bigquery(response.text.replace('```', '').replace("sql", ''))
    # response = gemini.askGemini(f"Refer the dataFrame below: {df.head(20)}. Generate a JSON with the corresponding fields: data: An array of only data for the chosen column, labels:labels for the chosen column and axis: name of the axis, with the best suited configuration so that the data will fit into matplotlib pie chart. The data field must consist of numeric values only. Only return in JSON format strictly without backticks.")
    response = gemini.askGemini(f"Refer the dataFrame below: {df.head(20)}. Generate a JSON with the corresponding fields: data: The name of the column to be chosen for data, labels:name of the column chosen for labelling and axis: name of the axis, with the best suited configuration so that the data will fit into matplotlib pie chart. The data field must consist of numeric values only. Only return in JSON format strictly without backticks.")
    print(response.text)
    fig_input = json.loads(response.text.replace('```', '').replace("json", ''))
    print(fig_input['data'])
    # df[response.text.split("\n")[0]]

    fig, ax = plt.subplots()
    ax.pie(df[fig_input['data']], labels=df[fig_input['labels']])
    ax.title.set_text(f"Based on {fig_input['axis']}" if fig_input['axis'] != None else "")
    return fig


def check_function_call(response_function):
    match response_function.name:
        case "get_results_from_query":
            return getResultsFromQuery(response_function.args)
            
        case "generate_pie_chart":
            return generatePieChart(response_function.args)
        
        case "generate_line_chart":
            return generateLineChart(response_function.args)
        
        case _:
            return None


def userPromptToFunctionCall(prompt):
    vertexai.init(project='trainingmlteam', location="asia-south1")


    generate_pie_chart = FunctionDeclaration(
        name="generate_pie_chart",
        description="This function generates a pie chart based on the provided data description. Only use when specifically asked to generate a pie chart.",
        # Function parameters are specified in OpenAPI JSON schema format
        parameters={
            "type": "object",
            "properties": {"dataDescription": {"type": "string", "description": "A description of the data for which the pie chart is to be generated. For example, \"top 5 employees\", \"sales by region\", etc."}},
        },
    )

    get_results_from_query = FunctionDeclaration(
        name="get_results_from_query",
        description="Get the results of a query from BigQuery. Used when the prompt doesnt specify to make a chart or dataframe, only a data description like 'names of the top 5 employees' or 'percentage of customers from distinct locations'.",
        # Function parameters are specified in OpenAPI JSON schema format
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Query description"}},
        },
    )
    # Define a tool that includes the above functions
    user_tools = Tool(
        function_declarations=[
            generate_pie_chart,
            get_results_from_query
        ],
    )

    # Initialize Gemini model
    model = GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=GenerationConfig(temperature=0),
        tools=[user_tools],
    )

    # Start a chat session
    chat = model.start_chat()

    # Send a prompt for the second conversation turn that should invoke the get_store_location function
    response = chat.send_message(
        prompt
    )

    # print(response)
    # api_response = None
    # try:
    function_call = response.candidates[0].function_calls[0]
    response = check_function_call(function_call)
    print(type(response))
    return response
# except:
#     print("No function calls!")
# # print(function_call)

# # # Return the API response to Gemini, so it can generate a model response or request another function call
# # if api_response:
# #     response = chat.send_message(
# #         Part.from_function_response(
# #             name=function_call.name,
# #             response={
# #                 "content": api_response,
# #             },
# #         ),
# #     )

# # Extract the text from the model response
    print(response.text)

