from .typeutils import Info
from .scalar import Int64
from .array import Array


class MetaRef(type):
    def __getitem__(cls, rtypes):
        if not isinstance(rtypes, tuple):
            rtypes = (rtypes,)
        return cls(*rtypes)


class Ref(metaclass=MetaRef):
    def __init__(self, *rtypes):
        self._rtypes = rtypes
        self._rtypes_names = [tt.__name__ for tt in rtypes]
        self.__name__ = "Ref_" + "_".join(tt.__name__ for tt in self._rtypes)

        if len(rtypes) == 1:
            self._isunion = False
            self._size = 8
        else:
            self._isunion = True
            self._size = 16

    def _typeid_from_type(self, typ):
        for ii, tt in enumerate(self._rtypes_names):
            if typ.__name__ == tt:
                return ii
        # If no match found:
        raise TypeError(f"{typ} not registered types!")

    def _type_from_typeid(self, typeid):
        for ii, tt in enumerate(self._rtypes):
            if ii == typeid:
                return tt
        # If no match found:
        raise TypeError(f"Invalid id: {typeid}!")

    def _type_from_name(self, name):
        for tt, nn in zip(self._rtypes, self._rtypes_names):
            if nn == name:
                return tt
        # If no match found:
        raise TypeError(f"Invalid id: {name}!")

    def _get_stored_type(self, buffer, offset):
        typeid = Int64._from_buffer(buffer, offset + 8)
        return self._type_from_typeid(typeid)

    def _from_buffer(self, buffer, offset):
        refoffset = Int64._from_buffer(buffer, offset)
        if refoffset >= 0:
            if self._isunion:
                rtype = self._get_stored_type(buffer, offset)
            else:
                rtype = self._rtypes[0]
            return rtype._from_buffer(buffer, refoffset)
        else:
            raise ValueError("Return uninitialized member")

    def _to_buffer(self, buffer, offset, value, info=None):

        # Get/set reference type
        if self._isunion:
            if value is None:
                # Use the first type (default)
                rtype = self._rtypes[0]
                Int64._to_buffer(buffer, offset + 8, -1)
            elif value.__class__.__name__ in self._rtypes_names:
                rtype = value.__class__
                typeid = self._typeid_from_type(rtype)
                Int64._to_buffer(buffer, offset + 8, typeid)
            elif isinstance(value, dict):
                raise NotImplementedError
            else:
                # Keep old type
                rtype = self._get_stored_type(buffer, offset)
        else:
            rtype = self._rtypes[0]

        # Get/set content
        if value is None:
            refoffset = -1
        elif (
            value.__class__.__name__ == rtype.__name__  # same type
            and value._buffer is buffer
        ):
            refoffset = value._offset
        else:
            newobj = rtype(value, _buffer=buffer)
            refoffset = newobj._offset
        Int64._to_buffer(buffer, offset, refoffset)

    def __call__(self, *args):
        if len(args) == 0:
            return None
        else:
            if self._isunion:
                name, value = args
                return self._type_from_name(name)(value)
            else:
                (value,) = args
                return self._rtypes[0](value)

    def _inspect_args(self, arg):
        return Info(size=self._size)

    def __getitem__(self, shape):
        return Array.mk_arrayclass(self, shape)
