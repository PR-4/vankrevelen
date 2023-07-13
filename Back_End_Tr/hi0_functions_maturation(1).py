import dash
import flask
from werkzeug.utils import redirect
from flask import url_for
from flask import send_file
from flask import send_from_directory
import os
import zipfile
import plotly.express as px
import re
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dash import no_update
from plotly import subplots
import plotly.graph_objs as go
from layout import dashboard as layout
from layout import guide_page, login_page, index_page, about_page
import dash_bootstrap_components as dbc
import dash_uploader as du

from functions.maturation_functions import *

import lasio
import pandas as pd
import numpy as np

def simulate_hi0(n_clicks,
                 maturation_depth,
                 s2s3_var, s2s3_constant, s2s3_check,
                 maturation_path,
                 s2s3_range,
                 hi0_select,
                 no_data,
                 eixo_x,
                 eixo_y):
    
    
    if not dash.callback_context.triggered:
        raise PreventUpdate

    active_s2s3 = False

    # Criando Dataframe:
    if active_s2s3 is False:
        if maturation_path is not None and s2s3_var is not None:
            if maturation_path is not None:
                if maturation_path[-3:] == 'csv':
                    simulations_df = pd.read_csv(maturation_path, na_values=no_data)
                if maturation_path[-3:] == 'txt':
                    simulations_df = pd.read_csv(maturation_path, sep='\t', na_values=no_data)
                if maturation_path[-3:] == 'xls':
                    simulations_df = pd.read_excel(maturation_path, sep='\t', na_values=no_data)
            simulations_df.dropna(inplace=True)
            print('Usando razão S2/S3 a partir dos dados txt, com coluna de profundidade ' + str(
                maturation_depth) + ' e variável ' + str(s2s3_var))

            simulations_df = simulations_df.loc[((simulations_df[maturation_depth] >= np.min(s2s3_range)) & (simulations_df[maturation_depth] <= np.max(s2s3_range)))]
            active_s2s3 = simulations_df[s2s3_var].dropna()
            active_s2s3_var = np.array(simulations_df[s2s3_var].dropna())

        if hi0_select == 'reftable':
            print('Calculando HI0 com :' + str(hi0_select))
            simulations_df = calculate_hi0_reftable(simulations_df, s2s3_var)

    if eixo_x == 'hi_eixox_hi' and eixo_y == 'hi_eixoy_s2s3':
        fig = subplots.make_subplots(rows=1, cols=1,
                                    shared_yaxes=True,
                                    horizontal_spacing=0)
        fig.append_trace(go.Scatter(
            x=simulations_df['Hi inicial'].dropna().values,
            y=simulations_df[maturation_depth].dropna().values,
            name='Hi inicial',
            line={'width': 0.75, 'dash': 'solid'},
        ), row=1, col=1)
        fig.update_layout(legend=dict(orientation="h",
                                    yanchor="bottom"))
        # layout do gráfico
        fig['layout']['yaxis'].update(
            title='Profundidade [m]',
            autorange='reversed'
        )
    elif eixo_x == 'hi_eixox_s2s3' and eixo_y == 'hi_eixoy_hi':
        fig = subplots.make_subplots(rows=1, cols=1,
                            shared_yaxes=True,
                            horizontal_spacing=0)
        fig.append_trace(go.Scatter(
            y=simulations_df['Hi inicial'].dropna().values,
            x=simulations_df[maturation_depth].dropna().values,
            name='Hi inicial',
            line={'width': 0.75, 'dash': 'solid'},
        ), row=1, col=1)
        fig.update_layout(legend=dict(orientation="h",
                                    yanchor="bottom"))
        # layout do gráfico
        fig['layout']['yaxis'].update(
            title='Profundidade [m]',
            autorange='reversed'
        )
    else:
        fig = subplots.make_subplots(rows=1, cols=1,
                            shared_yaxes=True,
                            horizontal_spacing=0)
        fig.append_trace(go.Scatter(
            x=simulations_df['Hi inicial'].dropna().values,
            y=simulations_df[maturation_depth].dropna().values,
            name='Hi inicial',
            line={'width': 0.75, 'dash': 'solid'},
        ), row=1, col=1)
        fig.update_layout(legend=dict(orientation="h",
                                    yanchor="bottom"))
        # layout do gráfico
        fig['layout']['yaxis'].update(
            title='Profundidade [m]',
            autorange='reversed'
        )
        
    # Salvando dataframes resultado:
    simulations_df.to_csv('static/hi0_simulation_' + str(n_clicks) + '.csv', index=False, sep=';')
    simulations_df.to_string("static/hi0_simulation_" + str(n_clicks) + ".txt", index=False)

    z = zipfile.ZipFile('static/hi0_simulation_' + str(n_clicks) + '.zip', 'w', zipfile.ZIP_DEFLATED)
    z.write('static/hi0_simulation_' + str(n_clicks) + '.txt')
    z.write('static/hi0_simulation_' + str(n_clicks) + '.csv')

    return fig

#############################################  TR  #########################################################

def simulate_tr(n_clicks, maturation_depth, s2s3_var, s2s3_constant, s2s3_check, maturation_path, hi_var, hi_constant, hi_check,
                s1_var, s1_constant, s1_check, s2_var, s2_constant, s2_check, tr_range, tr_select, hi0_select, eixo_x, eixo_y, no_data):

    if not dash.callback_context.triggered:
        raise PreventUpdate

    constantes = []

    # Criando dataframe:
    if maturation_path is not None:
        if maturation_path[-3:] == 'csv':
            simulations_df = pd.read_csv(maturation_path, na_values=no_data)
        if maturation_path[-3:] == 'txt':
            simulations_df = pd.read_csv(maturation_path, sep='\t', na_values=no_data)
        if maturation_path[-3:] == 'xls':
            simulations_df = pd.read_csv(maturation_path, na_values=no_data)

    if hi_var is None:
        get_hi = lambda row: hi_constant
        simulations_df['IH [mg HC/g COT]'] = simulations_df.apply(get_hi, axis=1)
        constantes.append('hi')
        hi_var = 'IH [mg HC/g COT]'
    if s1_var is None:
        get_s1 = lambda row: s1_constant
        simulations_df['S1 [mg HC/g rocha]'] = simulations_df.apply(get_s1, axis=1)
        constantes.append('s1')
        s1_var = 'S1 [mg HC/g rocha]'
    if s2_var is None:
        get_s2 = lambda row: s2_constant
        simulations_df['S2 [mg HC/g rocha]'] = simulations_df.apply(get_s2, axis=1)
        constantes.append('s2')
        s2_var = 'S2 [mg HC/g rocha]'

    # Cálculando HI0:
    if hi0_select == 'reftable':
        print('Calculando HI0 com :' + str(hi0_select))
        simulations_df = calculate_hi0_reftable(simulations_df, s2s3_var)

    # Cálculando TR:
    if tr_select == 'justwan-dahl-2005':
        print('Calculando TR com :' + str(tr_select))
        simulations_df = tr_justwan_dahl(simulations_df, 'Hi inicial', hi_var)
    if tr_select == 'peters-1996':
        print('Calculando TR com :' + str(tr_select))
        simulations_df = tr_peters_1996(simulations_df, hi_var, 'Hi inicial', s1_var, s2_var)
    if tr_select == 'jarvie-2007':
        print('Calculando TR com :' + str(tr_select))
        simulations_df = tr_jarvie_2007(simulations_df, hi_var, 'Hi inicial', s1_var, s2_var)
    if tr_select == 'jarvie-2012':
        print('Calculando TR com :' + str(tr_select))
        simulations_df = tr_jarvie_2012(simulations_df, hi_var, 'Hi inicial')
    if tr_select == 'zhuoheng-2015':
        print('Calculando TR com :' + str(tr_select))
        simulations_df = tr_zhuoheng_2015(simulations_df, hi_var, 'Hi inicial')

    if eixo_x == 'txTransformacao_eixox_txTransformacao' and eixo_y == 'txTransformacao_eixoy_profundidade':

        fig = subplots.make_subplots(rows=1, cols=1,
                                    shared_yaxes=True,
                                    horizontal_spacing=0)

        fig.append_trace(go.Scatter(
            x=simulations_df['Taxa de Transformação [v/v]'].dropna().values,
            y=simulations_df[maturation_depth].dropna().values,
            name='Taxa de Transformação [v/v]',
            line={'width': 0.75, 'dash': 'solid'},
        ), row=1, col=1)

        fig.update_layout(legend=dict(orientation="h",
                                    yanchor="bottom"))

        # layout do gráfico
        fig['layout']['yaxis'].update(
            title='Profundidade [m]',
            autorange='reversed'
        )

    elif eixo_x == 'txTransformacao_eixox_profundidade' and eixo_y == 'txTransformacao_eixoy_txTransformacao':
        fig = subplots.make_subplots(rows=1, cols=1,
                            shared_yaxes=True,
                            horizontal_spacing=0)

        fig.append_trace(go.Scatter(
            y=simulations_df['Taxa de Transformação [v/v]'].dropna().values,
            x=simulations_df[maturation_depth].dropna().values,
            name='Taxa de Transformação [v/v]',
            line={'width': 0.75, 'dash': 'solid'},
        ), row=1, col=1)

        fig.update_layout(legend=dict(orientation="h",
                                    yanchor="bottom"))

        # layout do gráfico
        fig['layout']['yaxis'].update(
            title='Profundidade [m]',
            autorange='reversed'
        )
    else:
        fig = subplots.make_subplots(rows=1, cols=1,
                            shared_yaxes=True,
                            horizontal_spacing=0)

        fig.append_trace(go.Scatter(
            x=simulations_df['Taxa de Transformação [v/v]'].dropna().values,
            y=simulations_df[maturation_depth].dropna().values,
            name='Taxa de Transformação [v/v]',
            line={'width': 0.75, 'dash': 'solid'},
        ), row=1, col=1)

        fig.update_layout(legend=dict(orientation="h",
                                    yanchor="bottom"))

        # layout do gráfico
        fig['layout']['yaxis'].update(
            title='Profundidade [m]',
            autorange='reversed'
        )

    # Salvando dataframes resultado:
    simulations_df.to_csv('static/tr_simulation_' + str(n_clicks) + '.csv', index=False, sep=';')
    simulations_df.to_string("static/tr_simulation_" + str(n_clicks) + ".txt", index=False)

    z = zipfile.ZipFile('static/tr_simulation_' + str(n_clicks) + '.zip', 'w', zipfile.ZIP_DEFLATED)
    z.write('static/tr_simulation_' + str(n_clicks) + '.txt')
    z.write('static/tr_simulation_' + str(n_clicks) + '.csv')


    return fig

################################# POTENCIAL DE GERAÇÃO #################################

def simulate_quantidade(n_clicks,
                        cotr_depth, cotr_var, cotr_constant, cotr_check,
                        maturation_path,
                        s2_var, s2_constant, s2_check,
                        quantidade_range,
                        quantidade_select,
                        no_data):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    constantes = []

    # Criando dataframe:
    if maturation_path is not None:
        if maturation_path[-3:] == 'csv':
            simulations_df = pd.read_csv(maturation_path, na_values=no_data)
        if maturation_path[-3:] == 'txt':
            simulations_df = pd.read_csv(maturation_path, sep='\t', na_values=no_data)
        if maturation_path[-3:] == 'xls':
            simulations_df = pd.read_csv(maturation_path, na_values=no_data)

    if cotr_var is None:
        get_cotr = lambda row: cotr_constant
        simulations_df['COTr [%]'] = simulations_df.apply(get_cotr, axis=1)
        constantes.append('cotr')
        cotr_var = 'COTr [%]'
    if s2_var is None:
        get_s2 = lambda row: s2_constant
        simulations_df['S2 [mg HC/g rocha]'] = simulations_df.apply(get_s2, axis=1)
        constantes.append('s2')
        s2_var = 'S2 [mg HC/g rocha]'
    print('print s2_var aqui', s2_var)
    if quantidade_select == 'reftable':
        # Aplicando condições da tabela de referência:
        conditions = [simulations_df[s2_var] <= 2.5,
                      (simulations_df[s2_var] >= 2.5) & (simulations_df[s2_var] < 5),
                      (simulations_df[s2_var] >= 5) & (simulations_df[s2_var] < 10),
                      (simulations_df[s2_var] >= 10)]
        choices = ["Pobre", "Razoável", "Bom", "Muito bom"]

        simulations_df['Quantidade'] = np.select(conditions, choices, default=np.nan)

        figure = px.scatter(simulations_df, x=cotr_var, y=s2_var, color='Quantidade')

    # Salvando dataframes resultado:
    simulations_df.to_csv('static/quantidade_simulation_'+str(n_clicks)+'.csv', index=False, sep=';')
    simulations_df.to_string("static/quantidade_simulation_"+str(n_clicks)+".txt", index=False)

    z = zipfile.ZipFile('static/quantidade_simulation_'+str(n_clicks)+'.zip', 'w', zipfile.ZIP_DEFLATED)
    z.write('static/quantidade_simulation_'+str(n_clicks)+'.txt')
    z.write('static/quantidade_simulation_'+str(n_clicks)+'.csv')

    return figure