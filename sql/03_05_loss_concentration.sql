WITH ranked AS (
  SELECT system_key, real_losses_af,
         ROW_NUMBER() OVER (ORDER BY real_losses_af DESC, system_key) AS loss_rank
  FROM water_loss
  WHERE analysis_year = (SELECT MAX(analysis_year) FROM water_loss)
)
SELECT COUNT(*) AS system_count, SUM(real_losses_af) AS total_real_losses_af,
       SUM(CASE WHEN loss_rank <= 10 THEN real_losses_af ELSE 0 END) AS top10_real_losses_af,
       100.0 * SUM(CASE WHEN loss_rank <= 10 THEN real_losses_af ELSE 0 END)
       / NULLIF(SUM(real_losses_af),0) AS top10_share_pct
FROM ranked;
