"""Read notebook 05 exports without loading version-dependent model binaries."""
import json
import numpy as np
import pandas as pd


def load_results(folder):
    summary = json.loads((folder / '05_model_summary.json').read_text(encoding='utf-8'))
    metrics = pd.read_csv(folder / '05_test_metrics.csv')
    predictions = pd.read_csv(folder / '05_test_predictions.csv')
    validation = pd.read_csv(folder / '05_validation_metrics.csv')
    name = summary['selection']['selected_ml']
    if summary['selection']['selection_uses_test']:
        raise ValueError('Pemilihan model menggunakan test; periksa notebook sumber.')
    if len(predictions) != summary['test_samples'] or predictions.empty:
        raise ValueError('Jumlah prediksi berbeda dari ringkasan evaluasi.')
    if not predictions.target_year.eq(summary['test_year']).all():
        raise ValueError('Tahun prediksi berbeda dari ringkasan evaluasi.')
    if metrics.model.duplicated().any() or set(metrics.model) != {'persistence', name}:
        raise ValueError('Daftar model pada metrik uji tidak sesuai.')
    if predictions.duplicated(['system_key','target_year']).any():
        raise ValueError('Prediksi uji memiliki pasangan sistem dan tahun duplikat.')
    actual = predictions.actual_real_losses_af.to_numpy(dtype=float)
    for model, column, error_column, summary_key in [
        ('persistence', 'prediction_baseline_af', 'abs_error_baseline_af', 'baseline_test_mae_af'),
        (name, 'prediction_ml_af', 'abs_error_ml_af', 'selected_ml_test_mae_af'),
    ]:
        pred = predictions[column].to_numpy(dtype=float)
        if not np.isfinite(actual).all() or not np.isfinite(pred).all() or (pred < 0).any():
            raise ValueError('Nilai aktual/prediksi tidak valid.')
        error = actual - pred
        row = metrics.set_index('model').loc[model]
        if int(row.samples) != len(predictions):
            raise ValueError('Jumlah sampel metrik tidak sesuai.')
        checks = [
            np.isclose(np.abs(error).mean(), row.mae_af),
            np.isclose(np.sqrt(np.mean(error ** 2)), row.rmse_af),
            np.isclose(np.median(np.abs(error)), row.median_ae_af),
            np.isclose(row.mae_af, summary[summary_key]),
            np.allclose(np.abs(error), predictions[error_column]),
        ]
        if not all(checks):
            raise ValueError('Metrik dan prediksi berasal dari hasil yang berbeda. Ekspor ulang notebook 05.')
    return summary, metrics, predictions, validation
