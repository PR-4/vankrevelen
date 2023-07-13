import dash
import zipfile
import plotly.express as px
from dash.exceptions import PreventUpdate
from plotly import subplots
import plotly.graph_objs as go
import  skfuzzy  as  fuzz
from  skfuzzy  import  control  as  ctrl
import pandas as pd
import numpy as np

# Índice de Hidrogênio Inicial
def hi0_dahl_2004(simulations_df, s2):
    get_hi0 = lambda row: (100*row[s2])/row['Carbono Ativo [%]']
    simulations_df['IH\u2080 Ativo [mg HC/g COT]'] = simulations_df.apply(get_hi0, axis=1)
    return simulations_df

def calculate_hi0_reftable(simulations_df, s2s3_var):
    simulations_df['Qualidade'] = simulations_df.apply(lambda row: 'Tipo I' if row[s2s3_var] >= 15
        else 'Tipo I/II' if (row[s2s3_var] < 15) & (row[s2s3_var] >= 11.25)
        else 'Tipo II/III' if (row[s2s3_var] < 11.25) & (row[s2s3_var] >= 4.25)
        else 'Tipo III/IV' if (row[s2s3_var] < 4.25) & (row[s2s3_var] > 1)
        else 'Tipo IV', axis=1)
    simulations_df['Hi inicial'] = simulations_df.apply(lambda row: 750 if row['Qualidade'] == 'Tipo I'
        # Mistura entre tipo I e II
        #  tipo I = (razão s2/s3 - 11.25)/(15 - 11.25)
        #  tipo II = 1 - tipo I
        else 750 * (row[s2s3_var] - 11.25) / (15 - 11.25) + 450 * (1 - ((row[s2s3_var] - 11.25) / (15 - 11.25))) if row['Qualidade'] == "Tipo I/II"
        # Mistura entre tipo II e III
        # Tipo II = (razão s2/s3 - 4.25)/(11.25 - 4.25)
        # Tipo III = 1 - tipo II
        else 450 * (row[s2s3_var] - 4.25) / (11.25 - 4.25) + 125 * (1 - ((row[s2s3_var] - 4.25) / (11.25 - 4.25))) if row['Qualidade'] == "Tipo II/III"
        # Mistura entre tipo III e IV
        # Tipo III = (razão s2/s3 - 1)/(4.25 - 1)
        # Tipo IV = 1 - tipo III
        else 125 * (row[s2s3_var] - 1) / (4.25 - 1) + 50 * (1 - ((row[s2s3_var] - 1) / (4.25 - 1))) if row['Qualidade'] == "Tipo III/IV"
        # 100% tipo IV
        else 50 if row['Qualidade'] == "Tipo IV"
        else np.nan, axis=1)
    return simulations_df

# Cálculo do Transformation Ratio (Tr)
def filter_tr_values(row):
    try:
        if row['Taxa de Transformação [v/v]'] > 1:
            row = 1
        if row['Taxa de Transformação [v/v]'] < 0:
            row = 0
        else:
            row = row['Taxa de Transformação [v/v]']
        return row
    except:
        row = 1
        return row

def waples(df, tr_type, ro_var, depth_val, lamina_dagua):
    import scipy

    filter_water_depth = lambda row: 0.2 if row[depth_val] < lamina_dagua else row[ro_var]
    df_no_na = df[[ro_var, depth_val]].dropna()
    x = df_no_na[depth_val].values
    y = df_no_na[ro_var].values

    log_fit = scipy.optimize.curve_fit(lambda t, a, b: a + b * np.log(t), x, y)
    a = log_fit[0][0]
    b = log_fit[0][1]

    #interpolated_ro = np.interp(df[depth_val], x, y)
    log_ro = a + b * np.log(df[depth_val])

    new_ro_var = f'{ro_var}'+'_ajustado'
    df[new_ro_var] = log_ro
    # Filtrando valores de Ro abaixo de 0:
    filter_ro = lambda row: 0.2 if row[new_ro_var] < 0 else row[new_ro_var]
    df[new_ro_var] = df.apply(filter_ro, axis=1)

    if tr_type == 'waples-1998-1':
        get_tr = lambda row: -34.430609 + (183.63837 * row[new_ro_var]) - (361.494 * row[new_ro_var]**2) + (309.9 * row[new_ro_var]**3) - (96.8 * row[new_ro_var]**4)

    if tr_type == 'waples-1998-2':
        get_tr = lambda row: -822.70308 + (6217.2684 * row[new_ro_var]) - (19265.314 * row[new_ro_var]**2) + (31326.872 * row[new_ro_var]**3) - (28204.703 * row[new_ro_var]**4) + (13345.477 * row[new_ro_var]**5) - (2595.9299 * row[new_ro_var]**6)

    if tr_type == 'waples-1998-3':
        get_tr = lambda row: 6.6516023 - (33.879196 * row[new_ro_var]) + (64.978399 * row[new_ro_var]**2) - (60.264818 * row[new_ro_var]**3) + (29.700408 * row[new_ro_var]**4) - (7.5019085 * row[new_ro_var]**5) + (0.7656397 * row[new_ro_var]**6)

    df['Taxa de Transformação [v/v]'] = df.apply(get_tr, axis=1)

    # Aplicando filtros:
    # Tr deve ser progressivamente maior
    # + possuir valores entre 0 e 1
    # Resultado de tr não pode ser menor que 0
    df.sort_values(depth_val, inplace=True)
    df['Taxa de Transformação [v/v]'] = df.apply(filter_tr_values, axis=1)
    # resultados progressivamente maiores ou constantes
    tr_values = df['Taxa de Transformação [v/v]'].values
    progressive_tr_values = []
    for idx in range(0, len(tr_values)):
        if idx == 0:
            progressive_tr_values.append(tr_values[idx])
        else:
            if tr_values[idx] < progressive_tr_values[-1]:
                progressive_tr_values.append(progressive_tr_values[-1])
            else:
                progressive_tr_values.append(tr_values[idx])
    tr_values = np.array(progressive_tr_values)
    df['Taxa de Transformação [v/v]'] = tr_values

    return df

## 1- Justwan and Dahl, 2005
def tr_justwan_dahl(df, hi0, hid, alpha=0.086):
    get_tr = lambda row: ((1/alpha)*100*(row[hi0]-row[hid]))/(row[hi0]*((1/alpha)*100-row[hid]))
    df['Taxa de Transformação [v/v]'] = df.apply(get_tr, axis=1)
    return df

##Cálculo do RHP
def calculate_RHP(df, s1, s2, toc):
    get_rhp = lambda row:((row[s1]+row[s2])/(row[toc]))
    df['RHP'] = df.apply(get_rhp, axis=1)
    return df

## 2. Peters et al., 1996
def tr_peters_1996(df, hipd, hio, s1, s2, pio=0.02):
    # Hipd: present day hydrogen index
    # Hio: original hydrogen index.
    # Pipd: (S1 / (S1 + S2)
    # PIo: original production index of thermally immature organic matter, equal to 0.02
    get_tr = lambda row: 1 - (row[hipd]*(1200-(row[hio]/(1-pio))))/(row[hio]*(1200-(row[hipd]/(1-(row[s1])/(row[s1]+row[s2])))))
    df['Taxa de Transformação [v/v]'] = df.apply(get_tr, axis=1)
    return df

## 3. Jarvie et al., 2007
def tr_jarvie_2007(df, hipd, hio, s1, s2, pio=0.02):
    # Hipd: present day hydrogen index
    # Hio: original hydrogen index.
    # Pipd: (S1 / (S1 + S2)
    # PIo: original production index of thermally immature organic matter, equal to 0.02
    get_tr = lambda row: 1 - (row[hipd]*(1200-(row[hio]*(1-pio))))/(row[hio]*(1200-(row[hipd]*((1-(row[s1])/(row[s1]+row[s2]))))))
    df['Taxa de Transformação [v/v]'] = df.apply(get_tr, axis=1)
    return df

## 4. Tissot and Welte (1984)
def tr_tissot_welte(df, s2original, s2residual):
    get_tr = lambda row: ((row[s2original]-row[s2residual])/row[s2original])*100
    df['Taxa de Transformação [v/v]'] = df.apply(get_tr, axis=1)
    return df

## 5. Jarvie et al., 2012
def tr_jarvie_2012(df, hipd, hio):
    # Hipd: present day hydrogen index
    # Hio: original hydrogen index.
    get_tr = lambda row: (row[hio]-row[hipd])/(row[hio])
    df['Taxa de Transformação [v/v]'] = df.apply(get_tr, axis=1)
    return df

## 6. Zhuoheng Chen, Chunqing Jiang, 2015
def tr_zhuoheng_2015(df, hipd, hio):
    # Hipd: present day hydrogen index
    # Hio: original hydrogen index.
    get_tr = lambda row: (1200*(row[hio]-row[hipd]))/(row[hio]*(1200-row[hipd]))
    df['Taxa de Transformação [v/v]'] = df.apply(get_tr, axis=1)
    return df

# Cálculo do carbono orgânico total inicial (COT 0 )
## 1- Justwan and Dahl, 2005
def cot0_justwan_dahl(df, toc, s2, tr, alpha):
    get_cot0 = lambda row: row[toc]+((row[s2]*row[tr])/(1-row[tr]))*alpha
    df['COT\u2080 [%]'] = df.apply(get_cot0, axis=1)
    return df

## 2. Peters et al., 1996
def cot0_peters_1996(df, hipd, tocpd, hio, tr):
    get_cot0 = lambda row: (83.33*row[hipd]*row[tocpd])/(row[hio]*(1-row[tr])*(83.33-row[tocpd])+row[hipd]*row[tocpd])
    df['COT\u2080 [%]'] = df.apply(get_cot0, axis=1)
    return df

## 3. Jarvie et al., 2007
def cot0_jarvie_2007(df, hipd, tocpd, hio, tr, k):
    get_cot0 = lambda row: (83.33*row[hipd]*(row[tocpd]/(1+k)))/(row[hio]*(1-row[tr])*(83.33-(row[tocpd]/(1+k)))+(row[hipd]*(row[tocpd]/(1+k))))
    df['COT\u2080 [%]'] = df.apply(get_cot0, axis=1)
    return df

# Cálculo de S2 0 inicial (S2 0 )
## 1. Justwan and Dahl, 2005
def s20_justwan_dahl(df, s2, tr):
    get_s20 = lambda row: row[s2]/(1-row[tr])
    df['S2\u2080 [mg HC/g rocha]'] = df.apply(get_s20, axis=1)
    return df

## 2. Jarvie et al., 2007
def s20_jarvie_2007(df, toc0, tr):
    get_s20 = lambda row: row[toc0]*0.36/0.08333
    df['S2\u2080 [mg HC/g rocha]'] = df.apply(get_s20, axis=1)
    return df

    ################################ abaixo, apenas funções relacionadas aos gráficos de plotagem da maturação ################################


def result_hi0_func(n_clicks,
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

def result_tr_func(n_clicks, maturation_depth, s2s3_var, s2s3_constant, s2s3_check, maturation_path, hi_var, hi_constant, hi_check,
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

def result_quantidade_func(n_clicks,
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


############ QUALIDADE DE M.O. #####################

def result_mo_func(n_clicks,
                       maturation_depth, hi_var, hi_constant, hi_check,
                       maturation_path,
                       oi_var, oi_constant, oi_check,
                       qualidade_range,
                       qualidade_select,
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
            simulations_df = pd.read_excel(maturation_path, na_values=no_data)

    if hi_var is None:
        get_hi = lambda row: hi_constant
        simulations_df['COTr [%]'] = simulations_df.apply(get_hi, axis=1)
        constantes.append('hi')
        hi_var = 'IH [mg HC/g COT]'
    if oi_var is None:
        get_oi = lambda row: oi_constant
        simulations_df['IO [mg CO\u2082/g COT]'] = simulations_df.apply(get_oi, axis=1)
        constantes.append('oi')
        oi_var = 'IO [mg CO\u2082/g COT]'

    if qualidade_select == 'reftable':
        # Aplicando condições da tabela de referência:
        conditions =  [simulations_df[hi_var] >= 600,
                      (simulations_df[hi_var] < 600) & (simulations_df[hi_var] >= 300),
                      (simulations_df[hi_var] < 300) & (simulations_df[hi_var] >= 200),
                      (simulations_df[hi_var] < 200) & (simulations_df[hi_var] >= 50),
                       simulations_df[hi_var] < 50]
        choices = ["Tipo I", "Tipo II", "Tipo III", "Tipo IV", "Tipo V"]

        simulations_df['Qualidade'] = np.select(conditions, choices, default=np.nan)

        figure = px.scatter(simulations_df, x=hi_var, y=oi_var, color='Qualidade')

    # Salvando dataframes resultado:
    simulations_df.to_csv('static/qualidade_simulation_' + str(n_clicks) + '.csv', index=False, sep=';')
    simulations_df.to_string("static/qualidade_simulation_" + str(n_clicks) + ".txt", index=False)

    z = zipfile.ZipFile('static/qualidade_simulation_' + str(n_clicks) + '.zip', 'w', zipfile.ZIP_DEFLATED)
    z.write('static/qualidade_simulation_' + str(n_clicks) + '.txt')
    z.write('static/qualidade_simulation_' + str(n_clicks) + '.csv')
                   
    return figure


################### MATURIDADE TERMICA ###########################

def result_maturidade_func(n_clicks,
                        maturation_depth,
                        hi_var, hi_constant, hi_check,
                        maturation_path,
                        tmax_var, tmax_constant, tmax_check,
                        ro_var, ro_constant, ro_check,
                        maturidade_range,
                        maturidade_select,
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
            simulations_df = pd.read_excel(maturation_path, na_values=no_data)

    if hi_var is None:
        get_hi = lambda row: hi_constant
        simulations_df['COTr [%]'] = simulations_df.apply(get_hi, axis=1)
        constantes.append('hi')
        hi_var = 'IH [mg HC/g COT]'
    if tmax_var is None:
        get_tmax = lambda row: tmax_constant
        simulations_df['Tmáx [°C]'] = simulations_df.apply(get_tmax, axis=1)
        constantes.append('tmax')
        tmax_var = 'Tmáx [°C]'
    if ro_var is None:
        get_ro = lambda row: ro_constant
        simulations_df['Tmáx [°C]'] = simulations_df.apply(get_ro, axis=1)
        constantes.append('ro')
        ro_var = 'Refletância da Vitrinita [Ro%]'

    if maturidade_select == 'reftable':
        # Aplicando condições da tabela de referência:

        conditions = [(simulations_df[ro_var] < 0.6),
                      (simulations_df[ro_var] >= 0.6) & (simulations_df[ro_var] < 0.65),
                      (simulations_df[ro_var] >= 0.65) & (simulations_df[ro_var] < 0.9),
                      (simulations_df[ro_var] >= 0.9) & (simulations_df[ro_var] < 1.35),
                      (simulations_df[ro_var] >= 1.35)]
        choices = ["Imaturo", "Maduro (Inicial)", "Maduro (Pico)", "Maduro (Final)", "Pós-Maduro"]

        simulations_df['Maturidade'] = np.select(conditions, choices, default=np.nan)

        figure = px.scatter(simulations_df, x=ro_var, y=tmax_var, color='Maturidade')

    # Salvando dataframes resultado:
    simulations_df.to_csv('static/maturidade_simulation_' + str(n_clicks) + '.csv', index=False, sep=';')
    simulations_df.to_string("static/maturidade_simulation_" + str(n_clicks) + ".txt", index=False)

    z = zipfile.ZipFile('static/maturidade_simulation_' + str(n_clicks) + '.zip', 'w', zipfile.ZIP_DEFLATED)
    z.write('static/maturidade_simulation_' + str(n_clicks) + '.txt')
    z.write('static/maturidade_simulation_' + str(n_clicks) + '.csv')

    return figure


################################## COT e S2 ###############################################

def result_cot_s2_func(n_clicks,
                  maturation_depth,
                  hi_var, hi_constant, hi_check,
                  maturation_path,
                  s1_var, s1_constant, s1_check,
                  s2_var, s2_constant, s2_check,
                  s2s3_var, s2s3_constant, s2s3_check,
                  ro_var, ro_constant, ro_check,
                  cotr_var, cotr_constant, cotr_check,
                  qualidade_range,
                  hi0_select, tr_select, qualidade_select, eixo_x, eixo_y,
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
            simulations_df = pd.read_excel(maturation_path, na_values=no_data)

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
    if ro_var is None:
        get_ro = lambda row: ro_constant
        simulations_df['Tmáx [°C]'] = simulations_df.apply(get_ro, axis=1)
        constantes.append('ro')
        ro_var = 'Refletância da Vitrinita [Ro%]'
    if cotr_var is None:
        get_cotr = lambda row: cotr_constant
        simulations_df['COTr [%]'] = simulations_df.apply(get_cotr, axis=1)
        constantes.append('cotr')
        cotr_var = 'COTr [%]'
    if s2s3_var is None:
        get_s2s3 = lambda row: s2s3_constant
        simulations_df['Razão S2/S3 [mg HC/g rocha]'] = simulations_df.apply(get_s2s3, axis=1)
        constantes.append('s2s3')
        s2s3_var = 'Razão S2/S3 [mg HC/g rocha]'
        
    # Cálculando HI0:
    if hi0_select == 'reftable':
        print('Calculando HI0 com :' + str(hi0_select))
        simulations_df = calculate_hi0_reftable(simulations_df, s2s3_var)

    # Cálculando Taxa de Transformação:
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

    if qualidade_select == 'justwan-dahl-2005':
        get_s20 = lambda row: row[s2_var]/(1-row['Taxa de Transformação [v/v]']) if row['Taxa de Transformação [v/v]'] is not np.nan else np.nan
        get_cot0 = lambda row: row[cotr_var] + row[s2_var]/(1-row['Taxa de Transformação [v/v]']) if row['Taxa de Transformação [v/v]'] is not np.nan else np.nan

        simulations_df['S2 inicial [mg HC/g rocha]'] = simulations_df.apply(get_s20, axis=1)
        simulations_df['COT inicial [mg HC/g rocha]'] = simulations_df.apply(get_cot0, axis=1)

        if eixo_x == 'cots2_eixox_cots2' and eixo_y == 'cots2_eixoy_profundidade':
            fig = subplots.make_subplots(rows=1, cols=2,
                                        shared_yaxes=True,
                                        horizontal_spacing=0)

            fig.append_trace(go.Scatter(
                x=simulations_df['S2 inicial [mg HC/g rocha]'].dropna().values,
                y=simulations_df[maturation_depth].dropna().values,
                name='S2 inicial [mg HC/g rocha]',
                line={'width': 0.75, 'dash': 'solid'},
            ), row=1, col=1)

            fig.append_trace(go.Scatter(
                x=simulations_df['COT inicial [mg HC/g rocha]'].dropna().values,
                y=simulations_df[maturation_depth].dropna().values,
                name='COT inicial [mg HC/g rocha]',
                line={'width': 0.75, 'dash': 'solid'},
            ), row=1, col=2)

            fig.update_layout(legend=dict(orientation="h",
                                        yanchor="bottom"))
            # layout do gráfico
            fig['layout']['yaxis'].update(
                title='Profundidade [m]',
                autorange='reversed'
            )
        elif eixo_x == 'cots2_eixox_profundidade' and eixo_y == 'cots2_eixoy_cots2':
            fig = subplots.make_subplots(rows=1, cols=2,
                            shared_yaxes=True,
                            horizontal_spacing=0)

            fig.append_trace(go.Scatter(
                y=simulations_df['S2 inicial [mg HC/g rocha]'].dropna().values,
                x=simulations_df[maturation_depth].dropna().values,
                name='S2 inicial [mg HC/g rocha]',
                line={'width': 0.75, 'dash': 'solid'},
            ), row=1, col=1)

            fig.append_trace(go.Scatter(
                y=simulations_df['COT inicial [mg HC/g rocha]'].dropna().values,
                x=simulations_df[maturation_depth].dropna().values,
                name='COT inicial [mg HC/g rocha]',
                line={'width': 0.75, 'dash': 'solid'},
            ), row=1, col=2)

            fig.update_layout(legend=dict(orientation="h",
                                        yanchor="bottom"))
            # layout do gráfico
            fig['layout']['yaxis'].update(
                title='Profundidade [m]',
                autorange='reversed'
            )
        else:
            fig = subplots.make_subplots(rows=1, cols=2,
                            shared_yaxes=True,
                            horizontal_spacing=0)

            fig.append_trace(go.Scatter(
                x=simulations_df['S2 inicial [mg HC/g rocha]'].dropna().values,
                y=simulations_df[maturation_depth].dropna().values,
                name='S2 inicial [mg HC/g rocha]',
                line={'width': 0.75, 'dash': 'solid'},
            ), row=1, col=1)

            fig.append_trace(go.Scatter(
                x=simulations_df['COT inicial [mg HC/g rocha]'].dropna().values,
                y=simulations_df[maturation_depth].dropna().values,
                name='COT inicial [mg HC/g rocha]',
                line={'width': 0.75, 'dash': 'solid'},
            ), row=1, col=2)

            fig.update_layout(legend=dict(orientation="h",
                                        yanchor="bottom"))
            # layout do gráfico
            fig['layout']['yaxis'].update(
                title='Profundidade [m]',
                autorange='reversed'
            )


    # Salvando dataframes resultado:
    simulations_df.to_csv('static/cot0_s20_simulation_' + str(n_clicks) + '.csv', index=False, sep=';')
    simulations_df.to_string("static/cot0_s20_simulation_" + str(n_clicks) + ".txt", index=False)

    z = zipfile.ZipFile('static/cot0_s20_simulation_' + str(n_clicks) + '.zip', 'w', zipfile.ZIP_DEFLATED)
    z.write('static/cot0_s20_simulation_' + str(n_clicks) + '.txt')
    z.write('static/cot0_s20_simulation_' + str(n_clicks) + '.csv')


    return fig

## FÁCIES ORGÂNICAS
def fuzzy_maturarion(input_df, depth_var, age_var=None):
    # input: dataframe containing Depth, Age*, Toc, HI e OI (*reserved for future use)
    # output: same as input but with the classification

    # note there is no test if the input_df as all columns necessary

    # of: organic facies - 7 categories following Jones, R.W., 1987. Organic Facies,
    # in: Brooks, J., Welte, D. (Eds.), Advances in Petroleum Geochemistry. Academic Press, London, pp. 78–80

    #fuzzy

    of_nclass = 7
    of_class = ['A', 'AB', 'B', 'BC', 'C', 'CD', 'D']

    # toc: total organic carbon classes
    toc_nclass = 3
    toc_class = ['low', 'high', 'very high']
    toc_class_bounds = [[0, 1],
                        [1, 3],
                        [3, 20]]

    # hi: hydrogen index classes
    hi_nclass = 7
    hi_class = ['ultra low', 'very low', 'low', 'intermediate', 'high', 'very high', 'ultra high']
    hi_class_bounds = [[0, 50],
                       [50, 125],
                       [125, 250],
                       [250, 400],
                       [400, 650],
                       [650, 850],
                       [850, 1500]]

    # oi: Oxygen index (regime) classes
    oi_nclass = 7
    oi_class = ['ultra low', 'very low', 'low', 'mid low', 'mid high', 'mid wide', 'wide']
    oi_class_bounds = [[10, 30],
                       [20, 50],
                       [30, 80],
                       [40, 80],
                       [50, 150],
                       [40, 150],
                       [20, 200]]

    # Fuzzy model definition (based on min/max values) and resolution defined below
    dtoc = 0.5
    dhi = 1
    doi = 1


    TOC = ctrl.Antecedent(np.arange(np.min(toc_class_bounds), np.max(toc_class_bounds), dtoc), 'toc')
    HI = ctrl.Antecedent(np.arange(np.min(hi_class_bounds), np.max(hi_class_bounds), dhi), 'hi')
    OI = ctrl.Antecedent(np.arange(np.min(oi_class_bounds), np.max(oi_class_bounds), doi), 'oi')
    # Consequents
    Organic_Facies = ctrl.Consequent(np.arange(0, of_nclass + 1, 1), 'of')

    # Model initialization
    for ii, tclass in enumerate(toc_class):
        # print(f'{ii} {tclass}') # for paranoics
        if ii == 0:
            TOC[tclass] = fuzz.trapmf(TOC.universe, [np.min(toc_class_bounds),
                                                     toc_class_bounds[ii][0],
                                                     toc_class_bounds[ii][1],
                                                     toc_class_bounds[ii + 1][0]])
        elif ii == len(toc_class) - 1:
            TOC[tclass] = fuzz.trapmf(TOC.universe, [toc_class_bounds[ii - 1][1],
                                                     toc_class_bounds[ii][0],
                                                     toc_class_bounds[ii][1],
                                                     np.max(toc_class_bounds)])
        else:
            TOC[tclass] = fuzz.trapmf(TOC.universe, [toc_class_bounds[ii - 1][1],
                                                     toc_class_bounds[ii][0],
                                                     toc_class_bounds[ii][1],
                                                     toc_class_bounds[ii + 1][0]])
    # TOC.view() # for paranoics
    for ii, hiclass in enumerate(hi_class):
        # print(f'{ii} {hiclass}') for paranoics
        if ii == 0:
            HI[hiclass] = fuzz.trapmf(HI.universe, [np.min(hi_class_bounds),
                                                    hi_class_bounds[ii][0],
                                                    hi_class_bounds[ii][1],
                                                    np.mean(hi_class_bounds[ii + 1][:])])
        elif ii == len(hi_class) - 1:
            HI[hiclass] = fuzz.trapmf(HI.universe, [np.mean(hi_class_bounds[ii - 1][:]),
                                                    hi_class_bounds[ii][0],
                                                    hi_class_bounds[ii][1],
                                                    np.max(hi_class_bounds)])
        else:
            HI[hiclass] = fuzz.trapmf(HI.universe, [np.mean(hi_class_bounds[ii - 1][:]),
                                                    hi_class_bounds[ii][0],
                                                    hi_class_bounds[ii][1],
                                                    np.mean(hi_class_bounds[ii + 1][:])])
    # HI.view() # for paranoics
    # *** NOTE for OI a gaussian membership function is used
    for ii, oiclass in enumerate(oi_class):
        # print(f'{ii} {oiclass}') # for paranoics
        OI[oiclass] = fuzz.gaussmf(OI.universe, np.mean(oi_class_bounds[ii][:]),
                                   np.std(oi_class_bounds[ii][:]))
    # OI.view() # for paranoics

    # output membership function (CRISP triangular)
    for ii, ofclass in enumerate(of_class):
        # print(f'{ii} {ofclass}') # for paranoics
        Organic_Facies[ofclass] = fuzz.trimf(Organic_Facies.universe, [ii - 1, ii, ii + 1])

        # Organic_Facies.view() # for paranoics

    # FUZZY rules

    rule1 = ctrl.Rule(TOC['very high'] & HI['ultra high'] & OI['ultra low'], Organic_Facies['A'])
    rule2 = ctrl.Rule(TOC['very high'] & HI['very high'] & OI['very low'], Organic_Facies['AB'])
    rule3 = ctrl.Rule(TOC['very high'] & HI['high'] & OI['low'], Organic_Facies['B'])
    rule4 = ctrl.Rule(TOC['high'] & HI['intermediate'] & OI['mid low'], Organic_Facies['BC'])
    rule5 = ctrl.Rule(TOC['high'] & HI['low'] & OI['mid high'], Organic_Facies['C'])
    rule6 = ctrl.Rule(TOC['low'] & HI['very low'] & OI['mid wide'], Organic_Facies['CD'])
    rule7 = ctrl.Rule(TOC['low'] & HI['ultra low'] & OI['wide'], Organic_Facies['D'])

    maturation_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])

    # fuzzy driver starts here
    maturation_apply = ctrl.ControlSystemSimulation(maturation_ctrl)

    # main loop for whole input
    of_computed = []
    of_computed_class = []
    
    toc = 'COT [%]'
    hi = 'IH [mg HC/g COT]'
    oi = 'IO  [mg CO₂/g COT]'
    
    # *** deal withy out of bounds for any input
    for index, row in input_df.iterrows():
        # print(f'Depth:{row[depth_var]} inputs:[{row[toc]:.2f}:{row[hi]:4.0f}:{row[oi]:4.0f}]')
        if row[toc] < np.min(toc_class_bounds) or row[toc] > np.max(toc_class_bounds):
            print(f'***warning: toc out of bounds Depth:{row[depth_var]} inputs:[{row[toc]:.2f}:{row[hi]:4.0f}:{row[oi]:4.0f}]')
        if row[hi] < np.min(hi_class_bounds) or row[hi] > np.max(hi_class_bounds):
            print(f'***warning: hi out of bounds Depth:{row[depth_var]} inputs:[{row[toc]:.2f}:{row[hi]:4.0f}:{row[oi]:4.0f}]')
        if row[oi] < np.min(oi_class_bounds) or row[oi] > np.max(oi_class_bounds):
            print(f'***warning: oi out of bounds Depth:{row[depth_var]} inputs:[{row[toc]:.2f}:{row[hi]:4.0f}:{row[oi]:4.0f}]')
        maturation_apply.inputs({'toc': np.float(row[toc]), 'hi': np.float(row[hi]), 'oi': np.float(row[oi])})
        try:
            maturation_apply.compute()
            of_computed.append(maturation_apply.output["of"])
            ii_class = np.int(np.floor(maturation_apply.output["of"]))
            of_computed_class.append(of_class[ii_class])
        except:
            print(
                f' Error defuzzing: Total area is zero! Depth:{row[depth_var]} inputs:[{row[toc]:.2f}:{row[hi]:4.0f}:{row[oi]:4.0f}]')
            of_computed.append(-99)
            of_computed_class.append('??')

    # creating output_df
    output_df = input_df
    output_df['of'] = of_computed
    output_df['of_class'] = of_computed_class

    return output_df