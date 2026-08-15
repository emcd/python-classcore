Add abstract base class support: `AbstractClass` metaclass and
`AbstractObject` base class combine standard behaviors with
`abc.ABCMeta` machinery (abstract method enforcement, virtual subclass
registration), and mix with external ABC-based classes without
metaclass conflicts. Re-parent `ProtocolClass` under `AbstractClass`,
unifying the standard metaclass taxonomy under `Class`.
