class Cuadrupla:

    def __init__(self, op=None, arg1=None, arg2=None, resultado=None, tab=0):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.resultado = resultado
        self.tab = tab

    def representacion(self):
        tab = '    '
        if(self.op == '='):
            return f"{tab*self.tab}{self.resultado} = {self.arg1}"
        elif(self.op == 'FUNCTION' or self.op == 'END FUNCTION'):
            return f"{tab*self.tab}{self.op} {self.arg1}:"

        return f"{tab*self.tab}{self.resultado} = {self.arg1} {self.op} {self.arg2}"

    def __repr__(self):
        return self.representacion()


if __name__ == '__main__':
    print(Cuadrupla(op='FUNCTION', arg1='main'))
    print(Cuadrupla(op='+', arg1='fp[0]', arg2='fp[4]', resultado='t0', tab=1))
    print(Cuadrupla(op='=', arg1='t1', resultado='G[0]', tab=1))
    print(Cuadrupla(op='END FUNCTION', arg1='main'))
