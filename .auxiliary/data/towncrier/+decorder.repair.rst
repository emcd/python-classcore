Standard Classes: Ensure that Dynadoc decorator applies last, after any
decorators which may potentially replace classes (e.g., ``dataclass( slots =
True )``), so that the Dynadoc visitees weak set captures the correct reference
to prevent multiple decoration.
