SELECT system_key, supplier_name, analysis_year, audit_status,
       real_losses_af, water_supplied_af, service_connections, validity_score,
       100.0 * real_losses_af / NULLIF(water_supplied_af,0) AS real_loss_share_pct,
       real_losses_af / NULLIF(service_connections,0) AS real_loss_af_per_connection_year,
       flag_nonstandard_system_id, flag_noninteger_connections
FROM water_loss
WHERE analysis_year = (SELECT MAX(analysis_year) FROM water_loss)
ORDER BY real_losses_af DESC, system_key
LIMIT 10;
