WITH eligible_systems AS (
    SELECT system_key
    FROM water_loss
    GROUP BY system_key
    HAVING COUNT(DISTINCT analysis_year) = (SELECT COUNT(DISTINCT analysis_year) FROM water_loss)
       AND COUNT(*) = (SELECT COUNT(DISTINCT analysis_year) FROM water_loss)
)
SELECT w.analysis_year, COUNT(*) AS system_count,
       SUM(w.water_supplied_af) AS supplied_af,
       SUM(w.non_revenue_water_af) AS nrw_af,
       SUM(w.real_losses_af) AS real_losses_af,
       100.0 * SUM(w.non_revenue_water_af) / NULLIF(SUM(w.water_supplied_af),0) AS nrw_pct
FROM water_loss w JOIN eligible_systems b ON w.system_key = b.system_key
GROUP BY w.analysis_year ORDER BY w.analysis_year;
