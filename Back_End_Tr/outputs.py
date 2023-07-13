# Arquivo para armazenamento de callbacks de saídas do Achilles: resultados, tabelas, etc
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
from dash.dash import no_update
import flask
from flask import send_from_directory
from flask import make_response
import mimetypes
import lasio
import plotly.graph_objs as go
from plotly import subplots
import re
import base64
import io
import os
import dash_table
import dash_html_components as html
import datetime
from functions.bacias import *
from plotly.subplots import make_subplots

def get_outputs_callbacks(app):
    ### RESULTADOS E EXPORTAÇÕES:
    ## ABA COT:
    @app.callback(Output('cot-results-collapse', 'is_open'),
                  [Input('sim-export-dd', 'value')])
    def open_collapse(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            return False
        else:
            return True

    # Tabelas de Resultado
    @app.callback([Output('results-table', 'children'),
                   Output('vars-table', 'children'),
                   Output('sim-table', 'children')],
                  [Input('sim-export-dd', 'value')])
    def update_tables(simulation_name):
        if not dash.callback_context.triggered:
            raise PreventUpdate

        results_df = pd.read_csv(f'static/{simulation_name}/{simulation_name}_estatisticas.csv', sep=',')
        vars_df = pd.read_csv(f'static/{simulation_name}/{simulation_name}_variaveis.csv', sep=',')
        sim_df = pd.read_csv(f'static/{simulation_name}/{simulation_name}_equacoes.csv', sep=',')

        return dbc.Table.from_dataframe(results_df, responsive=True, size='sm', striped=True, bordered=True,
                                        hover=True), \
            dbc.Table.from_dataframe(vars_df, responsive=True, size='sm', striped=True, bordered=True, hover=True), \
            dbc.Table.from_dataframe(sim_df, responsive=True, size='sm', striped=True, bordered=True, hover=True)

    # Exportação do Modelo de mistura:
    @app.callback(Output('export-mistura-button', 'className'),
                  [Input('mistura-export-dd', 'value'),
                   Input('mistura-figure', 'figure')])
    def enable_export(dd_value, mistura_fig):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if dd_value is not None:
            try:
                mistura_df = pd.read_csv(f'static/{dd_value}/{dd_value}_qualidade.csv')
                return 'btn btn-outline-success btn-block'
            except Exception as e:
                print(e)
                return 'btn btn-outline-success btn-block disabled'
        else:
            return 'btn btn-outline-success btn-block disabled'

    ## ABA MATURAÇÃO
    # Aba resultado de Maturação:
    @app.callback([Output('maturacao-results-collapse', 'is_open'),
                   Output('maturacao-ref-table', 'children'),
                   Output('maturacao-stats-table', 'children')],
                  [Input('maturacao-export-dd', 'value')])
    def update_results_tables(dataset):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if dataset is None:
            return False, no_update, no_update
        else:
            stats_df = pd.read_csv(f'static/{dataset}_estatisticas.csv', sep=',')
            ref_df = pd.read_csv(f'static/{dataset}_equacoes.csv', sep=',')
            return True, dbc.Table.from_dataframe(ref_df, responsive=True, size='sm', striped=True, bordered=True,
                                                  hover=True), dbc.Table.from_dataframe(stats_df, responsive=True,
                                                                                        size='sm', striped=True,
                                                                                        bordered=True, hover=True)

    @app.callback(Output('export-sim-button', 'className'),
                  [Input('sim-export-dd', 'value')])
    def enable_export(dd_options):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if dd_options is None:
            raise PreventUpdate
        if dd_options is not None:
            return 'btn btn-outline-success btn-block'
        else:
            return 'btn btn-outline-success btn-block disabled'

    @app.callback(Output('export-maturacao-button', 'className'),
                  [Input('maturacao-export-dd', 'value')])
    def enable_export(dd_options):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if dd_options is None:
            raise PreventUpdate
        if dd_options is not None:
            return 'btn btn-outline-success btn-block'
        else:
            return 'btn btn-outline-success btn-block disabled'

    @app.callback(Output('export-sim-button', 'href'),
                  [Input('sim-export-select-dd', 'value')],
                  [State('las-files', 'children')])
    def update_link(simulations_options, las_files):
        if simulations_options is None:
            return
        import zipfile
        z = zipfile.ZipFile('static/Resultados.zip', 'w', zipfile.ZIP_DEFLATED)
        for simulation_name in simulations_options:
            z.write(f'static/{simulation_name}/{simulation_name}.txt')
            z.write(f'static/{simulation_name}/{simulation_name}.csv')
            z.write(f'static/{simulation_name}/{simulation_name}_estatisticas.txt')
            z.write(f'static/{simulation_name}/{simulation_name}_estatisticas.csv')
            z.write(f'static/{simulation_name}/{simulation_name}_variaveis.txt')
            z.write(f'static/{simulation_name}/{simulation_name}_variaveis.csv')
            z.write(f'static/{simulation_name}/{simulation_name}_equacoes.txt')
            z.write(f'static/{simulation_name}/{simulation_name}_equacoes.csv')
            z.write(las_files[simulation_name])
            # z.write(f'{well_info["name"]}.las')
        return '/dash/urlToDownload?value={}'.format('Resultados')

    @app.callback(Output('export-maturacao-button', 'href'),
                  [Input('maturacao-export-dd', 'value')])
    def update_link(value):
        if value is None:
            return no_update
        return '/dash/urlToDownload?value={}'.format(value)

    @app.callback(Output('export-mistura-button', 'href'),
                  [Input('mistura-export-dd', 'value')])
    def update_link(value):
        if value is None:
            return no_update
        return '/dash/urlToDownload?value={}'.format(value)

    @app.server.route('/dash/urlToDownload')
    def download_csv():
        value = flask.request.args.get('value')
        return send_from_directory(directory=os.path.join(os.getcwd(), "static"), path=value + '.zip', as_attachment=True, cache_timeout=-1)

    # callback modal gráficos pré
    @app.callback(
        Output("modal-graficos-pre", "is_open"),
        [Input("open-graficos-pre", "n_clicks"), Input("close-modal-matur-1", "n_clicks")],
        [State("modal-graficos-pre", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # callback modal equações maturação
    @app.callback(
        Output("modal-equations-maturacao", "is_open"),
        [Input("open-maturation-equations", "n_clicks"), Input("close-modal-maturation-eq", "n_clicks")],
        [State("modal-equations-maturacao", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # callback modal gráficos pré (cluster)
    @app.callback(
        Output("modal-cluster", "is_open"),
        [Input("open-cluster", "n_clicks"), Input("close-modal-cluster", "n_clicks")],
        [State("modal-cluster", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # callback modal Valores-referência de IH
    @app.callback(
        Output("modal", "is_open"),
        [Input("open", "n_clicks"), Input("close", "n_clicks")],
        [State("modal", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # callback modal Valores-referência de IO
    @app.callback(
        Output("modal-1", "is_open"),
        [Input("open-1", "n_clicks"), Input("close-1", "n_clicks")],
        [State("modal-1", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # callback modal Valores-referência de δ¹³C
    @app.callback(
        Output("modal-2", "is_open"),
        [Input("open-2", "n_clicks"), Input("close-2", "n_clicks")],
        [State("modal-2", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # Classificação de Fácies Orgânicas:
    @app.callback(
        Output("modal-3", "is_open"),
        [Input("open-3", "n_clicks"), Input("close-3", "n_clicks")],
        [State("modal-3", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # Carbono Orgânico Marinho (COma)
    @app.callback(
        Output("modal-4", "is_open"),
        [Input("open-4", "n_clicks"), Input("close-4", "n_clicks")],
        [State("modal-4", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # Fluxo de Carbono (CF):
    @app.callback(
        Output("modal-5", "is_open"),
        [Input("open-5", "n_clicks"), Input("close-5", "n_clicks")],
        [State("modal-5", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # Classificação de Eficiência de Soterramento (BE)
    @app.callback(
        Output("modal-6", "is_open"),
        [Input("open-6", "n_clicks"), Input("close-6", "n_clicks")],
        [State("modal-6", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # Carbono Orgânico Terrestre (COte):
    @app.callback(
        Output("modal-7", "is_open"),
        [Input("open-7", "n_clicks"), Input("close-7", "n_clicks")],
        [State("modal-7", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    # Modal de Anoxia
    @app.callback(
        Output("modal-8", "is_open"),
        [Input("open-8", "n_clicks"), Input("close-8", "n_clicks")],
        [State("modal-8", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    #
    @app.callback(
        Output("modal-9", "is_open"),
        [Input("open-9", "n_clicks"), Input("close-9", "n_clicks")],
        [State("modal-9", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    ## CURSO:
    @app.server.route('/dash/DownloadAchilles')
    def download_dataset():
        value = flask.request.args.get('value')
        return send_from_directory(directory=os.path.join(os.getcwd(), "static"), path=value, as_attachment=True, cache_timeout=-1)

    @app.server.route('/dash/DownloadPdf')
    def download_pdf():
        value = flask.request.args.get('value')
        redirect_path = '/download_file/' + filename
        response = make_response("")
        response.headers["X-Accel-Redirect"] = redirect_path
        response.headers["Content-Type"] = mimetypes.guess_type(filename)

        return response

    @app.server.route('/dash/DownloadPaleoprodutividade')
    def download_paleoprodutividade():
        return send_from_directory(directory=os.path.join(os.getcwd(), "static"), path="paleobatimetria_achilles.csv", as_attachment=True,
                                   cache_timeout=-1)

    @app.server.route('/dash/DownloadTaxadeSedimentacao')
    def download_sedrate_biostrat():
        return send_from_directory(directory=os.path.join(os.getcwd(), "static"), path="taxa_sedmentacao_biostrat_achilles.csv",
                                   as_attachment=True, cache_timeout=-1)

    @app.server.route('/dash/DownloadTaxadeSedimentacaoCiclo')
    def download_sedrate_ciclostrat():
        return send_from_directory(directory=os.path.join(os.getcwd(), "static"), path="taxa_sedmentacao_cicloestrat_achilles.csv",
                                   as_attachment=True, cache_timeout=-1)

    ### DADOS DE POÇO (.LAS):
    # Ativando dropdown de curvas las:
    @app.callback([Output('output-las-file', 'disabled'),
                   Output('output-las-file', 'options'),
                   Output('loading-las', 'children'),
                   # Output('select-las-file-var', 'disabled'),
                   Output('age-las', 'disabled'),
                   Output('pp-las', 'disabled'),
                   Output('sedrate-las', 'disabled'),
                   Output('dbd-las', 'disabled'),
                   Output('wd-las', 'disabled'),
                   Output('sf-las', 'disabled'),
                   Output('age-las', 'options'),
                   Output('pp-las', 'options'),
                   Output('sedrate-las', 'options'),
                   Output('dbd-las', 'options'),
                   Output('wd-las', 'options'),
                   Output('sf-las', 'options')],
                  [Input('las-filenames-div', 'children')])
    def activate_button(las_hiddendiv_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if las_hiddendiv_filename is None:
            raise PreventUpdate
        if las_hiddendiv_filename is not None:
            lf = lasio.read(las_hiddendiv_filename)
            curves = list(lf.curves.keys())
            dd_options = [{'label': str(curve), 'value': str(curve)} for curve in curves]

            return False, dd_options, None, False, False, False, False, False, False, dd_options, dd_options, dd_options, dd_options, dd_options, dd_options

    @app.callback(Output('plot-las-curves', 'disabled'),
                  [Input('output-las-file', 'value')])
    def enable_plot_las(value):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if value is None:
            return True
        else:
            return False

    @app.callback(Output('las-figure', 'figure'),
                  [Input('plot-las-curves', 'n_clicks')],
                  [State('las-filenames-div', 'children'),
                   State('output-las-file', 'value')])
    def generate_las_figure(n_clicks, las_path, selected_curves):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if las_path is None:
            raise PreventUpdate
        if las_path is not None:
            lf = lasio.read(las_path)
            bg_color = 'white'
            font_size = 10
            tick_font_size = 8
            line_width = 0.5
            yvals = 'DEPT'

            def generate_axis_title(descr, unit):
                title_words = descr.split(' ')

                current_line = ''
                lines = []
                for word in title_words:
                    if len(current_line) + len(word) > 15:
                        lines.append(current_line[:-1])
                        current_line = ''
                    current_line += '{} '.format(word)
                lines.append(current_line)

                title = '<br>'.join(lines)
                title += '<br>({})'.format(unit)

                return title

            cols = list(lf.curves.keys())
            plots = []
            for col in selected_curves:
                plots.append([col])

            fig = subplots.make_subplots(rows=1, cols=len(plots),
                                         shared_yaxes=True,
                                         horizontal_spacing=0)
            for i in range(len(plots)):
                for column in plots[i]:
                    fig.append_trace(go.Scatter(
                        x=lf.curves[column].data,
                        # y=lf.curves[yvals].data,
                        y=lf.depth_m,
                        name=column,
                        line={'width': line_width,
                              'dash': 'solid'},
                    ), row=1, col=i + 1)
                    fig['layout']['xaxis{}'.format(i + 1)].update(
                        title=generate_axis_title(
                            lf.curves[plots[i][0]]['descr'],
                            lf.curves[plots[i][0]]['unit']
                        ),
                        type='log' if column in plots[i] else 'linear'
                    )

            # y axis title
            fig['layout']['yaxis'].update(
                title='Depth [m]',
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
                                family='Arial, sans-serif',
                                size=font_size
                            )
                        ),
                        tickfont=dict(
                            family='Arial, sans-serif',
                            size=tick_font_size
                        )
                    )

            fig['layout'].update(
                # height=height,
                # width=width,
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
                hovermode='y',
                legend={
                    'font': {
                        'size': tick_font_size
                    }
                },
                margin=go.layout.Margin(
                    r=100
                )
            )

        return fig

    def parse_contents(contents, filename, date):
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            return pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            return pd.read_excel(io.BytesIO(decoded))

    @app.callback([Output('ages-upload', 'children'),
                   Output('modal-conteudo', 'is_open')],
                  [Input('datatable-upload', 'contents'),
                   Input('close-conteudo', 'n_clicks')],
                  [State('datatable-upload', 'filename')])
    def update_output(contents, modal_close, filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate

        ctx = dash.callback_context
        user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]

        # If close button clicked, don't update datatable-upload contents (maybe you want too???) but close modal
        if not user_clicked or user_clicked == 'close-conteudo':
            return dash.no_update, False

        if contents is None:
            return [], False

        if not filename.endswith(('.xls', '.csv')):
            return [], True

        df = parse_contents(contents, filename)
        return html.Div([
            dash_table.DataTable(
                id='table',
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_table={'overflowX': 'scroll',
                             'maxHeight': '300',
                             'overflowY': 'scroll',
                             'maxWidth': '300'},
                style_cell={
                    'minWidth': '150px', 'maxWidth': '180px',
                    'whiteSpace': 'normal',
                    'textAlign': 'left'
                },
                style_header={
                    'fontWeight': 'bold',
                },
                fixed_rows={'headers': True, 'data': 0},
                columns=[{"name": i, "id": i, 'deletable': True, 'renamable': True} for i in df.columns],
                data=df.to_dict("records"),
            )
        ]), False

    eventos = pd.read_csv('OAES .csv')
    modal_opened = False

    def get_events(age, eve):
        filtered_indices = [i for j in age['Age [Ma]'] for i, v in eve.iterrows() if
                            v['Prof_min'] <= j <= v['Prof_max']]
        filtered_indices = list(set(filtered_indices))
        filtered_events = eve.loc[filtered_indices].drop(columns='Events')
        return filtered_events

    def read_file(filename, eventos):
        try:
            if filename[-3:] == 'csv':
                df = pd.read_csv(filename)
                events = get_events(df, eventos)
            if filename[-3:] == 'txt':
                df = pd.read_csv(filename, sep='\t')
                events = get_events(df, eventos)
        except UnicodeError:
            if filename[-3:] == 'csv':
                df = pd.read_csv(filename, encoding='iso-8859-1')
                events = get_events(df, eventos)
            if filename[-3:] == 'txt':
                df = pd.read_csv(filename, sep='\t', encoding='iso-8859-1')
                events = get_events(df, eventos)
        return events

    @app.callback(
        Output("modal-anox", "is_open"),
        [Input("add-anox-btn", "n_clicks"), Input("no", "n_clicks"), Input("yes", "n_clicks")],
        [State("modal-anox", "is_open"),
         State('age-filenames-div', 'children'),
         State('anox-flag-div', 'children')],
    )
    def toggle_modal(n_clicks_anox, n_clicks_no, n_clicks_yes, is_open, age_filename, anox_flag):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        # global modal_opened
        if dash.callback_context.triggered[0]['prop_id'] == "no.n_clicks" or dash.callback_context.triggered[0][
            'prop_id'] == "yes.n_clicks":
            return False
        if dash.callback_context.triggered[0]['prop_id'] == "add-anox-btn.n_clicks":
            if not anox_flag is None:
                # Nao ser None ignifica que os eventos anóxicos já foram adicionados (o hidden-div nao tem flag dizendo que foi adicionado)
                return no_update
            if age_filename is None:
                # Se age_filename é None, o usuário nao subiu um arquivo de idades
                return no_update
            # As condiçoes de anoxia ainda nao foram verificadas e também existe arquivo de idades na memória
            events = read_file(age_filename, eventos)
            if len(events) == 0:
                return no_update
            else:
                return True
            # if not modal_opened:
            #    modal_opened = True
            #    return True
            # else:
            #    return False
        else:
            print("no.n_clicks2")
            modal_opened = False
            return False

    # @app.callback(
    #    Output("yes", "n_clicks"),
    #    [Input("yes", "n_clicks")],
    # )
    # def update_clicked_button(n_clicks):
    #    if not dash.callback_context.triggered:
    #        raise PreventUpdate
    #    global clicked_button
    #    if n_clicks:
    #        clicked_button = "yes"
    #    return n_clicks
    #
    # @app.callback(
    #    Output("add-anox-btn", "n_clicks"),
    #    [Input("add-anox-btn", "n_clicks")],
    # )
    # def update_clicked_button(n_clicks):
    #    if not dash.callback_context.triggered:
    #        raise PreventUpdate
    #    global clicked_button
    #    if n_clicks:
    #        clicked_button = "add-anox-btn"
    #    return n_clicks

    @app.callback(
        [Output('table-anoxia', 'data'),
         Output('anox-flag-div', 'children')],
        [Input("yes", "n_clicks"),
         Input('add-anox-btn', 'n_clicks')],
        [State('age-filenames-div', 'children'),
         State('table-anoxia', 'data'),
         State('table-anoxia', 'columns')])
    def update_table(n_clicks_1, n_clicks_2, age_filename, rows, columns):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        # global clicked_button

        if dash.callback_context.triggered[0]['prop_id'] == "yes.n_clicks":
            if age_filename is not None:
                events = read_file(age_filename, eventos)
            return events.to_dict('records'), "already-added"

        elif dash.callback_context.triggered[0]['prop_id'] == "add-anox-btn.n_clicks":
            rows.append({'Prof_min': 0, 'Prof_max': 0, 'fp': 0, 'multi': 0})
            return rows, "not-added"

    @app.callback(
        Output('table-tx-sedimentacao', 'data'),
        [Input('add-sedrate-btn', 'n_clicks')],
        [State('table-tx-sedimentacao', 'data'),
         State('table-tx-sedimentacao', 'columns')])
    def add_row(n_clicks, rows, columns):
        if n_clicks is None:
            return no_update
        if n_clicks > 0:
            rows.append({'Profundidade [m]': 0, 'Idade [Ma]]': 0})
        return rows

    @app.callback([Output('sedrate-figure', 'figure'),
                   Output('download-btn-sedrate', 'className')],
                  [Input('plot-sedrate-btn', 'n_clicks')],
                  [State('table-tx-sedimentacao', 'data'),
                   State('table-tx-sedimentacao', 'columns')])
    def update_maturacao_graph(n_clicks, data, columns):
        if not dash.callback_context.triggered:
            raise PreventUpdate

        try:
            df = pd.DataFrame(data=data)
            # Conversão de Ma para ka
            df['Idades [ka]'] = df['Idade [Ma]'].astype(float) * 1000
            # Conversáo de m para cm
            df['Profundidade [cm]'] = df['Profundidade [m]'].astype(float) * 100
            
            df["Taxa de Sedimentação [cm/ka]"] = np.gradient(df['Profundidade [cm]'], df['Idades [ka]'])

            figure = px.line(df, x='Profundidade [m]', y="Taxa de Sedimentação [cm/ka]")
            df.to_csv("static/taxa_sedmentacao_biostrat_achilles.csv", index=False)
            return figure, "btn btn-block"

        except:
            return no_update, "btn btn-block disabled"

    @app.callback([Output('paleoprodutividade-figure', 'figure'),
                   Output("download-btn-produtividade", 'className')],
                  [Input('calcular-paleoprodutividade-btn', 'n_clicks')],
                  [State('paleobat-filenames-calculadora-div', 'children'),
                   State('select-paleobat-var', 'value'),
                   State('select-bacia-dd', 'value')])
    def generate_paleoprodutividade(n_clicks, paleobat_path, paleobat_col, bacia):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if paleobat_path is None or paleobat_path == []:
            raise PreventUpdate
        if type(paleobat_path) is str or len(paleobat_path) == 1:
            if type(paleobat_path) is str:
                filepath = paleobat_path
            else:
                filepath = paleobat_path[0]

            if filepath is not None:
                try:
                    if filepath[-3:] == 'csv':
                        paleobat_df = pd.read_csv(filepath)
                    if filepath[-3:] == 'txt':
                        paleobat_df = pd.read_csv(filepath, sep='\t')
                except UnicodeError:
                    if filepath[-3:] == 'csv':
                        paleobat_df = pd.read_csv(filepath, encoding='iso-8859-1')
                    if filepath[-3:] == 'txt':
                        paleobat_df = pd.read_csv(filepath, sep='\t', encoding='iso-8859-1')

            if bacia == 'amazonas':
                paleobat_df = bacia_de_amazonas(paleobat_df, paleobat_col)
            if bacia == 'barreirinhas':
                paleobat_df = bacia_de_barreirinhas(paleobat_df, paleobat_col)
            if bacia == 'camumu':
                paleobat_df = bacia_camamu_almada(paleobat_df, paleobat_col)
            if bacia == 'campos':
                paleobat_df = bacia_de_campos(paleobat_df, paleobat_col)
            if bacia == 'cumuruxatiba':
                paleobat_df = bacia_de_cumuruxatiba(paleobat_df, paleobat_col)
            if bacia == 'jacuipe':
                paleobat_df = bacia_de_jacuipe(paleobat_df, paleobat_col)
            if bacia == 'jequitinhonha':
                paleobat_df = bacia_de_jequitinhonha(paleobat_df, paleobat_col)
            if bacia == 'mucuri':
                paleobat_df = bacia_de_mucuri(paleobat_df, paleobat_col)
            if bacia == 'pelotas':
                paleobat_df = bacia_de_pelotas(paleobat_df, paleobat_col)
            if bacia == 'pernambuco':
                paleobat_df = bacia_de_pernambuco_paraiba(paleobat_df, paleobat_col)
            if bacia == 'santos':
                paleobat_df = bacia_de_santos(paleobat_df, paleobat_col)
            if bacia == 'seal':
                paleobat_df = bacia_de_seal(paleobat_df, paleobat_col)
            if bacia == 'potiguar':
                paleobat_df = bacia_de_potiguar(paleobat_df, paleobat_col)

            paleobat_df.to_csv("static/paleobatimetria_achilles.csv")

            bacias_dict = {'amazonas': 'Bacia do Foz do Amazonas',
                           'barreirinhas': 'Bacia de Barreirinhas',
                           'camumu': 'Bacia de Camamu-Almada',
                           'campos': 'Bacia de Campos',
                           'cumuruxatiba': 'Bacia de Cumuruxatiba',
                           'jacuipe': 'Bacia de Jacuipe',
                           'jequitinhonha': 'Bacia de Jequitinhonha',
                           'mucuri': 'Bacia de Mucuri',
                           'pelotas': 'Bacia de Pelotas',
                           'pernambuco': 'Bacia de Pernambuco Paraiba',
                           'santos': 'Bacia de Santos',
                           'seal': 'Bacia de Seal',
                           'potiguar': 'Bacia de Potiguar'}
            # return send_from_directory(directory="static", filename='paleobatimetria_achilles.csv', as_attachment=True,
            #                           cache_timeout=-1)

            paleo_figure = px.scatter(paleobat_df, paleobat_col, 'Produtividade Primária [gC/m²/yr]',
                                      title=bacias_dict[bacia])

            return paleo_figure, "btn btn-block"

    ### fração de areia e densidade aparente seca
    def igr(GR):
        GRmin = min(GR)
        GRmax = max(GR)
        IGR = np.zeros(np.size(GR))
        IGR = (GR - GRmin) / (GRmax - GRmin)
        return IGR

    def clavier(IGR):
        VSH = np.zeros(np.size(IGR))
        VSH = 1.7 - np.sqrt(3.38 - (IGR + 0.7) ** 2.0)
        return VSH

    def SandFraction(VSH):
        SF = (1 - VSH) * 100
        return SF

    def DensidadeAparenteSeca(RHOB, NPHI):
        NPHI = NPHI / 100  # Fator de conversão
        DAS = RHOB - NPHI
        return DAS

    def igr(GR):
        GRmin = min(GR)
        GRmax = max(GR)
        IGR = np.zeros(np.size(GR))
        IGR = (GR - GRmin) / (GRmax - GRmin)
        return IGR


    @app.callback(
        Output('fa-figure', 'figure'),
        [
            Input('target-select1', 'value'),
            Input('top-depth', 'value'),
            Input('base-depth', 'value'),
            Input('las-filenames-div2', 'children'),
            Input('calcular-fa', 'n_clicks'),
            Input('select-prof', 'value'),
            Input('select-gr', 'value'),
            Input('select-por', 'value'),
            Input('select-den', 'value')
        ]
    )
    def load_las_and_update_df(
            value,
            top_depth,
            base_depth,
            filename,
            n_clicks_fa,
            profundidade,
            gr,
            por,
            den
    ):
        figure_fa = px.line()
        las_fa = lasio.LASFile()

        if not all([profundidade, gr, por, den]):
            raise PreventUpdate

        if not dash.callback_context.triggered:
            raise PreventUpdate

        if profundidade and gr and por and den:
            # Lê o arquivo LAS e cria o DataFrame
            las_dasfa = lasio.read(filename)
            df_dasfa = las_dasfa.df().reset_index()
            df_dasfa = df_dasfa[[profundidade, gr, por, den]]

            # Filtra as linhas do DataFrame com base em top_depth e base_depth, se fornecidos
            if top_depth is not None and base_depth is not None:
                df_dasfa = df_dasfa[
                    (df_dasfa[profundidade] >= top_depth) &
                    (df_dasfa[profundidade] <= base_depth)
                    ]

            # Remove as linhas com valores ausentes se value for igual a 'yes_nulo'
            if value == 'yes_nulo':
                df_dasfa = df_dasfa.dropna(how='any')

            if dash.callback_context.triggered[0]['prop_id'] == "calcular-fa.n_clicks":
                df_fa1 = df_dasfa
                prof = np.array(df_fa1[profundidade])
                GR = np.array(df_fa1[gr])
                IGR = igr(GR)
                FA = SandFraction(clavier(IGR))
                df_fa = pd.DataFrame({
                    'Profundidade [m]': prof,
                    'Fração Areia [%]': FA
                })
                las_fa.add_curve('PROFUNDIDADE', df_fa['Profundidade [m]'].values, unit='m')
                las_fa.add_curve('FRAÇÃO AREIA', df_fa['Fração Areia [%]'].values, unit='%')
                path_fa = os.path.join(os.getcwd(), 'static')
                filename_fa = os.path.join(path_fa, 'fracao_areia.las')
                with open(filename_fa, mode='w') as file_fa:
                    las_fa.write(file_fa)
                # df_fa.to_csv("static/teste_fa.csv")
                figure_fa = px.line(
                    df_fa,
                    x='Fração Areia [%]',
                    y='Profundidade [m]',
                    title='Fração de Areia'
                )

            return figure_fa

    @app.callback(
        Output('das-figure', 'figure'),
        Input('target-select1', 'value'),
        Input('top-depth', 'value'),
        Input('base-depth', 'value'),
        Input('las-filenames-div2', 'children'),
        Input('calcular-das', 'n_clicks'),
        Input('select-prof', 'value'),
        Input('select-gr', 'value'),
        Input('select-por', 'value'),
        Input('select-den', 'value'),
    )
    def load_las_and_update_df(
            value,
            top_depth,
            base_depth,
            filename,
            n_clicks_das,
            profundidade,
            gr,
            por,
            den
    ):

        las_das = lasio.LASFile()
        figure_das = px.line()  # criar figura padrão para o gráfico DAS

        if not all([profundidade, gr, por, den]):
            raise PreventUpdate
        if not dash.callback_context.triggered:
            raise PreventUpdate

        if profundidade and gr and por and den:
            # Lê o arquivo LAS e cria o DataFrame
            las_dasfa = lasio.read(filename)
            df_dasfa = las_dasfa.df().reset_index()
            df_dasfa = df_dasfa[[profundidade, gr, por, den]]
            df_dasfa = df_dasfa.loc[(df_dasfa >= 0).all(axis=1)]

            # Filtra as linhas do DataFrame com base em top_depth e base_depth, se fornecidos
            if top_depth is not None and base_depth is not None:
                df_dasfa = df_dasfa[(df_dasfa[profundidade] >= top_depth) & (df_dasfa[profundidade] <= base_depth)]

            # Remove as linhas com valores ausentes se value for igual a 'yes_nulo'
            if value == 'yes_nulo':
                df_dasfa = df_dasfa.dropna(how='any')

            if dash.callback_context.triggered[0]['prop_id'] == "calcular-das.n_clicks":
                df_das1 = df_dasfa
                prof = np.array(df_das1[profundidade])
                NPHI = np.array(df_das1[por])
                RHOB = np.array(df_das1[den])
                DAS = DensidadeAparenteSeca(RHOB, NPHI)
                df_das = pd.DataFrame({'Profundidade [m]': prof, 'Densidade Aparente Seca [g/cm³]': DAS})
                las_das.add_curve('PROFUNDIDADE', df_das['Profundidade [m]'].values, unit='m')
                las_das.add_curve('DENSIDADE APARENTE SECA', df_das['Densidade Aparente Seca [g/cm³]'].values,
                                  unit='g/cm³')
                path_das = os.path.join(os.getcwd(), 'static')
                filename_das = os.path.join(path_das, 'den_aparente_seca.las')
                with open(filename_das, mode='w') as file_das:
                    las_das.write(file_das)
                # df_das.to_csv("static/teste_das.csv")
                figure_das = px.line(df_das, 'Densidade Aparente Seca [g/cm³]', 'Profundidade [m]',
                                     title='Densidade Aparente Seca')

            return figure_das

    @app.callback(
        Output('nulos-table', 'data'),
        Input('las-filenames-div2', 'children'),
        Input('select-prof', 'value'),
        Input('select-gr', 'value'),
        Input('select-por', 'value'),
        Input('select-den', 'value')
    )
    def nulos_table(filename, profundidade, gr, por, den):
        if not all([profundidade, gr, por, den]):
            raise PreventUpdate
        if profundidade and gr and por and den:
            # Lê o arquivo LAS e cria o DataFrame
            las_dasfa = lasio.read(filename)
            df_dasfa = las_dasfa.df().reset_index()
            df_dasfa = df_dasfa[[profundidade, gr, por, den]]
            nulos = (df_dasfa.isnull().sum() / df_dasfa.shape[0]).sort_values(ascending=False) * 100
            nulos_table = [{'Coluna': str(col), 'Porcentagem de Nulos': f'{val:.2f}%'} for col, val in nulos.items()]

        return nulos_table

    @app.server.route('/dash/DownloadFa')
    def download_fa():
        return send_from_directory(directory=os.path.join(os.getcwd(), "static"), path="fracao_areia.las", as_attachment=True, cache_timeout=-1)
    
    @app.server.route('/dash/DownloadDas')
    def download_das():
        return send_from_directory(directory=os.path.join(os.getcwd(), "static"), path="den_aparente_seca.las", as_attachment=True, cache_timeout=-1)





