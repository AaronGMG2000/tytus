from Instrucciones.TablaSimbolos.Instruccion import Instruccion
from Instrucciones.Sql_create.Tipo_Constraint import Tipo_Constraint, Tipo_Dato_Constraint
from Instrucciones.Excepcion import Excepcion
from Instrucciones.TablaSimbolos import Instruccion3D as c3d
#from storageManager.jsonMode import *

class AlterTableAddConstraint(Instruccion):
    def __init__(self, tabla, id, lista_col, strGram, linea, columna):
        Instruccion.__init__(self,None,linea,columna,strGram)
        self.tabla = tabla
        self.id = id
        self.lista_col = lista_col
    
    def ejecutar(self, tabla, arbol):
        super().ejecutar(tabla,arbol)
        if arbol.bdUsar != None:
            objetoTabla = arbol.devolviendoTablaDeBase(self.tabla)
            if objetoTabla != 0:
                existe = None
                for columnas in objetoTabla.lista_de_campos:
                    if columnas.constraint != None:
                        for const in columnas.constraint:
                            if const.id == self.id:
                                existe = True
                if existe:
                    error = Excepcion('42P01',"Semántico","la relación «"+self.id+"» ya existe",self.linea,self.columna)
                    arbol.excepciones.append(error)
                    arbol.consola.append(error.toString())
                    return error
                listaUnique = []
                listaNombres = []
                for c in self.lista_col:
                    for columnas in objetoTabla.lista_de_campos:
                        if columnas.nombre == c:
                            listaUnique.append(columnas)
                            listaNombres.append(columnas.nombre)
                if(len(listaUnique)==len(self.lista_col)):
                    #print(len(listaUnique),self.tabla, self.id)
                    #Insertar llaves Unique
                    for c in listaUnique:
                        if c.constraint != None:
                            c.constraint.append(Tipo_Constraint(self.id, Tipo_Dato_Constraint.UNIQUE, None))
                            #print("MÁS DE UNA-----------------",c.nombre, c.tipo.toString(),len(c.constraint))
                        else:
                            c.constraint = []
                            c.constraint.append(Tipo_Constraint(self.id, Tipo_Dato_Constraint.UNIQUE, None))
                            #print("SOLO UNA-------------",c.nombre, c.tipo.toString(),len(c.constraint)) 
                    arbol.consola.append("Consulta devuelta correctamente.")  
                else:
                    lista = set(self.lista_col) - set(listaNombres)
                    #print(listaNombres,self.lista_col)
                    #print(lista)
                    for i in lista:
                        error = Excepcion('42P01',"Semántico","No existe la columna «"+i+"» en la llave",self.linea,self.columna)
                        arbol.excepciones.append(error)
                        arbol.consola.append(error.toString())
                    return
            else:
                error = Excepcion('42P01',"Semántico","No existe la relación "+self.tabla,self.linea,self.columna)
                arbol.excepciones.append(error)
                arbol.consola.append(error.toString())
                return error
        else:
            error = Excepcion("100","Semantico","No ha seleccionado ninguna Base de Datos.",self.linea,self.columna)
            arbol.excepciones.append(error)
            arbol.consola.append(error.toString())
        
    def generar3DV2(self, tabla, arbol):
        super().generar3D(tabla,arbol)
        code = []
        code.append('h = p')
        code.append('h = h + 1')
        t0 = c3d.getTemporal()
        bd = arbol.getBaseDatos()
        if bd != None and bd != "":
            code.append(t0 + ' = "' + bd + '"')
        else:
            code.append(t0 + ' = ' + str(None))
        code.append('heap[h] = ' + t0)
        code.append('h = h + 1')
        t1 = c3d.getTemporal()
        code.append(t1 + ' = "' + str(self.tabla) + '"')
        code.append('heap[h] = ' + t1)
        code.append('h = h + 1')
        t2 = c3d.getTemporal()
        code.append(t2 + ' = "' + str(self.id) + '"')
        code.append('heap[h] = ' + t2)
        code.append('h = h + 1')
        if self.lista_col != None:
            code.append('heap[h] = []')
            for columna in self.lista_col:
                t3 = c3d.getTemporal()
                code.append(t3 + ' = ["' + str(columna) + '"]')
                code.append('heap[h] = heap[h] + ' + t3)
        else:
            code.append('heap[h] = None')
        code.append('p = h')
        code.append('call_alterTable_addConstraint()')
        
        return code