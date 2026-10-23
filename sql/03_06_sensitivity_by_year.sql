WITH scenarios AS (
 SELECT *, '01 Semua cakupan utama' AS scenario FROM water_loss
 UNION ALL
 SELECT *, '02 Requirements Addressed saja' FROM water_loss
 WHERE audit_status = 'Requirements Addressed'
 UNION ALL
 SELECT *, '03 Skor validitas >= 70 (eksploratif)' FROM water_loss WHERE validity_score >= 70
 UNION ALL
 SELECT *, '04 Tanpa penyesuaian numerik' FROM water_loss WHERE flag_numeric_adjustment = 0
 UNION ALL
 SELECT *, '05 Format ID CA dan 7 digit' FROM water_loss WHERE flag_nonstandard_system_id = 0
 UNION ALL
 SELECT *, '06 Jumlah sambungan bulat' FROM water_loss WHERE flag_noninteger_connections = 0
)
SELECT analysis_year, scenario, COUNT(*) AS audit_count,
       SUM(water_supplied_af) AS supplied_af,
       100.0 * SUM(non_revenue_water_af) / NULLIF(SUM(water_supplied_af),0) AS nrw_pct
FROM scenarios
GROUP BY analysis_year, scenario ORDER BY analysis_year, scenario;
