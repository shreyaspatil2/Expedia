def google_cloud_storage():

    import streamlit as st
    from google.cloud import bigquery
    import time
    import openai

    from Insight import insight
    from Insight_df_summary import insight_df_summary

    endpoint = 'https://allbirds.openai.azure.com/'
    region = 'eastus'
    key = 'd67d19908eba4902af4903c270547bba'
    openai.api_key = key
    openai.api_base = endpoint
    openai.api_type = 'azure'
    openai.api_version = "2023-03-15-preview"

    client = bigquery.Client()

    number_of_tables = 0
    flag = False
    flag_download = False
    file_name = ""

    # with st.sidebar:
    database = st.sidebar.selectbox("Select Database Name:", [
        "Select", "Retail"], index=0)

    if database != "Select":
        table_query = "SELECT table_name FROM affine2." + \
            database + ".INFORMATION_SCHEMA.TABLES"

        query_job1 = client.query(table_query)
        # while query_job1.state != 'DONE':

        #     time.sleep(3)

        table_df = query_job1.to_dataframe()

        table_list = table_df["table_name"].to_list()
        # with st.sidebar:

        if "button_clicked" not in st.session_state:
            st.session_state.button_clicked = False

        if "prev_tables" not in st.session_state:
            st.session_state.prev_tables = []

        selected_tables = st.sidebar.multiselect('Select Tables:', table_list)

        if selected_tables!=st.session_state.prev_tables:
            st.session_state.button_clicked = False

            if "text" in st.session_state:
                del st.session_state.text

            if "sample_5_rows" in st.session_state:
                del st.session_state.sample_5_rows

        st.session_state.prev_tables = selected_tables.copy()

        pre_prompt = '''SQL tables with their properties:'''

        def callbacks():
            # Button was clicked
            st.session_state.button_clicked = True

        if (st.sidebar.button("Load the files", on_click=callbacks) or st.session_state.button_clicked):

            if selected_tables:

                for i in range(len(selected_tables)):
                    number_of_tables += 1

                    table = selected_tables[i].replace("'", "")
                    column_query = '''SELECT column_name, data_type
                        FROM affine2.'''+database+'''.INFORMATION_SCHEMA.COLUMNS
                        WHERE table_name = "'''+table+'''"
                        '''
                    query_job2 = client.query(column_query)
                    while query_job2.state != 'DONE':

                        time.sleep(3)

                    column_df = query_job2.to_dataframe()

                    with st.sidebar:
                        st.markdown(table)

                        st.dataframe(column_df, hide_index=True)

                    final_str = database+"."+table + \
                        str(tuple(column_df["column_name"]))
                    final_str = final_str.replace("'", "")

                    pre_prompt = pre_prompt+'''\n'''+final_str

            ############################################################
                with st.form("plot_form"):
                    if number_of_tables == 1:

                        # plot dataframe
                        with st.spinner('Wait for it ...Fetching the data...'):
                            five_rows_query = '''select * from '''+database+'''.'''+table + \
                                ''' WHERE RAND() < 30/(select count(*) from ''' + \
                                database+'''.'''+table+''') limit 10'''

                            query_job_5_rows = client.query(
                                five_rows_query)
                            dataframe_five_rows = query_job_5_rows.to_dataframe()
                            st.dataframe(dataframe_five_rows, height=220)
                            flag = True
                        ######
                        # user_prompt = st.text_input(
                        #     "Any instruction or comments (Optional):", key="sql_prompt")
                        # user_prompt = "give more weightage to following sentence. "+user_prompt
                        user_prompt = " "
                        pre_prompt = pre_prompt+user_prompt
                        ######
                    else:

                        pre_prompt = pre_prompt + \
                            '\n#create a google bigquery  named sql_query to join these table.  '
                        post_prompt = "."

                        for i in range(len(selected_tables)):
                            if len(selected_tables) > 1:
                                table = selected_tables[i].replace("'", "")
                                prefix = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                                          "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
                                post_prompt = post_prompt + " use "+database + \
                                    "."+table+" table as "+prefix[i]+" and"

                        # user_prompt = st.text_input(
                        #     "Any instruction or comments (Optional):", key="sql_prompt")
                        # user_prompt = user_prompt + " "
                        user_prompt = " "
                        if user_prompt:
                            with st.spinner('Wait for it ...'):
                                if post_prompt == ".":
                                    final_prompt = pre_prompt+user_prompt
                                else:
                                    final_prompt = pre_prompt+user_prompt+post_prompt
                                    final_prompt = final_prompt[:-4]

                                final_prompt = final_prompt+". provide the query enclose in '{}'\n"

                                if "text" not in st.session_state:
                                    completion = openai.ChatCompletion.create(
                                                    engine="gpt4-8k",
                                                    temperature=0,
                                                    messages=[{'role': 'system', 'content': 'You are expert in google bigquery and will give the query to join multiple table based on the columns names provided for each table'},
                                                            {"role": "user", "content": final_prompt}])

                                    text = completion["choices"][0]["message"]['content']
                                    st.session_state.text = text

                                # st.text('sql query for join')
                                #st.text(completion)

                                sql_query = st.session_state.text
                                print(
                                    '#####################sql_query####################################')
                                print(sql_query)
                                #st.text(sql_query)
                                sql_query = sql_query[sql_query.rfind(
                                    '{')+1:sql_query.rfind('}')]
                                #st.text(sql_query)
                                sql_query1 = sql_query+""

                                sql_query = sql_query.replace(';', '')
                                sql_query = '''select * from ('''+sql_query+ \
                                ''') WHERE RAND() < 30/(select count(*) from (''' +sql_query+''')) limit 10'''
                                #sql_query = sql_query+' limit 5;'

                                #st.text(sql_query)
#####################################
                                if "sample_5_rows" not in st.session_state:
                                    st.session_state.sample_5_rows = client.query(sql_query)
                                
                                sample_5_rows = st.session_state.sample_5_rows
                                dataframe_five_rows = sample_5_rows.to_dataframe()
                                st.markdown("Joined Data Sample")
                                st.dataframe(dataframe_five_rows, height=220)


###################################
                            pre_prompt = 'consider the columns present in table in the following sql query: '+sql_query1
                            flag = True
                    ###############################################################

                    if flag:
                        # with st.form("plot_form"):
                        question_prompt = st.text_input(
                            "Ask Question:", key="question_prompt")

                        col1, col2, col3 = st.columns(3)

                        plot_submit = col1.form_submit_button(
                            "Generate Insights", on_click=callbacks)

                        show_code = col2.checkbox('Show the code')
                        explain_code = col3.checkbox('Explain the code')
                        # st.text(pre_prompt)

                        if plot_submit:
                            start_time = time.time()
                            with st.spinner('Wait for it...Generating the insight and plots...'):

                                pre_prompt_gpt = pre_prompt+"""\nGive relevant insights from this table based on the following question :"""+question_prompt +\
                                    """If the question is not relevant to the table provided give output as "Irrelenat question".give output in the form of dictionary where key will be name of the insight and values will be the sql query for google bigquery. Give proper name to the column in sql query. give the query in triple quotes. following is a sample from actual dataset for your referene : \n""" + \
                                    dataframe_five_rows.to_csv(index=False)
                                #st.text(pre_prompt_gpt)
                                output_dic = insight(pre_prompt_gpt)
                                if output_dic:

                                    print(
                                        '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@DICTIONARY@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                                    print(output_dic)

                                    for k, v in output_dic.items():
                                        print(
                                            '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@VALUE@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                                        print(v)

                                        # st.text(k)
                                        # st.text(v)
                                        query_job = client.query(v)
                                        insight_df = query_job.to_dataframe()
                                        print(
                                            '***********************************q_to_df***********************************')
                                        print(insight_df)
                                        if not insight_df.empty:

                                            try:
                                                st.markdown(
                                                    f"### <u>**{(k).replace('_',' ').title()}**</u>", unsafe_allow_html=True)

                                                if show_code:
                                                    # st.markdown(
                                                    #     f"### <u>**{(k).replace('_',' ').title()}**</u>", unsafe_allow_html=True)

                                                    st.markdown(
                                                        f"###### **{'SQL query to fetch relevant data'}**", unsafe_allow_html=True)
                                                    st.code(
                                                        v, language='sql')

                                                if explain_code:
                                                    with st.expander(f"###### **{'See code explaination'}**"):

                                                        prompt = """Explain the following query : """+v
                                                        completion = openai.ChatCompletion.create(
                                                            engine="gpt4-8k",
                                                            temperature=0,
                                                            messages=[{'role': 'system', 'content': 'Your job is to explain the code '},
                                                                      {"role": "user", "content": prompt}])

                                                        output = completion["choices"][0]["message"]['content']
                                                        st.write(output)

                                                insight_df_summary(
                                                    k, insight_df, show_code, explain_code, question_prompt)
                                                
                                                end_time = time.time()
                                                elapsed_time = end_time - start_time
                                                #st.text(f"Time taken: {elapsed_time:.6f} seconds")

                                            except openai.error.InvalidRequestError as r:
                                                st.text(r)
                                                print(
                                                    'Relevant data exceeded token limit')
                                                st.markdown(
                                                    f"### **Relevant data exceeded token limit**", unsafe_allow_html=True)
                                                #st.markdown(
                                                #    f"You can download the filtered data by clicking on Download button below", unsafe_allow_html=True)
                                                
                                                csv_data = insight_df.to_csv(index=False)
                                                file_name = k
                                                flag_download = True
                                            except Exception as e:
                                                st.text(e)
                                                print(
                                                    'Something went wrong')
                                                st.markdown(
                                                    f"### **Something went wrong**", unsafe_allow_html=True)
                                        else:
                                            st.markdown(
                                                f"### **No data available relevent to this query**", unsafe_allow_html=True)
                                            print(
                                                '********************************EMPTY DATAFRAME************')
                                            
                if flag_download:
                    st.markdown(f"**You can download the filtered data by clicking on Download button below**", unsafe_allow_html=True)
                    st.download_button(label="Download Data", data=csv_data, file_name=file_name+'.csv', mime='text/csv')
            #################################################################
