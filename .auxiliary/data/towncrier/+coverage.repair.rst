Properly report test coverage by considering doctests too. (Not a user-facing
fix; however important to note that coverage was 100% on initial release, but
Github Actions workflow was not properly setup to capture coverage from
doctests and so it only reported 95% coverage.)
