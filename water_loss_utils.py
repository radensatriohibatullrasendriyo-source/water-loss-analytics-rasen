"""Perhitungan dashboard; rasio agregat dihitung dari total volume."""
from pathlib import Path
import numpy as np
import pandas as pd

NUMERIC = ['analysis_year','water_supplied_af','real_losses_af','apparent_losses_af',
           'non_revenue_water_af','service_connections','validity_score']

def load_analysis(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding='utf-8-sig', dtype={
        'organization_id':'string','system_id':'string','system_key':'string'})
    required = NUMERIC + ['source_row','system_key','supplier_name','audit_status']
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError('Kolom hasil cleaning belum lengkap: ' + ', '.join(missing))
    if df.empty:
        raise ValueError('Tabel analisis kosong.')
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors='raise')
    if not np.isfinite(df[NUMERIC].to_numpy(dtype=float)).all():
        raise ValueError('Terdapat angka kosong atau tidak hingga.')
    if df['system_key'].isna().any() or df.duplicated(['system_key','analysis_year']).any():
        raise ValueError('Identitas sistem-tahun tidak unik atau kosong. Periksa notebook 02.')
    if not (df['water_supplied_af'].gt(0).all() and df['service_connections'].gt(0).all()):
        raise ValueError('Pasokan dan jumlah sambungan harus positif.')
    if df[['real_losses_af','apparent_losses_af','non_revenue_water_af']].lt(0).any().any():
        raise ValueError('Ada volume negatif; gunakan hasil cleaning yang sudah diverifikasi.')
    df['analysis_year'] = df['analysis_year'].astype(int)
    df['nrw_pct'] = 100 * df['non_revenue_water_af'] / df['water_supplied_af']
    df['real_loss_pct'] = 100 * df['real_losses_af'] / df['water_supplied_af']
    df['real_loss_af_per_connection_year'] = df['real_losses_af'] / df['service_connections']
    return df

def filter_data(df, years, statuses, minimum_score):
    return df.loc[df['analysis_year'].between(int(years[0]), int(years[1])) &
                  df['audit_status'].isin(statuses) & df['validity_score'].ge(minimum_score)].copy()

def aggregate_years(df):
    out = df.groupby('analysis_year', as_index=False).agg(
        audits=('source_row','size'), systems=('system_key','nunique'),
        supplied_af=('water_supplied_af','sum'), nrw_af=('non_revenue_water_af','sum'),
        real_losses_af=('real_losses_af','sum'))
    out['nrw_pct'] = 100 * out['nrw_af'] / out['supplied_af']
    return out

def balanced_panel(df, start, end):
    expected = set(range(int(start), int(end)+1))
    counts = df.groupby('system_key')['analysis_year'].agg(lambda x: set(x))
    keys = counts.index[counts.map(lambda years: years == expected)]
    return df.loc[df['system_key'].isin(keys)].copy()

def kpis(df):
    supplied = float(df['water_supplied_af'].sum())
    loss = float(df['real_losses_af'].sum())
    top = float(df.nlargest(min(10,len(df)), 'real_losses_af')['real_losses_af'].sum())
    return {'audits':len(df), 'systems':df['system_key'].nunique(),
            'nrw_pct':float(100*df['non_revenue_water_af'].sum()/supplied) if supplied else None,
            'real_losses_af':loss, 'top10_pct':100*top/loss if loss else None}
