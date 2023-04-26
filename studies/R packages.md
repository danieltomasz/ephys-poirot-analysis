# Installing R packages from github

```{R}
Sys.getenv("GITHUB_PAT")
remotes::install_github("ggseg/ggseg")
remotes::install_github("LCBC-UiO/ggsegSchaefer")
remotes::install_github("ggseg/ggseg3d", build_vignettes = TRUE)

```