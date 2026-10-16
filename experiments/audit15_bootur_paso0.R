# Auditoria A15 - Paso 0 de B15.1 (enmienda 2, B1): boot_adf de bootUR 1.0.5 sobre las 200 series de la familia 154.
# Uso: Rscript audit15_bootur_paso0.R <series.csv> <meta.csv> <salida.csv>
# series.csv: una columna por serie (T filas); meta.csv: j, case (c|ct), max_lag.
# Para cada serie: set.seed(154000 + j) y bootstrap = "SB"; set.seed(154500 + j) y bootstrap = "SWB".
suppressPackageStartupMessages(library(bootUR))
args <- commandArgs(trailingOnly = TRUE)
Y <- as.matrix(read.csv(args[1], header = FALSE))
meta <- read.csv(args[2])
out <- data.frame()
for (r in seq_len(nrow(meta))) {
  j <- meta$j[r]
  y <- Y[, r]
  det <- if (meta$case[r] == "c") "intercept" else "trend"
  res <- list()
  for (b in c("SB", "SWB")) {
    set.seed(if (b == "SB") 154000 + j else 154500 + j)
    f <- boot_adf(y, bootstrap = b, B = 399, deterministics = det, detrend = "QD", criterion = "MAIC",
                  criterion_scale = FALSE, min_lag = 0, max_lag = meta$max_lag[r], show_progress = FALSE,
                  do_parallel = FALSE)
    res[[b]] <- f
  }
  out <- rbind(out, data.frame(j = j, case = meta$case[r],
                               stat_SB = unname(res$SB$statistic), p_SB = unname(res$SB$p.value),
                               lag_SB = unname(res$SB$details$"selected lags"[1]),
                               stat_SWB = unname(res$SWB$statistic), p_SWB = unname(res$SWB$p.value),
                               lag_SWB = unname(res$SWB$details$"selected lags"[1])))
}
write.csv(out, args[3], row.names = FALSE)
cat("bootUR", as.character(packageVersion("bootUR")), "series", nrow(out), "\n")
