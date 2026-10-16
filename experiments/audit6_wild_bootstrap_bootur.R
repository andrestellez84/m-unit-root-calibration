# ==============================================================================
# Auditoría A6 — Experimento 1: Wild Bootstrap vía bootUR (R)
# Interoperabilidad R <-> Python
# ==============================================================================
#
# Requiere:
#   R >= 4.0.0
#   install.packages("bootUR")
#
# Especificación:
#   - DGP 3: r in {1, 2, 3, 4} x n in {200, 1000} (8 celdas, H0 con quiebre de varianza)
#   - DGP 1: rho in {0.95, 0.97, 0.99} x n in {200, 500, 1000} (9 celdas, H1 persistente)
#   - N_sim = 2000 por celda
#   - Bootstrap: AWB (Autoregressive Wild Bootstrap), B = 999 (B = 1999 para r=4 y rho=0.99)
#   - Orden de rezagos: fijo (p=0 para paseo aleatorio / AR(1) base), eliminando búsqueda AIC

suppressPackageStartupMessages({
  if (!requireNamespace("bootUR", quietly = TRUE)) {
    stop("El paquete 'bootUR' no está instalado. Ejecute install.packages('bootUR')")
  }
  library(bootUR)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
output_file <- ifelse(length(args) > 0, args[1], "experiments/results/wild_bootstrap_r_audit6.json")

# Parámetros del experimento recortado (Auditoría A6)
ALPHA <- 0.05
N_SIM <- 2000
DGP3_RATIOS <- c(1.0, 2.0, 3.0, 4.0)
DGP3_N <- c(200, 1000)

DGP1_RHOS <- c(0.95, 0.97, 0.99)
DGP1_N <- c(200, 500, 1000)

results <- list(
  metadata = list(
    r_version = R.version.string,
    bootur_version = as.character(packageVersion("bootUR")),
    timestamp_utc = format(as.POSIXlt(Sys.time(), tz = "UTC"), "%Y-%m-%dT%H:%M:%SZ"),
    alpha = ALPHA,
    N_sim = N_SIM,
    bootstrap_method = "AWB",
    lag_order = "fixed (p=0)"
  ),
  dgp3 = list(),
  dgp1 = list()
)

cat("======================================================================\n")
cat("  Auditoría A6: Wild Bootstrap (bootUR::boot_union)\n")
cat(sprintf("  R: %s | bootUR: %s\n", R.version.string, packageVersion("bootUR")))
cat("======================================================================\n\n")

# ------------------------------------------------------------------------------
# DGP 3: Paseo aleatorio con quiebre de varianza
# ------------------------------------------------------------------------------
cat("--- DGP 3: Quiebre de Varianza en Paseo Aleatorio ---\n")
for (n in DGP3_N) {
  n_key <- as.character(n)
  results$dgp3[[n_key]] <- list()
  
  for (r in DGP3_RATIOS) {
    r_key <- as.character(r)
    B <- ifelse(r == 4.0, 1999, 999)
    seed_base <- 300000 + n * 100 + as.integer(r * 10)
    set.seed(seed_base)
    
    t0 <- Sys.time()
    rejections <- 0
    
    for (i in 1:N_SIM) {
      # Generación DGP 3
      t_break <- floor(n / 2)
      eps <- rnorm(n)
      eps[(t_break + 1):n] <- eps[(t_break + 1):n] * r
      y <- c(0, cumsum(eps))
      
      # boot_union con orden fijo y AWB
      res <- bootUR::boot_union(y, bootstrap = "AWB", B = B, p = 0, print.progress = FALSE)
      if (res$p_value < ALPHA) {
        rejections <- rejections + 1
      }
    }
    
    rate <- rejections / N_SIM
    # Intervalo de confianza de Wilson / Clopper-Pearson
    binom_ci <- binom.test(rejections, N_SIM, conf.level = 0.95)$conf.int
    elapsed <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
    
    results$dgp3[[n_key]][[r_key]] <- list(
      rate = rate,
      ci_lower = binom_ci[1],
      ci_upper = binom_ci[2],
      rejections = rejections,
      B = B,
      elapsed_sec = elapsed
    )
    cat(sprintf("  [DGP3] n=%4d, r=%3.1f: Size = %.4f [%.4f, %.4f] (%.1fs)\n",
                n, r, rate, binom_ci[1], binom_ci[2], elapsed))
  }
}

# ------------------------------------------------------------------------------
# DGP 1: AR(1) persistente (Potencia local)
# ------------------------------------------------------------------------------
cat("\n--- DGP 1: AR(1) Persistente (Evaluación de Potencia) ---\n")
for (n in DGP1_N) {
  n_key <- as.character(n)
  results$dgp1[[n_key]] <- list()
  
  for (rho in DGP1_RHOS) {
    rho_key <- as.character(rho)
    B <- ifelse(rho == 0.99, 1999, 999)
    seed_base <- 100000 + n * 100 + as.integer(rho * 100)
    set.seed(seed_base)
    
    t0 <- Sys.time()
    rejections <- 0
    
    for (i in 1:N_SIM) {
      # Generación DGP 1 estacionario
      sigma_unc <- 1.0 / sqrt(1 - rho^2)
      y <- numeric(n + 1)
      y[1] <- rnorm(1, 0, sigma_unc)
      eps <- rnorm(n)
      for (t in 1:n) {
        y[t + 1] <- rho * y[t] + eps[t]
      }
      
      res <- bootUR::boot_union(y, bootstrap = "AWB", B = B, p = 0, print.progress = FALSE)
      if (res$p_value < ALPHA) {
        rejections <- rejections + 1
      }
    }
    
    rate <- rejections / N_SIM
    binom_ci <- binom.test(rejections, N_SIM, conf.level = 0.95)$conf.int
    elapsed <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
    
    results$dgp1[[n_key]][[rho_key]] <- list(
      rate = rate,
      ci_lower = binom_ci[1],
      ci_upper = binom_ci[2],
      rejections = rejections,
      B = B,
      elapsed_sec = elapsed
    )
    cat(sprintf("  [DGP1] n=%4d, rho=%.2f: Power = %.4f [%.4f, %.4f] (%.1fs)\n",
                n, rho, rate, binom_ci[1], binom_ci[2], elapsed))
  }
}

# Guardar salida JSON
write_json(results, output_file, pretty = TRUE, auto_unbox = TRUE)
cat(sprintf("\nResultados guardados exitosamente en: %s\n", output_file))
