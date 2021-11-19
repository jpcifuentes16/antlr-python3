class MIPS:

    def __init__(self):
        pass

    '''
        Etiquetas y saltos
    '''

    def construirGOTO(self, etiqueta):
        # hay varios tipos de jumps
        retorno = f"j {etiqueta}"
        pass

    def construirEtiqueta(self, etiqueta):
        print(f"{etiqueta}:")

    def construirIf(self, Rsrc, etiqueta):
        '''
            Bif. condicional si Rsrc es mayor que 0.
        '''
        retorno = f"bgtz {Rsrc}, {etiqueta}"
        pass

    '''
        Operaciones aritmeticas
    '''

    def construirMultiplicacion(self, Rdest, Rsrc1, Rsrc2):
        retorno = f"mul {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    def construirSuma(self, Rdest, Rsrc1, Rsrc2):
        retorno = f"add {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    def construirDivision(self, Rdest, Rsrc1, Rsrc2):
        retorno = f"div {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    def construirMenos(self, Rdest, Rsrc1):
        retorno = f"neg {Rdest}, {Rsrc1}"
        pass

    def construirResta(self, Rdest, Rsrc1, Rsrc2):
        retorno = f"sub {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    '''
        Operaciones logicas
    '''

    def construirNegacion(self, Rdest, Rsrc1):
        retorno = f"not {Rdest}, {Rsrc1}"
        pass

    def construirAnd(self, Rdest, Rsrc1, Rsrc2):
        retorno = f"and {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    def construirOr(self, Rdest, Rsrc1, Rsrc2):
        retorno = f"or {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    '''
        Operacion de comparacion
    '''

    def construirComparacionIgual(self, Rdest, Rsrc1, Rsrc2):
        '''
            Pone Rdest a 1 si Rsrc1 y Rsrc2 son iguales, en otro caso pone 0
        '''
        retorno = f"seq {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    def construirComparacionMayorIgual(self, Rdest, Rsrc1, Rsrc2):
        '''
            Pone Rdest a 1 si Rsrc1 es mayor o igual a Rsrc2,
            y 0 en otro caso (para números con signo).
        '''
        retorno = f"sge {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    def construirComparacionMayor(self, Rdest, Rsrc1, Rsrc2):
        '''
            Pone Rdest a 1 si Rsrc1 es mayor a Rsrc2,
            y 0 en otro caso (para números con signo).
        '''
        retorno = f"sgt {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    def construirComparacionMenorIgual(self, Rdest, Rsrc1, Rsrc2):
        '''
            Pone Rdest a 1 si Rsrc1 es menor o igual a Rsrc2,
            y 0 en otro caso (para números con signo).
        '''
        retorno = f"sle {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    def construirComparacionMenor(self, Rdest, Rsrc1, Rsrc2):
        '''
            Pone Rdest a 1 si Rsrc1 es menor a Rsrc2,
            y 0 en otro caso (para números con signo).
        '''
        retorno = f"slt {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    def construirComparacionNoIgual(self, Rdest, Rsrc1, Rsrc2):
        '''
            Pone Rdest to 1 si el registro Rsrc1 no es igual a Rsrc2
            y 0 en otro caso
        '''
        retorno = f"sne {Rdest}, {Rsrc1}, {Rsrc2}"
        pass

    '''
        Cargas
    '''

    def construirCarga(self, Rdest, Rsrc):
        '''
            TODO: preguntar como manejar este caso
            EJ: Rdest = Rsrc1
        '''
        retorno = f"move {Rdest}, {Rsrc}"
        pass

    '''
        Almacenamiento
    '''

    def construirAlmacenamiento(self, Rsrc, direccion):

        retorno = f"sw {Rsrc}, {direccion}"
        pass

    '''
        Funciones
    '''

    def construirLlamarFuncion(self, nombre, argumentos=[]):
        # TODO que pasa si hay mas argumentos?
        registrosArg = ['$a0', '$a1', '$a2', '$a3']
        retorno = ""
        for i in argumentos:
            retorno += f"move {registrosArg.pop(0)}, {i}"

        retorno = f"jal {nombre}"
        pass

    def construirRetorno(self, reg):
        retorno = f"move $v0, {reg}"
        retorno += "jr $ra"

    def construirRetornoSimple(self):
        print('\tjr $ra')

    def construirRetornoVoid(self):
        '''
            Transfiere el control de nuevo a la llamada de funcion
        '''
        retorno = "jr $ra"
        pass

    def constuirInputInt(self):
        print('''
\t# Se imprime mensaje al usuario
\tli $v0, 4
\tla $a0, mensajeInput
\tsyscall

\t# Se lee el input del usuario
\tli $v0,5
\tsyscall
\tjr $ra
        ''')

    def constuirOutputInt(self):
        print('''
\t# Se imprime numero en pantalla
\tli $v0, 1
\tsyscall

\t# Se hace un salto de linea
\tli $a0, saltoLinea
\tsyscall
\tjr $ra
        ''')

    '''
        Complementarias
    '''

    def encabezado(self, espacioGlobal):
        print(f'''
.data
.align 2
    G_: .space {espacioGlobal}
    mensajeInput: .asciiz "Ingrese un número entero: "
    saltoLinea: .asciiz "\n"
.text
        ''')

    def finPrograma(self):
        print('''
\t# fin del programa
\tli $v0, 10
\tsyscall
        ''')

    def generarCodigo(self, cuadruplas):
        funcionActual = ""
        for linea in cuadruplas:
            if linea.op == 'FUNCTION':
                self.construirEtiqueta(linea.arg1)
                funcionActual = linea.arg1
                if(linea.arg1 == 'InputInt'):
                    self.constuirInputInt()
                elif(linea.arg1 == 'OutputInt'):
                    self.constuirOutputInt()
            elif linea.op == 'RETURN':
                if (funcionActual == 'InputInt'):
                    self.construirRetornoSimple()

            elif linea.op == 'END FUNCTION':
                funcionActual = ""

            else:
                linea.debug()

    def __repr__(self):
        return f""
