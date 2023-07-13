# Módulo contendo callbacks relativos à uploads de arquivos
# Importações necessárias:
import dash
from dash.dash import no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import lasio
import re
import dash_uploader as du

def get_upload_callbacks(app):
    ##### CALLBACKS DE UPLOAD:
    ### ABA COT:
    @du.callback(output=Output('las-filenames-div', 'children'), id='upload-las-dlis')
    def update_las_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    # Ativando o Collapse do filtro de gráficos
    @app.callback(
        Output("collapse-cot-config", "is_open"),
        [Input("collapse-cot-config-button", "n_clicks")],
        [State("collapse-cot-config", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    # Collapse de Upload de COT:
    @app.callback([Output('collapse-upload-age', 'is_open'),
                   Output('collapse-upload-sedrate', 'is_open'),
                   Output('collapse-upload-pp', 'is_open'),
                   Output('collapse-upload-dbd', 'is_open'),
                   Output('collapse-upload-wd', 'is_open'),
                   Output('collapse-upload-sf', 'is_open'),
                   Output('collapse-upload-me', 'is_open')],
                  [Input('checklist-upload-files', 'value')])
    def update_collapses(checklist):
        if not dash.callback_context.triggered:
            raise PreventUpdate

        age = False
        sedrate = False
        pp = False
        dbd = False
        wd = False
        sf = False
        me = False

        for value in checklist:
            if value == 'age':
                age = True
            if value == 'sedrate':
                sedrate = True
            if value == 'pp':
                pp = True
            if value == 'dbd':
                dbd = True
            if value == 'wd':
                wd = True
            if value == 'sf':
                sf = True
            if value == 'me':
                me = True

        return age, sedrate, pp, dbd, wd, sf, me

    # Upload de idades
    @du.callback(output=Output('age-filenames-div', 'children'), id='upload-ages')
    def update_las_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    # Cor do collapse de idades:
    @app.callback(Output('card-ages', 'color'),
                  [Input('age-filenames-div', 'children')])
    def card_success(ages_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if ages_filename is None:
            raise PreventUpdate
        return 'success'

    # Ativando Dropdown de idades:
    @app.callback([Output('select-age-depth', 'disabled'),
                   Output('select-age-var', 'disabled'),
                   Output('select-age-depth', 'options'),
                   Output('select-age-var', 'options'),
                   Output('select-age-var', 'value'),
                   Output('select-age-depth', 'value')],
                  [Input('age-filenames-div', 'children')])
    def update_dd_ages(age_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if age_filename is None:
            raise PreventUpdate
        if age_filename is not None:
            try:
                if age_filename[-3:] == 'csv':
                    df = pd.read_csv(age_filename)
                if age_filename[-3:] == 'txt':
                    df = pd.read_csv(age_filename, sep='\t')
            except UnicodeError:
                if age_filename[-3:] == 'csv':
                    df = pd.read_csv(age_filename, encoding='iso-8859-1')
                if age_filename[-3:] == 'txt':
                    df = pd.read_csv(age_filename, sep='\t', encoding='iso-8859-1')

            dd_options = [{'label': str(col), 'value': str(col)} for col in df.columns]

            var_str = None
            dep_str = None
            for column in df:
                if var_str is None:
                    var_str = re.search("(^idade$|ma|age)", column, re.IGNORECASE)
                if dep_str is None:
                    dep_str = re.search("(depth|prof|dep |^md$)", column, re.IGNORECASE)

            return False, False, dd_options, dd_options, var_str.string if var_str is not None else None, dep_str.string if dep_str is not None else None

    # Upload de sedrate
    @du.callback(output=Output('sedrate-filenames-div', 'children'), id='upload-sedrate')
    def update_las_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    # Cor do collapse de sedrate:
    @app.callback(Output('card-sedrate', 'color'),
                  [Input('sedrate-filenames-div', 'children')])
    def card_success(sedrates_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if sedrates_filename is None:
            raise PreventUpdate
        return 'success'

    # Ativando Dropdown de sedrate:
    @app.callback([Output('select-sr-depth', 'disabled'),
                   Output('select-sr-var', 'disabled'),
                   Output('select-sr-depth', 'options'),
                   Output('select-sr-var', 'options'),
                   Output('select-sr-var', 'value'),
                   Output('select-sr-depth', 'value')],
                  [Input('sedrate-filenames-div', 'children')])
    def update_dd_sedrates(sedrate_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if sedrate_filename is None:
            raise PreventUpdate
        if sedrate_filename is not None:
            try:
                if sedrate_filename[-3:] == 'csv':
                    df = pd.read_csv(sedrate_filename)
                if sedrate_filename[-3:] == 'txt':
                    df = pd.read_csv(sedrate_filename, sep='\t')
            except UnicodeError:
                if sedrate_filename[-3:] == 'csv':
                    df = pd.read_csv(sedrate_filename, encoding='iso-8859-1')
                if sedrate_filename[-3:] == 'txt':
                    df = pd.read_csv(sedrate_filename, sep='\t', encoding='iso-8859-1')

            dd_options = [{'label': str(col), 'value': str(col)} for col in df.columns]

            var_str = None
            dep_str = None
            for column in df:
                if var_str is None:
                    var_str = re.search("(sed|rate|taxa|cm|ka)", column, re.IGNORECASE)
                if dep_str is None:
                    dep_str = re.search("(depth|prof|dep |^md$)", column, re.IGNORECASE)

            return False, False, dd_options, dd_options, var_str.string if var_str is not None else None, dep_str.string if dep_str is not None else None

    # Upload de pp
    @du.callback(output=Output('pp-filenames-div', 'children'), id='upload-pp')
    def update_las_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    # Cor do collapse de pp:
    @app.callback(Output('card-pp', 'color'),
                  [Input('pp-filenames-div', 'children')])
    def card_success(pp_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if pp_filename is None:
            raise PreventUpdate
        return 'success'

    # Ativando Dropdown de pp:
    @app.callback([Output('select-pp-depth', 'disabled'),
                   Output('select-pp-var', 'disabled'),
                   Output('select-pp-depth', 'options'),
                   Output('select-pp-var', 'options'),
                   Output('select-pp-var', 'value'),
                   Output('select-pp-depth', 'value')],
                  [Input('pp-filenames-div', 'children')])
    def update_dd_pp(pp_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if pp_filename is None:
            raise PreventUpdate
        if pp_filename is not None:
            try:
                if pp_filename[-3:] == 'csv':
                    df = pd.read_csv(pp_filename)
                if pp_filename[-3:] == 'txt':
                    df = pd.read_csv(pp_filename, sep='\t')
            except UnicodeError:
                if pp_filename[-3:] == 'csv':
                    df = pd.read_csv(pp_filename, encoding='iso-8859-1')
                if pp_filename[-3:] == 'txt':
                    df = pd.read_csv(pp_filename, sep='\t', encoding='iso-8859-1')

            dd_options = [{'label': str(col), 'value': str(col)} for col in df.columns]
            var_str = None
            dep_str = None
            for column in df:
                if var_str is None:
                    var_str = re.search("(pp|prod|prim|gc|m²)", column, re.IGNORECASE)
                if dep_str is None:
                    dep_str = re.search("(depth|prof|dep |^md$)", column, re.IGNORECASE)

            return False, False, dd_options, dd_options, var_str.string if var_str is not None else None, dep_str.string if dep_str is not None else None

    # Upload de dbd
    @du.callback(output=Output('dbd-filenames-div', 'children'), id='upload-dbd')
    def update_las_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    # Cor do collapse de dbd:
    @app.callback(Output('card-dbd', 'color'),
                  [Input('dbd-filenames-div', 'children')])
    def card_success(dbd_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if dbd_filename is None:
            raise PreventUpdate
        return 'success'

    # Ativando Dropdown de dbd:
    @app.callback([Output('select-dbd-depth', 'disabled'),
                   Output('select-dbd-var', 'disabled'),
                   Output('select-dbd-depth', 'options'),
                   Output('select-dbd-var', 'options'),
                   Output('select-dbd-var', 'value'),
                   Output('select-dbd-depth', 'value')],
                  [Input('dbd-filenames-div', 'children')])
    def update_dd_dbd(dbd_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if dbd_filename is None:
            raise PreventUpdate
        if dbd_filename is not None:
            try:
                if dbd_filename[-3:] == 'csv':
                    df = pd.read_csv(dbd_filename)
                if dbd_filename[-3:] == 'txt':
                    df = pd.read_csv(dbd_filename, sep='\t')
            except UnicodeError:
                if dbd_filename[-3:] == 'csv':
                    df = pd.read_csv(dbd_filename, encoding='iso-8859-1')
                if dbd_filename[-3:] == 'txt':
                    df = pd.read_csv(dbd_filename, sep='\t', encoding='iso-8859-1')

            dd_options = [{'label': str(col), 'value': str(col)} for col in df.columns]
            var_str = None
            dep_str = None
            for column in df:
                if var_str is None:
                    var_str = re.search("(rho|rhob|dry|bulk|dens|cm|dbd)", column, re.IGNORECASE)
                if dep_str is None:
                    dep_str = re.search("(depth|prof)", column, re.IGNORECASE)

            return False, False, dd_options, dd_options, var_str.string if var_str is not None else None, dep_str.string if dep_str is not None else None

    # Upload de idades
    @du.callback(output=Output('wd-filenames-div', 'children'), id='upload-wd')
    def update_las_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    # Cor do collapse de idades:
    @app.callback(Output('card-wd', 'color'),
                  [Input('wd-filenames-div', 'children')])
    def card_success(wd_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if wd_filename is None:
            raise PreventUpdate
        return 'success'

    # Ativando Dropdown de Water Depth:
    @app.callback([Output('select-wd-depth', 'disabled'),
                   Output('select-wd-var', 'disabled'),
                   Output('select-wd-depth', 'options'),
                   Output('select-wd-var', 'options'),
                   Output('select-wd-var', 'value'),
                   Output('select-wd-depth', 'value')],
                  [Input('wd-filenames-div', 'children')])
    def update_dd_wd(wd_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if wd_filename is None:
            raise PreventUpdate
        if wd_filename is not None:
            try:
                if wd_filename[-3:] == 'csv':
                    df = pd.read_csv(wd_filename)
                if wd_filename[-3:] == 'txt':
                    df = pd.read_csv(wd_filename, sep='\t')
            except UnicodeError:
                if wd_filename[-3:] == 'csv':
                    df = pd.read_csv(wd_filename, encoding='iso-8859-1')
                if wd_filename[-3:] == 'txt':
                    df = pd.read_csv(wd_filename, sep='\t', encoding='iso-8859-1')

            dd_options = [{'label': str(col), 'value': str(col)} for col in df.columns]

            var_str = None
            dep_str = None
            for column in df:
                if var_str is None:
                    var_str = re.search("(water|bat|paleobat|^wd$)", column, re.IGNORECASE)
                if dep_str is None:
                    dep_str = re.search("(depth|prof|dep |md)", column, re.IGNORECASE)

            return False, False, dd_options, dd_options, var_str.string if var_str is not None else None, dep_str.string if dep_str is not None else None

    # Upload de Sand Fraction
    @du.callback(output=Output('sf-filenames-div', 'children'), id='upload-sf')
    def update_las_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    # Cor do collapse de Sand Fraction:
    @app.callback(Output('card-sf', 'color'),
                  [Input('sf-filenames-div', 'children')])
    def card_success(sf_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if sf_filename is None:
            raise PreventUpdate
        return 'success'

    # Ativando Dropdown de Sand Fraction:
    @app.callback([Output('select-sf-depth', 'disabled'),
                   Output('select-sf-var', 'disabled'),
                   Output('select-sf-depth', 'options'),
                   Output('select-sf-var', 'options'),
                   Output('select-sf-var', 'value'),
                   Output('select-sf-depth', 'value')],
                  [Input('sf-filenames-div', 'children')])
    def update_dd_sf(sf_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if sf_filename is None:
            raise PreventUpdate
        if sf_filename is not None:
            try:
                if sf_filename[-3:] == 'csv':
                    df = pd.read_csv(sf_filename)
                if sf_filename[-3:] == 'txt':
                    df = pd.read_csv(sf_filename, sep='\t')
            except UnicodeError:
                if sf_filename[-3:] == 'csv':
                    df = pd.read_csv(sf_filename, encoding='iso-8859-1')
                if sf_filename[-3:] == 'txt':
                    df = pd.read_csv(sf_filename, sep='\t', encoding='iso-8859-1')

            dd_options = [{'label': str(col), 'value': str(col)} for col in df.columns]
            var_str = None
            dep_str = None
            for column in df:
                if var_str is None:
                    var_str = re.search("(sand|frac|%|fração|areia)", column, re.IGNORECASE)
                if dep_str is None:
                    dep_str = re.search("(depth|prof|dep |md )", column, re.IGNORECASE)

            return False, False, dd_options, dd_options, var_str.string if var_str is not None else None, dep_str.string if dep_str is not None else None

    # Upload de Marcadores estratigráficos
    @du.callback(output=Output('me-filenames-div', 'children'), id='upload-me')
    def update_las_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    # Cor do collapse de Marcadores estratigráficos:
    @app.callback(Output('card-me', 'color'),
                  [Input('me-filenames-div', 'children')])
    def card_success(me_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if me_filename is None:
            raise PreventUpdate
        return 'success'

    # Ativando Dropdown de Marcadores estratigráficos:
    @app.callback([Output('select-me-depth', 'disabled'),
                   Output('select-me-var', 'disabled'),
                   Output('select-me-depth', 'options'),
                   Output('select-me-var', 'options'),
                   Output('select-me-var', 'value'),
                   Output('select-me-depth', 'value')],
                  [Input('me-filenames-div', 'children')])
    def update_dd_me(me_filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if me_filename is None:
            raise PreventUpdate
        if me_filename is not None:
            try:
                if me_filename[-3:] == 'csv':
                    df = pd.read_csv(me_filename)
                if me_filename[-3:] == 'txt':
                    df = pd.read_csv(me_filename, sep='\t')
            except UnicodeError:
                if me_filename[-3:] == 'csv':
                    df = pd.read_csv(me_filename, encoding='iso-8859-1')
                if me_filename[-3:] == 'txt':
                    df = pd.read_csv(me_filename, sep='\t', encoding='iso-8859-1')

            dd_options = [{'label': str(col), 'value': str(col)} for col in df.columns]
            var_str = None
            dep_str = None
            for column in df:
                if var_str is None:
                    var_str = re.search("(marc|estr|%|Marcadores|Estratigráficos)", column, re.IGNORECASE)
                if dep_str is None:
                    dep_str = re.search("(depth|prof|dep |md )", column, re.IGNORECASE)

            return False, False, dd_options, dd_options, var_str.string if var_str is not None else None, dep_str.string if dep_str is not None else None

    ### Atualização de ranges:
    ## Las range
    @app.callback([Output('las-range-div', 'children')],
                  [Input('pp-las', 'value'),
                   Input('dbd-las', 'value'),
                   Input('sf-las', 'value'),
                   Input('sedrate-las', 'value'),
                   Input('wd-las', 'value')],
                  [State('las-filenames-div', 'children')])
    def update_las_range(pp_las, dbd_las, sf_las, sr_las, wd_las, las_path):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        curves = [pp_las, dbd_las, sf_las, sr_las, wd_las]
        lf = lasio.read(las_path)
        las_df = lf.df()
        mins = []
        maxs = []

        for curve in curves:
            if curve is not None:
                mins.append(np.min(las_df[curve].index))
                maxs.append(np.max(las_df[curve].index))

        children = [np.max(mins), np.min(maxs)]
        print('Profundidade mínima do las: ' + str(children[0]))
        print('Profundidade máxima do las: ' + str(children[1]))

        return [children]

    ### Atualização de ranges:
    # Sedrate range
    @app.callback([Output('sedrate-range-div', 'children')],
                  [Input('select-sr-var', 'value'),
                   Input('select-sr-depth', 'value'),
                   Input('sedrate-filenames-div', 'children')],
                  [State('no-data', 'value')])
    def update_sedrate_range(sr_var, sr_depth, sr_path, no_data):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if sr_var is not None and sr_depth is not None:
            if sr_path is not None:
                try:
                    if sr_path[-3:] == 'csv':
                        df = pd.read_csv(sr_path, na_values=no_data)
                    if sr_path[-3:] == 'txt':
                        df = pd.read_csv(sr_path, sep='\t', na_values=no_data)
                except UnicodeError:
                    if sr_path[-3:] == 'csv':
                        df = pd.read_csv(sr_path, na_values=no_data, encoding='iso-8859-1')
                    if sr_path[-3:] == 'txt':
                        df = pd.read_csv(sr_path, sep='\t', na_values=no_data, encoding='iso-8859-1')

            min_depth = np.min(df[sr_depth])
            max_depth = np.max(df[sr_depth])

            children = [min_depth, max_depth]
            print('Profundidade mínima do sedrate: ' + str(min_depth))
            print('Profundidade máxima do sedrate: ' + str(max_depth))

            return [children]
        else:
            return no_update

    # PP range
    @app.callback([Output('pp-range-div', 'children')],
                  [Input('select-pp-var', 'value'),
                   Input('select-pp-depth', 'value'),
                   Input('pp-filenames-div', 'children')],
                  [State('no-data', 'value')])
    def update_pp_range(pp_var, pp_depth, pp_path, no_data):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if pp_var is not None and pp_depth is not None:
            if pp_path is not None:
                try:
                    if pp_path[-3:] == 'csv':
                        df = pd.read_csv(pp_path, na_values=no_data)
                    if pp_path[-3:] == 'txt':
                        df = pd.read_csv(pp_path, sep='\t', na_values=no_data)
                except UnicodeError:
                    if pp_path[-3:] == 'csv':
                        df = pd.read_csv(pp_path, na_values=no_data, encoding='iso-8859-1')
                    if pp_path[-3:] == 'txt':
                        df = pd.read_csv(pp_path, sep='\t', na_values=no_data, encoding='iso-8859-1')

            min_depth = np.min(df[pp_depth])
            max_depth = np.max(df[pp_depth])

            children = [min_depth, max_depth]
            print('Profundidade mínima de Produtividade Primária: ' + str(min_depth))
            print('Profundidade máxima de Produtividade Primária: ' + str(max_depth))

            return [children]
        else:
            return no_update

    # DBD range
    @app.callback([Output('dbd-range-div', 'children')],
                  [Input('select-dbd-var', 'value'),
                   Input('select-dbd-depth', 'value'),
                   Input('dbd-filenames-div', 'children')],
                  [State('no-data', 'value')])
    def update_dbd_range(dbd_var, dbd_depth, dbd_path, no_data):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if dbd_var is not None and dbd_depth is not None:
            try:
                if dbd_path[-3:] == 'csv':
                    df = pd.read_csv(dbd_path, na_values=no_data)
                if dbd_path[-3:] == 'txt':
                    df = pd.read_csv(dbd_path, sep='\t', na_values=no_data)
            except UnicodeError:
                if dbd_path[-3:] == 'csv':
                    df = pd.read_csv(dbd_path, na_values=no_data, encoding='iso-8859-1')
                if dbd_path[-3:] == 'txt':
                    df = pd.read_csv(dbd_path, sep='\t', na_values=no_data, encoding='iso-8859-1')

            min_depth = np.min(df[dbd_depth])
            max_depth = np.max(df[dbd_depth])

            children = [min_depth, max_depth]
            print('Profundidade mínima de Produtividade Primária: ' + str(min_depth))
            print('Profundidade máxima de Produtividade Primária: ' + str(max_depth))

            return [children]
        else:
            return no_update

    # SF Range
    @app.callback([Output('sf-range-div', 'children')],
                  [Input('select-sf-var', 'value'),
                   Input('select-sf-depth', 'value'),
                   Input('sf-filenames-div', 'children')],
                  [State('no-data', 'value')])
    def update_pp_range(sf_var, sf_depth, sf_path, no_data):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if sf_var is not None and sf_depth is not None:
            try:
                if sf_path[-3:] == 'csv':
                    df = pd.read_csv(sf_path, na_values=no_data)
                if sf_path[-3:] == 'txt':
                    df = pd.read_csv(sf_path, sep='\t', na_values=no_data)
            except UnicodeError:
                if sf_path[-3:] == 'csv':
                    df = pd.read_csv(sf_path, na_values=no_data, encoding='iso-8859-1')
                if sf_path[-3:] == 'txt':
                    df = pd.read_csv(sf_path, sep='\t', na_values=no_data, encoding='iso-8859-1')

            min_depth = np.min(df[sf_depth])
            max_depth = np.max(df[sf_depth])

            children = [min_depth, max_depth]
            print('Profundidade mínima de Sand Fraction: ' + str(min_depth))
            print('Profundidade máxima de Sand Fraction: ' + str(max_depth))

            return [children]
        else:
            return no_update

    # Atualização de Range de profundidade:
    @app.callback([Output('range-toc', 'min'),
                   Output('range-toc', 'max'),
                   Output('range-toc', 'value'),
                   Output('range-toc', 'marks'),
                   Output('range-toc', 'disabled')],
                  [Input('las-range-div', 'children'),
                   Input('sedrate-range-div', 'children'),
                   Input('pp-range-div', 'children'),
                   Input('dbd-range-div', 'children'),
                   Input('sf-range-div', 'children')])
    def update_mom_depth_range(las_range, sr_range, pp_range, dbd_range, sf_range):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        ranges = [las_range, sr_range, pp_range, dbd_range, sf_range]

        if not any(ranges):
            raise PreventUpdate

        depth_values = []
        min_depths = []
        max_depths = []

        for range in ranges:
            if range is not None:
                min_depths.append(range[0])
                max_depths.append(range[1])
                for val in range:
                    depth_values.append(val)

        min_depth = np.max(min_depths)
        max_depth = np.min(max_depths)

        marks = {
            str(min_depth): {'label': str(min_depth) + 'm'},
            str(max_depth): {'label': str(max_depth) + 'm'}
        }

        return min_depth, max_depth, [min_depth, max_depth], marks, False

    # Profundidade mínima e máxima:
    @app.callback(Output('label-selected-mom-range', 'children'),
                  Input('range-toc', 'value'))
    def show_selected_mom_range(range_values):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if range_values is None:
            raise PreventUpdate
        txt = 'Profundidade Mínima: ' + str(min(range_values)) + 'm, Profundidade Máxima: ' + str(
            max(range_values)) + 'm'

        return txt

    ### ABA MATURAÇÃO:
    # Collapse de Upload de Maturação:
    @app.callback([Output('collapse-upload-s1', 'is_open'),
                   Output('collapse-upload-s2', 'is_open'),
                   Output('collapse-upload-hi', 'is_open'),
                   Output('collapse-upload-vitrinita', 'is_open'),
                   Output('collapse-upload-cotr', 'is_open'),
                   Output('collapse-upload-tmax', 'is_open')],
                  [Input('checklist-upload-files-2', 'value')])
    def update_collapses(checklist):
        if not dash.callback_context.triggered:
            raise PreventUpdate

        s1 = False
        s2 = False
        hi = False
        vitrinita = False
        cotr = False
        tmax = False

        for value in checklist:
            if value == 's1':
                s1 = True
            if value == 's2':
                s2 = True
            if value == 'hi':
                hi = True
            if value == 'vitrinita':
                vitrinita = True
            if value == 'cotr':
                cotr = True
            if value == 'tmax':
                tmax = True

        return s1, s2, hi, vitrinita, cotr, tmax
    
    # Upload tabela paleobatimetria
    @du.callback(output=Output('paleobat-filenames-calculadora-div', 'children'), id='upload-paleobat-table')
    def upload_paleobat(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]
    
    # Ativando Dropdowns de Paleobat:
    @app.callback([Output('select-paleobat-var', 'disabled'),
                   Output('select-paleobat-var', 'options'),
                   Output('select-paleobat-var', 'value')],
                   [Input('paleobat-filenames-calculadora-div', 'children')])
    def paleobat_dd_update(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        if filename is not None:
            try:
                if filename[-3:] == 'csv':
                    df = pd.read_csv(filename)
                if filename[-3:] == 'txt':
                    df = pd.read_csv(filename, sep='\t')
                if filename[-3:] == 'xls':
                    df = pd.read_excel(filename)
                if filename[-4:] == 'xlsx':
                    df = pd.read_excel(filename, engine="openpyxl")
            except UnicodeError:
                if filename[-3:] == 'csv':
                    df = pd.read_csv(filename, encoding='iso-8859-1')
                if filename[-3:] == 'txt':
                    df = pd.read_csv(filename, sep='\t', encoding='iso-8859-1')
                if filename[-3:] == 'xls':
                    df = pd.read_excel(filename, encoding='iso-8859-1')
                if filename[-4:] == 'xlsx':
                    df = pd.read_excel(filename, engine="openpyxl", encoding='iso-8859-1')

            dd_options = [{'label': str(col), 'value': str(col)} for col in df.columns]

            paleo_str = None
            
            for column in df:
                if re.search("(Paleobatimetria |^Paleobatimetria$)", column, re.IGNORECASE):
                    paleo_str = column
            else:
                paleo_str = no_update
                

            return False, dd_options, paleo_str, \
    \
    
    # Upload de tabela de maturação:
    @du.callback(output=Output('maturation-filenames-div', 'children'), id='upload-maturation-table')
    def update_s1_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    # Ativando Dropdowns de Maturação:
    @app.callback([Output('select-s1-var', 'disabled'),
                   Output('select-s1-var', 'options'),
                   Output('select-s1-var', 'value'),
                   Output('select-s2-var', 'disabled'),
                   Output('select-s2-var', 'options'),
                   Output('select-s2-var', 'value'),
                   Output('select-s3-var', 'disabled'),
                   Output('select-s3-var', 'options'),
                   Output('select-s3-var', 'value'),
                   Output('select-hi-var', 'disabled'),
                   Output('select-hi-var', 'options'),
                   Output('select-hi-var', 'value'),
                   Output('select-vitrinita-var', 'disabled'),
                   Output('select-vitrinita-var', 'options'),
                   Output('select-vitrinita-var', 'value'),
                   Output('select-cotr-var', 'disabled'),
                   Output('select-cotr-var', 'options'),
                   Output('select-cotr-var', 'value'),
                   Output('select-tmax-var', 'disabled'),
                   Output('select-tmax-var', 'options'),
                   Output('select-tmax-var', 'value'),
                   Output('maturation-depth', 'disabled'),
                   Output('maturation-depth', 'options'),
                   Output('maturation-depth', 'value')],
                  [Input('maturation-filenames-div', 'children'),
                   Input('calculate-ih-btn', 'n_clicks'),
                   Input('hi-div', 'children')])
    def update_maturation_vars(filename, n_clicks, hi_div):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        if filename is not None:
            try:
                if filename[-3:] == 'csv':
                    df = pd.read_csv(filename)
                if filename[-3:] == 'txt':
                    df = pd.read_csv(filename, sep='\t')
                if filename[-3:] == 'xls':
                    df = pd.read_excel(filename)
                if filename[-4:] == 'xlsx':
                    df = pd.read_excel(filename, engine="openpyxl")
            except UnicodeError:
                if filename[-3:] == 'csv':
                    df = pd.read_csv(filename, encoding='iso-8859-1')
                if filename[-3:] == 'txt':
                    df = pd.read_csv(filename, sep='\t', encoding='iso-8859-1')
                if filename[-3:] == 'xls':
                    df = pd.read_excel(filename, encoding='iso-8859-1')
                if filename[-4:] == 'xlsx':
                    df = pd.read_excel(filename, engine="openpyxl", encoding='iso-8859-1')

            ih_context = False
            for context in dash.callback_context.triggered:
                if 'hi-div.children' == context['prop_id']:
                    ih_context = True

            dd_options = [{'label': str(col), 'value': str(col)} for col in df.columns]

            s1_str = None
            s2_str = None
            s3_str = None
            hi_str = None
            vitrinita_str = None
            cotr_str = None
            tmax_str = None
            dep_str = None

            if not ih_context:
                for column in df:
                    if re.search("(dep|depth|prof|md )", column, re.IGNORECASE):
                        dep_str = column
                    if re.search("(s1 |^s1$)", column, re.IGNORECASE):
                        s1_str = column
                    if re.search("(s2 |^s2$)", column, re.IGNORECASE):
                        s2_str = column
                    if re.search("(s3 |^s3$)", column, re.IGNORECASE):
                        s3_str = column
                    if re.search("(hi |ih |^hi$|^ih$)", column, re.IGNORECASE):
                        hi_str = column
                        if column == 'IH Calculado [mg HC/g COT]':
                            hi_str = 'IH Calculado [mg HC/g COT]'
                    if re.search("(Ro |refletancia|refletância|vitrinita|^Ro$)", column, re.IGNORECASE):
                        vitrinita_str = column
                    if re.search("(cot |cotr |toc |^cot$|^toc$)", column, re.IGNORECASE):
                        cotr_str = column
                    if re.search("(temp|tmax |max |tmáx|tmax)", column, re.IGNORECASE):
                        tmax_str = column
            else:
                s1_str = no_update
                s2_str = no_update
                s3_str = no_update
                hi_str = 'IH Calculado [mg HC/g COT]'
                vitrinita_str = no_update
                cotr_str = no_update
                tmax_str = no_update
                dep_str = no_update

            return False, dd_options, s1_str, \
                   False, dd_options, s2_str, \
                   False, dd_options, s3_str, \
                   False, dd_options, hi_str, \
                   False, dd_options, vitrinita_str, \
                   False, dd_options, cotr_str, \
                   False, dd_options, tmax_str, \
                   False, dd_options, dep_str, \
 \
                # Range da Maturação:

    @app.callback([Output('maturation-range-div', 'children')],
                  [Input('maturation-depth', 'value'),
                   Input('maturation-filenames-div', 'children')])
    def update_maturation_range(maturation_depth, maturation_path):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if maturation_depth is not None:
            if maturation_path is not None:
                try:
                    if maturation_path[-3:] == 'csv':
                        df = pd.read_csv(maturation_path)
                    if maturation_path[-3:] == 'txt':
                        df = pd.read_csv(maturation_path, sep='\t')
                    if maturation_path[-4:] == 'xlsx':
                        df = pd.read_excel(maturation_path, engine="openpyxl")
                except UnicodeError:
                    if maturation_path[-3:] == 'csv':
                        df = pd.read_csv(maturation_path, encoding='iso-8859-1')
                    if maturation_path[-3:] == 'txt':
                        df = pd.read_csv(maturation_path, sep='\t', encoding='iso-8859-1')
                    if maturation_path[-4:] == 'xlsx':
                        df = pd.read_excel(maturation_path, engine="openpyxl", encoding='iso-8859-1')

            min_depth = np.min(df[maturation_depth].dropna())
            max_depth = np.max(df[maturation_depth].dropna())

            children = [min_depth, max_depth]
            print('Profundidade mínima do dataset de maturação: ' + str(min_depth))
            print('Profundidade máxima do dataset de maturação: ' + str(max_depth))

            return [children]
        else:
            return no_update

    ## UPLOAD COMPARAÇÃO:
    @du.callback(output=Output('compare-filenames-div', 'children'), id='compare-upload-extra')
    def update_compare_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        if filename[0].split('.')[-1] == 'las':
            lf = lasio.read(filename[0])
            las_df = lf.df()
            las_df['DEPTH'] = lf.depth_m
            las_df.to_csv(filename[0].split('.')[0] + '.txt', index=False, sep='\t')
            filename[0] = filename[0].split('.')[0] + '.txt'
        return filename[0]

    # Atualização de Seleção de Variável de Filtragem (aba Maturação):
    @app.callback(Output('filtro-var', 'options'),
                  [Input('maturation-filenames-div', 'children')])
    def update_filtro_optns(maturation_path):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if maturation_path is None:
            raise PreventUpdate
        if maturation_path is not None:
            try:
                if maturation_path[-3:] == 'csv':
                    maturation_df = pd.read_csv(maturation_path)
                if maturation_path[-3:] == 'txt':
                    maturation_df = pd.read_csv(maturation_path, sep='\t')
                if maturation_path[-3:] == 'xls':
                    maturation_df = pd.read_excel(maturation_path)
                if maturation_path[-4:] == 'xlsx':
                    maturation_df = pd.read_excel(maturation_path, engine="openpyxl")
            except UnicodeError:
                if maturation_path[-3:] == 'csv':
                    maturation_df = pd.read_csv(maturation_path, encoding='iso-8859-1')
                if maturation_path[-3:] == 'txt':
                    maturation_df = pd.read_csv(maturation_path, sep='\t', encoding='iso-8859-1')
                if maturation_path[-3:] == 'xls':
                    maturation_df = pd.read_excel(maturation_path, encoding='iso-8859-1')
                if maturation_path[-4:] == 'xlsx':
                    maturation_df = pd.read_excel(maturation_path, engine="openpyxl", encoding='iso-8859-1')

        options = [{'label': col, 'value': col} for col in maturation_df.columns]
        return options

    # Profundidade mínima e máxima:
    @app.callback(Output('label-selected-maturation-range', 'children'),
                  Input('range-maturation', 'value'))
    def show_selected_maturation_range(range_values):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if range_values is None:
            raise PreventUpdate
        txt = 'Profundidade Mínima: ' + str(min(range_values)) + 'm, Profundidade Máxima: ' + str(
            max(range_values)) + 'm'

        return txt

    # Upload de las para Cicloestratigrafia
    @du.callback(output=Output('las-files-sedrate', 'children'), id='upload-las-sedrate')
    def update_las_curves(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    @app.callback([
        Output('sedrate-depth', 'options'),
        Output('sedrate-gr', 'options'),
        Output('sedrate-depth', 'value'),
        Output('sedrate-gr', 'value'),
        Output('sedrate-base', 'value'),
        Output('sedrate-topo', 'value')
    ],
    [
        Input('las-files-sedrate', 'children')
    ])
    def update_depth_gr(las_path):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if las_path is None:
            raise PreventUpdate
        las = lasio.read(las_path)
        curves_options = [{'label':curve, 'value':curve} for curve in las.curvesdict]

        base = np.max(las.depth_m)
        topo = np.min(las.depth_m)

        var_str = None
        dep_str = None
        for column in las.df().columns:
            if var_str is None:
                var_str = re.search("(gr|gamma|ray)", column, re.IGNORECASE)
                if var_str:
                    var_str = var_str.string
            if dep_str is None:
                dep_str = re.search("(depth|prof|dep|dept|md|tvd)", column, re.IGNORECASE)
                if dep_str:
                    dep_str = dep_str.string

        return curves_options, curves_options, dep_str, var_str, base, topo

    ##aba fração de areia
    @du.callback(output=Output('las-filenames-div2', 'children'), id='upload-dasfa')
    def upload_las_dasfa(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate
        return filename[0]

    @app.callback(
        [
            Output('select-prof', 'disabled'),
            Output('select-prof', 'options'),
            Output('select-prof', 'value'),
            Output('select-gr', 'disabled'),
            Output('select-gr', 'options'),
            Output('select-gr', 'value'),
            Output('select-por', 'disabled'),
            Output('select-por', 'options'),
            Output('select-por', 'value'),
            Output('select-den', 'disabled'),
            Output('select-den', 'options'),
            Output('select-den', 'value'),
        ],
        [Input('las-filenames-div2', 'children')]
    )
    def update_dropdowns(filename):
        if not dash.callback_context.triggered:
            raise PreventUpdate
        if filename is None:
            raise PreventUpdate

        las_dasfa = lasio.read(filename)
        df_dasfa = las_dasfa.df().reset_index()

        prof_options = [{'label': str(col), 'value': str(col)} for col in df_dasfa.columns]
        gr_options = [{'label': str(col), 'value': str(col)} for col in df_dasfa.columns]
        por_options = [{'label': str(col), 'value': str(col)} for col in df_dasfa.columns]
        den_options = [{'label': str(col), 'value': str(col)} for col in df_dasfa.columns]

        return False, prof_options, None, False, gr_options, None, False, por_options, None, False, den_options, None
