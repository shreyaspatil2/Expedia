def azure_database():

    import streamlit as st
    import pypyodbc as odbc
    import pyodbc
    import pandas as pd
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

    #connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:quickazuredemo.database.windows.net,1433;Database=quickinsight;Uid=bhaskar;Pwd=Affine@123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    #connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:quickazuredemo.database.windows.net,1433;Database=quickinsight;Uid=bhaskar;Pwd=Affine@123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    #conn = odbc.connect(connection_string)

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";PWD="
        + st.secrets["password"]
    )
    cursor = conn.cursor()

    number_of_tables = 0
    flag = False

    # with st.sidebar:
    database = st.sidebar.selectbox("Select Database Name:", [
        "Select", "quickinsight"], index=0)

    if database != "Select":

        table_query = """select t.name as table_name from sys.tables t order by table_name;"""

        query_job1 = cursor.execute(table_query)
        table_list = []
        for table in query_job1:
            table_list.append(table[0])
        selected_tables = st.sidebar.multiselect('Select Tables:', table_list)

        pre_prompt = '''SQL tables with their properties:'''

        if "button_clicked" not in st.session_state:
            st.session_state.button_clicked = False

        def callbacks():
            # Button was clicked
            st.session_state.button_clicked = True

        if (st.sidebar.button("Load the files", on_click=callbacks) or st.session_state.button_clicked):

            if selected_tables:

                for i in range(len(selected_tables)):
                    number_of_tables += 1

                    table = selected_tables[i].replace("'", "")

                    query_job2 = cursor.execute(f'''SELECT column_name, data_type
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE table_name = '{table}' ''')


                    df2 = query_job2.fetchall()
                    df2 = [tuple(i) for i in df2]
                    column_df = pd.DataFrame(df2)
                    column_df.columns = [x[0] for x in query_job2.description]

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

                            five_rows_query = 'select top 10 * from ' + \
                                table + ' ORDER BY newid()'
                            # five_rows_query = 'select * from ' + \
                            #     table + ' TABLESAMPLE (20 ROWS)'

                            # SELECT column FROM table ORDER BY RAND ( ) LIMIT 10

                            query_job_5_rows = cursor.execute(
                                five_rows_query)
                            
                            dataframe_five_rows = query_job_5_rows.fetchall()
                            dataframe_five_rows = [tuple(i) for i in dataframe_five_rows]
                            dataframe_five_rows = pd.DataFrame(dataframe_five_rows)
                            dataframe_five_rows.columns = [x[0] for x in query_job_5_rows.description]
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

                        p1 = 'sql table with there columns--'
                        for table in selected_tables:

                            p1 += table+" : "

                            one_rows_query = 'select top 1 * from ' + table

                            query_job_1_rows = cursor.execute(
                                one_rows_query)

                            fetched = query_job_1_rows.fetchall()

                            fetched = [tuple(i) for i in fetched]

                            dataframe_five_rows = pd.DataFrame(fetched)

                            col_name = [x[0]
                                        for x in query_job_1_rows.description]

                            p1 += ','.join(col_name) + " ] \n, "

                        p2 = p1+'\n#create a sql query named sql_query to join given dataframe'

                        for i in range(len(selected_tables)):
                            if len(selected_tables) > 1:
                                table = selected_tables[i]
                                prefix = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                                          "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
                                p2 += " use "+table + \
                                    " table as "+prefix[i]+" and"

                        # user_prompt = st.text_input(
                        #     "Any instruction or comments (Optional):", key="sql_prompt")
                        # user_prompt = user_prompt + " "
                        user_prompt = " "
                        if user_prompt:
                            with st.spinner('Wait for it ...'):

                                final_prompt = p2+user_prompt+". provide the query enclose in '{}'\n"

                                completion = openai.ChatCompletion.create(
                                    engine="gpt4-8k",
                                    temperature=0,
                                    messages=[{'role': 'system', 'content': 'You are expert in sql query and will give the query to join multiple table based on the columns names provided for each table'},
                                              {"role": "user", "content": final_prompt}])

                                text = completion["choices"][0]["message"]['content']
                                # st.text('Join tables sql query')
                                # st.text(completion['usage'])

                                sql_query = text
                                print(
                                    '#####################sql_query####################################')
                                print(sql_query)
                                # st.write(sql_query)

                        flag = True

                    if flag:

                        question_prompt = st.text_input(
                            "Ask Question:", key="question_prompt")

                        col1, col2, col3 = st.columns(3)

                        plot_submit = col1.form_submit_button(
                            "Generate Insights", on_click=callbacks)

                        show_code = col2.checkbox('Show the code')
                        explain_code = col3.checkbox('Explain the code')

                        if plot_submit:

                            with st.spinner('Wait for it...Generating the insight and plots...'):

                                pre_prompt_gpt = pre_prompt+"""\nGive relevant insights from this table based on the following question :"""+question_prompt +\
                                    """If the question is not relevant to the table provided give output as "Irrelenat question".give output in the form of dictionary where key will be name of the insight and values will be the sql query to fetch data from azure sql database.
                                give proper name to the column in sql query. give the query in triple quotes. do not give google bigquery. following is a sample from actual dataset for your referene : \n""" + dataframe_five_rows.to_csv(index=False)
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
                                        v = v.replace('quickinsight.', '')
                                        query_job = cursor.execute(v)

                                        insight_fetch = query_job.fetchall()
                                        insight_fetch = [tuple(i) for i in insight_fetch]

                                        insight_df = pd.DataFrame(insight_fetch)
                                        
                                        insight_df.columns = [
                                            x[0] for x in query_job.description]

                                        print(
                                            '***********************************q_to_df***********************************')
                                        print(insight_df)
                                        if not insight_df.empty:

                                            try:
                                                st.markdown(
                                                    f"### <u>**{(k).replace('_',' ').title()}**</u>", unsafe_allow_html=True)

                                                if show_code:

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

                                            except openai.error.InvalidRequestError as r:
                                                st.text(r)
                                                print(
                                                    'Relevant data exceeded token limit')
                                                st.markdown(
                                                    f"### **Relevant data exceeded token limit**", unsafe_allow_html=True)
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
            #################################################################
    cursor.close()
    conn.close()
