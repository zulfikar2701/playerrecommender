import streamlit as st
import pandas as pd
import pickle
from pathlib import Path
import time

st.set_page_config(
    page_title="Player Recommender",
    page_icon=":soccer:"
)


@st.cache(show_spinner=False)
def getData():
    player_df = pd.read_pickle(r'Pickle Data/data_out_df.pickle')
    with open(r'Pickle Data/data_outfield_player_ID.pickle', 'rb') as file:
        player_ID = pickle.load(file)
    with open(r'Pickle Data/data_out_engine.pickle', 'rb') as file:
        engine = pickle.load(file)

    gk_df = pd.read_pickle(
        r'Pickle Data/data_gk_df.pickle')
    with open(r'Pickle Data/data_gk_player_ID.pickle', 'rb') as file:
        gk_ID = pickle.load(file)
    with open(r'Pickle Data/data_gk_engine.pickle', 'rb') as file:
        gk_engine = pickle.load(file)

    return [player_df, player_ID, engine], [gk_df, gk_ID, gk_engine]


outfield_data, gk_data = getData()

header = st.container()
data_info1 = st.container()
params = st.container()
result = st.container()

with header:
    st.title('Sistem Rekomendasi Pemain')

with data_info1:
    st.markdown('Berdasarkan data musim 2022/2023 untuk pemain di **Top 5** Liga Eropa (Premier League, La Liga, Ligue 1, Serie A, Bundesliga) :soccer:')
    @st.cache
    def read_info(path):
        return Path(path).read_text(encoding='utf8')
    
    


with params:
    st.text(' \n')
    st.text(' \n')
    st.header('Filter Pemain:')

    col1, col2 = st.columns([1, 2.2])
    with col1:
        radio = st.radio('Tipe pemain', ['Outfielder', 'Goalkeeper'])
    with col2:
        if radio == 'Outfielder':
            df, player_ID, engine = outfield_data
        else:
            df, player_ID, engine = gk_data
        players = sorted(list(player_ID.keys()))
        age_default = (15, 41)
        query = st.selectbox('Nama pemain', players,
            help='Ketik tanpa menghapus kata, untuk mencari pemain dari klub tertentu, ketikkan nama klub tersebut')

    col4, col5, col6, col7 = st.columns([0.7, 1, 1, 1])
    with col4:
        if radio == 'Outfield players':
            res, val, step = (5, 20), 10, 5
        else:
            res, val, step = (3, 10), 5, 1
        count = st.slider('Jumlah hasil', min_value=res[0], max_value=res[1], value=val, step=step)
    with col5:
        comp = st.selectbox('Liga', ['All', 'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1'],
            help='Filter liga pemain tersebut berada')
    with col6:
        comparison = st.selectbox('Bandingkan dengan', ['Semua posisi', 'Posisi yang sama'],
            help='Semua posisi akan menampilkan perbandingan dengan pemain dari berbagai posisi, Posisi yang sama hanya akan menampilkan pemain dengan posisi yang sama dengan pemain input')
    with col7:
        age = st.slider('Umur', min_value=age_default[0], max_value=age_default[1], value=age_default,
        help='Umur pemain yang akan menjadi perbandingan')

with result:
    st.text(' \n')
    st.text(' \n')
    st.text(' \n')
    st.markdown('_Menampilkan rekomendasi untuk pemain yang mirip dengan_ **{}**'.format(query))
    
    
    def getRecommendations(metric, df_type, league='All', comparison='Semua posisi', age=age_default, count=val):
        start_time = time.time()
        if df_type == 'outfield':
            df_res = df.iloc[:, [13, 15, 14, 16, 17]].copy()
        else:
            df_res = df.iloc[:, [4, 6, 5, 7,8]].copy()
        df_res['Player'] = list(player_ID.keys())
        df_res.insert(1, 'Similarity', metric)
        df_res = df_res.sort_values(by=['Similarity'], ascending=False)
        metric = [str(num) + '%' for num in df_res['Similarity']]
        df_res['Similarity'] = metric
        df_res = df_res.iloc[13:, :]
            
        if comparison == 'Posisi yang sama' and df_type == 'outfield':
            q_pos = list(df[df['Player'] == query.split(' (')[0]].Pos)[0]
            df_res = df_res[df_res['Pos'] == q_pos]
            
        if league == 'All':
            pass
        else:
            df_res = df_res[df_res['Comp'] == league]
            
        if age == age_default:
            pass
        else:
            df_res = df_res[(df_res['Age'] >= age[0]) & (df_res['Age'] <= age[1])]


        df_res = df_res.iloc[:count, :].reset_index(drop=True)
        df_res.index = df_res.index + 1
        if len(df) == 2040:
            mp90 = [str(round(num, 1)) for num in df_res['90s']]
            df_res['90s'] = mp90
        df_res.rename(columns={'Pos': 'Position', 'Comp': 'League'}, inplace=True)
        end_time = time.time()
        running_time = end_time - start_time
        st.write(f"Recommendation Function Running Time: {running_time:.2f} seconds")
        return df_res
    

    sims = engine[query]
    df_type = 'outfield' if len(df) == 2033 else 'gk'
    recoms = getRecommendations(sims, df_type=df_type, league=comp, comparison=comparison, age=age, count=count)
    st.table(recoms)
