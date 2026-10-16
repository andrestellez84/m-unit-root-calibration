# Auditoria A6 - Benchmark de costo de bootUR. Escribe JSON incremental tras CADA
# medicion: si el proceso muere, no se pierde ninguna medicion ya hecha.
suppressPackageStartupMessages({ library(bootUR); library(parallel) })
Sys.setenv(OMP_NUM_THREADS = 1); Sys.setenv(RCPP_PARALLEL_NUM_THREADS = 1)

args <- commandArgs(trailingOnly = TRUE)
bin200 <- args[1]; bin500 <- args[2]; bin1000 <- args[3]; out_json <- args[4]

load_mat <- function(path, n, ncol) {
  raw <- readBin(path, what = "double", n = (n + 1) * ncol, size = 8)
  matrix(raw, nrow = n + 1, ncol = ncol)
}
M <- list("200" = load_mat(bin200, 200, 20),
          "500" = load_mat(bin500, 500, 20),
          "1000" = load_mat(bin1000, 1000, 20))

rows <- character(0)
emit <- function(...) {
  rows <<- c(rows, sprintf(...))
  cat(paste0("[\n  ", paste(rows, collapse = ",\n  "), "\n]\n"), file = out_json)
}

run_adf <- function(y, B) bootUR::boot_adf(y, bootstrap = "AWB", B = B,
  deterministics = "intercept", detrend = "QD", min_lag = 0, max_lag = 0,
  show_progress = FALSE, do_parallel = FALSE)[["p.value"]]
run_union <- function(y, B) bootUR::boot_union(y, bootstrap = "AWB", B = B,
  min_lag = 0, max_lag = 0, show_progress = FALSE, do_parallel = FALSE)[["p.value"]]

cat("=== FASE A: escalamiento uni-hilo (1 serie, 1 nucleo) ===\n"); flush.console()
for (n in c(200, 500, 1000)) {
  y <- M[[as.character(n)]][, 1]
  for (B in c(399, 999)) {
    for (fn in c("boot_adf", "boot_union")) {
      if (fn == "boot_union" && B == 399) next   # union solo a B=999
      t0 <- Sys.time()
      pv <- if (fn == "boot_adf") run_adf(y, B) else run_union(y, B)
      el <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
      emit('{"phase":"A","fn":"%s","n":%d,"B":%d,"cores":1,"n_series":1,"sec":%.3f,"sec_per_series":%.3f,"p":%.4f}',
           fn, n, B, el, el, pv)
      cat(sprintf("  n=%-5d B=%-4d %-11s %8.2f s  (p=%.4f)\n", n, B, fn, el, pv)); flush.console()
    }
  }
}

cat("\n=== FASE B: rendimiento paralelo (n=1000, boot_adf, B=999, 14 series) ===\n"); flush.console()
for (nc in c(6, 10, 14)) {
  mat <- M[["1000"]]
  cl <- makeCluster(nc)
  invisible(clusterEvalQ(cl, { Sys.setenv(OMP_NUM_THREADS = 1)
                     Sys.setenv(RCPP_PARALLEL_NUM_THREADS = 1)
                     suppressPackageStartupMessages(library(bootUR)) }))
  clusterExport(cl, c("mat"))
  t0 <- Sys.time()
  invisible(parSapply(cl, 1:14, function(i) bootUR::boot_adf(mat[, i],
    bootstrap = "AWB", B = 999, deterministics = "intercept", detrend = "QD",
    min_lag = 0, max_lag = 0, show_progress = FALSE, do_parallel = FALSE)[["p.value"]]))
  el <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
  stopCluster(cl)
  emit('{"phase":"B","fn":"boot_adf","n":1000,"B":999,"cores":%d,"n_series":14,"sec":%.3f,"sec_per_series":%.3f}',
       nc, el, el / 14)
  cat(sprintf("  cores=%-3d 14 series en %8.2f s  -> %6.2f s/serie de pared\n", nc, el, el / 14))
  flush.console()
}
cat("\nBENCH DONE\n")
