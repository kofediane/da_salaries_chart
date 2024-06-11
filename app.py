#импортируем библиотеки
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd
import plotly.express as px
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os 
import glob

#считываем данные
path = os.getcwd() 
csv_files = glob.glob(os.path.join(path, '*.csv')) 

for f in csv_files: 
    df = pd.read_csv(f)

data = df[((df['job_title'] == 'Data Analyst') | (df['job_title'] == 'Data Scientist') | (df['job_title'] == 'Data Engineer'))&
            (df['work_year'].isin([2020,2021,2022,2023]))]
data['month_salary'] = round(data['salary_in_usd']/12)
bar_graph_df = data.groupby(['experience_level', 'job_title'], as_index = False)['month_salary'].mean().round().sort_values(by = 'month_salary')

#Создаем приложение для дэшборда
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#настройки дизайна и внешнего вида
graphs_template = go.layout.Template(
    layout = dict(font = dict(family = 'Times New Roman', size = 14),
        legend = dict(
            orientation = 'h', 
            title_text = '',
            x = 0,
            y = 1.1
        )
    )
)

color_values = ['#EEC6F8', '#D86BF3', '#8E1AAA']


#фильтры для графиков
filter_country= dcc.Dropdown(
                data['company_location'].unique(),
                id = 'dropdown_country',
                value = 'United States',
                multi = False)

filter_job = dcc.Dropdown(
                data['job_title'].unique(),
                id = 'dropdown_job',
                value = 'Data Scientist',
                multi = False)

tbl = dash_table.DataTable(data = data.head(20).to_dict('records'), 
                           columns = [{'name': i, 'id': i} for i in data], 
                           style_data = {'width': '100px',
                                        'maxWidth':'100px', 
                                        'minWidth':'100px'},
                            style_header= {'textAlign':'center'})

#содержание вкладок

#первая вкладка
tab1_content = [dbc.Row([
        dbc.Col([html.H4('Страна'), html.Div(filter_country)]),
        dbc.Col([html.H4('Специальность'), html.Div(filter_job)])], style = {'margin-bottom': 30}),
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph1')),
        dbc.Col(dcc.Graph(id='graph2')),
        dbc.Col(dcc.Graph(id='graph3'))
        ]),
    dbc.Row([
        dbc.Col([html.H6('Динамика размера оклада по годам'), dcc.Graph(id='graph4')]),
        dbc.Col([html.H6('Сравнение зарплат по уровням'), dcc.Graph(id='graph5')])
    ])
]

#вторая вкладка
tab2_content = dbc.Row([html.H4('Таблица с данными', style = {'margin-bottom': 30}), html.Div(tbl)])

#третья вкладка
table_header = [
    html.Thead(html.Tr([html.Th('Имя колонки'), html.Th('Содержание')]))
]
dict_explain = {'work_year':'Год сбора данных',
                'job_title':'Название конкретной должности. Поле необходио для понимания разброса зарплат разных специальностей в области работы с данными',
                'job_category':'Более расширенное обозначение специализации в области работы с данными',
                'salary_currency':'Валюта, в которой происходит выплаты зарплаты',
                'salary':'Годовой доход до вычета налогов в местной валюте',
                'salary_in_usd':'Годовой доход до вычета налогов сконвертированный в доллары США',
                'employee_residence':'Страна проживания специалиста',
                'experience_level':'Уровень экспертизы. Включает категории "Джун", "Мидл","Синиор" и "Руководитель"',
                'employment_type':'Типы занятости: "Полный рабочий день", "Частиная занятость", "Проектная занятость" и т.д.',
                'work_setting':'График работы: "удаленка", "гибрид" или "офис"',
                'company_location':'Страна расположения компании',
                'company_size':'Размер компании: маленькая(S), средняя(M), крупная(L)'}

table_rows = []
for i in dict_explain:
    table_rows.append(html.Tr([html.Td(i), html.Td(dict_explain[i])]))
table_body = [html.Tbody(table_rows)]
table = dbc.Table(table_header + table_body, bordered=True)

text_for_tab3 = 'Данные были взяты с сайта Kaggle'
tab3_content = [dbc.Row(html.A(text_for_tab3, href = 'https://www.kaggle.com/datasets/hummaamqaasim/jobs-in-data'), style = {'margin-bottom': 30}),
                dbc.Row(html.Div(children = table), style = {'margin-bottom': 30})]

#приложение
app.layout = html.Div([

    dbc.Row(html.H1(children = 'Данные зарплат специалистов в сфере работы с данными 🧑‍💻'), style = {'margin-bottom': 20}),
    dbc.Row(html.H4(children = 'Сравнительный анализ зарплат дата-специалистов из разных стран'), style = {'margin-bottom': 20}),
    dbc.Tabs([dbc.Tab(tab1_content, label = 'Графики'), 
              dbc.Tab(tab2_content, label = 'Данные'),
              dbc.Tab(tab3_content, label = 'Состав данных')],
                style = {'margin-bottom': 30})
])

#Настраиваем коллбэк по всем фильтрам для первого графика
@callback(
    Output(component_id = 'graph1', component_property = 'figure'),
    Input(component_id = 'dropdown_country', component_property = 'value'),
    Input(component_id = 'dropdown_job', component_property = 'value')
)

def update_fig1_chart(country, job_title):
    final_df = data[(data['company_location'] == country) & (data['job_title'] == job_title)]
    min_salary = final_df['month_salary'].min()
    figure = go.Figure(go.Indicator(mode = 'number', value = min_salary, title = {'text': 'Минимум'}, 
                                    number = {'font_color':'#8E1AAA', 'font_size':100}))
    figure.update_layout(template = graphs_template)

    return figure

#Настраиваем коллбэк по всем фильтрам для второго графика
@callback(
    Output(component_id = 'graph2', component_property = 'figure'),
    Input(component_id = 'dropdown_country', component_property = 'value'),
    Input(component_id = 'dropdown_job', component_property = 'value')
)

def update_fig2_chart(country, job_title):
    final_df = data[(data['company_location'] == country) & (data['job_title'] == job_title)]
    mean_salary = final_df['month_salary'].mean()
    figure = go.Figure(go.Indicator(mode = 'number', value = mean_salary, title = {'text': 'Средняя зарплата'},
                                    number = {'font_color':'#8E1AAA', 'font_size':100}))
    figure.update_layout(template = graphs_template)

    return figure

#Настраиваем коллбэк по всем фильтрам для третьго графика
@callback(
    Output(component_id = 'graph3', component_property = 'figure'),
    Input(component_id = 'dropdown_country', component_property = 'value'),
    Input(component_id = 'dropdown_job', component_property = 'value')
)

def update_fig3_chart(country, job_title):
    final_df = data[(data['company_location'] == country) & (data['job_title'] == job_title)]
    max_salary = final_df['month_salary'].max()
    figure = go.Figure(go.Indicator(mode = 'number', value = max_salary, title = {'text': 'Максимум'},
                                    number = {'font_color':'#8E1AAA', 'font_size':100}))
    figure.update_layout(template = graphs_template)

    return figure


#Настраиваем коллбэк по всем фильтрам для четвертого графика
@callback(
    Output(component_id = 'graph4', component_property = 'figure'),
    Input(component_id = 'dropdown_country', component_property = 'value'),
    Input(component_id = 'dropdown_job', component_property = 'value')
)

def update_fig4_chart(country, job_title):
    final_df = data[(data['company_location'] == country) & (data['job_title'] == job_title)].groupby('work_year', as_index = False).agg({'salary_in_usd':'mean'})
    figure = px.line(final_df, x='work_year', y = 'salary_in_usd', color_discrete_sequence=color_values,
                     labels={
                     'work_year': 'Год',
                     'salary_in_usd': 'Зарплата в долларах США'
                 })
    figure.update_layout(template = graphs_template)

    return figure


#Настраиваем коллбэк по всем фильтрам для пятого графика
@callback(
    Output(component_id = 'graph5', component_property = 'figure'),
    Input(component_id = 'dropdown_country', component_property = 'value')
)

def update_fig5_chart(country):
    final_df = data[data['company_location'] == country].groupby(['experience_level', 'job_title'], as_index = False)['month_salary'].mean().round().sort_values(by = 'month_salary')
    figure = px.bar(bar_graph_df, x='experience_level', y='month_salary', color = 'job_title',  barmode='group', color_discrete_sequence=color_values,
                    labels={
                     'experience_level': 'Уровни экспертизы',
                     'month_salary': 'Зарплата в месяц',
                     'job_title':'Должность'
                 })
    figure.update_layout(template = graphs_template)

    return figure


if __name__ == '__main__':
    app.run(debug=True, port = 8051)
