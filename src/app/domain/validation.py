
def type_validate(obj: object, obj_name: str, cls_compare: type):
    if not isinstance(obj, cls_compare):
        raise TypeError(obj_name + " must be type " + cls_compare.__name__)