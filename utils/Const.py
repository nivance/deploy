# -*- coding:utf-8 -*-

class _const:

    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise self.ConstError("can't rebind const(%s)", key)
        if not key.isupper():
            raise self.ConstCaseError('const name "%s" is not all uppercase', key)
        self.__dict__[key] = value


Const = _const()
Const.CONFIG_SECTIONS_GLOBAL = 'global'
Const.CONFIG_SECTIONS_LOCAL = 'local'
Const.CONFIG_SECTIONS_REMOTE = 'remote'
