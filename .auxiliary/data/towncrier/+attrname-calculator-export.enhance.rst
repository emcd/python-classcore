Export the reference attribute-name calculator publicly from
``classcore.standard.nomina`` with a configurable package prefix:
downstream packages construct ``AttrnameCalculator( package_name =
... )`` to generate and detect grammar-conformant internal names
under their own prefix, sharing classcore's vocabulary by
construction instead of mirroring it. The grammar containers stay
private; detection consults reserved framework vocabulary.
