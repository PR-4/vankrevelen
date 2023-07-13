# Arquivo contendo callbacks relativos às simulações da aba COT e MATURAÇÃO
# Importações:
import os

import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd
import re
import lasio
from dash.dash import no_update
import dash_html_components as html
from plotly.subplots import make_subplots
from math import log10
from modules.utils import *
from functions.sedrate_cicloestrat import *

## EQUAÇÕES PRINCIPAIS:
from functions.mom_functions import *
from functions.maturation_functions import *

def get_simulations_callbacks(app):
    ##### CALLBACKS DE SIMULAÇÃO:
    @app.callback([  # Output('sim-figure', 'figure'),
        # Tem que mudar o primeiro output pro VALUE
        # e também acrescentar as opções no segundo
        Output('cot-simulations-plot-dd', 'value'),
        Output('cot-simulations-plot-dd', 'options'),
        Output('plot-toc-spinner', 'children'),
        Output('sim-export-dd', 'disabled'),
        Output('sim-export-dd', 'options'),
        Output('sim-export-dd', 'value'),
        Output('mistura-export-dd', 'disabled'),
        Output('mistura-export-dd', 'options'),
        Output('mistura-export-dd', 'value'),
        Output('sim-export-select-dd', 'options'),
        Output('sim-export-select-dd', 'disabled'),
        Output('las-files', 'children'),
        Output('compare-cot-results', 'options')
    ],
        [Input('plot-toc', 'n_clicks')],
        [State('select-dbd-depth', 'value'),  # dbd
         State('select-dbd-var', 'value'),  # dbd
         State('dbd-constant', 'value'),  # dbd
         State('dbd-check', 'value'),  # dbd
         State('dbd-filenames-div', 'children'),  # dbd
         State('select-pp-depth', 'value'),  # pp
         State('select-pp-var', 'value'),  # pp
         State('pp-constant', 'value'),  # pp
         State('pp-check', 'value'),  # pp
         State('pp-filenames-div', 'children'),  # pp
         State('select-sr-depth', 'value'),  # sedrate
         State('select-sr-var', 'value'),  # sedrate
         State('sr-constant', 'value'),  # sedrate
         State('sr-check', 'value'),  # sedrate
         State('sedrate-filenames-div', 'children'),  # sedrate
         State('select-wd-depth', 'value'),  # water depth
         State('select-wd-var', 'value'),  # water depth
         State('wd-constant', 'value'),  # water depth
         State('wd-check', 'value'),  # water depth
         State('wd-filenames-div', 'children'),  # water depth,
         State('select-age-depth', 'value'),  # ages depth
         State('select-age-var', 'value'),  # ages depth
         State('age-constant', 'value'),  # ages depth
         State('age-check', 'value'),  # ages depth
         State('age-filenames-div', 'children'),  # ages depth,
         State('dbd-las', 'value'),
         State('pp-las', 'value'),
         State('sedrate-las', 'value'),
         State('wd-las', 'value'),
         State('sf-las', 'value'),
         State('age-las', 'value'),
         State('las-filenames-div', 'children'),  # las
         State('select-sf-depth', 'value'),  # sand fraction
         State('select-sf-var', 'value'),  # sand fraction
         State('sf-constant', 'value'),  # sand fraction
         State('sf-check', 'value'),  # sand fraction
         State('sf-filenames-div', 'children'),  # sand fraction
         State('range-toc', 'value'),  # mom-range
         State('simtoc-check', 'value'),  # checklist de simulações
         State('toc-resolution', 'value'),
         State('select-mom-equation', 'value'),
         State('select-cf-equation', 'value'),
         State('select-be-equation', 'value'),
         State('select-tom-equation', 'value'),
         State('no-data', 'value'),
         State('sim-list', 'children'),
         State('simulate-events', 'value'),
         # State('event-age-min', 'value'),
         # State('event-age-max', 'value'),
         # State('event-fp', 'value'),
         State('table-anoxia', 'data'),
         State('event-var', 'value'),
         State('well-name', 'value'),
         State('well-datum', 'value'),
         State('well-x', 'value'),
         State('well-y', 'value'),
         State('well-lat', 'value'),
         State('well-long', 'value'),
         State('well-lam', 'value'),
         State('well-mesa', 'value'),
         State('cot-simulations-plot-dd', 'options'),
         State('simulation-name', 'value'),
         State('las-files', 'children'),
         State('event-eq', 'value')])
    def simulate_cot(n_clicks,
                     dbd_depth, dbd_var, dbd_constant, dbd_check, dbd_filepath,
                     pp_depth, pp_var, pp_constant, pp_check, pp_filepath,
                     sr_depth, sr_var, sr_constant, sr_check, sr_filepath,
                     wd_depth, wd_var, wd_constant, wd_check, wd_filepath,
                     ages_depth, ages_var, ages_constant, ages_check, ages_filepath,
                     dbd_las, pp_las, sedrate_las, wd_las, sf_las, ages_las,
                     las_filepath,
                     sf_depth, sf_var, sf_constant, sf_check, sf_filepath,
                     mom_range,
                     toc_check,
                     toc_resolution,
                     mom_equation, cf_equation, be_equation, tom_equation,
                     no_data,
                     sim_list,
                     events_check, anox_table_data, anoxic_var,  # events_min, events_max, events_fp, anoxic_var,
                     well_name, well_datum, well_x, well_y, well_lat, well_long, well_lam, well_mesa,
                     cot_dd_options, simulation_name,
                     las_files,
                     anoxia_equation):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        # print(sorted(toc_check))
        if sorted(toc_check) == ['plot-toc'] or sorted(toc_check) == ['plot-mom', 'plot-toc'] or sorted(toc_check) == [
            'plot-toc', 'plot-tom']:
            return cot_dd_options, no_update, no_update, True, no_update, \
                no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

        if simulation_name is None:
            simulation_name = f'Simulação {n_clicks}'

        # dict de informações do poço:
        well_info = {
            'name': well_name if well_name is not None else 'Simulacao_COT_' + str(n_clicks),
            'datum': well_datum,
            'x': well_x,
            'y': well_y,
            'lat': well_lat,
            'long': well_long,
            # 'lam': well_lam if well_lam is not None else None,
            # 'mesa': well_mesa if well_mesa is not None else None,
        }
        # Conjunto vazio para armazenar cada um dos strings dos gráficos gerados:
        simulations = []

        ## Define variáveis dicionários para armazenar variáveis:

        vars_dict = {'Densidade Aparente Seca': False,
                     'Produtividade Primária': False,
                     'Taxa de Sedimentação': False,
                     'Paleobatimetria': False,
                     'Fração de Areia': False,
                     'Idades': False}

        lasvars_dict = {'Densidade Aparente Seca': dbd_las,
                        'Produtividade Primária': pp_las,
                        'Taxa de Sedimentação': sedrate_las,
                        'Paleobatimetria': wd_las,
                        'Fração de Areia': sf_las,
                        'Idades': ages_las
                        }

        txtpaths_dict = {'Densidade Aparente Seca': dbd_filepath,
                         'Produtividade Primária': pp_filepath,
                         'Taxa de Sedimentação': sr_filepath,
                         'Paleobatimetria': wd_filepath,
                         'Fração de Areia': sf_filepath,
                         'Idades': ages_filepath}

        txtcols_dict = {'Densidade Aparente Seca': dbd_var,
                        'Produtividade Primária': pp_var,
                        'Taxa de Sedimentação': sr_var,
                        'Paleobatimetria': wd_var,
                        'Fração de Areia': sf_var,
                        'Idades': ages_var}

        txtdepths_dict = {'Densidade Aparente Seca': dbd_depth,
                          'Produtividade Primária': pp_depth,
                          'Taxa de Sedimentação': sr_depth,
                          'Paleobatimetria': wd_depth,
                          'Fração de Areia': sf_depth,
                          'Idades': ages_depth}

        depths_dict = {'Densidade Aparente Seca': None,
                       'Produtividade Primária': None,
                       'Taxa de Sedimentação': None,
                       'Paleobatimetria': None,
                       'Fração de Areia': None,
                       'Idades': None}

        if las_filepath:
            print('Realizando leitura do arquivo Las')
            las = lasio.read(las_filepath)
            las_df = las.df()
            # Associando variáveis à curvas do .las:
            from functions.parse_functions import parse_las_vars
            vars_dict, depths_dict = parse_las_vars(vars_dict, lasvars_dict, depths_dict, las_df)

        from functions.parse_functions import parse_constants, parse_txts
        # Associando variáveis à constantes:
        constants_list = [dbd_constant, pp_constant, sr_constant, wd_constant, sf_constant, ages_constant]
        checks_list = [dbd_check, pp_check, sr_check, wd_check, sf_check, ages_check]
        vars_dict, used_constants = parse_constants(vars_dict, checks_list, constants_list)

        vars_dict, depths_dict = parse_txts(vars_dict, txtpaths_dict, txtdepths_dict, txtcols_dict, depths_dict,
                                            no_data)

        # Definindo resolução:
        depth_resolution = [i for i in np.arange(np.min(mom_range), np.max(mom_range), float(toc_resolution))]
        print('Resolução de ' + str(toc_resolution) + 'm (fase de testes) com range de profundidade de ' + str(
            np.min(mom_range)) + 'm a ' + str(np.max(mom_range)) + 'm.')
        # Criando interpolações
        print('Interpolação 1d com numpy.interp()...')

        # Criando dataframe vazio, apenas com a coluna de profundidade utilizada:
        interp_dataframe = pd.DataFrame(data={'Profundidade [m]': depth_resolution})

        # Adicionando constantes ao dataframe:
        for var, value in vars_dict.items():
            if value is not False:
                if isinstance(value, float) or isinstance(value, int):
                    get_constant = lambda row: value
                    interp_dataframe[var] = interp_dataframe.apply(get_constant, axis=1)

        # Interpolando Séries e adicionando ao dataframe:
        for var, value in vars_dict.items():
            if isinstance(value, pd.Series):
                print('Interpolando ' + str(var))
                interp_series = np.interp(np.array(depth_resolution), depths_dict[var], value)
                interp_dataframe.insert(loc=len(interp_dataframe.columns), column=var, value=interp_series)
        print('Interpolações concluídas.')

        # Calculando COma (MOM):
        if 'plot-mom' in toc_check:
            print('Aplicando função de cálculo de CO\u2098\u2090:')
            if mom_equation == 'muller-suess-1979':
                print('Equação Selecionada: Muller & Suess 1979')
                interp_dataframe = muller_suess(interp_dataframe)

            if mom_equation == 'stein-1986' or mom_equation == 'def-equation':
                # Calculando Carbon Flux:
                interp_dataframe = carbon_flux(interp_dataframe, cf_equation)

                if mom_equation == 'stein-1986':
                    interp_dataframe = stein(interp_dataframe)

                if mom_equation == 'def-equation':
                    interp_dataframe = defequation(interp_dataframe, be_equation)

            # Aplicando condições de anoxia:
            if events_check is not None:
                if 'use-events' in events_check:
                    event_idx = 0
                    for event in anox_table_data:
                        try:
                            if anoxic_var != 'idades':
                                anoxic_var = 'Profundidade [m]'
                            else:
                                anoxic_var = 'Idades'
                            events_min = float(event['Prof_min'])
                            events_max = float(event['Prof_max'])
                            events_fp = float(event['fp'])
                            events_multi = float(event['multi'])
                            # Define intervalo (pd.Series) contendo o evento anóxico:
                            anoxic_interval_series = interp_dataframe.loc[
                                (interp_dataframe[anoxic_var] >= events_min) & (
                                            interp_dataframe[anoxic_var] <= events_max)]
                            # Define a mediana do intervalo:
                            from statistics import median_low
                            median_ages = median_low(anoxic_interval_series[anoxic_var].values)
                            # Cria função lambda para aplicar mediana:
                            if anoxia_equation == 'sedrate_normal':
                                get_anoxic = lambda row: (((row['Produtividade Primária'] * events_fp) / (
                                        row['Densidade Aparente Seca'] * row[
                                    'Taxa de Sedimentação']))) * events_multi if row[
                                                                                     anoxic_var] == median_ages else \
                                    row['CO\u2098\u2090 [%]']
                            else:
                                get_anoxic = lambda row: ((row['Produtividade Primária'] * events_fp) / \
                                                          (((row['Produtividade Primária'] * events_fp) + 10) * (
                                                                      row['Taxa de Sedimentação'] * row[
                                                                  'Densidade Aparente Seca']))) * events_multi if row[
                                                                                                                      anoxic_var] == median_ages else \
                                    row['CO\u2098\u2090 [%]']
                            # if row[anoxic_var] == median_ages\
                            # else row
                            # Aplica a condição acima no dataframe:
                            interp_dataframe['CO\u2098\u2090 [%]'] = interp_dataframe.apply(get_anoxic, axis=1)
                            # Determina mom no intervalo linear do evento anóxico:
                            length_below = len(
                                interp_dataframe['CO\u2098\u2090 [%]'][(interp_dataframe[anoxic_var] > np.min(
                                    anoxic_interval_series[anoxic_var])) & (interp_dataframe[
                                                                                anoxic_var] < median_ages)])
                            length_above = len(
                                interp_dataframe['CO\u2098\u2090 [%]'][(interp_dataframe[anoxic_var] < np.max(
                                    anoxic_interval_series[anoxic_var])) & (interp_dataframe[
                                                                                anoxic_var] > median_ages)])
                            mom_anoxic_below_median = np.linspace(anoxic_interval_series['CO\u2098\u2090 [%]'][
                                                                      anoxic_interval_series[anoxic_var] == np.min(
                                                                          anoxic_interval_series[anoxic_var])].values,
                                                                  interp_dataframe['CO\u2098\u2090 [%]'][
                                                                      interp_dataframe[
                                                                          anoxic_var] == median_ages].values,
                                                                  length_below)
                            mom_anoxic_above_median = np.linspace(
                                interp_dataframe['CO\u2098\u2090 [%]'][
                                    interp_dataframe[anoxic_var] == median_ages].values,
                                anoxic_interval_series['CO\u2098\u2090 [%]'][
                                    anoxic_interval_series[anoxic_var] == np.max(
                                        anoxic_interval_series[anoxic_var])].values,
                                length_above)
                            # Adicionando os valores no dataframe original:
                            interp_dataframe['CO\u2098\u2090 [%]'][
                                (interp_dataframe[anoxic_var] > np.min(anoxic_interval_series[anoxic_var])) & (
                                        interp_dataframe[anoxic_var] < median_ages)] = mom_anoxic_below_median[:, 0]
                            interp_dataframe['CO\u2098\u2090 [%]'][
                                (interp_dataframe[anoxic_var] < np.max(anoxic_interval_series[anoxic_var])) & (
                                        interp_dataframe[anoxic_var] > median_ages)] = mom_anoxic_above_median[:, 0]
                        # Cria função lambda para interpolar os valores intermediários (menores e maiores que a mediana, contidos no intervalo anóxico)
                        except Exception as e:
                            print(e)
                    event_idx += 1
                # events_check, events_min, events_max, events_fp
            simulations.append(['CO\u2098\u2090 [%]'])

        if 'plot-tom' in toc_check:
            # Calculando COte (TOM = qCO + rCO):
            get_soc = lambda row: -0.005 * (row['Fração de Areia']) + 0.5
            interp_dataframe['rCO [%]'] = interp_dataframe.apply(get_soc, axis=1)
            if tom_equation == 'tom-equation-2':  # Médio (antigo baixo)
                # Definindo cálculo de ptoc:
                get_ptoc = lambda row: 0.02 * row['Fração de Areia'] if row['Fração de Areia'] < 75 else -0.06 * row[
                    'Fração de Areia'] + 6
                interp_dataframe['qCO [%]'] = interp_dataframe.apply(get_ptoc, axis=1)

            if tom_equation == 'tom-equation-3':  # Alto (permanece igual, porém agora é a eqation-3)
                # Definindo cálculo de ptoc:
                get_ptoc = lambda row: 0.0667 * row['Fração de Areia'] if row['Fração de Areia'] < 75 else -0.2 * row[
                    'Fração de Areia'] + 20
                interp_dataframe['qCO [%]'] = interp_dataframe.apply(get_ptoc, axis=1)

            if tom_equation == 'tom-equation-1':  # Baixo (nova eq.)
                # Definindo cálculo de ptoc:
                get_ptoc = lambda row: 0.01 * row['Fração de Areia'] if row['Fração de Areia'] < 75 else -0.03 * row[
                    'Fração de Areia'] + 3
                interp_dataframe['qCO [%]'] = interp_dataframe.apply(get_ptoc, axis=1)

            # Definindo cálculo de COte (TOM):
            get_tom = lambda row: row['rCO [%]'] + row['qCO [%]']
            interp_dataframe['CO\u209c\u2091 [%]'] = interp_dataframe.apply(get_tom, axis=1)
            print('rCO e qCO calculados')
            simulations.append(['qCO [%]', 'rCO [%]'])

        # Calculando TOC (COma + COte):
        if 'plot-toc' in toc_check and 'plot-tom' in toc_check and 'plot-mom' in toc_check:
            get_toc = lambda row: row['CO\u2098\u2090 [%]'] + row['CO\u209c\u2091 [%]']
            print('Calculando COT com resolução de ' + str(toc_resolution) + 'm')
            # TODO: colocar novamente a resolução do TOC
            interp_dataframe['COT [%]'] = interp_dataframe.apply(get_toc, axis=1)
            simulations.append(['COT [%]'])

        # Criando valores de TVD
        prof_graph = 'Profundidade [m]'
        if well_mesa and well_lam:
            create_mesa = lambda row: well_mesa
            create_lam = lambda row: well_lam
            create_tvd = lambda row: (row['Mesa Giratória'] + row["Lâmina D'água"]) - row['Profundidade [m]']

            interp_dataframe['Mesa Giratória'] = interp_dataframe.apply(create_mesa, axis=1)
            interp_dataframe["Lâmina D'água"] = interp_dataframe.apply(create_lam, axis=1)
            interp_dataframe["TVD"] = interp_dataframe.apply(create_tvd, axis=1)

            prof_graph = "TVD"

        fig = subplots.make_subplots(rows=1, cols=len(simulations),
                                     shared_yaxes=True,
                                     horizontal_spacing=0)
        for i in range(len(simulations)):
            for column in simulations[i]:
                print(column)
                if column == 'CO\u2098\u2090 [%]':
                    fig.append_trace(go.Scatter(
                        x=interp_dataframe[column].values,

                        y=interp_dataframe[prof_graph].values,
                        name=column,
                        line={'width': 0.75,
                              'dash': 'solid'},
                    ), row=1, col=i + 1)
                    fig['layout']['xaxis{}'.format(i + 1)].update(
                        title=column
                    )
                if column == 'qCO [%]' or column == 'rCO [%]':
                    fig.append_trace(go.Scatter(
                        x=interp_dataframe[column].values,
                        y=interp_dataframe[prof_graph].values,
                        name=column,
                        line={'width': 0.75,
                              'dash': 'solid'},
                    ), row=1, col=i + 1)
                    fig['layout']['xaxis{}'.format(i + 1)].update(
                        title='qCO [%]'
                    )
                    if column == 'rCO [%]':
                        eixo_ptoc = i + 1
                if column == 'COT [%]':
                    fig.append_trace(go.Scatter(
                        x=interp_dataframe[column].values,
                        y=interp_dataframe[prof_graph].values,
                        name=column,
                        line={'width': 0.75,
                              'dash': 'solid'},
                    ), row=1, col=i + 1)
                    fig['layout']['xaxis{}'.format(i + 1)].update(
                        title='COT [%]'
                    )
        if ['qCO [%]', 'rCO [%]'] in simulations:
            fig['data'][eixo_ptoc]['xaxis'] = 'x' + str(len(fig['data']))
            fig['layout']['xaxis' + str(len(fig['data']))] = dict(
                overlaying='x' + str(eixo_ptoc),
                anchor='y',
                side='top',
                title='rCO [%]'
            )
        fig.update_layout(legend=dict(orientation="h",
                                      yanchor="bottom"))
        # layout do gráfico
        fig['layout']['yaxis'].update(
            title=prof_graph,
            autorange='reversed'
        )
        for axis in fig['layout']:
            if re.search(r'[xy]axis[0-9]*', axis):
                fig['layout'][axis].update(
                    mirror='all',
                    automargin=True,
                    showline=True,
                    title=dict(
                        font=dict(
                            family='Arial, sans-serif'
                        )
                    ),
                    tickfont=dict(
                        family='Arial, sans-serif'
                    )
                )
        fig['layout'].update(hovermode='y')

        # Salvando dataframes resultado:
        try:
            os.makedirs(f'static/{simulation_name}')
        except:
            pass

        # Gerando Las
        generate_las(interp_dataframe, well_info, simulation_name)

        # Criando DataFrames da aba resultado
        simulated_data = dict()
        if 'plot-mom' in toc_check:
            simulated_data['CO\u2098\u2090'] = interp_dataframe['CO\u2098\u2090 [%]'].values

        if 'plot-tom' in toc_check:
            simulated_data['rCO'] = interp_dataframe['rCO [%]'].values
            simulated_data['qCO'] = interp_dataframe['qCO [%]'].values
            simulated_data['CO\u209c\u2091'] = interp_dataframe['CO\u209c\u2091 [%]'].values

        if 'plot-toc' in toc_check:
            simulated_data['COT'] = interp_dataframe['COT [%]'].values

        results_df = pd.DataFrame.from_dict(simulated_data, orient='index').T
        results_df = results_df.describe().transpose().round(2).rename(
            columns={'mean': 'média', 'std': '2σ', 'max': 'máx'})
        results_df.drop(columns='count', inplace=True)
        results_df.insert(0, 'Estatísticas Básicas', results_df.index)

        variaveis_results_list = []
        for var, value in vars_dict.items():
            if isinstance(value, float) or isinstance(value, int):
                variaveis_results_list.append(str(value))
            if isinstance(value, pd.Series) or isinstance(value, pd.DataFrame):
                variaveis_results_list.append('Carregado pelo usuário')
            if isinstance(value, bool):
                variaveis_results_list.append('Não possui')

        var_results = pd.DataFrame({
            'Variável': ['Taxa de Sedimentação [cm/ka]', 'Produtividade Primária [gC/m²/yr]',
                         'Densidade Aparente Seca [g/cm³]',
                         'Batimetria/Paleobatimetria [m]', 'Fração de areia [%]', 'Idades [Ma]'],
            'Valor': [variaveis_results_list[0], variaveis_results_list[1], variaveis_results_list[2],
                      variaveis_results_list[3], variaveis_results_list[4],
                      variaveis_results_list[5]]})
        vars_dict = {
            False: 'Não utilizado.',
            'False': 'Não utilizado.',
            None: 'Não utilizado.',
            'None': 'Não utilizado.',
            '': 'Não utilizado.'
        }
        var_results.replace(vars_dict, inplace=True)
        equations_list = [mom_equation, cf_equation, be_equation, tom_equation]
        equations_results = pd.DataFrame(
            {'Simulações': ['Carbôno Orgânico Marinho (CO\u2098\u2090)', 'Fluxo de Carbono',
                            'Eficiência de Soterramento', 'Carbôno Orgânico Terrestre (CO\u209c\u2091)'],
             'Equaçã': [str(equations_list[0]), str(equations_list[1]),
                        str(equations_list[2]), equations_list[3]]})
        equations_dict = {
            'def-equation': 'Definition Equation',
            'stein-1986': 'Stein (1986)',
            'muller-suess-1979': 'Muller & Suess (1979)',
            'suess-1980': 'Suess (1980)',
            'betzer-1984': 'Betzer et al. (1984)',
            'berger-1987': 'Berger et al. (1987)',
            'sarnthein-1988': 'Sarnthein et al. (1988)',
            'antia-2001': 'Antia et al. (2001)',
            'achillesbr-2021': 'ACHILLES.BR (2021)',
            'henrichs-reedburgh-1987': 'Henrichs & Reeburgh (1987)',
            'betts-holland-1991': 'Betts & Holland (1991)',
            'tom-equation-1': 'Equação de CO\u209c\u2091 (baixo)',
            'tom-equation-2': 'Equação de CO\u209c\u2091 (médio)',
            'tom-equation-3': 'Equação de CO\u209c\u2091 (alto)',
            False: 'Não utilizado.',
            None: 'Não utilizado.',
            'None': 'Não utilizado.',
            '': 'Não utilizado.'
        }
        equations_results.replace(equations_dict, inplace=True)

        interp_dataframe.to_csv(f'static/{simulation_name}/{simulation_name}.csv', index=False, sep=',',
                                encoding='utf-8-sig')
        interp_dataframe.to_string(f"static/{simulation_name}/{simulation_name}.txt", index=False)

        results_df.to_csv(f'static/{simulation_name}/{simulation_name}_estatisticas.csv', index=False, sep=',',
                          encoding='utf-8-sig')
        results_df.to_string(f"static/{simulation_name}/{simulation_name}_estatisticas.txt", index=False)

        var_results.to_csv(f'static/{simulation_name}/{simulation_name}_variaveis.csv', index=False, sep=',',
                           encoding='utf-8-sig')
        var_results.to_string(f"static/{simulation_name}/{simulation_name}_variaveis.txt", index=False)

        equations_results.to_csv(f'static/{simulation_name}/{simulation_name}_equacoes.csv', index=False, sep=',',
                                 encoding='utf-8-sig')
        equations_results.to_string(f"static/{simulation_name}/{simulation_name}_equacoes.txt", index=False)

        # z = zipfile.ZipFile('static/Simulacao_COT_' + str(n_clicks) + '.zip', 'w', zipfile.ZIP_DEFLATED)
        # z.write('static/Simulacao_COT_' + str(n_clicks) + '.txt')
        # z.write('static/Simulacao_COT_' + str(n_clicks) + '.csv')
        # z.write('static/Simulacao_COT_' + str(n_clicks) + '_estatisticas.txt')
        # z.write('static/Simulacao_COT_' + str(n_clicks) + '_estatisticas.csv')
        # z.write('static/Simulacao_COT_' + str(n_clicks) + '_variaveis.txt')
        # z.write('static/Simulacao_COT_' + str(n_clicks) + '_variaveis.csv')
        # z.write('static/Simulacao_COT_' + str(n_clicks) + '_equacoes.txt')
        # z.write('static/Simulacao_COT_' + str(n_clicks) + '_equacoes.csv')
        # z.write(f'static/{well_info["name"]}.las')
        #
        # z.close()
        sim_options = [{'label': 'Simulação ' + str(i + 1), 'value': 'Simulacao_COT_' + str(i + 1)} for i in
                       range(0, n_clicks, 1)]

        if cot_dd_options is None:
            cot_dd_options = []
        cot_dd_options.append({'label': simulation_name, 'value': simulation_name})
        if las_files is None:
            las_files = {}
        las_files[simulation_name] = f'static/{simulation_name}/{well_info["name"]}.las'
        return simulation_name, cot_dd_options, no_update, False, \
            cot_dd_options, simulation_name, False, cot_dd_options, simulation_name, cot_dd_options, False, las_files, cot_dd_options
    ## Plot das simulações:
    @app.callback([Output('sim-figure', 'figure'),
                  Output("positioned-toast", 'is_open')],
                  [Input('cot-simulations-plot-dd', 'value')],
                  [State('select-me-depth', 'value'),  # M.E
                   State('select-me-var', 'value'),  # M.E
                   State('me-filenames-div', 'children')])
    def generate_cot_fig(simulation_name, me_depth, me_var, me_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if simulation_name is None or simulation_name == []:
            raise PreventUpdate
        is_open = False
        if type(simulation_name) is str or len(simulation_name) == 1:
            if type(simulation_name) is str:
                filepath = simulation_name
            else:
                filepath = simulation_name[0]

            marcadores_exist = False
            if me_filename is not None:
                try:
                    if me_filename[-3:] == 'csv':
                        marcadores_df = pd.read_csv(me_filename)
                    if me_filename[-3:] == 'txt':
                        marcadores_df = pd.read_csv(me_filename, sep='\t')
                except UnicodeError:
                    if me_filename[-3:] == 'csv':
                        marcadores_df = pd.read_csv(me_filename, encoding='iso-8859-1')
                    if me_filename[-3:] == 'txt':
                        marcadores_df = pd.read_csv(me_filename, sep='\t', encoding='iso-8859-1')
                if me_var and me_filename:
                    marcadores_exist = True

            interp_dataframe = pd.read_csv(f'static/{filepath}/{filepath}.csv', sep=',', encoding='utf-8-sig')
            simulations_vars = ['CO\u2098\u2090 [%]', 'qCO [%]', 'COT [%]']
            simulations = []
            for var in simulations_vars:
                if var in interp_dataframe.columns:
                    if var == 'qCO [%]':
                        simulations.append([var, 'rCO [%]'])
                    else:
                        simulations.append([var])
            fig = subplots.make_subplots(rows=1, cols=len(simulations),
                                         shared_yaxes=True,
                                         horizontal_spacing=0)
            for i in range(len(simulations)):
                for column in simulations[i]:
                    print(column)
                    if column == 'CO\u2098\u2090 [%]':
                        fig.append_trace(go.Scatter(
                            x=interp_dataframe[column].values,
                            y=interp_dataframe['Profundidade [m]'].values,
                            name=column,
                            line={'width': 0.75,
                                  'dash': 'solid'},
                        ), row=1, col=i + 1)
                        fig['layout']['xaxis{}'.format(i + 1)].update(
                            title=column
                        )
                    if column == 'qCO [%]' or column == 'rCO [%]':
                        fig.append_trace(go.Scatter(
                            x=interp_dataframe[column].values,
                            y=interp_dataframe['Profundidade [m]'].values,
                            name=column,
                            line={'width': 0.75,
                                  'dash': 'solid'},
                        ), row=1, col=i + 1)
                        fig['layout']['xaxis{}'.format(i + 1)].update(
                            title='qCO [%]'
                        )
                        if column == 'rCO [%]':
                            eixo_ptoc = i + 1
                    if column == 'COT [%]':
                        fig.append_trace(go.Scatter(
                            x=interp_dataframe[column].values,
                            y=interp_dataframe['Profundidade [m]'].values,
                            name=column,
                            line={'width': 0.75,
                                  'dash': 'solid'},
                        ), row=1, col=i + 1)
                        fig['layout']['xaxis{}'.format(i + 1)].update(
                            title='COT [%]'
                        )
            if ['qCO [%]', 'rCO [%]'] in simulations:
                fig['data'][eixo_ptoc]['xaxis'] = 'x' + str(len(fig['data']))
                fig['layout']['xaxis' + str(len(fig['data']))] = dict(
                    overlaying='x' + str(eixo_ptoc),
                    anchor='y',
                    side='top',
                    title='rCO [%]'
                )
            fig.update_layout(legend=dict(orientation="h",
                                          yanchor="bottom"))

            for axis in fig['layout']:
                if re.search(r'[xy]axis[0-9]*', axis):
                    fig['layout'][axis].update(
                        mirror='all',
                        automargin=True,
                        showline=True,
                        title=dict(
                            font=dict(
                                family='Arial, sans-serif'
                            )
                        ),
                        tickfont=dict(
                            family='Arial, sans-serif'
                        )
                    )
            fig['layout'].update(hovermode='y', title=filepath)

        else:
            try:
                fig = subplots.make_subplots(rows=1, cols=len(simulation_name),
                                             shared_yaxes=True,
                                             horizontal_spacing=0)
                i = 1
                for sim in simulation_name:
                    interp_dataframe = pd.read_csv(f'static/{sim}/{sim}.csv', sep=',', encoding='utf-8-sig')
                    fig.add_trace(
                        go.Scatter(
                            x=interp_dataframe['COT [%]'].values,
                            y=interp_dataframe['Profundidade [m]'].values,
                            name=f'{sim} COT [%]',
                            line={'width': 0.75,
                                  'dash': 'solid'},
                        ), row=1, col= i
                    )
                    if i == 1:
                        fig['layout']['xaxis'].update(
                            title='COT [%]'
                        )
                    else:
                        fig['layout'][f'xaxis{i}'].update(
                            title='COT [%]'
                        )
                    i = i + 1
            except KeyError:
                fig = no_update
                is_open = True

        if marcadores_exist:
            try:
                for idx, row in marcadores_df.iterrows():
                    for col in range(0, len(simulations)):
                        if col == 0:
                            fig.add_hline(y=row[me_depth], row=0, col=col, line_dash="dot", annotation_text=str(row[me_var]), annotation_position="top right")
                        else:
                            fig.add_hline(y=row[me_depth], row=0, col=col, line_dash="dot")
            except Exception as e:
                print(f'[Gráfico de COT] Exceção: {str(e)}')
        # layout do gráfico
        if not is_open:
            fig['layout']['yaxis'].update(
                title='Profundidade [m]',
                autorange='reversed'
            )
        return fig, is_open

    #### Callbacks para cálculo de CO\u209c\u2091:
    # Checklist de variáveis necessárias:
    @app.callback(Output('tom-check', 'value'),
                  [Input('select-sf-depth', 'value'),
                   Input('select-sf-var', 'value'),
                   Input('sf-check', 'value'),
                   Input('sf-las', 'value'),
                   Input('select-tom-equation', 'value')],
                  [State('sf-constant', 'value')])
    def update_mom_check(sf_depth, sf_var, sf_check, sf_las,
                         tom_eq, sf_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []
        if tom_eq is None:
            return []
        # Checando se curva do las é alguma variável:
        if sf_las is not None:
            values.append('sf-ready-tom')

        # Checando se as variáveis estão definidas:
        if sf_check is not None and sf_constant is not None:
            if 'use-constant' in sf_check:
                values.append('sf-ready-tom')
        if sf_var is not None and sf_depth is not None:
            if 'pp-ready-mom' not in values:
                values.append('sf-ready-tom')
        return values

    # Eventos anóxicos
    @app.callback(
        Output("events-collapse", "is_open"),
        [Input("events-collapse-button", "n_clicks")],
        [State("events-collapse", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback([Output('simulate-events', 'options'),
                   Output('simulate-events', 'value'),
                   Output('card-events', 'color')],
                  [Input('table-anoxia', 'data')])
    def enable_events(anox_table_data):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        try:
            if len(anox_table_data) > 0:
                return [{'label': '', 'value': 'use-events', 'disabled': False}], 'use-events', 'success'
            else:
                return [{'label': '', 'value': 'use-events', 'disabled': True}], 'no-events', 'secondary'
        except:
            return PreventUpdate

    @app.callback([Output('tom-alert', 'color'),
                   Output('tom-alert', 'is_open'),
                   Output('tom-alert', 'children')],
                  [Input('tom-check', 'value'),
                   Input('select-tom-equation', 'value'),
                   Input('range-toc', 'disabled')])
    def update_tom_alert(tom_check, tom_equation, range_available):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if tom_check is None:
            raise PreventUpdate
        if tom_equation == 'tom-equation-1' or tom_equation == 'tom-equation-2' or tom_equation == 'tom-equation-3':
            if sorted(tom_check) == ['sf-ready-tom']:
                if range_available is False:
                    return 'success', True, 'Variáveis prontas para simulação! (ajuste as CONFIGURAÇÕES e clique em EXECUTAR na guia de gráficos)'
                if range_available is True:
                    return 'warning', True, 'Intervalo de profundidade não disponível (está usando só constantes?)'

            else:
                return no_update, False, no_update
        else:
            return no_update, False, no_update

    ## Plot Simulation
    @app.callback(Output('plot-toc', 'disabled'),
                  [Input('tom-alert', 'color'),
                   Input('mom-alert', 'color')])
    def enable_sim_button(tom_color, mom_color):
        if not dash.callback_context.triggered:
            raise PreventUpdate

        if tom_color == 'success' or mom_color == 'success':
            return False
        else:
            return no_update

    # Simulation Check
    @app.callback([Output('simtoc-check', 'options'),
                   Output('simtoc-check', 'value')],
                  [Input('tom-alert', 'color'),
                   Input('mom-alert', 'color'),
                   Input('tom-alert', 'is_open'),
                   Input('mom-alert', 'is_open')],
                  [State('simtoc-check', 'value')])
    def simulation_options(tom_color, mom_color, tom_isopen, mom_isopen,check_value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []
        if tom_color == 'success' and mom_color == 'success' and tom_isopen is True and mom_isopen is True:
            values.append('plot-mom')
            values.append('plot-tom')
            values.append('plot-toc')
            options = [{'label': 'Carbono Orgânico Marinho', 'value': 'plot-mom'},
                       {'label': 'Carbono Orgânico Terrestre', 'value': 'plot-tom'},
                       {'label': 'Carbono Orgânico Total', 'value': 'plot-toc'}]
            return options, values
        if tom_color == 'success' and tom_isopen is True:
            values.append('plot-tom')
            options = [{'label': 'Carbono Orgânico Marinho', 'value': 'plot-mom', 'disabled': True},
                       {'label': 'Carbono Orgânico Terrestre', 'value': 'plot-tom'},
                       {'label': 'Carbono Orgânico Total', 'value': 'plot-toc', 'disabled': True}]
            return options, values
        if mom_color == 'success' and mom_isopen is True:
            values.append('plot-mom')
            options = [{'label': 'Carbono Orgânico Marinho', 'value': 'plot-mom'},
                       {'label': 'Carbono Orgânico Terrestre', 'value': 'plot-tom', 'disabled': True},
                       {'label': 'Carbono Orgânico Total', 'value': 'plot-toc', 'disabled': True}]
            return options, values
        else:
            return no_update, no_update

    # Dropdown de Mistura:
    @app.callback([Output('hi-cmar', 'disabled'),
                   Output('hi-cterr', 'disabled'),
                   Output('hi-cres', 'disabled'),
                   Output('oi-cmar', 'disabled'),
                   Output('oi-cterr', 'disabled'),
                   Output('oi-cres', 'disabled'),
                   Output('d13c-cmar', 'disabled'),
                   Output('d13c-cterr', 'disabled'),
                   Output('d13c-cres', 'disabled'),
                   Output('mistura-alert', 'is_open'),
                   Output('mistura-alert', 'children')],
                  [Input('mistura-export-dd', 'value')])
    def enable_mistura(simulation_name):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if simulation_name is None:
            raise PreventUpdate
        # print(dd_value)
        simulation_df = pd.read_csv(f'static/{simulation_name}/{simulation_name}.csv', sep=',')
        if 'COT [%]' in simulation_df.columns:
            return False, False, False, False, False, False, False, False, False, False, no_update
        else:
            return True, True, True, True, True, True, True, True, True, True, 'Não há COT nesta simulação.'

    # Mistura Check
    @app.callback(Output('mistura-check', 'options'),
                  [Input('hi-cmar', 'value'),
                   Input('hi-cterr', 'value'),
                   Input('hi-cres', 'value'),
                   Input('oi-cmar', 'value'),
                   Input('oi-cterr', 'value'),
                   Input('oi-cres', 'value'),
                   Input('d13c-cmar', 'value'),
                   Input('d13c-cterr', 'value'),
                   Input('d13c-cres', 'value')])
    def simulation_options(hi_cmar, hi_cterr, hi_cres,
                           oi_cmar, oi_cterr, oi_cres,
                           d13c_cmar, d13c_cterr, d13c_cres):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        options = []
        if hi_cmar is not None and hi_cterr is not None and hi_cres is not None:
            options.append({'label': 'Índice de Hidrogênio (IH)', 'value': 'plot-hi'})
        if hi_cmar is None or hi_cterr is None or hi_cres is None:
            options.append({'label': 'Índice de Hidrogênio (IH)', 'value': 'plot-hi', 'disabled': True})
        if oi_cmar is not None and oi_cterr is not None and oi_cres is not None:
            options.append({'label': 'Índice de Oxigênio (IO)', 'value': 'plot-oi'})
        if oi_cmar is None or oi_cterr is None or oi_cres is None:
            options.append({'label': 'Índice de Oxigênio (IO)', 'value': 'plot-oi', 'disabled': True})
        if d13c_cmar is not None and d13c_cterr is not None and d13c_cres is not None:
            options.append({'label': 'δ¹³C', 'value': 'plot-d13c'})
        if d13c_cmar is None or d13c_cterr is None or d13c_cres is None:
            options.append({'label': 'δ¹³C', 'value': 'plot-d13c', 'disabled': True})

        return options

    # Ativando botão de Mistura:
    @app.callback(Output('plot-mistura', 'disabled'),
                  [Input('mistura-check', 'value')])
    def mistura_enable(mistura_check):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if mistura_check is not []:
            return False
        else:
            return True

    # Simulação do Modelo de Mistura:
    @app.callback([Output('mistura-figure', 'figure'),
                   Output('plot-mistura-spinner', 'children')],
                  [Input('plot-mistura', 'n_clicks')],
                  [State('hi-cmar', 'value'),
                   State('hi-cterr', 'value'),
                   State('hi-cres', 'value'),
                   State('oi-cmar', 'value'),
                   State('oi-cterr', 'value'),
                   State('oi-cres', 'value'),
                   State('d13c-cmar', 'value'),
                   State('d13c-cterr', 'value'),
                   State('d13c-cres', 'value'),
                   State('mistura-check', 'value'),
                   State('mistura-export-dd', 'value'),
                   State('well-name', 'value'),
                   State('well-datum', 'value'),
                   State('well-x', 'value'),
                   State('well-y', 'value'),
                   State('well-lat', 'value'),
                   State('well-long', 'value')]
    )
    def sim_mistura(n_clicks,
                    hi_cmar, hi_cterr, hi_cres,
                    oi_cmar, oi_cterr, oi_cres,
                    d13c_cmar, d13c_cterr, d13c_cres,
                    mistura_check,
                    dd_value,
                    well_name, well_datum, well_x, well_y, well_lat, well_long):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        else:
            df = pd.read_csv(f'static/{dd_value}/{dd_value}.csv', sep=',')
            #df = maturation_df[['Profundidade [m]', 'CO\u2098\u2090 [%]', 'qCO [%]', 'rCO [%]', 'COT [%]']]
            # df = pd.DataFrame({'Profundidade [m]': sim_fig['data'][0]['y'],
            #                   'CO\u2098\u2090': sim_fig['data'][0]['x'],
            #                   'pTOC': sim_fig['data'][1]['x'],
            #                   'rCO': sim_fig['data'][2]['x'],
            #                   'TOC': sim_fig['data'][3]['x']})
            if 'plot-hi' in mistura_check:
                get_hi = lambda row: (row['CO\u2098\u2090 [%]'] / row['COT [%]']) * hi_cmar + (
                        row['qCO [%]'] / row['COT [%]']) * hi_cterr + (row['rCO [%]'] / row['COT [%]']) * hi_cres
                df['IH [mg HC/g COT]'] = df.apply(get_hi, axis=1)
            if 'plot-oi' in mistura_check:
                get_oi = lambda row: (row['CO\u2098\u2090 [%]'] / row['COT [%]']) * oi_cmar + (
                        row['qCO [%]'] / row['COT [%]']) * oi_cterr + (row['rCO [%]'] / row['COT [%]']) * oi_cres
                df['IO  [mg CO\u2082/g COT]'] = df.apply(get_oi, axis=1)
            if 'plot-d13c' in mistura_check:
                get_d13c = lambda row: (row['CO\u2098\u2090 [%]'] / row['COT [%]']) * d13c_cmar + (
                        row['qCO [%]'] / row['COT [%]']) * d13c_cterr + (row['rCO [%]'] / row['COT [%]']) * d13c_cres
                df['δ¹³C [‰]'] = df.apply(get_d13c, axis=1)

            # Exportando df de Modelo de Mistura:
            df.to_csv(f'static/{dd_value}/{dd_value}_qualidade.csv', index=False, sep=',', encoding='utf-8-sig')
            df.to_string(f'static/{dd_value}/{dd_value}_qualidade.txt', index=False)
            df.to_csv(f'static/{dd_value}/{dd_value}.csv', sep=',')

            well_name = dd_value
            well_info = {
                'name': well_name,
                'datum': well_datum,
                'x': well_x,
                'y': well_y,
                'lat': well_lat,
                'long': well_long
            }

            # Gerando las
            generate_las(df, well_info, well_name, qualidade_flag=True)

            z = zipfile.ZipFile(f'static/{dd_value}.zip', 'w', zipfile.ZIP_DEFLATED)
            z.write(f'static/{dd_value}/{dd_value}_qualidade.csv')
            z.write(f'static/{dd_value}/{dd_value}_qualidade.txt')
            z.write(f'static/{dd_value}/{dd_value}_qualidade.las')
            z.close()

            fig = subplots.make_subplots(rows=1, cols=len(mistura_check),
                                         shared_yaxes=True,
                                         horizontal_spacing=0)
            col = 1
            for i in mistura_check:
                if i == 'plot-hi':
                    fig.append_trace(go.Scatter(
                        x=df['IH [mg HC/g COT]'].values,
                        y=df['Profundidade [m]'].values,
                        name='IH [mg HC/g COT]',
                        line={'width': 0.75, 'dash': 'solid'},

                    ), row=1, col=col)
                    fig['layout']['xaxis{}'.format(col)].update(
                        title='IH [mg HC/g COT]'
                    )
                    col = col + 1
                if i == 'plot-oi':
                    fig.append_trace(go.Scatter(
                        x=df['IO  [mg CO\u2082/g COT]'].values,
                        y=df['Profundidade [m]'].values,
                        name='IO [mg CO\u2082/g COT]',
                        line={'width': 0.75, 'dash': 'solid'},

                    ), row=1, col=col)
                    fig['layout']['xaxis{}'.format(col)].update(
                        title='IO  [mg CO\u2082/g COT]'
                    )
                    col = col + 1
                if i == 'plot-d13c':
                    fig.append_trace(go.Scatter(
                        x=df['δ¹³C [‰]'].values,
                        y=df['Profundidade [m]'].values,
                        name='δ¹³C [‰]',
                        line={'width': 0.75, 'dash': 'solid'},

                    ), row=1, col=col)
                    fig['layout']['xaxis{}'.format(col)].update(
                        title='δ¹³C [‰]'
                    )
                    col = col + 1
            fig.update_layout(legend=dict(orientation="h",
                                          yanchor="bottom"))
            # layout do gráfico
            fig['layout']['yaxis'].update(
                title='Profundidade [m]',
                autorange='reversed'
            )

            return fig, no_update

    # Checklist de variáveis necessárias:
    @app.callback(Output('mom-check', 'value'),
                  [Input('select-pp-depth', 'value'),
                   Input('select-pp-var', 'value'),
                   Input('pp-check', 'value'),
                   Input('select-sr-depth', 'value'),
                   Input('select-sr-var', 'value'),
                   Input('sr-check', 'value'),
                   Input('select-dbd-depth', 'value'),
                   Input('select-dbd-var', 'value'),
                   Input('dbd-check', 'value'),
                   Input('select-wd-depth', 'value'),
                   Input('select-wd-var', 'value'),
                   Input('wd-check', 'value'),
                   Input('pp-las', 'value'),
                   Input('sedrate-las', 'value'),
                   Input('dbd-las', 'value'),
                   Input('wd-las', 'value')],
                  [State('pp-constant', 'value'),
                   State('sr-constant', 'value'),
                   State('dbd-constant', 'value'),
                   State('wd-constant', 'value')])
    def update_mom_check(pp_depth, pp_var, pp_check,
                         sr_depth, sr_var, sr_check,
                         dbd_depth, dbd_var, dbd_check,
                         wd_depth, wd_var, wd_check,
                         pp_las, sr_las, dbd_las, wd_las,
                         pp_constant, sr_constant, dbd_constant, wd_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []

        # Checando se curva do las é alguma variável:
        if pp_las is not None:
            values.append('pp-ready-mom')
        if sr_las is not None:
            values.append('sr-ready-mom')
        if dbd_las is not None:
            values.append('dbd-ready-mom')
        if wd_las is not None:
            values.append('wd-ready-mom')

        # Checando se as variáveis estão definidas:
        if pp_check is not None and pp_constant is not None:
            if 'use-constant' in pp_check:
                values.append('pp-ready-mom')
        if pp_var is not None and pp_depth is not None:
            if 'pp-ready-mom' not in values:
                values.append('pp-ready-mom')
        if sr_check is not None and sr_constant is not None:
            if 'use-constant' in sr_check:
                values.append('sr-ready-mom')
        if sr_var is not None and sr_depth is not None:
            if 'sr-ready-mom' not in values:
                values.append('sr-ready-mom')
        if dbd_check is not None and dbd_constant is not None:
            if 'use-constant' in dbd_check:
                values.append('dbd-ready-mom')
        if dbd_var is not None and dbd_depth is not None:
            if 'dbd-ready-mom' not in values:
                values.append('dbd-ready-mom')
        if wd_check is not None and wd_constant is not None:
            if 'use-constant' in wd_check:
                values.append('wd-ready-mom')
        if wd_var is not None and wd_depth is not None:
            if 'wd-ready-mom' not in values:
                values.append('wd-ready-mom')

        return values

    # Atualização de Seleção de Variável de anoxia:
    @app.callback(Output('event-var', 'options'),
                  [Input('select-age-var', 'value'),
                   Input('select-age-depth', 'value'),
                   Input('age-las', 'value')])
    def update_events_optns(var_str, var_depth, las_age):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        options = [{'label': 'Profundidade', 'value': 'prof'}]
        if var_str is not None and var_depth is not None:
            options.append({'label': var_str, 'value': 'idades'})
        if las_age is not None:
            options.append({'label': las_age, 'value': 'idades'})
        return options

    # Alert do COma (MOM):
    @app.callback([Output('mom-alert', 'color'),
                   Output('mom-alert', 'is_open'),
                   Output('mom-alert', 'children')],
                  [Input('mom-check', 'value'),
                   Input('select-mom-equation', 'value'),
                   Input('range-toc', 'disabled'),
                   Input('select-cf-equation', 'value'),
                   Input('select-be-equation', 'value')])
    def update_mom_alert(mom_check, mom_equation, range_available, cf_equation, be_equation):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if mom_check is None:
            raise PreventUpdate

        if mom_equation == 'muller-suess-1979':
            if sorted(mom_check) == ['dbd-ready-mom', 'pp-ready-mom', 'sr-ready-mom'] or sorted(mom_check) == [
                'dbd-ready-mom', 'pp-ready-mom', 'sr-ready-mom', 'wd-ready-mom']:
                if range_available is False:
                    return 'success', True, 'Variáveis prontas para simulação! (ajuste as CONFIGURAÇÕES e clique em EXECUTAR na guia de gráficos)'
                if range_available is True:
                    return 'warning', True, 'Intervalo de profundidade não disponível (está usando só constantes?)'

            else:
                return no_update, False, no_update

        if mom_equation == 'stein-1986':
            if sorted(mom_check) == ['dbd-ready-mom', 'pp-ready-mom', 'sr-ready-mom',
                                     'wd-ready-mom'] and cf_equation is not None:
                if range_available is False:
                    return 'success', True, 'Variáveis prontas para simulação! (apertar Plot Sim.Toc na guia de gráficos)'
                if range_available is True:
                    return 'warning', True, 'Intervalo de profundidade não disponível (está usando só constantes?)'

        if mom_equation == 'def-equation':
            if sorted(mom_check) == ['dbd-ready-mom', 'pp-ready-mom', 'sr-ready-mom',
                                     'wd-ready-mom'] and cf_equation is not None and be_equation is not None:
                if range_available is False:
                    return 'success', True, 'Variáveis prontas para simulação! (ajuste as CONFIGURAÇÕES e clique em EXECUTAR na guia de gráficos)'
                if range_available is True:
                    return 'warning', True, 'Intervalo de profundidade não disponível (está usando só constantes?)'

            else:
                return no_update, False, no_update
        else:
            return no_update, False, no_update

    ## Disable das opções de Carbon Flux e Burial Efficiency:
    @app.callback([Output('select-cf-equation', 'disabled'),
                   Output('select-be-equation', 'disabled')],
                  [Input('select-mom-equation', 'value')])
    def enable_cf_equation(mom_equation):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if mom_equation is None:
            raise PreventUpdate

        if mom_equation == 'stein-1986':
            return False, True
        if mom_equation == 'def-equation':
            return False, False
        else:
            return True, True

    ## Classificação de fácies:
    # Atualização de valores da checklist:
    @app.callback(Output('facies-checklist', 'value'),
                  [Input('mistura-export-dd', 'value'),
                   Input('mistura-figure', 'figure')])
    def update_checklist_facies(simulation_name, mistura_figure):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if simulation_name is None:
            return no_update

        df = pd.read_csv(f'static/{simulation_name}/{simulation_name}.csv', sep=',')
        vars = ['COT [%]', 'IH [mg HC/g COT]', 'IO  [mg CO₂/g COT]']
        values = []

        if vars[0] in df.columns:
            values.append('cot')
        if vars[1] in df.columns:
            values.append('ih')
        if vars[2] in df.columns:
            values.append('io')

        return values

    # Fácies - Fuzzy (Andre)
    @app.callback([Output('facies-figure', 'figure'),
                   Output('facies-spinner', 'children')],
                  [Input('facies-checklist', 'value')],
                  [State('mistura-export-dd', 'value')])
    def simulate_facies_fuzzy(checklist, simulation_name):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if simulation_name is None:
            return no_update
        if sorted(checklist) == ['cot', 'ih', 'io']:
            print('Simulando fácies (fuzzy)')
            df = pd.read_csv(f'static/{simulation_name}/{simulation_name}.csv', sep=',')
            fuzzy_df = fuzzy_maturarion(df, 'Profundidade [m]')
            fig = generate_curves(fuzzy_df, 'Profundidade [m]', ['COT [%]', 'IH [mg HC/g COT]', 'IO  [mg CO₂/g COT]'], ['of_class'])

            fuzzy_df.to_csv(f'static/{simulation_name}/{simulation_name}_qualidade.csv', index=False, sep=',', encoding='utf-8-sig')
            fuzzy_df.to_string(f'static/{simulation_name}/{simulation_name}_qualidade.txt', index=False)
            fuzzy_df.to_csv(f'static/{simulation_name}/{simulation_name}.csv', sep=',')
            las = lasio.read(f'static/{simulation_name}/{simulation_name}_qualidade.las')

            las.add_curve('Fácies Orgânicas', fuzzy_df['of_class'].values, unit='')

            with open(f'static/{simulation_name}/{simulation_name}_qualidade.las', mode='w', encoding='utf-8-sig') as f:
                las.write(f, version=2.0)

            z = zipfile.ZipFile(f'static/{simulation_name}.zip', 'w', zipfile.ZIP_DEFLATED)
            z.write(f'static/{simulation_name}/{simulation_name}_qualidade.csv')
            z.write(f'static/{simulation_name}/{simulation_name}_qualidade.txt')
            z.write(f'static/{simulation_name}/{simulation_name}_qualidade.las')
            z.close()
            return fig, no_update
        else:
            return no_update, no_update

    #### ABA MATURAÇÃO:
    @app.callback([  # Output('graficos-figure', 'figure'),
        Output('hi0-export-dd', 'options'),
        Output('hi0-export-dd', 'disabled'),
        Output('tr-export-dd', 'options'),
        Output('tr-export-dd', 'disabled'),
        Output('quantidade-export-dd', 'options'),
        Output('quantidade-export-dd', 'disabled'),
        Output('qualidade-export-dd', 'options'),
        Output('qualidade-export-dd', 'disabled'),
        Output('maturidade-export-dd', 'options'),
        Output('maturidade-export-dd', 'disabled'),
        Output('cot0-export-dd', 'options'),
        Output('cot0-export-dd', 'disabled'),
        Output('botao-plotagem-spinner', 'children')],

        [Input('botao-plotagem', 'n_clicks')],

        [
            # OPÇÕES
            State('hi0-export-dd', 'options'),
            State('tr-export-dd', 'options'),
            State('quantidade-export-dd', 'options'),
            State('qualidade-export-dd', 'options'),
            State('maturidade-export-dd', 'options'),
            State('cot0-export-dd', 'options'),
            # FIM OPÇÕES

            # COMEÇO hi0
            State('maturation-depth', 'value'),
            State('select-s2s3-var', 'value'),
            State('s2s3-constant', 'value'),
            State('s2s3-check', 'value'),
            State('maturation-filenames-div', 'children'),
            State('range-maturation', 'value'),
            State('select-hi0', 'value'),
            State('no-data-maturação', 'value'),
            State('select-tipo-grafico', 'value'),

            # FIM hi0

            # COMEÇO TR
            State('select-hi-var', 'value'),  # ih
            State('hi-constant', 'value'),  # ih
            State('hi-check', 'value'),  # ih
            State('select-s1-var', 'value'),  # s1
            State('s1-constant', 'value'),  # s1
            State('s1-check', 'value'),  # s1
            State('select-s2-var', 'value'),  # s2
            State('s2-constant', 'value'),  # s2
            State('s2-check', 'value'),  # s2
            State('range-maturation', 'value'),
            State('select-tr', 'value'),
            # State('select-eixo-x-txTransformacao', 'value'),
            # State('select-eixo-y-txTransformacao', 'value'),
            # FIM TR

            # COMEÇO POTENCIAL DE GERAÇÃO
            State('select-cotr-var', 'value'),  # cotr
            State('cotr-constant', 'value'),  # cotr
            State('cotr-check', 'value'),  # cotr
            State('select-quantidade-potencial', 'value'),
            # FIM POTENCILA DE GERAÇÃO

            # COMEÇO QUALIDADE DE MO
            State('select-io-var', 'value'),  # oi
            State('io-constant', 'value'),  # oi
            State('io-check', 'value'),  # oi
            State('select-qualidade-mo', 'value'),

            # COMEÇO MATURIDADE TÉRMICA
            State('select-tmax-var', 'value'),  # tmax
            State('tmax-constant', 'value'),  # tmax
            State('tmax-check', 'value'),  # tmax
            State('select-vitrinita-var', 'value'),  # vitrinita
            State('vitrinita-constant', 'value'),  # vitrinita
            State('vitrinita-check', 'value'),  # vitrinita
            State('select-maturidade-termica', 'value'),
            # FIM MATURIDADE TÉRMICA

            # COMEÇO COT E S2
            State('select-cot0', 'value')
            # FIM COT E S2
        ])
    def graph_maturation(n_clicks,
                            hi0_options, tr_options, quantidade_options, qualidade_options, maturidade_options,
                            cot0_options,
                            maturation_depth, s2s3_var, s2s3_constant, s2s3_check, maturation_path, s2s3_range,
                            hi0_select,
                            no_data, tipo_grafico,
                            hi_var, hi_constant, hi_check, s1_var, s1_constant, s1_check, s2_var, s2_constant, s2_check,
                            maturidade_range, tr_select,
                            cotr_var, cotr_constant, cotr_check, quantidade_select,
                            oi_var, oi_constant, oi_check, qualidade_select,
                            tmax_var, tmax_constant, tmax_check, ro_var, ro_constant, ro_check, maturidade_select,
                            qualidade_cot_select):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        print(n_clicks)
        print(tipo_grafico)
        eixo_x = ''
        eixo_y = ''

        if (tipo_grafico == 'grafico-hi'):

            if (hi0_options != None):
                valor_options_hi0 = len(hi0_options) + 1
                hi0_sim_options = [
                    {'label': 'Simulação de HI inicial ' + str(i + 1), 'value': 'hi0_simulation_' + str(i + 1)} for i in
                    range(0, valor_options_hi0, 1)]
            else:
                valor_options_hi0 = 1
                hi0_sim_options = [{'label': 'Simulação de HI inicial ' + str(1), 'value': 'hi0_simulation_' + str(1)}]

            result_hi0 = result_hi0_func(valor_options_hi0, maturation_depth, s2s3_var, s2s3_constant, s2s3_check,
                                         maturation_path, s2s3_range, hi0_select, no_data, eixo_x, eixo_y)

            fig = result_hi0

            return fig, hi0_sim_options, False, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

        if (tipo_grafico == 'grafico-transformacao'):

            if (tr_options != None):
                valor_options_tr = len(tr_options) + 1
                tr_sim_options = [
                    {'label': 'Simulação de Taxa de Tranformação ' + str(i + 1), 'value': 'tr_simulation_' + str(i + 1)}
                    for
                    i in range(0, valor_options_tr, 1)]
            else:
                valor_options_tr = 1
                tr_sim_options = [
                    {'label': 'Simulação de Taxa de Tranformação ' + str(1), 'value': 'tr_simulation_' + str(1)}]

            result_tr = result_tr_func(valor_options_tr,
                                       maturation_depth, s2s3_var, s2s3_constant, s2s3_check, maturation_path,
                                       hi_var, hi_constant, hi_check,
                                       s1_var, s1_constant, s1_check,
                                       s2_var, s2_constant, s2_check,
                                       maturidade_range, tr_select, hi0_select, eixo_x, eixo_y,
                                       no_data)

            fig = result_tr

            return fig, no_update, no_update, tr_sim_options, False, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

        if (tipo_grafico == 'grafico-potencial'):

            if (quantidade_options != None):
                valor_options_quantidade = len(quantidade_options) + 1
                quantidade_sim_options = [{'label': 'Simulação de Potencial de Geração ' + str(i + 1),
                                           'value': 'quantidade_simulation_' + str(i + 1)} for i in
                                          range(0, valor_options_quantidade, 1)]
            else:
                valor_options_quantidade = 1
                quantidade_sim_options = [
                    {'label': 'Simulação de Potencial de Geração ' + str(1),
                     'value': 'quantidade_simulation_' + str(1)}]

            result_quantidade = result_quantidade_func(valor_options_quantidade,
                                                       maturation_depth, cotr_var, cotr_constant, cotr_check,
                                                       maturation_path, s2_var, s2_constant,
                                                       s2_check, maturidade_range, quantidade_select, no_data)

            fig = result_quantidade

            return fig, no_update, no_update, no_update, no_update, quantidade_sim_options, False, no_update, no_update, no_update, no_update, no_update, no_update, no_update

        if (tipo_grafico == 'grafico-mo'):

            if (qualidade_options != None):
                valor_options_qualidade = len(qualidade_options) + 1
                qualidade_sim_options = [
                    {'label': 'Simulação de Qualidade ' + str(i + 1), 'value': 'qualidade_simulation_' + str(i + 1)} for
                    i
                    in range(0, valor_options_qualidade, 1)]
            else:
                valor_options_qualidade = 1
                qualidade_sim_options = [
                    {'label': 'Simulação de Qualidade ' + str(1), 'value': 'qualidade_simulation_' + str(1)}]

            result_mo = result_mo_func(valor_options_qualidade, maturation_depth,
                                       hi_var, hi_constant, hi_check,
                                       maturation_path, oi_var, oi_constant, oi_check,
                                       maturidade_range, qualidade_select, no_data)

            fig = result_mo
            return fig, no_update, no_update, no_update, no_update, no_update, no_update, qualidade_sim_options, False, no_update, no_update, no_update, no_update, no_update

        if (tipo_grafico == 'grafico-termica'):

            if (maturidade_options != None):
                valor_options_maturidade = len(maturidade_options) + 1
                maturidade_sim_options = [
                    {'label': 'Simulação de Maturidade ' + str(i + 1), 'value': 'maturidade_simulation_' + str(i + 1)}
                    for i
                    in range(0, valor_options_maturidade, 1)]
            else:
                valor_options_maturidade = 1
                maturidade_sim_options = [
                    {'label': 'Simulação de Maturidade ' + str(1), 'value': 'maturidade_simulation_' + str(1)}]

            result_maturidade_termica = result_maturidade_func(valor_options_maturidade, maturation_depth,
                                                               hi_var, hi_constant, hi_check,
                                                               maturation_path, tmax_var, tmax_constant, tmax_check,
                                                               ro_var, ro_constant, ro_check, maturidade_range,
                                                               maturidade_select, no_data)

            fig = result_maturidade_termica
            return fig, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, maturidade_sim_options, False, no_update, no_update, no_update

        if (tipo_grafico == 'grafico-cot-s2'):

            if (cot0_options != None):
                valor_options_cot0 = len(cot0_options) + 1
                cot0_sim_options = [
                    {'label': 'Simulação de COT e S2 iniciais ' + str(i + 1),
                     'value': 'cot0_s20_simulation_' + str(i + 1)}
                    for i in range(0, valor_options_cot0, 1)]
            else:
                valor_options_cot0 = 1
                cot0_sim_options = [
                    {'label': 'Simulação de COT e S2 iniciais ' + str(1), 'value': 'cot0_s20_simulation_' + str(1)}]

            result_cot_s2 = result_cot_s2_func(valor_options_cot0, maturation_depth, hi_var, hi_constant, hi_check,
                                               maturation_path, s1_var, s1_constant, s1_check,
                                               s2_var, s2_constant, s2_check,
                                               s2s3_var, s2s3_constant, s2s3_check,
                                               ro_var, ro_constant, ro_check,
                                               cotr_var, cotr_constant, cotr_check, maturidade_range,
                                               hi0_select, tr_select, qualidade_cot_select, eixo_x, eixo_y, no_data)

            fig = result_cot_s2
            return fig, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, cot0_sim_options, False, no_update

    # Nova simulação de Maturação:
    @app.callback([Output('maturation-simulations-dd', 'options'),
                   Output('maturation-simulations-dd', 'value'),
                   Output('maturacao-export-dd', 'options'),
                   Output('maturacao-export-dd', 'value'),
                   Output('compare-maturation-results', 'options')
                   ],
                  [Input('simulate-maturacao-button', 'n_clicks')],
                  [State('eq-dataset', 'value'),
                   State('eq-clusters', 'value'),
                   State('maturacao-vars-check', 'value'),
                   State('select-cotr-var', 'value'),  # cotr
                   State('cotr-constant', 'value'),  # cotr
                   State('cotr-check', 'value'),  # cotr
                   State('select-s2-var', 'value'),  # s2
                   State('s2-constant', 'value'),  # s2
                   State('s2-check', 'value'),  # s2
                   State('select-hi-var', 'value'),  # hi
                   State('hi-constant', 'value'),  # hi
                   State('hi-check', 'value'),  # hi
                   State('select-tmax-var', 'value'),  # tmax
                   State('tmax-constant', 'value'),  # tmax
                   State('tmax-check', 'value'),  # tmax
                   State('select-vitrinita-var', 'value'),  # vitrinita
                   State('vitrinita-constant', 'value'),  # vitrinita
                   State('vitrinita-check', 'value'),  # vitrinita
                   State('select-tr', 'value'),  # tr
                   State('maturation-simulations-dd', 'options'),
                   State('maturacao-export-dd', 'options'),
                   State('no-data-maturação', 'value'),
                   State('maturation-depth', 'value'),
                   State('lamina-dagua', 'value')
                   ])
    def simulate_maturation(n_clicks, filepath, clusters, simulate_vars,
                            cotr_val, cotr_const, cotr_check,
                            s2_val, s2_const, s2_check,
                            hi_val, hi_const, hi_check,
                            tmax_val, tmax_const, tmax_check,
                            ro_val, ro_const, ro_check,
                            tr_eq,
                            options_dataset, options_export,
                            no_data,
                            depth_val,
                            lamina_dagua):
        # Exceções:
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filepath is None or clusters is None:
            return no_update

        # Leitura dos dados:
        maturation_df = pd.read_csv(filepath, sep=',', na_values=no_data)
        # maturation_df.dropna(inplace=True)
        maturation_df.Cluster = maturation_df.Cluster.astype(str)
        maturation_df = maturation_df[maturation_df['Cluster'].isin(list(clusters))]
        # Simulações:
        equations = []
        simulations = []
        simulated_val = []
        if dash.callback_context.triggered[0]['prop_id'] == 'simulate-maturacao-button.n_clicks':
            if 'ca' in simulate_vars:
                if s2_val is None and 'use-constant' in s2_check:
                    get_s2 = lambda row: s2_const
                    maturation_df['S2 [mg HC/g rocha]'] = maturation_df.apply(get_s2, axis=1)
                    s2_val = 'S2 [mg HC/g rocha]'
                if cotr_val is None and 'use-constant' in cotr_check:
                    get_cotr = lambda row: cotr_const
                    maturation_df['COTr (COT medido na rocha) [%]'] = maturation_df.apply(get_cotr, axis=1)
                    cotr_val = 'COTr (COT medido na rocha) [%]'
                # maturation_df.dropna(subset=[cotr_val, s2_val], inplace=True)
                ca_df = maturation_df[[cotr_val, s2_val, 'Cluster']].dropna(subset=[cotr_val, s2_val])
                cot_inerte = []
                from sklearn import linear_model
                from sklearn.preprocessing import StandardScaler
                for k in clusters:
                    Y = ca_df[ca_df.Cluster == str(k)][cotr_val].values
                    X = ca_df[ca_df.Cluster == str(k)][s2_val].values

                    X = X.reshape(len(X), 1)
                    Y = Y.reshape(len(Y), 1)

                    # Normalizando X e Y
                    scaler = StandardScaler()
                    X = scaler.fit_transform(X)
                    Y = scaler.fit_transform(Y)

                    regr = linear_model.LinearRegression(fit_intercept=True)
                    regr.fit(X, Y)

                    cot_inerte.append(regr.intercept_[0])
                contador = 0
                for ci in range(0, len(cot_inerte)):
                    if contador == 0:
                        calculate_ca = lambda row: row[cotr_val] - cot_inerte[ci] if row['Cluster'] == str(
                            clusters[ci]) else np.nan
                        get_ci = lambda row: cot_inerte[ci] if row['Cluster'] == str(clusters[ci]) else np.nan
                    else:
                        calculate_ca = lambda row: row[cotr_val] - cot_inerte[ci] if row['Cluster'] == str(
                            clusters[ci]) else row['Carbono Ativo [%]']
                        get_ci = lambda row: cot_inerte[ci] if row['Cluster'] == str(clusters[ci]) else row[
                            'Carbono Inerte [%]']
                    ca_df['Carbono Ativo [%]'] = ca_df.apply(calculate_ca, axis=1)
                    ca_df['Carbono Inerte [%]'] = ca_df.apply(get_ci, axis=1)
                    contador = contador + 1
                maturation_df = pd.merge(maturation_df, ca_df, on=[cotr_val, s2_val, 'Cluster'], how='left', suffixes=('_antigo', None))
                maturation_df.drop_duplicates(inplace=True)
                equations.append('Dahl. et al (2004)')
                simulations.append('Carbono Ativo [%]')
                simulated_val.append('Carbono Ativo [%]')
                maturation_df['Carbono Inerte [%]'] = maturation_df.apply(
                    lambda x: x[cotr_val] if x[cotr_val] <= x['Carbono Inerte [%]'] else x['Carbono Inerte [%]'],
                    axis=1)
                maturation_df['Carbono Ativo [%]'] = maturation_df.apply(
                    lambda x: x[cotr_val] - x['Carbono Inerte [%]'],
                    axis=1)

            if 'hi0' in simulate_vars:
                if s2_val is None and 'use-constant' in s2_check:
                    get_s2 = lambda row: s2_const
                    maturation_df['S2 [mg HC/g rocha]'] = maturation_df.apply(get_s2, axis=1)
                    s2_val = 'S2 [mg HC/g rocha]'
                # maturation_df.dropna(subset=[s2_val], inplace=True)
                hi0_df = maturation_df[[s2_val, 'Carbono Ativo [%]']].dropna(subset=[s2_val])
                hi0_df = hi0_dahl_2004(hi0_df, s2_val)
                maturation_df = pd.merge(maturation_df, hi0_df, on=[s2_val, 'Carbono Ativo [%]'], how='left', suffixes=('_antigo', None))
                maturation_df.drop_duplicates(inplace=True)
                equations.append('Dahl. et al (2004)')
                simulations.append('IH\u2080 Ativo [mg HC/g COT]')
                simulated_val.append('IH\u2080 Ativo [mg HC/g COT]')
                maturation_df['IH\u2080 Ativo [mg HC/g COT]'] = maturation_df.apply(
                    lambda x: 999 if x['IH\u2080 Ativo [mg HC/g COT]'] > 999 else x['IH\u2080 Ativo [mg HC/g COT]'],
                    axis=1)

            if 'tr' in simulate_vars:
                if hi_val is None and 'use-constant' in hi_const:
                    get_hi = lambda row: hi_const
                    maturation_df['IH [mg HC/g COT]'] = maturation_df.apply(get_hi, axis=1)
                    hi_val = 'IH [mg HC/g COT]'
                if ro_val is None and 'use-constant' in ro_const:
                    get_ro = lambda row: ro_const
                    maturation_df['Refletância da Vitrinita [Ro%]'] = maturation_df.apply(get_ro, axis=1)
                    hi_val = 'Refletância da Vitrinita [Ro%]'
                # maturation_df.dropna(subset=[hi_val], inplace=True)
                #tr_df = maturation_df[[hi_val, 'IH\u2080 Ativo [mg HC/g COT]']].dropna(subset=[hi_val])
                #if tr_eq == 'justwan-dahl-2005':
                #    tr_df = tr_justwan_dahl(tr_df, 'IH\u2080 Ativo [mg HC/g COT]', hi_val)
                #    equations.append('Justwan & Dahl (2005)')
                #    simulations.append('Taxa de Transformação [v/v]')
                #if tr_eq == 'jarvie-2012':
                #    tr_df = tr_jarvie_2012(tr_df, hi_val, 'IH\u2080 Ativo [mg HC/g COT]')
                #    equations.append('Jarvie el al. (2012)')
                #    simulations.append('Taxa de Transformação [v/v]')
                if tr_eq == 'justwan-dahl-2005' or tr_eq == 'jarvie-2012':
                    tr_df = maturation_df[[hi_val, 'IH\u2080 Ativo [mg HC/g COT]']].dropna(subset=[hi_val])
                    if tr_eq == 'justwan-dahl-2005':
                        tr_df = tr_justwan_dahl(tr_df, 'IH\u2080 Ativo [mg HC/g COT]', hi_val)
                        equations.append('Justwan & Dahl (2005)')
                        simulations.append('Taxa de Transformação [v/v]')
                    if tr_eq == 'jarvie-2012':
                        tr_df = tr_jarvie_2012(tr_df, hi_val, 'IH\u2080 Ativo [mg HC/g COT]')
                        equations.append('Jarvie el al. (2012)')
                        simulations.append('Taxa de Transformação [v/v]')

                    maturation_df = pd.merge(maturation_df, tr_df, on=[hi_val, 'IH\u2080 Ativo [mg HC/g COT]'],
                                             how='left', suffixes=('_antigo', None))
                    maturation_df.drop_duplicates(inplace=True)
                    get_max_tr = lambda row: 1 if row['Taxa de Transformação [v/v]'] > 1 else row[
                        'Taxa de Transformação [v/v]']
                    maturation_df['Taxa de Transformação [v/v]'] = maturation_df.apply(get_max_tr, axis=1)
                else:
                    maturation_df = waples(maturation_df, tr_eq, ro_val, depth_val, lamina_dagua)
                    tr_eq_dict = {
                        'waples-1998-1': 'Waples & Marzi (1998) Tipo 1',
                        'waples-1998-2': 'Waples & Marzi (1998) Tipo 2',
                        'waples-1998-3': 'Waples & Marzi (1998) Tipo 3'
                    }
                    equations.append(tr_eq_dict[tr_eq])
                    simulations.append('Taxa de Transformação [v/v]')
                #maturation_df = pd.merge(maturation_df, tr_df, on=[hi_val, 'IH\u2080 Ativo [mg HC/g COT]'], how='left', suffixes=('_antigo', None))
                #maturation_df.drop_duplicates(inplace=True)
                #get_max_tr = lambda row: 1 if row['Taxa de Transformação [v/v]'] > 1 else row[
                #    'Taxa de Transformação [v/v]']
                #maturation_df['Taxa de Transformação [v/v]'] = maturation_df.apply(get_max_tr, axis=1)
                simulated_val.append('Taxa de Transformação [v/v]')

            if 'cot0' in simulate_vars:
                if s2_val is None and 'use-constant' in s2_check:
                    get_s2 = lambda row: s2_const
                    maturation_df['S2 [mg HC/g rocha]'] = maturation_df.apply(get_s2, axis=1)
                    s2_val = 'S2 [mg HC/g rocha]'
                if cotr_val is None and 'use-constant' in cotr_check:
                    get_cotr = lambda row: cotr_const
                    maturation_df['COTr (COT medido na rocha) [%]'] = maturation_df.apply(get_cotr, axis=1)
                    cotr_val = 'COTr (COT medido na rocha) [%]'
                # maturation_df.dropna(subset=[s2_val, cotr_val], inplace=True)
                cot0_df = maturation_df[[cotr_val, s2_val, 'Taxa de Transformação [v/v]']].dropna(
                    subset=[cotr_val, s2_val, 'Taxa de Transformação [v/v]'])
                cot0_df = cot0_justwan_dahl(cot0_df, cotr_val, s2_val, 'Taxa de Transformação [v/v]', 0.086)
                maturation_df = pd.merge(maturation_df, cot0_df, on=[cotr_val, s2_val, 'Taxa de Transformação [v/v]'],
                                         how='left', suffixes=('_antigo', None))
                maturation_df.drop_duplicates(inplace=True)
                equations.append('Justwan & Dahl (2005)')
                simulations.append('COT\u2080 [%]')
                simulated_val.append('COT\u2080 [%]')

            if 's20' in simulate_vars:
                if s2_val is None and 'use-constant' in s2_check:
                    get_s2 = lambda row: s2_const
                    maturation_df['S2 [mg HC/g rocha]'] = maturation_df.apply(get_s2, axis=1)
                    s2_val = 'S2 [mg HC/g rocha]'
                # maturation_df.dropna(subset=[s2_val], inplace=True)
                s20_df = maturation_df[[s2_val, 'Taxa de Transformação [v/v]']].dropna(
                    subset=[s2_val, 'Taxa de Transformação [v/v]'])
                s20_df = s20_justwan_dahl(s20_df, s2_val, 'Taxa de Transformação [v/v]')
                maturation_df = pd.merge(maturation_df, s20_df, on=[s2_val, 'Taxa de Transformação [v/v]'], how='left', suffixes=('_antigo', None))
                maturation_df.drop_duplicates(inplace=True)
                equations.append('Justwan & Dahl (2005)')
                simulations.append('S2\u2080 [mg HC/g rocha]')
                simulated_val.append('S2\u2080 [mg HC/g rocha]')

            if 'ro' in simulate_vars:
                if tmax_val is None and 'use-constant' in tmax_check:
                    get_tmax = lambda row: tmax_const
                    maturation_df['Temperatura Máxima [ºC]'] = maturation_df.apply(get_tmax, axis=1)
                    tmax_val = 'Temperatura Máxima [ºC]'
                get_ro = lambda row: 0.018 * row[tmax_val] - 7.16
                # maturation_df.dropna(subset=[tmax_val], inplace=True)
                ro_df = maturation_df[[tmax_val]].dropna(subset=[tmax_val])
                ro_df['R\u2092 calculada [%]'] = ro_df.apply(get_ro, axis=1)
                maturation_df = pd.merge(maturation_df, ro_df, on=[tmax_val], how='left', suffixes=('_antigo', None))
                maturation_df.drop_duplicates(inplace=True)
                equations.append('Jarvie et al. (2001)')
                simulations.append('R\u2092 calculada [%]')
                simulated_val.append('R\u2092 calculada [%]')
                maturation_df['R\u2092 calculada [%]'] = maturation_df.apply(
                    lambda x: 0 if x['R\u2092 calculada [%]'] < 0 else x['R\u2092 calculada [%]'] if
                    x['R\u2092 calculada [%]'] < 2 else 2, axis=1)

                maturation_df['Carbono Inerte [%]'] = maturation_df.apply(
                    lambda x: x[cotr_val] if x[cotr_val] <= x['Carbono Inerte [%]'] else x['Carbono Inerte [%]'],
                    axis=1)
                maturation_df['Carbono Ativo [%]'] = maturation_df.apply(
                    lambda x: x[cotr_val] - x['Carbono Inerte [%]'],
                    axis=1)

            if 'hi0-normal' in simulate_vars:
                get_hi0 = lambda row: (row['S2\u2080 [mg HC/g rocha]'] * 100) / row['COT\u2080 [%]']
                maturation_df['IH\u2080 [mg HC/g COT]'] = maturation_df.apply(get_hi0, axis=1)
                maturation_df.drop_duplicates(inplace=True)
                equations.append('Dahl et al. (2004)')
                simulations.append('IH\u2080 [mg HC/g COT]')
                simulated_val.append('IH\u2080 [mg HC/g COT]')

            # Salvando simulações:
            filename = f'Simulacao_maturacao_{n_clicks}'
            value = 'static/' + filename + '.csv'
            maturation_df.to_csv('static/' + filename + '.csv', index=False, sep=',')
            if options_dataset is not None:
                options_dataset.append({'label': filename, 'value': value})
            else:
                options_dataset = [{'label': filename, 'value': value}]

            # Criando tabelas resultado:
            config_equations = pd.DataFrame({'Simulação': simulations,
                                             'Referência': equations}).sort_values('Simulação')

            # Tabela com dados simulados:
            simulated_vars_df = maturation_df[simulated_val].describe().transpose().round(2).rename(
                columns={'mean': 'média', 'std': '2σ', 'max': 'máx'})
            simulated_vars_df.drop(columns='count', inplace=True)
            simulated_vars_df.insert(0, 'Simulações', simulated_vars_df.index)

            # Criando exportações:
            maturation_df.to_csv(f'static/{filename}.csv', index=False, sep=',', encoding='utf-8-sig')
            maturation_df.to_string(f'static/{filename}.txt', index=False)
            maturation_df.to_excel(f'static/{filename}.xlsx', sheet_name=f'{filename}')

            config_equations.to_csv(f'static/{filename}_equacoes.csv', index=False, sep=',', encoding='utf-8-sig')
            config_equations.to_string(f'static/{filename}_equacoes.txt', index=False)

            simulated_vars_df.to_csv(f'static/{filename}_estatisticas.csv', index=False, sep=',', encoding='utf-8-sig')
            simulated_vars_df.to_string(f'static/{filename}_estatisticas.txt', index=False)

            z = zipfile.ZipFile(f'static/{filename}.zip', 'w', zipfile.ZIP_DEFLATED)
            z.write(f'static/{filename}.txt')
            z.write(f'static/{filename}.csv')
            z.write(f'static/{filename}_equacoes.txt')
            z.write(f'static/{filename}_equacoes.csv')
            z.write(f'static/{filename}_estatisticas.txt')
            z.write(f'static/{filename}_estatisticas.csv')
            z.write(f'static/{filename}.xlsx')
            z.close()

            if options_export is not None:
                options_export.append({'label': f'Simulação {n_clicks}', 'value': filename})
            else:
                options_export = [{'label': f'Simulação {n_clicks}', 'value': filename}]

        return options_dataset, value, options_export, filename, options_dataset

    @app.callback(Output('justwan-dahl-2005-s20-check', 'value'),
                  [Input('select-s2-var', 'value'),
                   Input('s2-check', 'value'),
                   Input('tr-card', 'color')],
                  [State('s2-constant', 'value')])
    def update_s20_check(s2_var, s2_check, color, s2_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []
        # Checando se as variáveis estão definidas:
        if s2_check is not None and s2_constant is not None:
            if 'use-constant' in s2_check:
                values.append('s2')
        if s2_var is not None:
            if 's2' not in values:
                values.append('s2')
        if color == 'success':
            values.append('tr')
        return values

    @app.callback(Output('eq1-ro-check', 'value'),
                  [Input('select-tmax-var', 'value'),
                   Input('tmax-check', 'value')],
                  [State('tmax-constant', 'value')])
    def update_ro_check(tmax_var, tmax_check, tmax_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []
        # Checando se as variáveis estão definidas:
        if tmax_check is not None and tmax_constant is not None:
            if 'use-constant' in tmax_check:
                values.append('tmax')
        if tmax_var is not None:
            if 'tmax' not in values:
                values.append('tmax')
        return values

    @app.callback(Output('maturacao-figure', 'figure'),
                  [Input('maturation-x-dd', 'value'),
                   Input('maturation-y-dd', 'value'),
                   Input('maturation-z-dd', 'value'),
                   Input('maturation-scale', 'value'),
                   Input('colorscale-dd', 'value'),
                   Input('eixo-y', 'value'),
                   Input('plot-type', 'value')],
                  [State('maturation-simulations-dd', 'value'),
                   State('maturacao-figure', 'figure')])
    def update_maturacao_graph(x, y, z, scale, colorscale, eixo_y, plot_type, filepath, figure):
        if not dash.callback_context.triggered:
            raise PreventUpdate

        if filepath is None:
            raise PreventUpdate

        if x == [] or y is None:
            return no_update

        func_dict = {
            'scatter': px.scatter,
            'line': px.line
        }

        plot = func_dict[plot_type]

        if len(x) == 1:
            x = x[0]

        if dash.callback_context.triggered[0]['prop_id'] == 'maturation-scale.value':
            # Alterou os eixos
            if scale == 'linear':
                figure['layout']['xaxis']['type'] = 'linear'
                figure['layout']['yaxis']['type'] = 'linear'

                figure['layout']['xaxis']['range'] = [(min(figure['data'][0]['x'])), (max(figure['data'][0]['x']))]
                figure['layout']['yaxis']['range'] = [(max(figure['data'][0]['y'])), (min(figure['data'][0]['y']))]

            if scale == 'log':
                figure['layout']['xaxis']['type'] = 'log'
                figure['layout']['yaxis']['type'] = 'log'

                figure['layout']['xaxis']['range'] = [log10(min(figure['data'][0]['x'])),
                                                      log10(max(figure['data'][0]['x']))]
                figure['layout']['yaxis']['range'] = [log10(max(figure['data'][0]['y'])),
                                                      log10(min(figure['data'][0]['y']))]

            return figure

        if dash.callback_context.triggered[0]['prop_id'] == 'eixo-y.value':
            # Alterou os eixos
            range_min = min(figure['layout']['yaxis']['range'])
            range_max = max(figure['layout']['yaxis']['range'])
            if eixo_y == 'normal':
                figure['layout']['yaxis']['range'] = [range_min, range_max]
            if eixo_y == 'inverse':
                figure['layout']['yaxis']['range'] = [range_max, range_min]
            return figure

        maturation_df = pd.read_csv(filepath, sep=',')
        maturation_df['Cluster'] = maturation_df['Cluster'].astype(str)
        if x is not None and y is not None:
            print("print aqui", x, y)
            if plot_type == 'line':
                fig = plot(data_frame=maturation_df, x=x, y=y)

                if (x == 'COT [%]' and y == 'S2 [mg HC/g rocha]'):
                    # Marcações de S2
                    # figura.add_hline(y=0, line_dash="dot",
                    #      annotation_text="Ruim", fillcolor="green",
                    #      annotation=dict(font_size=14, font_family="Times New Roman"),
                    #      annotation_position="top right")
                    fig.add_hline(y=2.5, line_dash="dot",
                                  annotation_text="Razoável", fillcolor="green",
                                  annotation=dict(font_size=12, font_family="Times New Roman"),
                                  annotation_position="top right")
                    fig.add_hline(y=5, line_dash="dot",
                                  annotation_text="Bom", fillcolor="green",
                                  annotation=dict(font_size=12, font_family="Times New Roman"),
                                  annotation_position="top right")
                    fig.add_hline(y=10, line_dash="dot",
                                  annotation_text="Excelente", fillcolor="green",
                                  annotation=dict(font_size=12, font_family="Times New Roman"),
                                  annotation_position="top right")

                    # Marcações de COT
                    # figura.add_vline(x=0, line_dash="dot",
                    #      annotation_text="Ruim", fillcolor="green",
                    #      annotation=dict(font_size=14, font_family="Times New Roman"),
                    #      annotation_position="top right")
                    fig.add_vline(x=0.5, line_dash="dot",
                                  annotation_text="Razoável", fillcolor="green",
                                  annotation=dict(font_size=12, font_family="Times New Roman"),
                                  annotation_position="top right")
                    fig.add_vline(x=1, line_dash="dot",
                                  annotation_text="Bom", fillcolor="green",
                                  annotation=dict(font_size=12, font_family="Times New Roman"),
                                  annotation_position="top right")
                    fig.add_vline(x=2, line_dash="dot",
                                  annotation_text="Excelente", fillcolor="green",
                                  annotation=dict(font_size=12, font_family="Times New Roman"),
                                  annotation_position="top right")

                range_min = min(maturation_df[y].values)
                range_max = max(maturation_df[y].values)
                if eixo_y == 'normal':
                    fig['layout']['yaxis']['range'] = [range_min, range_max]
                if eixo_y == 'inverse':
                    fig['layout']['yaxis']['range'] = [range_max, range_min]

                return fig
            else:
                if colorscale:
                    fig = plot(data_frame=maturation_df, x=x, y=y, color_continuous_scale=colorscale)

                    if (x == 'COT [%]' and y == 'S2 [mg HC/g rocha]'):
                        # Marcações de S2
                        # figura.add_hline(y=0, line_dash="dot",
                        #      annotation_text="Ruim", fillcolor="green",
                        #      annotation=dict(font_size=14, font_family="Times New Roman"),
                        #      annotation_position="top right")
                        fig.add_hline(y=2.5, line_dash="dot",
                                      annotation_text="Razoável", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")
                        fig.add_hline(y=5, line_dash="dot",
                                      annotation_text="Bom", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")
                        fig.add_hline(y=10, line_dash="dot",
                                      annotation_text="Excelente", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")

                        # Marcações de COT
                        # figura.add_vline(x=0, line_dash="dot",
                        #      annotation_text="Ruim", fillcolor="green",
                        #      annotation=dict(font_size=14, font_family="Times New Roman"),
                        #      annotation_position="top right")
                        fig.add_vline(x=0.5, line_dash="dot",
                                      annotation_text="Razoável", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")
                        fig.add_vline(x=1, line_dash="dot",
                                      annotation_text="Bom", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")
                        fig.add_vline(x=2, line_dash="dot",
                                      annotation_text="Excelente", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")

                    if z is not None:
                        fig = plot(data_frame=maturation_df, x=x, y=y, color=z, color_continuous_scale=colorscale)

                else:
                    fig = plot(data_frame=maturation_df, x=x, y=y)

                    if (x == 'COT [%]' and y == 'S2 [mg HC/g rocha]'):
                        # Marcações de S2
                        # figura.add_hline(y=0, line_dash="dot",
                        #      annotation_text="Ruim", fillcolor="green",
                        #      annotation=dict(font_size=14, font_family="Times New Roman"),
                        #      annotation_position="top right")
                        fig.add_hline(y=2.5, line_dash="dot",
                                      annotation_text="Razoável", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")
                        fig.add_hline(y=5, line_dash="dot",
                                      annotation_text="Bom", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")
                        fig.add_hline(y=10, line_dash="dot",
                                      annotation_text="Excelente", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")

                        # Marcações de COT
                        # figura.add_vline(x=0, line_dash="dot",
                        #      annotation_text="Ruim", fillcolor="green",
                        #      annotation=dict(font_size=14, font_family="Times New Roman"),
                        #      annotation_position="top right")
                        fig.add_vline(x=0.5, line_dash="dot",
                                      annotation_text="Razoável", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")
                        fig.add_vline(x=1, line_dash="dot",
                                      annotation_text="Bom", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")
                        fig.add_vline(x=2, line_dash="dot",
                                      annotation_text="Excelente", fillcolor="green",
                                      annotation=dict(font_size=12, font_family="Times New Roman"),
                                      annotation_position="top right")

                    if z is not None:
                        fig = plot(data_frame=maturation_df, x=x, y=y, color=z)

                range_min = min(maturation_df[y].values)
                range_max = max(maturation_df[y].values)
                if eixo_y == 'normal':
                    fig['layout']['yaxis']['range'] = [range_min, range_max]
                if eixo_y == 'inverse':
                    fig['layout']['yaxis']['range'] = [range_max, range_min]

                return fig
        else:
            return figure

    # Callbacks de checagens das equações:
    @app.callback(Output('reftable-collapse', 'is_open'),
                  Input('select-quantidade-potencial', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            raise PreventUpdate
        if value == 'reftable':
            return True
        else:
            return False

    @app.callback(Output('hi0-collapse', 'is_open'),
                  Input('select-hi0', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value == 'reftable':
            return True
        else:
            return False

    @app.callback(Output('eq1-hi0-normal-collapse', 'is_open'),
                  Input('select-hi0-normal', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value == 'dahl-2004':
            return True
        else:
            return False

    @app.callback(Output('justwan-dahl-2005-collapse', 'is_open'),
                  Input('select-tr', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value == 'justwan-dahl-2005':
            return True
        else:
            return False

    @app.callback(Output('waples-collapse', 'is_open'),
                  Input('select-tr', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value == 'waples-1998-1' or value == 'waples-1998-2' or value == 'waples-1998-3':
            return True
        else:
            return False

    @app.callback(Output('jarvie-2012-collapse', 'is_open'),
                  Input('select-tr', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value == 'jarvie-2012':
            return True
        else:
            return False

    @app.callback(Output('zhuoheng-2015-collapse', 'is_open'),
                  Input('select-tr', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value == 'zhuoheng-2015':
            return True
        else:
            return False

    @app.callback(Output('peters-1996-collapse', 'is_open'),
                  Input('select-tr', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value == 'peters-1996':
            return True
        else:
            return False

    @app.callback(Output('jarvie-2007-collapse', 'is_open'),
                  Input('select-tr', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value == 'jarvie-2007':
            return True
        else:
            return False

    @app.callback(Output('reftable-qualidade-collapse', 'is_open'),
                  Input('select-qualidade-mo', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            raise PreventUpdate
        if value == 'reftable':
            return True
        else:
            return False

    @app.callback(Output('reftable-maturidade-collapse', 'is_open'),
                  Input('select-maturidade-termica', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            return False
        if value == 'reftable':
            return True
        else:
            return False

    @app.callback(Output('justwan-dahl-2005-cot0-collapse', 'is_open'),
                  Input('select-cot0', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            return False
        if value == 'justwan-dahl-2005':
            return True
        else:
            return False

    @app.callback(Output('jarvie-2012-cot0-collapse', 'is_open'),
                  Input('select-cot0', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            return False
        if value == 'jarvie-2012':
            return True
        else:
            return False

    @app.callback(Output('cotinerte-dahl-2004-collapse', 'is_open'),
                  Input('select-cotinerte', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            return False
        if value == 'dahl-2004':
            return True
        else:
            return False

    @app.callback(Output('justwan-dahl-2005-s20-collapse', 'is_open'),
                  Input('select-s20', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            return False
        if value == 'justwan-dahl-2005':
            return True
        else:
            return False

    @app.callback(Output('hi0-dahl-2004-collapse', 'is_open'),
                  Input('select-hi0', 'value'))
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            return False
        if value == 'dahl-2004':
            return True
        else:
            return False

    @app.callback(Output('eq1-ro-collapse', 'is_open'),
                  Input('select-ro', 'value'))
    def open_ro_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            return False
        if value == 'eq1':
            return True
        else:
            return False

    @app.callback(Output('maturacao-vars-check', 'value'),
                  [Input('cotinerte-card', 'color'),
                   Input('hi0-card', 'color'),
                   Input('tr-card', 'color'),
                   Input('cot0-card', 'color'),
                   Input('s20-card', 'color'),
                   Input('ro-card', 'color'),
                   Input('hi0-normal-card', 'color')])
    def update_maturacao_check(cotinerte, hi0, tr, cot0, s20, ro, hi0_normal):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        value = []
        if cotinerte == 'success':
            value.append('ca')
        if hi0 == 'success':
            value.append('hi0')
        if tr == 'success':
            value.append('tr')
        if cot0 == 'success':
            value.append('cot0')
        if s20 == 'success':
            value.append('s20')
        if ro == 'success':
            value.append('ro')
        if hi0_normal == 'success':
            value.append('hi0-normal')
        return value

    # Checklist de variáveis necessárias:
    @app.callback(Output('quantidade-potencial-check', 'value'),
                  [Input('maturation-depth', 'value'),
                   Input('select-cotr-var', 'value'),
                   Input('cotr-check', 'value'),
                   Input('select-s2-var', 'value'),
                   Input('s2-check', 'value')],
                  [State('cotr-constant', 'value'),
                   State('s2-constant', 'value')])
    def update_quantidade_check(maturation_depth, cotr_var, cotr_check,
                                s2_var, s2_check,
                                cotr_constant, s2_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []

        # Checando se as variáveis estão definidas:
        if cotr_check is not None and cotr_constant is not None:
            if 'use-constant' in cotr_check:
                values.append('cotr')
        if cotr_var is not None and maturation_depth is not None:
            if 'cotr-ready-mom' not in values:
                values.append('cotr')
        if s2_check is not None and s2_constant is not None:
            if 'use-constant' in s2_check:
                values.append('s2')
        if s2_var is not None and maturation_depth is not None:
            if 's2-ready-mom' not in values:
                values.append('s2')

        return values

    @app.callback(Output('qualidade-mo-check', 'value'),
                  [Input('maturation-depth', 'value'),
                   Input('select-hi-var', 'value'),
                   Input('hi-check', 'value'),
                   Input('select-io-var', 'value'),
                   Input('io-check', 'value')],
                  [State('hi-constant', 'value'),
                   State('io-constant', 'value')])
    def update_qualidade_check(maturation_depth, ih_var, ih_check,
                               io_var, io_check,
                               ih_constant, io_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []

        # Checando se as variáveis estão definidas:
        if ih_check is not None and ih_constant is not None:
            if 'use-constant' in ih_check:
                values.append('ih')
        if ih_var is not None and maturation_depth is not None:
            if 'ih-ready-mom' not in values:
                values.append('ih')
        if io_check is not None and io_constant is not None:
            if 'use-constant' in io_check:
                values.append('io')
        if io_var is not None and maturation_depth is not None:
            if 'io-ready-mom' not in values:
                values.append('io')

        return values

    # Checagem de carbono ativo:
    @app.callback(Output('cotinerte-dahl-2004-check', 'value'),
                  [Input('select-cotr-var', 'value'),
                   Input('cotr-check', 'value')],
                  [State('cotr-constant', 'value')])
    def update_carbonoativo_check(cotr_var, cotr_check, cotr_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []
        # Checando se as variáveis estão definidas:
        if cotr_check is not None and cotr_constant is not None:
            if 'use-constant' in cotr_check:
                values.append('cotr')
        if cotr_var is not None:
            if 'cotr' not in values:
                values.append('cotr')
        return values

    @app.callback([Output('cotinerte-dahl-2004-alert', 'is_open'),
                   Output('cotinerte-dahl-2004-alert', 'color'),
                   Output('cotinerte-dahl-2004-alert', 'children'),
                   Output('cotinerte-card', 'color')],
                  [Input('cotinerte-dahl-2004-check', 'value'),
                   Input('select-cotinerte', 'value')])
    def update_carbonoativo_alert(cotinerte_value, cotinerte_eq):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if cotinerte_value == ['cotr'] and cotinerte_eq == 'dahl-2004':
            return True, 'success', 'Carbono ativo pronto para simulação.', 'success'
        else:
            return False, no_update, no_update, 'secondary'

    # checagem de hi0:
    @app.callback(Output('hi0-dahl-2004-check', 'value'),
                  [Input('select-s2-var', 'value'),
                   Input('s2-check', 'value'),
                   Input('cotinerte-card', 'color')],
                  [State('s2-constant', 'value')])
    def update_hi0_check(s2_var, s2_check, cotinerte_color, s2_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []
        # Checando se as variáveis estão definidas:
        if s2_check is not None and s2_constant is not None:
            if 'use-constant' in s2_check:
                values.append('s2')
        if s2_var is not None:
            if 's2' not in values:
                values.append('s2')
        if cotinerte_color == 'success':
            values.append('ca')
        return values

    @app.callback(Output('eq1-hi0-normal-check', 'value'),
                  [Input('select-cotr-var', 'value'),
                   Input('cotr-check', 'value'),
                   Input('s20-card', 'color')],
                  [State('cotr-constant', 'value')])
    def update_hi0_normal_check(cotr_var, cotr_check, s20_color, cotr_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []
        # Checando se as variáveis estão definidas:
        if cotr_check is not None and cotr_constant is not None:
            if 'use-constant' in cotr_check:
                values.append('cotr')
        if cotr_var is not None:
            if 'cotr' not in values:
                values.append('cotr')
        if s20_color == 'success':
            values.append('s20')
        return values

    @app.callback([Output('hi0-dahl-2004-alert', 'is_open'),
                   Output('hi0-dahl-2004-alert', 'color'),
                   Output('hi0-dahl-2004-alert', 'children'),
                   Output('hi0-card', 'color')],
                  [Input('hi0-dahl-2004-check', 'value'),
                   Input('select-hi0', 'value')])
    def update_hi0_alert(hi0_value, hi0_eq):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if sorted(hi0_value) == ['ca', 's2'] and hi0_eq == 'dahl-2004':
            return True, 'success', 'IH\u2080 ativo pronto para simulação.', 'success'
        else:
            return False, no_update, no_update, 'secondary'

    # Checagem de TR:
    @app.callback(Output('waples-check', 'value'),
                  [Input('select-vitrinita-var', 'value'),
                   Input('vitrinita-check', 'value'),
                   Input('lamina-dagua', 'value')],
                  [State('vitrinita-constant', 'value')])
    def update_tr_check(ro_var, ro_check, lamina_dagua, ro_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []
        # Checando se as variáveis estão definidas:
        if ro_check is not None and ro_constant is not None:
            if 'use-constant' in ro_check:
                values.append('ro')
        if ro_var is not None:
            if 'ro' not in values:
                values.append('ro')
        if lamina_dagua:
            values.append('lamina')
        return values

    @app.callback([Output('tr-justwan-dahl-2005-check', 'value'),
                   Output('tr-jarvie-2012-check', 'value')],
                  [Input('select-hi-var', 'value'),
                   Input('hi-check', 'value'),
                   Input('hi0-card', 'color')],
                  [State('hi-constant', 'value')])
    def update_hi0_check(hi_var, hi_check, hi0_color, hi_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []
        # Checando se as variáveis estão definidas:
        if hi_check is not None and hi_constant is not None:
            if 'use-constant' in hi_check:
                values.append('hi')
        if hi_var is not None:
            if 's2' not in values:
                values.append('hi')
        if hi0_color == 'success':
            values.append('hi0')
        return values, values

    @app.callback([Output('tr-alert', 'is_open'),
                   Output('tr-alert', 'color'),
                   Output('tr-alert', 'children'),
                   Output('tr-card', 'color')],
                  [Input('tr-justwan-dahl-2005-check', 'value'),
                   Input('waples-check', 'value'),
                   Input('select-tr', 'value')])
    def update_tr_alert(tr_value, waples_value, tr_eq):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if tr_eq is None:
            return False, no_update, 'no_update', 'secondary'
        if tr_eq == 'waples-1998-1' or tr_eq == 'waples-1998-2' or tr_eq == 'waples-1998-3':
            if sorted(waples_value) == ['lamina', 'ro']:
                return True, 'success', 'Taxa de Transformação pronta para simulação.', 'success'
            else:
                return False, no_update, 'no_update', 'secondary'
        if tr_value is not None:
            if sorted(tr_value) == ['hi', 'hi0']:
                if tr_eq == 'justwan-dahl-2005' or tr_eq == 'jarvie-2012':
                    return True, 'success', 'Taxa de Transformação pronta para simulação.', 'success'
                else:
                    return False, no_update, 'no_update', 'secondary'
            else:
                return False, no_update, 'no_update', 'secondary'
        else:
            return False, no_update, 'no_update', 'secondary'

    # Checagem de COT ativo:
    @app.callback(Output('justwan-dahl-2005-cot0-check', 'value'),
                  [Input('select-cotr-var', 'value'),
                   Input('select-s2-var', 'value'),
                   Input('cotr-check', 'value'),
                   Input('s2-check', 'value'),
                   Input('tr-card', 'color')],
                  [State('cotr-constant', 'value'),
                   State('s2-constant', 'value')])
    def update_cot0_check(cotr_var, s2_var, cotr_check, s2_check, tr_color, cotr_constant, s2_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values_justwan = []
        values_jarvie = []
        # Checando se as variáveis estão definidas:
        if s2_check is not None and s2_constant is not None:
            if 'use-constant' in s2_check:
                values_justwan.append('s2')
                values_jarvie.append('s2')
        if s2_var is not None:
            if 's2' not in values_justwan:
                values_justwan.append('s2')
            if 's2' not in values_jarvie:
                values_jarvie.append('s2')
        # Checando se as variáveis estão definidas:
        if cotr_check is not None and cotr_constant is not None:
            if 'use-constant' in cotr_check:
                values_justwan.append('cotr')
        if cotr_var is not None:
            if 'cotr' not in values_jarvie:
                values_justwan.append('cotr')
        if tr_color == 'success':
            values_justwan.append('tr')
        return values_justwan

    @app.callback([Output('justwan-dahl-2005-cot0-alert', 'is_open'),
                   Output('justwan-dahl-2005-cot0-alert', 'color'),
                   Output('justwan-dahl-2005-cot0-alert', 'children'),
                   Output('cot0-card', 'color')],
                  [Input('justwan-dahl-2005-cot0-check', 'value'),
                   Input('select-cot0', 'value')])
    def update_cot0_alert(justwan_value, cot0_eq):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if cot0_eq is None:
            return False, 'success', no_update, 'secondary'
        if cot0_eq == 'justwan-dahl-2005':
            if sorted(justwan_value) == ['cotr', 's2', 'tr']:
                return True, 'success', 'Carbono ativo\u2080 pronto para simulação.', 'success'
            else:
                return False, 'success', no_update, 'secondary'
        else:
            return False, 'success', no_update, 'secondary'

    @app.callback([Output('eq1-hi0-normal-alert', 'is_open'),
                   Output('eq1-hi0-normal-alert', 'color'),
                   Output('eq1-hi0-normal-alert', 'children'),
                   Output('hi0-normal-card', 'color')],
                  [Input('eq1-hi0-normal-check', 'value'),
                   Input('select-hi0-normal', 'value')])
    def update_hi0normal_alert(justwan_value, hi0_eq):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if hi0_eq is None:
            return False, 'success', no_update, 'secondary'
        if hi0_eq == 'dahl-2004':
            if sorted(justwan_value) == ['cotr', 's20']:
                return True, 'success', 'HI\u2080 pronto para simulação.', 'success'
            else:
                return False, 'success', no_update, 'secondary'
        else:
            return False, 'success', no_update, 'secondary'

    @app.callback([Output('justwan-dahl-2005-s20-alert', 'is_open'),
                   Output('justwan-dahl-2005-s20-alert', 'color'),
                   Output('justwan-dahl-2005-s20-alert', 'children'),
                   Output('s20-card', 'color')],
                  [Input('justwan-dahl-2005-s20-check', 'value'),
                   Input('select-s20', 'value')])
    def update_s20_alert(justwan_value, s20_eq):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if s20_eq is None:
            return False, 'success', no_update, 'secondary'
        if s20_eq == 'justwan-dahl-2005':
            if sorted(justwan_value) == ['s2', 'tr']:
                return True, 'success', 'S2\u2080 pronto para simulação.', 'success'
            else:
                return False, 'success', no_update, 'secondary'
        else:
            return False, 'success', no_update, 'secondary'

    @app.callback([Output('eq1-ro-alert', 'is_open'),
                   Output('eq1-ro-alert', 'color'),
                   Output('eq1-ro-alert', 'children'),
                   Output('ro-card', 'color')],
                  [Input('eq1-ro-check', 'value'),
                   Input('select-ro', 'value')])
    def update_s20_alert(eq1_value, ro_eq):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if eq1_value is None:
            return False, 'success', no_update, 'secondary'
        if ro_eq is None:
            return False, 'success', no_update, 'secondary'
        if ro_eq == 'eq1':
            if sorted(eq1_value) == ['tmax']:
                return True, 'success', 'R\u2092 pronto para simulação.', 'success'
            else:
                return False, 'success', no_update, 'secondary'
        else:
            return False, 'success', no_update, 'secondary'

    @app.callback(Output('maturidade-termica-check', 'value'),
                  [Input('maturation-depth', 'value'),
                   Input('select-hi-var', 'value'),
                   Input('hi-check', 'value'),
                   Input('select-tmax-var', 'value'),
                   Input('tmax-check', 'value'),
                   Input('select-vitrinita-var', 'value'),
                   Input('vitrinita-check', 'value')],
                  [State('hi-constant', 'value'),
                   State('tmax-constant', 'value'),
                   State('vitrinita-constant', 'value')])
    def update_maturidade_check(maturation_depth, ih_var, ih_check,
                                tmax_var, tmax_check,
                                vitrinita_var, vitrinita_check,
                                ih_constant, tmax_constant, vitrinita_constant):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        values = []

        # Checando se as variáveis estão definidas:
        if ih_check is not None and ih_constant is not None:
            if 'use-constant' in ih_check:
                values.append('ih')
        if ih_var is not None and maturation_depth is not None:
            if 'ih-ready-mom' not in values:
                values.append('ih')
        if tmax_check is not None and tmax_constant is not None:
            if 'use-constant' in tmax_check:
                values.append('tmax')
        if tmax_var is not None and maturation_depth is not None:
            if 'tmax-ready-mom' not in values:
                values.append('tmax')
        if vitrinita_check is not None and vitrinita_constant is not None:
            if 'use-constant' in vitrinita_check:
                values.append('ro')
        if vitrinita_var is not None and maturation_depth is not None:
            if 'vitrinita-ready-mom' not in values:
                values.append('ro')

        return values

    # Alert de Maturação:
    @app.callback([Output('maturação-alert', 'color'),
                   Output('maturação-alert', 'is_open'),
                   Output('maturação-alert', 'children')],
                  [Input('maturidade-termica-check', 'value'),
                   Input('select-maturidade-termica', 'value')])
    def update_maturidade_alert(maturidade_check, maturidade_equation):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if not dash.callback_context.triggered:
            raise PreventUpdate
        try:
            if maturidade_equation == 'reftable' and sorted(maturidade_check) == ['ih', 'ro', 'tmax']:
                return 'success', True, 'Maturidade Térmica pronta para Simualação!'
            else:
                return no_update, False, no_update
        except:
            return no_update, False, no_update

    # botão plotagem
    @app.callback(Output('botao-plotagem', 'disabled'),
                  [Input('select-tipo-grafico', 'value')],
                  [State('hi0-alert', 'color'),
                   State('tr-alert', 'color'),
                   State('qualidade-alert', 'color'),
                   State('quantidade-alert', 'color'),
                   State('maturação-alert', 'color'),
                   State('cot0-alert', 'color')])
    def enable_botao(tipo_grafico, is_open_hi0, is_open_tr, is_open_qualidade, is_open_quantidade, is_open_maturacao,
                     is_open_cot_s2):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if is_open_hi0 == 'success' and tipo_grafico == 'grafico-hi':
            return False
        elif is_open_tr == 'success' and tipo_grafico == 'grafico-transformacao':
            return False
        elif is_open_quantidade == 'success' and tipo_grafico == 'grafico-potencial':
            return False
        elif is_open_qualidade == 'success' and tipo_grafico == 'grafico-mo':
            return False
        elif is_open_maturacao == 'success' and tipo_grafico == 'grafico-termica':
            return False
        elif is_open_cot_s2 == 'success' and tipo_grafico == 'grafico-cot-s2':
            return False
        else:
            return True

    ### Módulo COMPARAÇÃO:
    # Opções COT
    @app.callback([Output('compare-cot-y', 'options'),
                   Output('compare-cot-vars', 'options'),
                   Output('compare-cot-facies', 'options')],
                  [Input('compare-cot-results', 'value')])
    def update_compare_cot_vars(simulation_name):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if simulation_name is None or simulation_name == []:
            raise PreventUpdate

        if type(simulation_name) is str or len(simulation_name) == 1:
            if type(simulation_name) is str:
                filepath = simulation_name
            else:
                filepath = simulation_name[0]

            interp_dataframe = pd.read_csv(f'static/{filepath}/{filepath}.csv', sep=',', encoding='utf-8-sig')

            options_dd = []
            for col in interp_dataframe.columns:
                options_dd.append({'label':col, 'value':col})

            return options_dd, options_dd, options_dd

    # Opções Maturação:
    @app.callback([Output('compare-maturation-y', 'options'),
                   Output('compare-maturation-vars', 'options')],
                   [Input('compare-maturation-results', 'value')])
    def update_compare_maturation_vars(simulation_name):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if simulation_name is None or simulation_name == []:
            raise PreventUpdate

        maturation_df = pd.read_csv(simulation_name, sep=',')
        options = [{'label': col, 'value': col} for col in maturation_df.columns]

        return options, options

    # Opções extra:
    @app.callback([Output('compare-upload-y', 'options'),
                   Output('compare-upload-vars', 'options')],
                   [Input('compare-filenames-div', 'children')])
    def update_compare_maturation_vars(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        try:
            if filename[-3:] == 'csv':
                df = pd.read_csv(filename)
            if filename[-3:] == 'txt':
                df = pd.read_csv(filename, sep='\t')
        except UnicodeError:
            if filename[-3:] == 'csv':
                df = pd.read_csv(filename, encoding='iso-8859-1')
            if filename[-3:] == 'txt':
                df = pd.read_csv(filename, sep='\t', encoding='iso-8859-1')

        options = [{'label': col, 'value': col} for col in df.columns]

        return options, options

    # Plot:
    @app.callback(Output('compare-figure', 'figure'),
                  [Input('compare-plot-btn', 'n_clicks')],
                  [State('compare-cot-y', 'value'),
                   State('compare-cot-vars', 'value'),
                   State('compare-maturation-y', 'value'),
                   State('compare-maturation-vars', 'value'),
                   State('compare-cot-facies', 'value'),
                   State('compare-upload-y', 'value'),
                   State('compare-upload-vars', 'value'),
                   State('compare-maturation-results', 'value'),
                   State('compare-cot-results', 'value'),
                   State('compare-filenames-div', 'children')])
    def compare_plot_fig(n_clicks, cot_y, cot_vars, maturation_y, maturation_vars, cot_facies, upload_y, upload_vars, simulation_maturation_name, simulation_cot_name, compare_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate

        # DF Cot:
        try:
            interp_dataframe = pd.read_csv(f'static/{simulation_cot_name}/{simulation_cot_name}.csv', sep=',', encoding='utf-8-sig')
        except:
            interp_dataframe = pd.DataFrame()
        # DF Maturação:
        try:
            maturation_df = pd.read_csv(simulation_maturation_name, sep=',')
        except:
            maturation_df = pd.DataFrame()
        # DF de Comparação:
        try:
            if compare_filename[-3:] == 'csv':
                compare_df = pd.read_csv(compare_filename)
            if compare_filename[-3:] == 'txt':
                compare_df = pd.read_csv(compare_filename, sep='\t')
        except UnicodeError:
            if compare_filename[-3:] == 'csv':
                compare_df = pd.read_csv(compare_filename, encoding='iso-8859-1')
            if compare_filename[-3:] == 'txt':
                compare_df = pd.read_csv(compare_filename, sep='\t', encoding='iso-8859-1')
        except:
            compare_df = pd.DataFrame()

        if interp_dataframe.empty and maturation_df.empty and compare_df.empty:
            # Não conseguiu ler os resultados
            print('Não possui DF de COT e nem de MATURAÇÃO')
            return no_update

        else:
            # Criando plots:
            # nº de subplots:
            if not maturation_df.empty and maturation_vars and maturation_y:
                maturation_len = len(maturation_vars)
                if cot_facies:
                    maturation_len = maturation_len + 1
            else:
                maturation_len = 0

            if not interp_dataframe.empty and cot_vars and cot_y:
                cot_len = len(cot_vars)
            else:
                cot_len = 0

            if not compare_df.empty and upload_vars and upload_y:
                upload_len = len(upload_vars)
            else:
                upload_len = 0

            vars_len = maturation_len + cot_len + upload_len

            if vars_len == 0:
                print('Sem variáveis selecionadas.')
                return no_update
            if cot_facies:
                vars_len = vars_len + 1
            fig = subplots.make_subplots(rows=1, cols= vars_len,
                                         shared_yaxes=True,
                                         horizontal_spacing=0)
            fig.update_layout(legend=dict(orientation="h", yanchor="bottom"))
            fig['layout'].update(hovermode='y')

            all_vars = []
            if cot_facies:
                all_vars.append(cot_facies)

            i = 0
            for var_list in [cot_vars, maturation_vars, upload_vars]:
                if type(var_list) is list:
                    for var_string in var_list:
                        all_vars.append(var_string)
                else:
                    if i == 0:
                        cot_vars = []
                    if i == 1:
                        maturation_vars = []
                    if i == 2:
                        upload_vars = []
                i = i +1

            col = 1
            for var in all_vars:
                if var in cot_vars:
                    df = interp_dataframe
                    y = cot_y
                if var in maturation_vars:
                    df = maturation_df
                    y = maturation_y
                if var in upload_vars:
                    df = compare_df
                    y = upload_y
                if var == cot_facies:
                    #i_col = len(fig['data'])
                    df = interp_dataframe
                    y = cot_y
                    fig = generate_categorical_subplot(df, y, var, px.colors.qualitative.Prism + px.colors.qualitative.Safe + px.colors.qualitative.Antique, fig, 1, col)
                    col = col + 1
                if df.empty:
                    pass
                else:
                    try:
                        fig.append_trace(go.Scatter(
                            x=df[var].values,
                            y=df[y].values,
                            name=var,
                            line={'width': 0.75, 'dash': 'solid'},
                        ), row=1, col=col)
                        fig['layout']['xaxis{}'.format(col)].update(
                            title=var
                        )
                        col = col + 1
                    except KeyError:
                        pass

            fig['layout']['yaxis'].update(
                title='Profundidade [m]',
                autorange='reversed'
            )

            return fig

    # Cicloestratigrafia:
    def format_age(age: int) -> str:
        if age > 1000:
            # Convert to Ma with one decimal place
            age_str = f"{age / 1000:.1f} Ma"
        else:
            # Use kyr with all decimal places
            age_str = f"{age} kyr"

        return age_str

    @app.callback(
        [Output('cicloestrat-fig', 'figure'),
        Output('btn-download-cicloestrat', 'className'),
        Output('btn-plot-sedrate', 'disabled'),
        Output('sedrate-spinner', 'children'),
        Output('cicloestrat-toast', 'is_open'),
        Output('cicloestrat-toast', 'children'),
        Output('cicloestrat-toast', 'icon')],
        [Input('btn-execute-cicloestrat', 'n_clicks'),
         Input('btn-plot-sedrate', 'n_clicks'),
         Input('sedrate-depth', 'options')],
        [State('sedrate-base', 'value'),
         State('sedrate-topo', 'value'),
         State('sedrate-gr', 'value'),
         State('sedrate-depth', 'value'),
         State('las-files-sedrate', 'children'),
         State('sedrate-cycles', 'value'),
         State('cicloestrat-fig', 'figure')]
    )
    def calculate_sedrate_cicloestrat(n_clicks, n_clicks_sedrate, sedrate_options, bottom, top, gr, depth, las_path, cycles, fig_data):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if dash.callback_context.triggered[0]['prop_id'] == 'sedrate-depth.options':
            return no_update, no_update, no_update, no_update, True, [html.P("Os cálculos desta abordagem podem levar tempo. Recomenda-se a utilização de dados de baixa resolução de profundidade ou a seleção de intervalos específicos para a estimação.", className="mb-0")], 'warning'
        if dash.callback_context.triggered[0]['prop_id'] == 'btn-execute-cicloestrat.n_clicks':
            las = lasio.read(las_path)

            las_df = las.df().reset_index().dropna(how='any')
            las_df = las_df[(las_df[depth] <= bottom) & (las_df[depth] >= top)]

            model, time, well_ps, picos = apply_pyleo(las_df, gr, depth)
            #model, time, well_ps, picos = None, None, None

            layout = go.Layout(
                # title="Title",
                xaxis=dict(
                    title=depth
                ),
                yaxis=dict(
                    title=f'Shorter INPEFA [{gr}]'
                ))
            
            fig = go.Figure(layout=layout)
            fig.add_trace(go.Scatter(y=well_ps.value, x=well_ps.time, mode='lines', marker=dict(size=1), name=f'Shorter INPEFA [{gr}]'))
            fig.add_trace(go.Scatter(y=model, x=time, mode='lines', marker=dict(color='orange', size=3), name='SSA reconstruction, first mode'))
            fig.add_trace(go.Scatter(y=picos[1], x=picos[0], mode='markers', marker=dict(color='red', size=6), name='Máximos detectados'))

            return fig, no_update, False, no_update, True, [html.P("Os picos de sedimentação foram calculados. Para calcular a taxa de sedimentação, selecione o melhor ajuste de período de ciclo orbital para o seu modelo.", className="mb-0")], 'primary'
        else:
            depths = fig_data['data'][2]['x']
            peaks = fig_data['data'][2]['y']

            cycle = int(cycles)

            ages_peaks = []
            initial_peak = 0
            for peak in peaks:
                ages_peaks.append(initial_peak)
                initial_peak = initial_peak + cycle

            ages_array = np.array(ages_peaks)
            sedrate = np.gradient(depths, ages_array)
            age_sum = np.sum(ages_array)

            legend_age = format_age(int(age_sum))

            df = pd.DataFrame(data={depth: depths, 'Taxa de Sedimentação [cm/ka]': sedrate*100})
            df.to_csv("static/taxa_sedmentacao_cicloestrat_achilles.csv")

            fig_subplot = make_subplots(rows=2, cols=1, shared_xaxes=True)

            fig_subplot.add_trace(go.Scatter(y=fig_data['data'][0]['y'], x=fig_data['data'][0]['x'], mode='lines', marker=dict(size=1), name=f'Shorter INPEFA [{gr}]'),  row=1, col=1)
            fig_subplot.add_trace(go.Scatter(y=fig_data['data'][1]['y'], x=fig_data['data'][1]['x'], mode='lines', marker=dict(color='orange', size=3), name='SSA reconstruction, first mode'),  row=1, col=1)
            fig_subplot.add_trace(go.Scatter(y=fig_data['data'][2]['y'], x=fig_data['data'][2]['x'], mode='markers', marker=dict(color='red', size=6), name='Máximos detectados'),  row=1, col=1)

            fig_subplot.add_trace(go.Scatter(x=depths, y=sedrate*100, name='Taxa de Sedimentação'), row=2, col=1)

            fig_subplot.update_xaxes(title_text=depth, row=1, col=1)
            fig_subplot.update_yaxes(title_text=f'Shorter INPEFA [{gr}]', row=1, col=1)

            fig_subplot.update_xaxes(title_text=depth, row=2, col=1)
            fig_subplot.update_yaxes(title_text='Taxa de Sedimentação [cm/ka]', row=2, col=1)

            fig_subplot.add_annotation(xref="x domain", x=0.95,
                                       yref="y domain", y=0.95,
                                       text=f'Tempo de deposição total: {legend_age}', showarrow=False,
                                       font=dict(size=16, color='black'), row=2, col=1)

            return fig_subplot, "btn btn-block", no_update, no_update, no_update, no_update, no_update
    @app.callback(
        Output('btn-execute-cicloestrat', 'disabled'),
        [Input('las-files-sedrate', 'children'),
         Input('sedrate-base', 'value'),
         Input('sedrate-topo', 'value'),
         Input('sedrate-gr', 'value'),
         Input('sedrate-depth', 'value'),
         Input('sedrate-cycles', 'value')
         ])
    def add_row(las_path, base, topo, gr, depth, cycles):
        if las_path and base is not None and topo is not None and gr is not None and depth is not None and cycles is not None:
            return False
        else:
            return True