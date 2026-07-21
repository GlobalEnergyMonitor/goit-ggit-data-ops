import pandas
import numpy
import pygsheets
import geopandas
import shapely

import dash
import plotly.express as px
#import jupyter_dash
import dash_bootstrap_components as dbc

gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')

# ****************************************
# set up keys, colors, columns for things
# ****************************************
gas_pipelines_key = '1t5jjXU3URGxNnTyeaC3Om8QDtQg_W-J9xd9mcuAHG04'
lng_terminals_key = '167f4FQl_QpZ0Qesv5-jPUk97-MSBhUPhx85BKxU0o3I'
gas_plants_key = '1w8AAF7L6EUTYxbuONU9oVwtyNTJm6lSJt7TbrsgxKbY'
gas_extraction_key = '10yXq6IF6xNY4fzHu_S9gTwtq8_m_U6Fd0UMjrF5JdJc'

pipeline_colors = 'greens'
pipeline_colors_map = px.colors.sequential.Greens
terminal_colors_import = 'reds'
terminal_import_colors_map = px.colors.sequential.Reds
terminal_colors_export = 'oranges'
terminal_export_colors_map = px.colors.sequential.Oranges
gas_plant_colors = 'purples'
gas_plant_colors_map = px.colors.sequential.Purples
gas_extraction_colors = 'blues'
gas_extraction_colors_map = px.colors.sequential.Blues

columns_gas_extraction = ['Pre-Production (discovered + in development) ']
columns_pipelines = ['Proposed','Construction']
columns_terminals = ['Proposed','Construction']
columns_gas_plants = ['Announced','Pre-construction','Construction']

# ****************************************
# import pipelines data
# ****************************************

spreadsheet = gc.open_by_key(gas_pipelines_key)

pipes_df_length_sum = spreadsheet.worksheet('title', 'Kilometers by country').get_as_df(start='A5')
pipes_df_length_sum.set_index('Country', inplace=True)
pipes_df_length_sum.drop('Total', inplace=True)

country_df = spreadsheet.worksheet('title', 'Country/region dictionary').get_as_df(start='A2')
country_df.set_index('Country', inplace=True)
# ****************************************
# import terminals data
# ****************************************

spreadsheet = gc.open_by_key(lng_terminals_key)

terms_df_import_capacity_sum = spreadsheet.worksheet('title', 'LNG import capacity by country').get_as_df(start='A5')
terms_df_export_capacity_sum = spreadsheet.worksheet('title', 'LNG export capacity by country').get_as_df(start='A5')

terms_df_import_capacity_sum.set_index('Country', inplace=True)
terms_df_export_capacity_sum.set_index('Country', inplace=True)

terms_df_import_capacity_sum.drop('Total', inplace=True)
terms_df_export_capacity_sum.drop('Total', inplace=True)

# ****************************************
# import gas plants data
# ****************************************

spreadsheet = gc.open_by_key(gas_plants_key)

gas_plants_df_capacity_sum = spreadsheet.worksheet('title', 'Gas plants by country (MW)').get_as_df(start='A5')
gas_plants_df_capacity_sum.set_index('Country', inplace=True)
gas_plants_df_capacity_sum.replace('',0,inplace=True)
gas_plants_df_capacity_sum.drop('Total', inplace=True)

# ****************************************
# import gas extraction data
# ****************************************

spreadsheet = gc.open_by_key(gas_extraction_key)

gas_extraction_df_reserves_sum = spreadsheet.worksheet('title', 'Gas Reserves by Country').get_as_df(start='A5')
gas_extraction_df_reserves_sum.drop(0, inplace=True) # remove units row
gas_extraction_df_reserves_sum.replace('--',numpy.nan,inplace=True)
gas_extraction_df_reserves_sum.dropna(subset=['Pre-Production (discovered + in development) '], inplace=True)
gas_extraction_df_reserves_sum.set_index('Country', inplace=True)
# drop all rows including/after Total row
n_rows_to_drop = gas_extraction_df_reserves_sum.shape[0]-gas_extraction_df_reserves_sum.index.get_loc('Total')
gas_extraction_df_reserves_sum.drop(gas_extraction_df_reserves_sum.tail(n_rows_to_drop).index, inplace=True)

def fig_length(df):

    df = df.loc[~(df[columns_pipelines]==0).all(axis=1)]
    
    pipes_df_length_sum = df.copy()

    pipes_df_length_sum.replace(numpy.nan,0,inplace=True)

    # reorder for descending values
    country_order = pipes_df_length_sum[['Proposed','Construction']].sum(axis=1).sort_values(ascending=True).index
    pipes_df_length_sum = pipes_df_length_sum.reindex(country_order)

    # ****************************************

    colorscale_touse = pipeline_colors

    bar_dark = px.colors.sample_colorscale(colorscale_touse, 0.9)
    bar_light = px.colors.sample_colorscale(colorscale_touse, 0.6)

    nbars = pipes_df_length_sum.index.size

    fig = px.bar(pipes_df_length_sum[['Construction','Proposed']], 
                 color_discrete_sequence=bar_dark+bar_light, 
                 orientation='h', height=10,
                 title='Km of planned gas pipelines')

    fig.update_layout(
        font_family='Helvetica',
        font_color=px.colors.sample_colorscale('greys', 0.5)[0],
        bargap=0.5, 
        plot_bgcolor='white',
        paper_bgcolor='white',

        yaxis_title='',
        xaxis_title='km',
        xaxis={'side':'top'},
        title_y=.97,
        title_yanchor='top',
        title={'x':0.5, 'xanchor': 'center'},

        legend_title='Click to toggle on/off',
        legend=dict(yanchor="bottom",y=.01,xanchor="right",x=.95),#,bgcolor='rgba(0,0,0,0)'),
    
        margin=dict(l=0, r=0),
    )
    
    fig.update_layout(barmode='stack', bargap=0.333)#, bargroupgap=0.0)

    fig.update_yaxes(
        dtick=1
    )

    fig.update_xaxes(
        gridcolor=px.colors.sample_colorscale('greys', 0.25)[0]
    )
    
    return(fig)

def fig_import_capacity(df):
    
    df = df.loc[~(df[columns_terminals]==0).all(axis=1)]
    
    terms_df_capacity_sum = df.copy()

    # reorder for descending values
    country_order = terms_df_capacity_sum[['Proposed','Construction']].sum(axis=1).sort_values(ascending=True).index
    terms_df_capacity_sum = terms_df_capacity_sum.reindex(country_order)

    # ****************************************

    colorscale_touse = terminal_colors_import

    bar_dark = px.colors.sample_colorscale(colorscale_touse, 0.9)
    bar_light = px.colors.sample_colorscale(colorscale_touse, 0.6)

    nbars = terms_df_capacity_sum.index.size

    fig = px.bar(terms_df_capacity_sum[['Construction','Proposed']], 
                 color_discrete_sequence=bar_dark+bar_light, 
                 orientation='h',
                 title='Capacity of planned LNG import terminals')

    fig.update_layout(
        font_family='Helvetica',
        font_color=px.colors.sample_colorscale('greys', 0.5)[0],
        bargap=0.25,
        plot_bgcolor='white',
        paper_bgcolor='white',

        yaxis_title='',
        xaxis_title='bcm/y',
        xaxis={'side':'top'},
        title_y=.97,
        title_yanchor='top',
        title={'x':0.5, 'xanchor': 'center'},

        legend_title='Click to toggle on/off',
        legend=dict(yanchor="bottom",y=.01,xanchor="right",x=.95),#,bgcolor='rgba(0,0,0,0)'),
    
        margin=dict(l=0, r=0),
    )

    fig.update_yaxes(
        dtick=1
    )

    fig.update_xaxes(
        gridcolor=px.colors.sample_colorscale('greys', 0.25)[0]
    )
    
    return(fig)

def fig_export_capacity(df):
    
    df = df.loc[~(df[columns_terminals]==0).all(axis=1)]
    
    terms_df_capacity_sum = df.copy()

    # reorder for descending values
    country_order = terms_df_capacity_sum[['Proposed','Construction']].sum(axis=1).sort_values(ascending=True).index
    terms_df_capacity_sum = terms_df_capacity_sum.reindex(country_order)

    # ****************************************

    colorscale_touse = terminal_colors_export

    bar_dark = px.colors.sample_colorscale(colorscale_touse, 0.9)
    bar_light = px.colors.sample_colorscale(colorscale_touse, 0.6)

    nbars = terms_df_capacity_sum.index.size

    fig = px.bar(terms_df_capacity_sum[['Construction','Proposed']], 
                 color_discrete_sequence=bar_dark+bar_light, 
                 orientation='h',
                 title='Capacity of planned LNG export terminals')

    fig.update_layout(
        font_family='Helvetica',
        font_color=px.colors.sample_colorscale('greys', 0.5)[0],
        bargap=0.25,
        plot_bgcolor='white',
        paper_bgcolor='white',

        yaxis_title='',
        xaxis_title='bcm/y',
        xaxis={'side':'top'},
        title_y=.97,
        title_yanchor='top',
        title={'x':0.5, 'xanchor': 'center'},

        legend_title='Click to toggle on/off',
        legend=dict(yanchor="bottom",y=.01,xanchor="right",x=.95),#,bgcolor='rgba(0,0,0,0)'),
    
        margin=dict(l=0, r=0),
    )

    fig.update_yaxes(
        dtick=1
    )

    fig.update_xaxes(
        gridcolor=px.colors.sample_colorscale('greys', 0.25)[0]
    )
    
    return(fig)

def fig_gas_plants_capacity(df):

    df = df.loc[~(df[columns_gas_plants]==0).all(axis=1)]
    
    gas_plants_df_capacity_sum = df.copy()

    # reorder for descending values
    country_order = gas_plants_df_capacity_sum[['Announced', 'Pre-construction', 'Construction']].sum(axis=1).sort_values(ascending=True).index
    gas_plants_df_capacity_sum = gas_plants_df_capacity_sum.reindex(country_order)

    # ****************************************

    colorscale_touse = gas_plant_colors

    bar_dark = px.colors.sample_colorscale(colorscale_touse, 0.9)
    bar_med = px.colors.sample_colorscale(colorscale_touse, 0.6)
    bar_light = px.colors.sample_colorscale(colorscale_touse, 0.3)

    nbars = gas_plants_df_capacity_sum.index.size

    fig = px.bar(gas_plants_df_capacity_sum[['Construction','Pre-construction','Announced']], 
                 color_discrete_sequence=bar_dark+bar_med+bar_light, 
                 orientation='h',
                 title='Capacity of planned gas-fired power plants')

    fig.update_layout(
        font_family='Helvetica',
        font_color=px.colors.sample_colorscale('greys', 0.5)[0],
        bargap=0.25,
        plot_bgcolor='white',
        paper_bgcolor='white',

        yaxis_title='',
        xaxis_title='MW',
        xaxis={'side':'top'},
        title_y=.97,
        title_yanchor='top',
        title={'x':0.5, 'xanchor': 'center'},

        legend_title='Click to toggle on/off',
        legend=dict(yanchor="bottom",y=.01,xanchor="right",x=.95),#,bgcolor='rgba(0,0,0,0)'),
    
        margin=dict(l=0, r=0),
    )

    fig.update_yaxes(
        dtick=1
    )

    fig.update_xaxes(
        gridcolor=px.colors.sample_colorscale('greys', 0.25)[0]
    )

    return(fig)

def fig_gas_extraction(df):
    
    # different from the rest, only plotting ONE color/status
    # and already has zero countries eliminated

    df = df.loc[~(df[columns_gas_extraction]==0).all(axis=1)]
    
    gas_extraction_df_reserves_sum = df.copy()

    # reorder for descending values
    country_order = gas_extraction_df_reserves_sum[['Pre-Production (discovered + in development) ']].sum(axis=1).sort_values(ascending=True).index
    gas_extraction_df_reserves_sum = gas_extraction_df_reserves_sum.reindex(country_order)
    
    # ****************************************

    colorscale_touse = gas_extraction_colors

    bar_dark = px.colors.sample_colorscale(colorscale_touse, 0.8)
    #bar_light = px.colors.sample_colorscale(colorscale_touse, 0.6)

    nbars = gas_extraction_df_reserves_sum.index.size

    fig = px.bar(gas_extraction_df_reserves_sum,
                 x='Pre-Production (discovered + in development) ',
                 y=gas_extraction_df_reserves_sum.index,
                 color_discrete_sequence=bar_dark,#+bar_light, 
                 orientation='h',
                 title='Volume of gas reserves')

    fig.update_layout(
        font_family='Helvetica',
        font_color=px.colors.sample_colorscale('greys', 0.5)[0],
        bargap=0.25,
        plot_bgcolor='white',
        paper_bgcolor='white',

        yaxis_title='',
        xaxis_title='bcm',
        xaxis={'side':'top'},
        title_y=.97,
        title_yanchor='top',
        title={'x':0.5, 'xanchor': 'center'},

        legend_title='Click to toggle on/off',
        legend=dict(yanchor="bottom",y=.01,xanchor="right",x=.95),#,bgcolor='rgba(0,0,0,0)'),
    
        margin=dict(l=0, r=0),
    )

    fig.update_yaxes(
        dtick=1
    )

    fig.update_xaxes(
        gridcolor=px.colors.sample_colorscale('greys', 0.25)[0]
    )

    return(fig)

def fig_map(df,
            plot_column,
            plot_units_long,
            plot_units_short,
            plot_title,
            map_colors):

    # create cloropleth info
    df = df.copy()

    # add ISO Code for interaction with nat earth data
    # here we're adding all countries even if they're all zeros
    df['ISOCode'] = ''
    for idx,row in country_df.loc[country_df.AfricaGasTracker=='Yes'].iterrows():#df.iterrows():
        df.loc[idx,'ISOCode'] = country_df.loc[row.name,'CountryISO3166-1alpha-3']
    df.replace(numpy.nan,0,inplace=True)

    fig = px.choropleth(df,
                        locations=df['ISOCode'],
                        color=plot_column, color_continuous_scale=map_colors)
    
    note = plot_title
    fig.add_annotation(x=0.5, y=1.1,
                       xref='x domain',
                       yref='y domain',
                       text=note,
                       showarrow=False,
                       align='center',
                       font=dict(size=16))

    fig.update_geos(
        resolution=50,
        showcoastlines=False,
        landcolor=px.colors.sample_colorscale('greys', 1e-5)[0],

        showocean=True,
        oceancolor=px.colors.sample_colorscale('blues', 0.05)[0],

        showlakes=True,
        lakecolor=px.colors.sample_colorscale('blues', 0.05)[0],
        
        projection_type='azimuthal equal area',
        center=dict(lat=1, lon=15),
        projection_rotation=dict(lon=30),
        projection_scale=2.75)
    
    fig.update_layout(
        font_family='Helvetica',
        font_color=px.colors.sample_colorscale('greys', 0.5)[0],
        plot_bgcolor='white',
        paper_bgcolor='white',

        yaxis_title='',
        xaxis_title=plot_units_short,
        #title_y=.97,
        title_yanchor='top',
        dragmode=False,
    
        margin=dict(l=0, r=0),)

        #coloraxis_colorbar_x=1.01)
    
    fig.update_coloraxes(
        colorbar=dict(thickness=15, title={'side':'right','text':plot_units_short}))
    
    fig.update_traces(
        selector=dict(type='choropleth'))
    
    return(fig)

# ****************************************
# dashboard details with tab
# ****************************************

external_stylesheets = [dbc.themes.BOOTSTRAP,
                        #'assets/typography.css'
                       ]
app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets,
               )
app.title = "Africa Gas Tracker dashboard"
server = app.server

# ******************************
# create graphs of charts
# use dcc.Graph to create these

import_capacity_figure = dash.dcc.Graph(id='fig_import_capacity_id', 
                                        config={'displayModeBar':False},
                                        figure=fig_import_capacity(terms_df_import_capacity_sum),
                                        className='h-100')

export_capacity_figure = dash.dcc.Graph(id='fig_export_capacity_id', 
                                        config={'displayModeBar':False},
                                        figure=fig_export_capacity(terms_df_export_capacity_sum),
                                        className='h-100')

length_figure = dash.dcc.Graph(id='fig_length_id', 
                               config={'displayModeBar':False},
                               figure=fig_length(pipes_df_length_sum),
                               className='h-100')

gogpt_capacity_figure = dash.dcc.Graph(id='fig_gogpt_capacity_id',
                                       config={'displayModeBar':False},
                                       figure=fig_gas_plants_capacity(gas_plants_df_capacity_sum),
                                       className='h-100')
goget_volume_figure = dash.dcc.Graph(id='fig_goget_volume_id',
                                     config={'displayModeBar':False},
                                     figure=fig_gas_extraction(gas_extraction_df_reserves_sum),
                                     className='h-100')

# fid_figure = dash.dcc.Graph(id='fig_fid_id', 
#                                config={'displayModeBar':False},
#                                figure=fig_fid(),
#                             className='h-100')
# year_counts_figure = dash.dcc.Graph(id='fig_year_counts_id',
#                               config={'displayModeBar':False},
#                               figure=fig_year_counts(),
#                                     className='h-100')

# import capacity figure
fig = fig_map(df=terms_df_import_capacity_sum,
              plot_column='In Development (Proposed + Construction)',
              plot_units_long = 'Capacity (bcm/y)',
              plot_units_short = 'bcm/y',
              plot_title = 'Capacity of planned LNG import terminals',
              map_colors = terminal_import_colors_map)

map_import_capacity_figure = dash.dcc.Graph(id='fig_import_capacity_map_id',
                                            config={'displayModeBar':False},
                                            figure=fig,
                                            className='h-100')

# export capacity map
fig = fig_map(df=terms_df_export_capacity_sum,
              plot_column='In Development (Proposed + Construction)',
              plot_units_long = 'Capacity (bcm/y)',
              plot_units_short = 'bcm/y',
              plot_title = 'Capacity of planned LNG export terminals',
              map_colors = terminal_export_colors_map)

map_export_capacity_figure = dash.dcc.Graph(id='fig_export_capacity_map_id',
                                            config={'displayModeBar':False},
                                            figure=fig,
                                            className='h-100')

# pipeline length map
fig = fig_map(df=pipes_df_length_sum,
              plot_column='In Development (Proposed + Construction)',
              plot_units_long = 'Length (km)',
              plot_units_short = 'km',
              plot_title = 'Planned gas pipeline length',
              map_colors = pipeline_colors_map)

map_kilometers_figure = dash.dcc.Graph(id='fig_kilometers_map_id',
                                       config={'displayModeBar':False},
                                       figure=fig,
                                       className='h-100')

# gas extraction reserves map
fig = fig_map(df=gas_extraction_df_reserves_sum,
              plot_column='Pre-Production (discovered + in development) ',
              plot_units_long = 'bcm',
              plot_units_short = 'bcm',
              plot_title = 'Volume of gas reserves',
              map_colors = gas_extraction_colors_map)

map_goget_volume_figure = dash.dcc.Graph(id='fig_goget_volume_map_id',
                                         config={'displayModeBar':False},
                                         figure=fig,
                                         className='h-100')

# gas plants map
fig = fig_map(df=gas_plants_df_capacity_sum,
              plot_column='In Development (Announced + Pre-construction + Construction)',
              plot_units_long = 'Capacity (MW)',
              plot_units_short = 'MW',
              plot_title = 'Capacity of planned gas-fired power plants',
              map_colors = gas_plant_colors_map)

map_gogpt_capacity_figure = dash.dcc.Graph(id='fig_gogpt_capacity_map_id',
                                           config={'displayModeBar':False},
                                           figure=fig,
                                           className='h-100')


# ******************************
# define layout tabs etc.

tab_import_terminals_content = dbc.Container(fluid=True, 
                                             children=[
                                                 dbc.Row([
                                                     dbc.Col(map_import_capacity_figure, 
                                                             align='start', 
                                                             lg=6, 
                                                             md=12),
                                                 ], 
                                                     justify='center'),
                                                 dbc.Row([
                                                     dbc.Col(import_capacity_figure, 
                                                             align='start', 
                                                             lg=5, 
                                                             md=12,)
                                                             #style={'height':'800px'}),
                                                 ], 
                                                     justify='center'),
                                             ])

tab_export_terminals_content = dbc.Container(fluid=True, 
                                             children=[
                                                 dbc.Row([
                                                     dbc.Col(map_export_capacity_figure, 
                                                             align='start', 
                                                             lg=6, 
                                                             md=12),
                                                 ], 
                                                     justify='center'),
                                                 dbc.Row([
                                                     dbc.Col(export_capacity_figure, 
                                                             align='start', 
                                                             lg=5, 
                                                             md=12,)
                                                             #style={'height':'800px'}),
                                                 ], 
                                                     justify='center'),
                                             ])

tab_pipelines_content = dbc.Container(fluid=True, 
                                      children=[
                                          dbc.Row([
                                              dbc.Col(map_kilometers_figure, 
                                                      align='start', 
                                                      lg=6, 
                                                      md=12),
                                          ], 
                                              justify='center'),
                                          dbc.Row([
                                              dbc.Col(length_figure, 
                                                      align='start', 
                                                      lg=5, 
                                                      md=12,
                                                      style={'height':'800px'}),
                                          ], 
                                              justify='center'),
                                      ])

tab_goget_content = dbc.Container(fluid=True, 
                                  children=[
                                      dbc.Row([
                                          dbc.Col(map_goget_volume_figure, 
                                                  align='start', 
                                                  lg=6, 
                                                  md=12),
                                      ], 
                                          justify='center'),
                                      dbc.Row([
                                          dbc.Col(goget_volume_figure, 
                                                  align='start', 
                                                  lg=5, 
                                                  md=12,)
                                          #style={'height':'800px'}),
                                      ], 
                                          justify='center'),
                                  ])

tab_gogpt_content = dbc.Container(fluid=True, 
                                  children=[
                                      dbc.Row([
                                          dbc.Col(map_gogpt_capacity_figure, 
                                                  align='start', 
                                                  lg=6, 
                                                  md=12),
                                      ], 
                                          justify='center'),
                                      dbc.Row([
                                          dbc.Col(gogpt_capacity_figure, 
                                                  align='start', 
                                                  lg=5, 
                                                  md=12,
                                                  style={'height':'800px'}),
                                      ], 
                                          justify='center'),
                                  ])

# put all the tabs together
tabs = dbc.Tabs([
    dbc.Tab(tab_import_terminals_content, label="LNG import terminals",
            label_style={"color": "#002b36"},
            active_label_style={"color": "#839496"}),
    
    dbc.Tab(tab_export_terminals_content, label="LNG export terminals",
            label_style={"color": "#002b36"},
            active_label_style={"color": "#839496"}),
    
    dbc.Tab(tab_pipelines_content, label="Gas pipelines",
            label_style={"color": "#002b36"},
            active_label_style={"color": "#839496"}),
    
    dbc.Tab(tab_goget_content, label="Gas extraction areas",
            label_style={"color": "#002b36"},
            active_label_style={"color": "#839496"}),
    
    dbc.Tab(tab_gogpt_content, label="Gas-fired power plants",
            label_style={"color": "#002b36"},
            active_label_style={"color": "#839496"}),
])

# fluid=True means it will fill horiz space and resize
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
app.layout = dbc.Container([
    tabs,
],
    fluid=True)

if __name__ == '__main__':
    app.run_server()
