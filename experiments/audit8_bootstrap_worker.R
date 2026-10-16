# =============================================================================
# Auditoria A8 - worker de wild bootstrap (bootUR::boot_adf, AWB, QD, intercepto,
# lag 0, como en A6/A7) con UNA SEMILLA EXPLICITA POR SERIE.
#
# Diferencia con audit7_bootstrap_worker.R: la semilla de cada serie no es
# seed_start + j - 1, sino el entero j-esimo de un archivo binario (int32) que
# Python deriva de numpy.random.SeedSequence(family, spawn_key = (celda, i, 1)),
# segun el protocolo de A8.
#
# Uso:
#   Rscript audit8_bootstrap_worker.R <bin> <n> <n_series> <B> <cores> \
#           <out_json> <expected_first5_csv> <seeds_bin>
# =============================================================================
suppressPackageStartupMessages({ library(bootUR); library(parallel) })
Sys.setenv(OMP_NUM_THREADS = 1)
Sys.setenv(RCPP_PARALLEL_NUM_THREADS = 1)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 8) {
  stop("Uso: Rscript audit8_bootstrap_worker.R <bin> <n> <n_series> <B> <cores> <out_json> <expected5> <seeds_bin>")
}
bin_file  <- args[1]
n         <- as.integer(args[2])
n_series  <- as.integer(args[3])
B         <- as.integer(args[4])
cores     <- as.integer(args[5])
out_json  <- args[6]
expected5 <- args[7]
seeds_bin <- args[8]

raw_data <- readBin(bin_file, what = "double", n = (n + 1) * n_series, size = 8)
if (length(raw_data) != (n + 1) * n_series) {
  stop(sprintf("BIN TRUNCADO: leidos %d doubles, esperados %d", length(raw_data), (n + 1) * n_series))
}
mat <- matrix(raw_data, nrow = n + 1, ncol = n_series)
seeds <- readBin(seeds_bin, what = "integer", n = n_series, size = 4)
if (length(seeds) != n_series || any(is.na(seeds))) {
  stop(sprintf("SEMILLAS: leidas %d, esperadas %d", length(seeds), n_series))
}

expected_vals <- as.numeric(strsplit(expected5, ",")[[1]])
max_diff <- max(abs(mat[1:5, 1] - expected_vals))
if (!is.finite(max_diff) || max_diff > 1e-6) {
  stop(sprintf("GUARDIA DE ORDEN DE BYTES FALLIDA: max|diff| = %.3e", max_diff))
}

cl <- makeCluster(cores)
on.exit(try(stopCluster(cl), silent = TRUE), add = TRUE)
invisible(clusterEvalQ(cl, {
  Sys.setenv(OMP_NUM_THREADS = 1)
  Sys.setenv(RCPP_PARALLEL_NUM_THREADS = 1)
  RNGkind("Mersenne-Twister", "Inversion", "Rejection")
  suppressPackageStartupMessages(library(bootUR))
}))
clusterExport(cl, c("mat", "B", "seeds"))

t0 <- Sys.time()
p <- parSapply(cl, seq_len(n_series), function(i) {
  set.seed(seeds[i])
  as.numeric(bootUR::boot_adf(
    mat[, i], bootstrap = "AWB", B = B, deterministics = "intercept", detrend = "QD",
    min_lag = 0, max_lag = 0, show_progress = FALSE, do_parallel = FALSE)[["p.value"]])
})
stopCluster(cl)
elapsed <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

vec <- paste0("[", paste(ifelse(is.na(p), "null", sprintf("%.6f", p)), collapse = ", "), "]")
cat(sprintf('{"n": %d, "n_series": %d, "B": %d, "cores": %d, "elapsed_sec": %.3f, "sec_per_series": %.4f, "p_adf": %s}',
            n, n_series, B, cores, elapsed, elapsed / n_series, vec), file = out_json)
cat(sprintf("    [LOTE R] %d series en %.1f s (%.2f s/serie de pared)\n", n_series, elapsed, elapsed / n_series))
