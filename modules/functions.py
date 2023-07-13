import numpy as np

#-------------Content---------------#
# Total Organic Content calculations#
#-----------------------------------#

class COT:
    pass
def dlogr(res,x,m):
    '''Função que determina o Delta log R dos pares ordenados de propriedades
    Resistividade e Sônico ou Resistividade ou Densidade. 
    Entradas:
    res, dados de resistividade
    x, canal de densidade ou sônico
    m, coeficiente de cimentação
    Saída:
    DlogR, Delta Log R'''
    
    import math
    dado  = len(res)
    DlogR = np.zeros(dado)
    res   = np.array(res)
    x     = np.array(x)
    resb  = np.min(res)
    xb    = np.median(x)
    
    #Recurso computacional para eliminar os zeros:
    dummy = 1e-100000
    
    for i in range(dado):
        DlogR[i]=math.log10(res[i]/(resb+dummy))+((1/np.log(10))*(m/(x[i]-xb))*(x[i]-xb))
        if x[i]/xb < 0:
            print(x[i]-xb)
        if res[i]/resb < 0:
            print("Cuidado! Log negativo!",res[i]-resb)
     
        
    return DlogR


def dlogr90(res,resb,x,xb):
    
    
    if np.size(res) > 1:
        dado  = len(res)
        DlogR = np.zeros(dado)
        res   = np.array(res)
        x     = np.array(x)
        resb  = np.min(res)
        xb    = np.median(x)
        for i in range(dado):
            DlogR[i]=math.log10(res[i]/(resb))+(0.02*(x[i]-xb))
            if x[i]/xb < 0:
                print(x[i]-xb)
                if res[i]/resb < 0:
                    print("Cuidado! Log negativo!",res[i]-resb)
    else:
        res = float(res)
        resb = float(resb)
        x = float(x)
        xb = float(xb)
        DlogR=math.log10(res/(resb))+(0.02*(x-xb))
        
    return DlogR

def passey16(drlog,alfa,beta,delta,eta,Tmax,gr):
    '''Função que determina COT via delta log R
        Entradas:
    drlog,parâmetro calculado
    alfa, parâmetro estimado
    beta, parâmetro estimado
    delta, parâmetro estimado
    eta, parâmetro estimado
    Tmax, indicador de maturidade em oC
    gr, canal raio gama
    Saída:
    COT, Conteúdo orgânico total
    '''
    dado = len(gr)
    COT  = np.zeros(dado)
    gr   = np.array(gr)
    grb  = np.median(gr) 
    
    for i in range(dado):
        COT[i] = (alfa*drlog[i] + beta*(gr[i]-grb))*10**(delta-eta*Tmax)
        #print(COT[i],delta-eta*Tmax)
            
    return COT

def empirico(pp,pf,zm,sr):
    '''
    Ressurgencia project (2023) empirical equation based on lake parameters that consider a preservation factor. Preservation factor takes into account geochemistry parameters such as O2, pH, carbon preservation factor in lake sediments. The sedimentation rate is a conditional that changes sedimentation's rate of position.   
    Input:
      -pp, primary productivity
      -sr, sedimentation rate
      -pf, preservation factor
      -zm, depth in meters

    Output:
      -COT: discrete total organic content
    '''
    if 1 <= sr <= 0:
        COT = (pp*pf*zm)/sr
    else:
        COT = pp*pf*zm*sr

    return COT
 

def igor(pp,pf,dbd,sr):
    '''
    Igor(2023) prediction TOC formulae.
    Inputs:
      -pp, primary productivity
      -sr, sedimentation rate
      -pf, preservation factor
      -dbd, dry bulk density
   Output:
      -COT: discrete total organic content
      '''
    COT = (pp * pf)/(dbd * sr)

    return COT

def muller(rho_sed):
    '''
    Müller (2005) definition of the empirical prediction of total organic content (TOC) by sediment density.
    
    Input:
     -rho_sed: grain sediment density array
    
    Output:
     - COT: or TOC total organic content array
    '''
    
    COT = (rho_sed - 2.65/0.0523)

    return COT

def dean(rho_sed):
    '''
    Dean and Gorham (1998) definition of the empirical prediction of total organic content (TOC) by sediment density.
    
    Input:
     -rho_sed: grain sediment density array
    
    Output:
     - COT: or TOC total organic content array
    '''

    COT = (rho_sed/1.665)**(1/-0.887)

    return COT

def stein(rho_sed,sr):
    '''
    Stein(1986) definition of the empirical prediction of total organic content (TOC) by sediment density.
    
    Input:
     -rho_sed: grain sediment density array
     -sr: sedimentation rate
     -pp: primary production
    Output:
     - COT: or TOC total organic content array
    '''
   

    COT = pp/(5*sr*rho_sed)

    return COT
#-------------Content--------------#
# Burial Efficiency calculations   #
#----------------------------------#


def alin(pp):
    '''
    Alin et al.(2007)  burial efficiency as a function of primary productivity.
    Input
     - pp: primary productivy array
    Output:
     - be: burial effiency array
    '''

    be = 204 * pp**(0.800)

    return be

def alin2(zm):
   '''
    Alin et al.(2007)  burial efficiency as a function of depth.
    Input
     - zm: depth array
    Output:
     - be: burial effiency array
    '''

   be = 0.0055 * zm + 0.621

   return be

def sobek(sr):
    '''
    Sobek et al.(2009) burial efficiency as a function of sedimentation rate for marine and non-marine environment.
    Input:
    - sr: sedimentation rate array
    Output:
    - be: burial efficiency array
    '''
    
    C = input('Is it a marine environment? (yes or no): ')
    
    if C == no:
        be = 31.1 + 27.9 * np.log(sr)
    if C == yes:
        be = ((sr * 1000)**(0.4))/2.1

    return be

def sobek2(oet,matterial):
    '''
    Sobek et al.(2009) defines burial efficiency as a function of oxygen time exposition and the distance of the source area. The source matterial can be allochthonous or autochthonous.
    Input:
     -oet: oxygen exposure time (years) array
     -matterial: list containing origin of organic matter. Can be autochthonous or allochthonous.
     Output:
     -be: burial efficiency array
    '''


    if matterial == []:
        print("WARNING! The list containing the organic matter origin is empty.")
    if matterial == allochthonous or aloctone:
        be = 61.2 - 16.7 * np.log(oet)
    if matterial == autochthonous or autoctone:
        be = 23.3 - 4.39 * np.log(oet)
    else:
        print("WARNING! You mispel the organic origin character.")
    
    return be

 
def alin3(cot,pp):
    '''
    Alin et al(2007) definition of burial efficiency by total organic content and primary productivity.
    Input:
     -cot: Total organic content array
     -pp: primary productivity array
    Output:
     -be: burial efficiency
    '''

    return be
#----------------------#
# Primary Productivity #
#----------------------#

def alin4(zm):
    '''
    Alin et al(2007) primary productivity calculations.
    Input:
     -zm: Depth array in meters
    Output:
     -pp: primary productivity
    '''

    pp = (2597 * zm)**-0.337

    return pp

def alin5(e):
    """
    Alin et al(2007) primary productivity calculation based on insolation parameter.
    Input:
     -e: insolation rate array in kWh m^-2 y^-1
    Output:
     -pp: primary productivity array
    """

    pp = 0.322 * e**(0.0015)

    return pp

#------------------------#
# Mass Accumulation Rate #
#------------------------#

def alin6(oc,phi,lsr,rho):
    """
    Alin et al(2007) mass accumulation rate caluculation based in oc parameter.
    Inputs:
     - oc: oc index array in %
     - phi: porosity array
     - lsr: linear sedimentation rate array
     - rho: sediment density array.
    Output:
     - mar: mass accumulation rate
    """

    marsed = (1-phi)*lsr*rho

    mar = marsed * (oc/100)

    return mar


#-------------#
# Carbon Flux #
#-------------#


def pace(pp,zm):
    '''
    Pace et al(1987) carbon flux calculation model for marine environments.
    Input:
     -pp: primary productivity
     -zm: depth array in meters
    Output:
     - cf: carbon flux array
    '''
   
    cf = 3.523 * zm**(-0.734) * pp

    return cf
    
#--------------------------------------------#
# Shale Volume, Sand Fraction, Dry Density   #
#--------------------------------------------#      


class calculadoras:
    pass
    
def igr(GR):
    GRmin=min(GR)
    GRmax=max(GR)
    IGR = np.zeros(np.size(GR))
    IGR = (GR-GRmin)/(GRmax-GRmin)
    return IGR

def clavier(IGR):
    VSH = np.zeros(np.size(IGR))
    VSH = 1.7 - np.sqrt(3.38-(IGR+0.7)**2.0)
    return VSH

def SandFraction(VSH):
    SF= (1-VSH) * 100
    return SF

def DensidadeAparenteSeca(RHOB,NPHI):
    NPHI= NPHI / 100 # Fator de conversão
    DAS=RHOB-NPHI
    return DAS 
    
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
