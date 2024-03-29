from Estructura import Estructura
from antlr4 import *
from antlr4.tree.Trees import TerminalNode
from decafLexer import decafLexer
from decafListener import decafListener
from decafParser import decafParser
from Variable import *
from Funcion import *
from Tipos import *
from Error import *
import copy
import sys

pilaVariable = []
pilaFuncion = []
pilaEstructura = []
funcionTemp = None
funcionNombreTemp = None

procesandoReturnExp = False
expressionReturnTemp = []

procesandoArrayExp = False
expressionArrayTemp = []

procesandoArgExp = False
expressionArgTemp = []
listaTiposArg = []
controlCantidadParam = False

procesandoLocation = False
locationList = []
idLocationTemp = None

'''
Aqui se guardan los parametros de la funcion
para luego al entrar al ambito de la funcion
ingresar esas variables
'''
ambitoVariableTemp = {}


class DecafPrinter(decafListener):
    def __init__(self) -> None:
        super().__init__()

    def agregarVariableATabla(self, nombre, variable):
        '''
        Funcion que valida si una variable ya existe en la tabla actual
        si ya existe retorna error, caso contrario agrega a tabla (no retorna nada).

        Parametros
        - nombre: string con el nombre de la variable
        - variable: objeto Variable con la informacion de la variable a ingresar.
        '''

        # print()

        if(nombre in pilaVariable[-1].keys()):
            return Error('Esta variable ya existe')
        else:
            pilaVariable[-1][nombre] = variable
        """
        print(f'''
                # Pila Variables
                {pilaVariable}
                ''')
        """

    def agregarStructATabla(self, nombre, estructura):
        '''
        Funcion que valida si una estructura ya existe en la tabla actual
        si ya existe retorna error, caso contrario agrega a tabla (no retorna nada).

        Parametros
        - nombre: string con el nombre de la estructura
        - estructura: objeto estructura con la informacion de la estructura a ingresar.
        '''
        """
        print(f'''
        agregarStructATabla
        nombre = {nombre}
        pila = {pilaEstructura}
        ''')
        """
        if(nombre in pilaEstructura[-1].keys()):
            return Error(f"La estructura '{nombre}' ya ha sido declarada antes.")
        else:
            pilaEstructura[-1][nombre] = estructura

        """
        print(f'''
                # Pila Estructura
                {pilaEstructura}
                ''')
        """

    def validarEstructura(self, nombreEstructura):
        '''
        Funcion que valida si una estructura ya existe en la tabla actual
        si no existe retorna error, caso contrario True.

        Parametros
        - nombreEstructura: string con el nombre de la estructura
        '''
        if(nombreEstructura in pilaEstructura[-1].keys()):
            return True
        else:
            return Error(f"La estructura '{nombreEstructura}' no ha sido definida.")

    def validarCantidadParametrosFunc(self, nombreFunc, hijosNodo):
        '''
        Funcion para validar la cantidad de parametros en la llamada de una funcion

        Parametros:
        - nombreFunc: Nombre de la funcion a evaluar
        - hijosNodo: todos los hijos del nodo <methodCallDec>

        Retorno:
        - Error en el caso de que la cantidad de argumentos no coincida con la definicion
        '''
        cantidadReal = len(pilaFuncion[-1][nombreFunc].argumentosTipos)

        contador = 0
        for i in hijosNodo:
            if(isinstance(i, decafParser.ArgDecContext)):
                contador += 1

        if not(cantidadReal == contador):
            return Error(f"Se esperaban {cantidadReal} argumentos en lugar de {contador}")

    def agregarVariableAmbitoTemp(self, nombre, variable):
        '''
        Funcion que valida si una variable ya existe en el ambito temporal
        si ya existe retorna error, caso contrario agrega a tabla (no retorna nada).

        El ambito temporal se crea para registrar los parametros de una funcion, antes
        de ingresar al block donde se crea el verdadero ambito.

        Parametros
        - nombre: string con el nombre de la variable
        - variable: objeto Variable con la informacion de la variable a ingresar.
        '''
        if(nombre in ambitoVariableTemp.keys()):
            return Error(f'La variable "{nombre}" ya existe dentro de los parametros de la funcion')
        else:
            ambitoVariableTemp[nombre] = variable

        """
        print(f'''
                # Pila Variables [temp]
                {ambitoVariableTemp}
                ''')
        """

    def agregarAmbitoTempATabla(self):
        '''
        Pasa el ambitoTemp al ambito de la funcion y limpia
        el ambitoTemp.
        No retorna nada
        '''
        global ambitoVariableTemp
        pilaVariable[-1].update(ambitoVariableTemp)
        ambitoVariableTemp = {}

        """
        print(f'''
                # Pila Variables
                {pilaVariable}
                ''')
        """

    def validarReglaMain(self):
        try:
            if not(len(pilaFuncion[-1]['main'].argumentosTipos) == 0):
                return Error('La funcion main contiene parametros')
        except:
            # no existe main
            return Error('Programa sin funcion main')

    def agregarAmbito(self):
        pilaVariable.append({})

    def quitarAmbito(self):
        pilaVariable.pop()
        # pilaEstructura.pop()

    def agregarFuncionATabla(self, nombre, funcion):
        '''
        Funcion que valida si una funcion ya existe en la tabla actual
        si ya existe retorna error, caso contrario agrega a tabla (no retorna nada).

        Solo se agrega a la tabla si no tiene errores en los argumentos

        Parametros
        - nombre: string con el nombre de la funcion
        - funcion: objeto Funcion con la informacion de la funcion a ingresar.
        '''
        # si no tiene error en los  argumentos se agrega a talba
        if not(isinstance(funcion.argumentosTipos, str)):
            if(nombre in pilaFuncion[-1].keys()):
                return Error('Esta funcion ya existe')
            else:
                pilaFuncion[-1][nombre] = copy.deepcopy(funcion)

            """
            print(f'''
                    # Pila funciones
                    {pilaFuncion}
                    ''')
            """

    def procesarParametros(self, parametros):
        '''
        Funcion para procesar parametros, valida si tiene de parametro void
        no puede ir acompañado de mas tipos.

        Parametros
        - parametros: lista de nodos tipo parameter
        '''
        parametrosList = []

        # revisa si contiene de parametros void, no puede ir acompañado de más tipos
        if (parametros[0].getText() == 'void'):
            if (len(parametros) == 1):
                return None, parametrosList
            else:
                return Error('parametro void no puede ir acompañado de mas parametros'), []

        for i in parametros:
            nombre = i.id_tok().getText()
            tipo = i.parameterType().getText()

            # Se agregan parametros a la tabla del ambito de esta funcion
            declaracionTemp = self.agregarVariableAmbitoTemp(
                nombre, Variable(tipo))
            if (isinstance(declaracionTemp, Error)):
                return declaracionTemp, parametrosList

            parametrosList.append(tipo)

        return None, parametrosList

    def enterMethodDec(self, ctx: decafParser.MethodDecContext):
        global funcionTemp
        global funcionNombreTemp
        tipo = ctx.methodType().getText()
        nombre = ctx.id_tok().getText()
        parametros = []

        if(len(ctx.parameter()) > 0):
            # Hay parametros
            errorPara, parametros = self.procesarParametros(ctx.parameter())

            if (isinstance(errorPara, Error)):
                # hay error
                print(
                    f"Error en declaracion de funcion linea {ctx.start.line}: {errorPara.mensaje}")

        funcionTemp = copy.deepcopy(Funcion(tipo, parametros))
        funcionNombreTemp = nombre

    def enterReturnStmt(self, ctx: decafParser.ReturnStmtContext):
        global procesandoReturnExp
        procesandoReturnExp = True

    def enterIntLiteral(self, ctx: decafParser.IntLiteralContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('int')

        if (procesandoArrayExp):
            expressionArrayTemp.append('int')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('int')

    def enterCharLiteral(self, ctx: decafParser.CharLiteralContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('char')

        if (procesandoArrayExp):
            expressionArrayTemp.append('char')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('char')

    def enterBoolLiteral(self, ctx: decafParser.BoolLiteralContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('boolean')

        if (procesandoArrayExp):
            expressionArrayTemp.append('boolean')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('boolean')

    # TODO expression con arrayLocationDot
    def enterArrayLocationDot(self, ctx: decafParser.ArrayLocationDotContext):
        # print('enterArrayLocationDot')

        nodosHijos = list(ctx.getChildren())
        for i in range(len(nodosHijos)):
            #print(f'{nodosHijos[i].getText()} = {type(nodosHijos[i])}')
            if (isinstance(nodosHijos[i], decafParser.IdDecContext)):
                # print(nodosHijos[i].getText())
                pass

            elif (isinstance(nodosHijos[i], decafParser.IdLocationContext)):
                # print('Solo')
                # print(nodosHijos[i].getText())
                pass

            elif (isinstance(nodosHijos[i], decafParser.IdLocationDotContext)):
                # print('Doble')  # a.b
                # print(nodosHijos[i].getText())
                pass

            try:
                if(nodosHijos[i + 1].getText() == '['):
                    #print('Es array ^')
                    pass
            except:
                pass

    def enterIdLocationDot(self, ctx: decafParser.IdLocationDotContext):
        global procesandoLocation
        global locationList
        global idLocationTemp

        procesandoLocation = True
        nodosHijos = list(ctx.getChildren())

        for i in range(len(nodosHijos)):
            if (isinstance(nodosHijos[i], decafParser.IdDecContext)):
                tipoTemp = getidLocationType(
                    nodosHijos[i].getText(), pilaVariable)
                if (len(locationList) == 0):
                    if (isinstance(tipoTemp, Error)):
                        print(
                            f"Error en llamada de variable linea {ctx.start.line}: {tipoTemp.mensaje}")
                        locationList.append('err')
                    else:
                        locationList.append(Variable(tipoTemp))
                else:
                    locationList.append(Variable(nodosHijos[i].getText()))
            elif (isinstance(nodosHijos[i], decafParser.IdLocationContext)):
                idLocationTemp = Variable(nodosHijos[i].getText())

    def exitIdLocationDot(self, ctx: decafParser.IdLocationDotContext):
        global procesandoLocation
        global locationList
        global idLocationTemp

        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArgExp
        global expressionArgTemp

        """
        print(f'''
        exitIdLocationDot
        procesandoLocation = {procesandoLocation}
        locationList = {locationList}
        idLocationTemp = {idLocationTemp}
        ''')
        """

        # validar idLocation y obtener tipo
        tipoTemp = getLocationDotType(
            pilaEstructura[-1], locationList, idLocationTemp)

        if (procesandoReturnExp):
            if (isinstance(tipoTemp, Error)):
                print(
                    f"Error en llamada de variable linea {ctx.start.line}: {tipoTemp.mensaje}")
                expressionReturnTemp.append('err')
            else:
                # obtenemos el tipo
                #print('Se ' + str(tipoTemp))
                if (tipoTemp):
                    expressionReturnTemp.append(tipoTemp)

        if (procesandoArgExp):
            if (isinstance(tipoTemp, Error)):
                print(
                    f"Error en llamada de variable linea {ctx.start.line}: {tipoTemp.mensaje}")
                expressionArgTemp.append('err')
            else:
                # obtenemos el tipo
                #print('Se ' + str(tipoTemp))
                if (tipoTemp):
                    expressionArgTemp.append(tipoTemp)

        procesandoLocation = False
        locationList = []
        idLocationTemp = None

    def enterArrayLocation(self, ctx: decafParser.ArrayLocationContext):
        global procesandoArrayExp
        global expressionArrayTemp

        procesandoArrayExp = True

    def exitArrayLocation(self, ctx: decafParser.ArrayLocationContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp
        # TODO validar que no estemos procesando un idLocationDot o arrayLocationDot
        # se validan los tipos y se agregan en arrays correspondientes
        nombre = ctx.id_tok().getText()
        expType = procesarExp(expressionArrayTemp)
        tipo = getArrayLocationType(nombre, pilaVariable, expType)

        if (procesandoReturnExp):
            if (isinstance(tipo, Error)):
                print(
                    f"Error en llamada de array linea {ctx.start.line}: {tipo.mensaje}")
                expressionReturnTemp.append('err')
            else:
                expressionReturnTemp.append(tipo)

        procesandoArrayExp = False
        expressionArrayTemp = []

    def enterIdLocation(self, ctx: decafParser.IdLocationContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoLocation

        global procesandoArgExp
        global expressionArgTemp

        # TODO validar que no estemos procesando un idLocationDot o arrayLocationDot
        if (procesandoLocation):
            return

        tipo = getidLocationType(ctx.id_tok().getText(), pilaVariable)

        if (procesandoArrayExp):
            if (isinstance(tipo, Error)):
                print(
                    f"Error en llamada de variable linea {ctx.start.line}: {tipo.mensaje}")
                expressionArrayTemp.append('err')
            else:
                expressionArrayTemp.append(tipo)

        elif (procesandoReturnExp):
            if (isinstance(tipo, Error)):
                print(
                    f"Error en llamada de variable linea {ctx.start.line}: {tipo.mensaje}")
                expressionReturnTemp.append('err')
            else:
                expressionReturnTemp.append(tipo)

        if (procesandoArgExp):
            if (isinstance(tipo, Error)):
                print(
                    f"Error en llamada de variable linea {ctx.start.line}: {tipo.mensaje}")
                expressionArgTemp.append('err')
            else:
                expressionArgTemp.append(tipo)

    def enterIfStmt(self, ctx: decafParser.IfStmtContext):
        global procesandoReturnExp
        procesandoReturnExp = True

    def enterWhileStmt(self, ctx: decafParser.WhileStmtContext):
        global procesandoReturnExp
        procesandoReturnExp = True

    def enterMethodCallDec(self, ctx: decafParser.MethodCallDecContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global controlCantidadParam
        global procesandoArgExp
        global expressionArgTemp
        global listaTiposArg

        tipo = getMethodType(ctx.id_tok().getText(), pilaFuncion)

        if (procesandoArrayExp):
            if (isinstance(tipo, Error)):
                print(
                    f"Error en llamada de funcion linea {ctx.start.line}: {tipo.mensaje}")
                expressionArrayTemp.append('err')
            else:
                if (tipo == 'void'):
                    print(
                        f"Error en llamada de funcion linea {ctx.start.line}: No se puede usar funcion void en exp")
                expressionArrayTemp.append(tipo)

        elif (procesandoReturnExp):
            if (isinstance(tipo, Error)):
                print(
                    f"Error en llamada de funcion linea {ctx.start.line}: {tipo.mensaje}")
                expressionReturnTemp.append('err')
            else:
                if (tipo == 'void'):
                    print(
                        f"Error en llamada de funcion linea {ctx.start.line}: No se puede usar funcion void en exp")
                expressionReturnTemp.append(tipo)

        # validar cantidad de parametros
        if (isinstance(tipo, Error)):
            print(
                f"Error en llamada de funcion linea {ctx.start.line}: {tipo.mensaje}")
            return
        else:
            #print(f'Llamada {ctx.start.line}')
            errParametros = self.validarCantidadParametrosFunc(
                ctx.id_tok().getText(), ctx.getChildren())
            if(isinstance(errParametros, Error)):
                print(
                    f"Error en llamada de funcion linea {ctx.start.line}: {errParametros.mensaje}")
            else:
                # iniciar el proceso de tipos de argumentos
                controlCantidadParam = True
                procesandoArgExp = True
                listaTiposArg = []

    def enterArgDec(self, ctx: decafParser.ArgDecContext):
        global expressionArgTemp
        expressionArgTemp = []

    def exitArgDec(self, ctx: decafParser.ArgDecContext):
        global listaTiposArg
        global expressionArgTemp

        listaTiposArg.append(procesarExp(expressionArgTemp))
        expressionArgTemp = []

    def exitMethodCallDec(self, ctx: decafParser.MethodCallDecContext):
        global controlCantidadParam
        global procesandoArgExp
        global expressionArgTemp
        global listaTiposArg

        if (controlCantidadParam):
            # Si tienen la misma cantidad de param
            # validar tipos
            #print(f'{ctx.start.line}: listaTiposArg = {listaTiposArg}')
            err = validarTiposArgumentos(
                ctx.id_tok().getText(), listaTiposArg, pilaFuncion)
            if (isinstance(err, Error)):
                print(
                    f"Error en llamada de funcion linea {ctx.start.line}: {err.mensaje}")

        controlCantidadParam = False
        procesandoArgExp = False
        expressionArgTemp = []
        listaTiposArg = []

    def enterNegativeExpr(self, ctx: decafParser.NegativeExprContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('negative')

        if (procesandoArrayExp):
            expressionArrayTemp.append('negative')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('negative')

    def enterNotExpr(self, ctx: decafParser.NotExprContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('not')

        if (procesandoArrayExp):
            expressionArrayTemp.append('not')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('not')

    def enterFirstArithExpr(self, ctx: decafParser.FirstArithExprContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('intOp')

        if (procesandoArrayExp):
            expressionArrayTemp.append('intOp')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('intOp')

    def enterSecondArithExpr(self, ctx: decafParser.SecondArithExprContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('intOp')

        if (procesandoArrayExp):
            expressionArrayTemp.append('intOp')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('intOp')

    def enterRelExpr(self, ctx: decafParser.RelExprContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('relOp')

        if (procesandoArrayExp):
            expressionArrayTemp.append('relOp')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('relOp')

    def enterEqExpr(self, ctx: decafParser.EqExprContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('eqOp')

        if (procesandoArrayExp):
            expressionArrayTemp.append('eqOp')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('eqOp')

    def enterCondExpr(self, ctx: decafParser.CondExprContext):
        global procesandoReturnExp
        global expressionReturnTemp

        global procesandoArrayExp
        global expressionArrayTemp

        global procesandoArgExp
        global expressionArgTemp

        if (procesandoArgExp):
            expressionArgTemp.append('boolOp')

        if (procesandoArrayExp):
            expressionArrayTemp.append('boolOp')

        elif (procesandoReturnExp):
            expressionReturnTemp.append('boolOp')

    def exitReturnStmt(self, ctx: decafParser.ReturnStmtContext):
        global procesandoReturnExp
        global funcionTemp
        global expressionReturnTemp
        """
        print(f'''
        -----
        exitReturnStatement {ctx.start.line}
        -----
        expressionReturnTemp {expressionReturnTemp}
        ''')
        """
        funcionTemp.agregarReturn(procesarExp(expressionReturnTemp))
        expressionReturnTemp = []
        procesandoReturnExp = False

    def exitMethodDec(self, ctx: decafParser.MethodDecContext):
        global funcionTemp
        global funcionNombreTemp
        global procesandoReturnExp
        global expressionReturnTemp

        funcionTemp.validar()
        if (isinstance(funcionTemp.err, Error)):
            # si hay error en definicion de funcion
            print(
                f"Error en declaracion de funcion linea {ctx.start.line}: {funcionTemp.err.mensaje}")
        else:
            # si no hay error se agrega a tabla
            err = self.agregarFuncionATabla(funcionNombreTemp, funcionTemp)
            if (isinstance(err, Error)):
                print(
                    f"Error en declaracion de funcion linea {ctx.start.line}: {err.mensaje}")

        funcionTemp = None
        funcionNombreTemp = None

    def enterVarDec(self, ctx: decafParser.VarDecContext):
        # es la declaracion de una variable
        nombre = ctx.id_tok().getText()
        tipo = ctx.varType().getText()
        estructura = False

        if (tipo.find('struct') != -1):
            # es de tipo estructura
            tipo = tipo.replace('struct', '')

            # validar si existe la estructura
            estructError = self.validarEstructura(tipo)
            if (isinstance(estructError, Error)):
                print(
                    f"Error en declaracion de variable linea {ctx.start.line}: {estructError.mensaje}")
            else:
                estructura = True

        declaracionTemp = self.agregarVariableATabla(
            nombre, Variable(tipo, isEstructura=estructura))
        if(isinstance(declaracionTemp, Error)):
            print(
                f"Error en declaracion de variable linea {ctx.start.line}: {declaracionTemp.mensaje}")

    def enterArrayDec(self, ctx: decafParser.ArrayDecContext):
        # es la declaracion de un array
        long = int(ctx.children[3].getText())
        if(long <= 0):
            print(
                f"Error en declaracion de array linea {ctx.start.line}: la dimension debe ser mayor a 0")
        else:
            nombre = ctx.id_tok().getText()
            tipo = ctx.varType().getText()
            estructura = False

            if (tipo.find('struct') != -1):
                # es de tipo estructura
                tipo = tipo.replace('struct', '')

                # validar si existe la estructura
                estructError = self.validarEstructura(tipo)
                if (isinstance(estructError, Error)):
                    print(
                        f"Error en declaracion de variable linea {ctx.start.line}: {estructError.mensaje}")
                else:
                    estructura = True

            declaracionTemp = self.agregarVariableATabla(
                nombre, Variable(tipo, long=long, isEstructura=estructura))
            if(isinstance(declaracionTemp, Error)):
                print(
                    f"Error en declaracion de variable linea {ctx.start.line}: {declaracionTemp.mensaje}")

    def enterProgramStart(self, ctx: decafParser.ProgramStartContext):
        # Se crea el ambito global
        self.agregarAmbito()
        pilaFuncion.append({})
        pilaEstructura.append({})

    def enterStructDec(self, ctx: decafParser.StructDecContext):
        self.agregarAmbito()

    def exitStructDec(self, ctx: decafParser.StructDecContext):
        # pasar este ambito a las propiedades de la estructura
        nombre = ctx.id_tok().getText()
        structErr = self.agregarStructATabla(nombre, Estructura(
            copy.deepcopy(pilaVariable[-1])))
        if (isinstance(structErr, Error)):
            print(
                f"Error en declaracion de estructura linea {ctx.start.line}: {structErr.mensaje}")
        self.quitarAmbito()

    def enterBlockDec(self, ctx: decafParser.BlockDecContext):
        global procesandoReturnExp
        global expressionReturnTemp

        if (procesandoReturnExp):
            # sabemos que estamos procesando una Exp de if o while

            # Evaluamos que el tipo de dato sea boolean
            if not(procesarExp(expressionReturnTemp) == 'boolean'):
                print(
                    f"Error en exp condicional {ctx.parentCtx.start.line}: No es de tipo 'boolean'")

            expressionReturnTemp = []
            procesandoReturnExp = False

        self.agregarAmbito()
        if (len(ambitoVariableTemp) > 0):
            self.agregarAmbitoTempATabla()

    def exitBlockDec(self, ctx: decafParser.BlockDecContext):
        self.quitarAmbito()

    def exitProgramStart(self, ctx: decafParser.ProgramStartContext):
        # este metodo se ejecuta al salir del ultimo nodo del arbol
        reglaMain = self.validarReglaMain()
        if (isinstance(reglaMain, Error)):
            print(
                f"Error en linea {ctx.start.line}: {reglaMain.mensaje}")


def main():
    # print("Listo")
    data = open('./decafPrograms/multiple_tests.txt').read()
    #data = open('./decafPrograms/hello_world.txt').read()
    #data = open('./decafPrograms/param.txt').read()
    #data = open('./decafPrograms/scope.txt').read()
    #data = open('./decafPrograms/structs.txt').read()

    lexer = decafLexer(InputStream(data))
    stream = CommonTokenStream(lexer)
    parser = decafParser(stream)
    tree = parser.start()

    printer = DecafPrinter()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

    # traverse(tree, parser.ruleNames)

    # print(tree.getText())
    # print(tree.getRuleIndex())
    # print(parser.ruleNames)

    # print(tree.getChild(1))

    # print(tree.getToken(3, 0))
    # print(tree.getTokens(3))

    print()


if __name__ == '__main__':
    main()
