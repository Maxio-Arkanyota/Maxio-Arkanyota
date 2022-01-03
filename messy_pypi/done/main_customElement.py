from __future__ import annotations

from typing import Iterator


class List(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def prepend(self, value) -> None:
        self.insert(0, value)

    def rmAllBeside(self, elt: any = None, index: int = None):
        if index:
            del self[index + 1:]
        if elt:
            del self[self.find(elt) + 1:]

    def rmAllBehind(self, elt: any = None, index: int = None):
        if index:
            del self[:index]
        if elt:
            del self[:self.find(elt)]

    def rmMAll(self, elts: list[any]) -> None:
        for elt in elts:
            self.rmAll(elt)

    def rmAll(self, elt: any) -> None:
        while elt in self:
            self.remove(elt)

    def rm(self, elt: any) -> None:
        if elt in self:
            self.remove(elt)

    def indexExist(self, index: int) -> bool:
        if 0 <= index < len(self):
            return True
        return False

    def replace(self, start: any, end: any) -> None:
        if start in self:
            self[self.index(start)] = end

    def replaceAll(self, start: any, end: any, maxreplace: int = float('inf')) -> None:
        i = 0
        while (start in self) and i < maxreplace:
            self[self.index(start)] = end

    def find(self, elt: any) -> int:
        if elt in self:
            return self.index(elt)
        return None

    def findAll(self, elt: any) -> list[int]:
        indexl = list()
        for key, val in enumerate(self):
            if val == elt:
                indexl.append(key)
        return indexl

    def clearNotValue(self) -> None:
        for k, v in self:
            if not v:
                del self[k]

    def clearDuplicate(self) -> None:
        dup = List(set(self))
        self.clear()
        self.extend(dup)

    def showDuplicate(self) -> list:
        dup = []
        counta = self.countAll()
        for i in counta:
            if i[1] > 1:
                dup.append(i[0])
        return dup

    def countAll(self) -> list[tuple[any, int]]:
        counta = []
        unique = list(set(self))
        for elt in unique:
            counta.append((elt, self.count(elt)))
        return counta

    def toType(self) -> None:
        for key, val in enumerate(self):
            if val.replace('.', '', 1).lstrip('-').isdigit():
                if '.' in val:
                    self[key] = float(val)
                else:
                    self[key] = int(val)

    def include(self, elt: any) -> bool:
        if elt in self:
            return True
        return False

    def includes(self, elts: list) -> bool:
        for elt in elts:
            if elt not in self:
                return False
        return True

    def __copy__(self) -> List:
        return List(self)

    def copy(self) -> List:
        return List(self)

    @property
    def help(self) -> None:
        print("""list custom pour python, avec 
        `- prepend(elt)` : permet d'inserer l'element a l'index zero \
        `- rmAllBeside(elt, index)` : permet de supprimer tout les element après la premiere itération de l'element ou après l'index \
        `- rmAllBehind(elt, index)` : permet de supprimer tout les element avant la premiere itération de l'element ou avant l'index \
        `- rm(elt)` : permet de supprimer le premier element dans la liste correspondant, s'il n'existe pas ne renvoie pas d'erreur \
        `- rmAll(elt)` : permet de supprimer tout les element dans la liste correspondant, s'il n'existe pas ne renvoie pas d'erreur \
        `- rmMAll([elt,...])` : permet de supprimer tout les element dans la liste contenue dans le tableau, s'ils n'existe pas ne renvoie pas d'erreur \
        `- indexExist(index)` : renvoie True si l'index existe sinon False \
        `- replace(start,end)` : remplace la valeur de depart part la nouvelle, sur le premiere element trouvé \
        `- replaceAll(start,end,maxreplace)` : remplace la valeur de depart part le nouveau, opération sur tout le tableau \
        `- find(elt)` : trouve l'index d'un element par sa valeur, retourne l'index \
        `- findAll(elt)` : retourne tout l'index de tout les element correspondent \
        `- clearNotValue()` : supprime toutes les valeurs null : [0,'',None,False, ...] \
        `- clearDuplicate()` : supprimer toutes les doublont \
        `- showDuplicate()` : renvoie les valeurs dupliquer \
        `- countAll()` : renvoie une list de tuple avec le count de chaque element \
        `- toType()` : transforme tout les float et int sous forme de string ex: '1.0' -> 1.0, '1'-> 1  \
        `- include(elt)`: retourne True ou False dépendant si l'element est present ou non \
        `- includes(elts)`: retourne True ou False dépendant si les elements sont present ou non \
        `- copy()`: return copy of list with init new class List \
        `- help`: affiche la doc suivant \
        `- enumerate` : un iterator enumerate -> list(liste.enumerate) => [(index,value),...] \
        `- renumerate` : un iterator enumerate reverse -> list(liste.renumerate) => [(index-1,value-1),...] \
        `- maxv` : retourne la valeur max du tableau \
        `- maxi` : retourne l'index de la valeur max \
        `- maxl` : retourne la valeur avec le len max du tableau \
        `- minv` : retourne la valeur min du tableau \
        `- mini` : retourne l'index de la valeur min \
        `- minl` : retourne la valeur avec le len min du tableau \
        `- length` : renvoie le poid du tableau \
        """)
        func = []
        for x in self.__dir__():
            if not x[:2] == x[-2:] == '__':
                func.append(x)
        return func

    @property
    def enumerate(self) -> enumerate:
        return enumerate(self)

    @property
    def renumerate(self) -> Iterator:
        return reversed(list(self.enumerate))

    @property
    def maxv(self) -> any:
        return max(self)

    @property
    def maxi(self) -> int:
        return self.index(max(self))

    @property
    def maxl(self) -> any:
        l = list(map(lambda x: len(x), self))
        return self[l.index(max(l))]

    @property
    def minv(self) -> any:
        return min(self)

    @property
    def mini(self) -> int:
        return self.index(min(self))

    @property
    def minl(self) -> any:
        l = list(map(lambda x: len(x), self))
        return self[l.index(min(l))]

    @property
    def length(self) -> int:
        return len(self)
