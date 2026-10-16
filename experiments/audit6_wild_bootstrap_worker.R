# =============================================================================
# Auditoria A6 - Worker de wild bootstrap (bootUR), granularidad de LOTE.
#
# Procesa UN lote de series y escribe su JSON al terminar ese lote. La version
# anterior de este script acumulaba las 2,000 replicas de la celda en memoria y
# escribia una sola vez al final, de modo que la celda era un bloque atomico:
# a n=1000 eso significo 32.5 h irrecuperables al interrumpirse la corrida.
# Aqui el lote es la unidad de perdida maxima.
#
# Uso:
#   Rscript audit6_wild_bootstrap_worker.R <bin> <n> <n_series> <B> <cores> \
#           <out_json> <expected_first5_csv> <tests>
#   tests in {adf, union, both}
# =============================================================================
suppressPackageStartupMessages({ library(bootUR); library(parallel) })
Sys.setenv(OMP_NUM_THREADS = 1)
Sys.setenv(RCPP_PARALLEL_NUM_THREADS = 1)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 8) {
  stop(paste("Uso: Rscript audit6_wild_bootstrap_worker.R <bin> <n> <n_series>",
             "<B> <cores> <out_json> <expected_first5_csv> <tests>"))
}
bin_file   <- args[1]
n          <- as.integer(args[2])
n_series   <- as.integer(args[3])
B          <- as.integer(args[4])
cores      <- as.integer(args[5])
out_json   <- args[6]
expected5  <- args[7]
tests      <- args[8]

if (!tests %in% c("adf", "union", "both")) {
  stop(sprintf("tests debe ser adf|union|both, recibido '%s'", tests))
}

# --- carga y guardia de integridad --------------------------------------------
raw_data <- readBin(bin_file, what = "double", n = (n + 1) * n_series, size = 8)
if (length(raw_data) != (n + 1) * n_series) {
  stop(sprintf("BIN TRUNCADO: leidos %d doubles, esperados %d",
               length(raw_data), (n + 1) * n_series))
}
mat <- matrix(raw_data, nrow = n + 1, ncol = n_series)

# El .bin se escribe desde Python con mat.T.tofile() (disposicion columnar que R
# espera). Un mat.tofile() en orden C produce una matriz transpuesta cuyos
# primeros valores son todos 0.0 y cuyos p-valores salen todos < 0.05: un fallo
# silencioso. Esta guardia lo convierte en un error duro.
expected_vals <- as.numeric(strsplit(expected5, ",")[[1]])
got_vals <- mat[1:5, 1]
max_diff <- max(abs(got_vals - expected_vals))
if (!is.finite(max_diff) || max_diff > 1e-6) {
  stop(sprintf(paste("GUARDIA DE ORDEN DE BYTES FALLIDA: max|diff| = %.3e.",
                     "Esperado [%s], leido [%s]"),
               max_diff, paste(sprintf("%.6f", expected_vals), collapse = ", "),
               paste(sprintf("%.6f", got_vals), collapse = ", ")))
}

# --- ejecucion paralela del lote ----------------------------------------------
cl <- makeCluster(cores)
on.exit(try(stopCluster(cl), silent = TRUE), add = TRUE)
invisible(clusterEvalQ(cl, {
  Sys.setenv(OMP_NUM_THREADS = 1)
  Sys.setenv(RCPP_PARALLEL_NUM_THREADS = 1)
  suppressPackageStartupMessages(library(bootUR))
}))
clusterExport(cl, c("mat", "B", "tests"))

t0 <- Sys.time()
res <- parSapply(cl, seq_len(n_series), function(i) {
  y <- mat[, i]
  pa <- NA_real_
  pu <- NA_real_
  if (tests %in% c("adf", "both")) {
    pa <- as.numeric(bootUR::boot_adf(
      y, bootstrap = "AWB", B = B, deterministics = "intercept", detrend = "QD",
      min_lag = 0, max_lag = 0, show_progress = FALSE,
      do_parallel = FALSE)[["p.value"]])
  }
  if (tests %in% c("union", "both")) {
    pu <- as.numeric(bootUR::boot_union(
      y, bootstrap = "AWB", B = B, min_lag = 0, max_lag = 0,
      show_progress = FALSE, do_parallel = FALSE)[["p.value"]])
  }
  c(adf = pa, union = pu)
})
stopCluster(cl)
elapsed <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

p_adf   <- as.numeric(res["adf", ])
p_union <- as.numeric(res["union", ])

num_vec <- function(v) {
  if (all(is.na(v))) return("null")
  paste0("[", paste(ifelse(is.na(v), "null", sprintf("%.6f", v)),
                    collapse = ", "), "]")
}

json_str <- sprintf(
  paste0('{"n": %d, "n_series": %d, "B": %d, "cores": %d, "tests": "%s",',
         ' "elapsed_sec": %.3f, "sec_per_series": %.4f,',
         ' "p_adf": %s, "p_union": %s}'),
  n, n_series, B, cores, tests, elapsed, elapsed / n_series,
  num_vec(p_adf), num_vec(p_union))
cat(json_str, file = out_json)

cat(sprintf("    [LOTE] %d series en %.1f s (%.2f s/serie de pared)\n",
            n_series, elapsed, elapsed / n_series))
