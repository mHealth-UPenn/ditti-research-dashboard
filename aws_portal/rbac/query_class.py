class _QueryClass:
    def __get__(self, instance, owner):
        raise RuntimeError("`query` cannot be used on RBAC-enabled tables. Use `cls.select` instead.")
