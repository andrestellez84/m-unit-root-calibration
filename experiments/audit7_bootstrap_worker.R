# =============================================================================
# Auditoria A7 - worker de wild bootstrap (bootUR) con SEMILLA POR SERIE.
#
# Copia del worker de A6 (granularidad de lote, guardia de orden de bytes) con un
# unico cambio de fondo: set.seed por serie antes del bootstrap.
#
# Motivo: el worker de A6 nunca fija la semilla del generador de R, de modo que
# el remuestreo de bootUR cambia en cada ejecucion. Medido en A7 sobre una misma
# serie (n=200, B=399): dos llamadas seguidas sin semilla dieron p = 0.0777 y
# 0.0602; con set.seed(42) dos veces, 0.070175 y 0.070175. Una variacion de ese
# tamano basta para mover rechazos cerca de 0.05, y un p-valor que no se
# reproduce no cumple la convencion de fijar todas las semillas.
#
# La semilla de la serie j del lote es (seed_start + j - 1) mod SEED_MODULUS, con
# seed_start calculado en Python a partir de la semilla de la celda y del indice
# global de la primera serie del lote. Asi la semilla de cada serie depende solo
# de su indice global, no de como parSapply reparte las series entre nucleos ni
# de las fronteras de lote.
#
# Uso:
#   Rscript audit7_bootstrap_worker.R <bin> <n> <n_series> <B> <cores> \
#           <out_json> <expected_first5_csv> <tests> <seed_start>
#   tests in {adf, union, both}
# =============================================================================
suppressPackageStartupMessages({ library(bootUR); library(parallel) })
Sys.setenv(OMP_NUM_THREADS = 1)
Sys.setenv(RCPP_PARALLEL_NUM_THREADS = 1)

SEED_MODULUS <- 2147483647 - 1000000

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 9) {
  stop(paste("Uso: Rscript audit7_bootstrap_worker.R <bin> <n> <n_series>",
             "<B> <cores> <out_json> <expected_first5_csv> <tests> <seed_start>"))
}
bin_file   <- args[1]
n          <- as.integer(args[2])
n_series   <- as.integer(args[3])
B          <- as.integer(args[4])
cores      <- as.integer(args[5])
out_json   <- args[6]
expected5  <- args[7]
tests      <- args[8]
seed_start <- as.numeric(args[9])

if (!tests %in% c("adf", "union", "both")) {
  stop(sprintf("tests debe ser adf|union|both, recibido '%s'", tests))
}
if (!is.finite(seed_start) || seed_start < 0 || seed_start >= SEED_MODULUS ||
    seed_start != floor(seed_start)) {
  stop(sprintf("seed_start invalido: %s", args[9]))
}

# --- carga y guardia de integridad --------------------------------------------
raw_data <- readBin(bin_file, what = "double", n = (n + 1) * n_series, size = 8)
if (length(raw_data) != (n + 1) * n_series) {
  stop(sprintf("BIN TRUNCADO: leidos %d doubles, esperados %d",
               length(raw_data), (n + 1) * n_series))
}
mat <- matrix(raw_data, nrow = n + 1, ncol = n_series)

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
  RNGkind("Mersenne-Twister", "Inversion", "Rejection")
  suppressPackageStartupMessages(library(bootUR))
}))
clusterExport(cl, c("mat", "B", "tests", "seed_start", "SEED_MODULUS"))

t0 <- Sys.time()
res <- parSapply(cl, seq_len(n_series), function(i) {
  y <- mat[, i]
  set.seed((seed_start + (i - 1)) %% SEED_MODULUS)
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
         ' "seed_start": %.0f, "seed_modulus": %.0f,',
         ' "elapsed_sec": %.3f, "sec_per_series": %.4f,',
         ' "p_adf": %s, "p_union": %s}'),
  n, n_series, B, cores, tests, seed_start, SEED_MODULUS,
  elapsed, elapsed / n_series, num_vec(p_adf), num_vec(p_union))
cat(json_str, file = out_json)

cat(sprintf("    [LOTE] %d series en %.1f s (%.2f s/serie de pared)\n",
            n_series, elapsed, elapsed / n_series))
