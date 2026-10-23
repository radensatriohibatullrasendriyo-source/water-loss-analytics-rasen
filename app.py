"""Water Loss Analytics — dashboard portofolio berbasis hasil notebook 02–05."""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from water_loss_utils import load_analysis, filter_data, aggregate_years, balanced_panel, kpis

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data/processed/water_loss_analysis.csv'
SOURCE = 'https://data.ca.gov/@california-department-of-water-resources/ca-urban-retail-water-system-water-loss-annual-loss-audit-data'
AUTHOR = 'Raden Satrio Hibatull Rasendriyo'
COLOR = '#167C80'

st.set_page_config(page_title='Water Loss Analytics', layout='wide')
st.markdown('''<style>
.block-container {padding-top:2rem; padding-bottom:2.5rem; max-width:1440px;}
[data-testid="stMetric"] {border:1px solid #CBDDDC; border-radius:12px; padding:16px;}
h1,h2,h3 {letter-spacing:-.025em;}
</style>''', unsafe_allow_html=True)
st.sidebar.title('Water Loss Analytics')
st.sidebar.caption('California · Audit kehilangan air')
page = st.sidebar.radio('Halaman', ['Ringkasan','Tren antarperiode','Profil sistem','Evaluasi ML','Metode dan kualitas'], key='page')
st.sidebar.divider()
st.sidebar.caption(AUTHOR)
st.sidebar.markdown('[LinkedIn](https://www.linkedin.com/in/raden-satrio) · [Email](mailto:radensatriohibatullrasendriyo@gmail.com)')
st.sidebar.caption('Data Analyst with SQL & Python in Google Platform · Batch 25')

@st.cache_data
def get_data(path, modified_time):
    return load_analysis(Path(path))

if not DATA.is_file():
    st.title('Data analisis belum tersedia')
    st.info('Letakkan app.py di folder water_loss_analytics, sejajar dengan folder data dan notebooks. Jalankan notebook 02 untuk membuat data/processed/water_loss_analysis.csv.')
    st.stop()
try:
    df = get_data(str(DATA), DATA.stat().st_mtime_ns)
except (ValueError, OSError, KeyError) as exc:
    st.error(f'Data belum dapat dibaca: {exc}')
    st.stop()
years = sorted(df.analysis_year.unique().tolist())
statuses = sorted(df.audit_status.dropna().unique().tolist())

LABELS = {'supplier_name':'Penyedia air', 'system_key':'ID organisasi | sistem',
          'analysis_year':'Tahun', 'audit_status':'Status laporan',
          'real_losses_af':'Kehilangan fisik (AF)', 'non_revenue_water_af':'NRW (AF)',
          'water_supplied_af':'Pasokan (AF)', 'service_connections':'Sambungan',
          'validity_score':'Skor validitas', 'nrw_pct':'NRW (%)',
          'real_loss_pct':'Kehilangan fisik / pasokan (%)',
          'real_loss_af_per_connection_year':'Kehilangan fisik (AF/sambungan/tahun)'}

def chart(fig):
    fig.update_layout(template='plotly_white', font=dict(family='Arial',size=13),
                      margin=dict(l=10,r=10,t=40,b=15), legend_title_text='')
    st.plotly_chart(fig, width='stretch')

def show_table(data, columns):
    st.dataframe(data[columns].rename(columns=LABELS), hide_index=True, width='stretch')

def download(data, name):
    st.download_button('Unduh tabel sesuai pilihan', data.to_csv(index=False).encode('utf-8-sig'),
                       file_name=name, mime='text/csv')

def scope():
    st.caption('Sampel proyek: laporan tahun kalender 2016–2024 yang lolos aturan notebook 02. AF = acre-feet. Hasil tidak mewakili total seluruh California.')

def selection(prefix):
    c1,c2=st.columns([2,1])
    with c1:
        selected=st.multiselect('Status laporan', statuses, default=statuses, key=prefix+'_status')
    with c2:
        score=st.slider('Skor validitas minimum',0,100,0, key=prefix+'_score',
                        help='Filter eksploratif pengguna, bukan ambang resmi kelayakan audit.')
    return selected,score

if page == 'Ringkasan':
    st.title('Memahami kehilangan air dalam distribusi')
    st.write('Lihat besarnya kehilangan air, cakupan pelaporan, dan konteks kualitas audit pada satu tahun.')
    scope()
    year=st.selectbox('Tahun laporan',years,index=len(years)-1,key='overview_year')
    selected,score=selection('overview')
    current=filter_data(df,(year,year),selected,score)
    if current.empty:
        st.info('Tidak ada laporan untuk kombinasi filter ini. Coba pilih status lain atau turunkan skor minimum.')
    else:
        values=kpis(current)
        a,b,c,d=st.columns(4)
        a.metric('Sistem dalam sampel',f"{values['systems']:,}")
        b.metric('NRW agregat',f"{values['nrw_pct']:.2f}%")
        c.metric('Kehilangan fisik',f"{values['real_losses_af']:,.0f} AF")
        d.metric('Porsi 10 volume terbesar',f"{values['top10_pct']:.2f}%" if values['top10_pct'] is not None else 'Tidak tersedia')
        st.caption(f'{len(current):,} laporan tahun {year}. NRW agregat = jumlah NRW / jumlah pasokan. Porsi 10 terbesar dihitung dari kehilangan fisik pada sampel yang sedang dipilih; bila kurang dari 10 sistem, seluruh sistem digunakan.')
        st.subheader('Laporan dengan volume kehilangan fisik terbesar')
        st.write('Volume besar dapat dipengaruhi ukuran sistem. Daftar ini membantu peninjauan awal dan belum menunjukkan sistem mana yang paling tidak efisien.')
        top=current.sort_values(['real_losses_af','system_key'],ascending=[False,True]).head(10).copy()
        top['label']=top['supplier_name']+' ['+top['system_key']+']'
        chart(px.bar(top.sort_values('real_losses_af'), x='real_losses_af',y='label',orientation='h',
                     color_discrete_sequence=[COLOR], labels={'real_losses_af':'Kehilangan fisik (AF)','label':''},
                     hover_data=['validity_score','real_loss_pct'],height=490))
        show_table(top,['supplier_name','system_key','real_losses_af','real_loss_pct','service_connections','validity_score','audit_status'])
        st.subheader('Kualitas laporan dan besarnya NRW')
        chart(px.scatter(current,x='validity_score',y='nrw_pct',color='audit_status',
                         hover_name='supplier_name',hover_data=['system_key'],labels=LABELS,
                         color_discrete_sequence=[COLOR,'#D08B45']))
        st.caption('Hubungan pada grafik bersifat deskriptif. Skor validitas tinggi tidak menjamin semua angka benar; pola sebaran tidak membuktikan sebab-akibat.')
        download(current,'water_loss_selected_year.csv')

elif page == 'Tren antarperiode':
    st.title('Membandingkan periode dengan cakupan yang jelas')
    scope()
    interval=st.select_slider('Rentang tahun',options=years,value=(years[0],years[-1]),key='trend_years')
    selected,score=selection('trend')
    filtered=filter_data(df,interval,selected,score)
    st.caption('Filter pada halaman ini berlaku sebelum pembentukan panel. Panel hanya mencakup ID gabungan sistem yang memiliki laporan pada setiap tahun dalam rentang pilihan.')
    if filtered.empty:
        st.info('Tidak ada laporan untuk kombinasi filter ini.')
    else:
        annual=aggregate_years(filtered)
        panel=balanced_panel(filtered,*interval)
        chart_data=annual[['analysis_year','nrw_pct']].assign(kelompok='Semua laporan terpilih')
        a,b=st.columns(2)
        a.metric('Laporan terpilih',f'{len(filtered):,}')
        b.metric('Sistem dalam panel lengkap',f'{panel.system_key.nunique():,}')
        if panel.empty:
            st.info('Tidak ada sistem yang memenuhi filter pada setiap tahun. Tren panel tidak ditampilkan. Ini dapat terjadi jika memilih Requirements Addressed pada rentang yang mencakup 2022–2024.')
        else:
            p=aggregate_years(panel)
            chart_data=pd.concat([chart_data,p[['analysis_year','nrw_pct']].assign(kelompok='Panel sistem yang sama')],ignore_index=True)
            if interval[0] != interval[1]:
                delta=p.iloc[-1].nrw_pct-p.iloc[0].nrw_pct
                st.write(f"NRW agregat panel berubah dari {p.iloc[0].nrw_pct:.2f}% menjadi {p.iloc[-1].nrw_pct:.2f}% ({delta:+.2f} poin persentase).")
        # Sertakan tahun kosong sebagai NaN agar garis tidak menyambungkan celah data.
        axis_years=list(range(interval[0],interval[1]+1))
        expanded=[]
        for name,g in chart_data.groupby('kelompok'):
            expanded.append(g.set_index('analysis_year').reindex(axis_years).assign(kelompok=name).rename_axis('analysis_year').reset_index())
        plot=pd.concat(expanded,ignore_index=True)
        fig=px.line(plot,x='analysis_year',y='nrw_pct',color='kelompok',markers=True,
                    labels={'analysis_year':'Tahun','nrw_pct':'NRW agregat (%)'},
                    color_discrete_sequence=[COLOR,'#D08B45'])
        fig.update_traces(connectgaps=False)
        chart(fig)
        st.caption('Panel membantu mengurangi perubahan komposisi pelapor, tetapi wilayah layanan, metode ukur, atau pengelola sistem dapat berubah. ID yang berubah antarperiode belum digabungkan secara manual. Tidak ada estimasi untuk tahun tanpa laporan.')
        st.subheader('Cakupan laporan per tahun')
        coverage=filtered.groupby(['analysis_year','audit_status']).size().rename('laporan').reset_index()
        chart(px.bar(coverage,x='analysis_year',y='laporan',color='audit_status',
                     labels={'analysis_year':'Tahun','laporan':'Jumlah laporan','audit_status':'Status'},
                     color_discrete_sequence=[COLOR,'#D08B45']))
        st.dataframe(annual,hide_index=True,width='stretch')
        download(plot,'water_loss_nrw_trend.csv')

elif page == 'Profil sistem':
    st.title('Riwayat satu sistem')
    scope()
    st.caption('Halaman ini menampilkan seluruh laporan sistem yang tersedia dalam tabel analisis utama; filter halaman lain tidak berlaku di sini.')
    identities=df.sort_values('analysis_year').drop_duplicates('system_key',keep='last')
    labels=dict(zip(identities.system_key, identities.supplier_name+' ['+identities.system_key+']'))
    keys=sorted(labels,key=lambda k:labels[k])
    chosen=st.selectbox('Cari nama penyedia atau ID sistem',keys,format_func=lambda k:labels[k],key='profile_system')
    history=df.loc[df.system_key.eq(chosen)].sort_values('analysis_year')
    st.subheader(labels[chosen])
    st.write(f'Tersedia {len(history)} laporan dalam cakupan analisis. Tahun tanpa laporan tidak dianggap bernilai nol.')
    hist_plot=history.set_index('analysis_year').reindex(range(years[0],years[-1]+1)).rename_axis('analysis_year').reset_index()
    fig=px.line(hist_plot,x='analysis_year',y=['nrw_pct','real_loss_pct'],markers=True,
                labels={'analysis_year':'Tahun','value':'Persentase pasokan (%)','variable':'Metrik'},
                color_discrete_sequence=[COLOR,'#D08B45'])
    fig.update_traces(connectgaps=False)
    chart(fig)
    show_table(history,['analysis_year','supplier_name','water_supplied_af','real_losses_af','non_revenue_water_af',
                        'nrw_pct','service_connections','validity_score','audit_status'])
    st.caption('NRW mencakup kehilangan fisik, kehilangan semu, dan konsumsi resmi yang tidak ditagihkan. NRW bukan sinonim kebocoran fisik.')
    download(history,'water_loss_system_history.csv')

elif page == 'Evaluasi ML':
    st.title('Evaluasi prediksi kehilangan fisik')
    st.write('Menggunakan informasi audit tahun t untuk memperkirakan volume kehilangan fisik tahun t+1. Baseline persistence memakai nilai kehilangan fisik tahun sebelumnya.')
    st.caption('Evaluasi retrospektif dari notebook 05. Tanggal ketersediaan laporan dan revisi historis belum diverifikasi, sehingga hasil ini belum membuktikan kesiapan prediksi operasional.')
    from ml_results import load_results
    try:
        result = load_results(ROOT / 'outputs/modeling')
    except (OSError, ValueError, KeyError) as exc:
        st.info(f'Hasil ML belum tersedia atau tidak konsisten: {exc}')
        st.write('Jalankan seluruh notebook 05 dari proyek yang sama. Pertahankan folder outputs/modeling beserta file CSV dan JSON hasil ekspornya.')
        st.stop()
    summary, metrics, predictions, validation = result
    name = summary['selection']['selected_ml']
    baseline = metrics.set_index('model').loc['persistence']
    model = metrics.set_index('model').loc[name]
    change = 100 * (model.mae_af / baseline.mae_af - 1) if baseline.mae_af else None
    a,b,c = st.columns(3)
    a.metric('Observasi uji', f'{len(predictions):,}')
    b.metric('MAE baseline', f'{baseline.mae_af:,.2f} AF')
    c.metric('MAE model ML', f'{model.mae_af:,.2f} AF')
    st.caption(f"Tahun target uji: {summary['test_year']}. Metrik utama memakai seluruh data uji dan tidak berubah saat memilih grafik. MAE dan RMSE lebih kecil berarti lebih baik.")
    if change is not None and change > 0:
        st.warning(f'MAE model ML lebih besar {change:.2f}% dibanding baseline pada data uji. Model terpilih belum mengungguli baseline pada periode ini.')
    elif change is not None:
        st.info(f'Perubahan MAE model ML terhadap baseline: {change:+.2f}%. Hasil ini hanya berlaku untuk sampel uji tersebut.')
    st.subheader('Perbandingan pada data uji')
    plot = metrics.melt(id_vars='model', value_vars=['mae_af','rmse_af'], var_name='Metrik', value_name='Error (AF)')
    chart(px.bar(plot, x='Metrik', y='Error (AF)', color='model', barmode='group', color_discrete_sequence=[COLOR,'#D08B45']))
    st.dataframe(metrics, hide_index=True, width='stretch')
    st.caption('Prediksi negatif dibatasi ke nol sesuai aturan yang ditetapkan sebelum evaluasi. Jumlahnya tercatat pada negative_predictions_clipped. Target berupa volume absolut, sehingga kesalahan sistem besar dapat mendominasi MAE dan RMSE.')
    st.subheader('Aktual dan prediksi per sistem')
    chosen = st.selectbox('Prediksi yang ditampilkan', ['Model ML','Baseline'], key='ml_prediction')
    column = 'prediction_ml_af' if chosen == 'Model ML' else 'prediction_baseline_af'
    fig = px.scatter(predictions, x='actual_real_losses_af', y=column, hover_name='supplier_name', hover_data=['system_key'], labels={'actual_real_losses_af':'Aktual (AF)',column:'Prediksi (AF)'}, color_discrete_sequence=[COLOR])
    limit = float(max(predictions.actual_real_losses_af.max(), predictions[column].max()))
    fig.add_shape(type='line',x0=0,y0=0,x1=limit,y1=limit,line=dict(color='#9CA3AF',dash='dash'))
    chart(fig)
    st.caption('Garis putus-putus menunjukkan prediksi sama dengan aktual. Titik di atas garis berarti prediksi terlalu tinggi.')
    st.subheader('Kesalahan menurut ukuran sistem')
    grouped = predictions.groupby('supply_size_group', observed=True).agg(observasi=('system_key','size'), baseline_mae_af=('abs_error_baseline_af','mean'), ml_mae_af=('abs_error_ml_af','mean')).reset_index()
    st.dataframe(grouped, hide_index=True, width='stretch')
    st.caption('Kelompok ukuran mengikuti batas kuartil pasokan dari data pengembangan (train + validation), bukan dari data uji. Jumlah observasi perlu diperhatikan saat membandingkan kelompok.')
    st.subheader('Sepuluh kesalahan absolut ML terbesar')
    cols = ['supplier_name','system_key','actual_real_losses_af','prediction_baseline_af','prediction_ml_af','abs_error_baseline_af','abs_error_ml_af']
    st.dataframe(predictions.nlargest(10,'abs_error_ml_af')[cols], hide_index=True, width='stretch')
    download(predictions, 'water_loss_test_predictions.csv')
    with st.expander('Pemilihan model dan pemisahan waktu'):
        st.write('Train: tahun target 2017–2021. Validation: 2022–2023. Test: 2024. Enam kandidat ML dibandingkan pada validation; kandidat terpilih dilatih ulang memakai train + validation sebelum diuji satu kali pada test.')
        st.write(f'Model ML terpilih: {name}. Pemilihan memakai MAE validation, dengan RMSE sebagai pemecah seri. Baseline tetap menjadi pembanding terpisah.')
        st.dataframe(validation.sort_values(['mae_af','rmse_af','model']), hide_index=True, width='stretch')
        st.write('Hasil test tidak digunakan untuk memilih parameter atau mengganti model. Dashboard membaca ekspor evaluasi dan tidak melatih model atau menghasilkan prediksi masa depan secara langsung.')

else:
    st.title('Metode, cakupan, dan kualitas data')
    st.write('Proyek ini menggunakan audit kehilangan air California Department of Water Resources. Pengolahan dilakukan melalui notebook Python, analisis SQL lokal, dan visualisasi Streamlit.')
    st.markdown(f'[Buka katalog sumber resmi]({SOURCE})')
    st.subheader('Aturan tabel analisis utama')
    st.markdown('''- Tahun kalender 2016–2024, dengan identitas organisasi dan sistem lengkap serta unik per periode.
- Status Requirements Addressed atau Preliminarily Approved; keduanya tetap dibedakan.
- Volume memakai acre-feet dari kolom sumber berakhiran _AF.
- Angka utama harus terbaca, tidak negatif setelah toleransi numerik, serta memiliki pasokan dan sambungan positif.
- Tiga nilai negatif sangat kecil disesuaikan ke nol pada snapshot proyek, dengan toleransi 1e-9 AF dan log penyesuaian.
- Format ID yang berbeda dan jumlah sambungan pecahan ditandai untuk peninjauan, tanpa penggabungan ID atau pembulatan otomatis.''')
    st.subheader('Jejak cleaning')
    meta_path=ROOT/'outputs/tables/02_cleaning_metadata.json'
    filter_path=ROOT/'outputs/tables/02_filter_summary.csv'
    if filter_path.is_file():
        st.dataframe(pd.read_csv(filter_path),hide_index=True,width='stretch')
    else:
        st.info('Jalankan notebook 02 untuk menampilkan tabel jejak cleaning dari outputs/tables.')
    if meta_path.is_file():
        with st.expander('Parameter dan identitas snapshot sumber'):
            st.json(json.loads(meta_path.read_text(encoding='utf-8')))
    st.subheader('Batas interpretasi')
    st.write('Hasil berlaku untuk sampel terpilih, bukan total California. Skor audit merupakan indikator kualitas data yang dilaporkan, bukan sertifikasi ketepatan setiap nilai. Status sangat terkait dengan tahun: dalam sampel proyek, Requirements Addressed tidak tersedia pada 2022–2024.')
    st.write('Volume besar belum membuktikan inefisiensi. Dashboard ini membantu peninjauan laporan; tidak mengestimasi penghematan, membuktikan penyebab kehilangan air, atau membuktikan kesiapan prediksi operasional. Evaluasi ML ditampilkan pada halaman tersendiri.')
    st.subheader('Rumus yang digunakan')
    st.code('NRW agregat (%) = 100 × jumlah NRW / jumlah pasokan\nPorsi 10 terbesar (%) = 100 × kehilangan fisik 10 terbesar / kehilangan fisik sampel')
    st.subheader('Tentang proyek')
    st.write(AUTHOR)
    st.write('Bootcamp Data Analyst with SQL & Python in Google Platform — Batch 25')
    st.write('Alur: memahami data → cleaning → SQL dan EDA → persiapan ML → evaluasi model → dashboard → dokumentasi dan presentasi.')
    st.caption('Analisis SQL saat ini dijalankan melalui SQLite lokal. Evaluasi ML menggunakan pemisahan waktu dan baseline persistence. Proyek ini belum menjalankan BigQuery.')

st.divider()
st.caption('Water Loss Analytics · Data audit tahunan California DWR · Portfolio project')
