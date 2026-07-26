#Excepciones relacionadas a RAW MATERIALS

class RawMaterialCodeAlreadyExistsError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class UnitNotFoundError(Exception):
    pass

class RawMaterialNotFoundError(Exception):
    pass

#Excepciones relacionadas a CATEGORIAS
class CategoryNameAlreadyExistsError(Exception):
    pass


#Excepciones relacionadas a UNITS
class UnitNameAlreadyExistsError(Exception):
    pass

class UnitSymbolAlreadyExistsError(Exception):
    pass

#Excepciones relacionadas a SUPPLIERS
class SupplierNameAlreadyExistsError(Exception):
    pass

class SupplierTaxIdAlreadyExistsError(Exception):
    pass