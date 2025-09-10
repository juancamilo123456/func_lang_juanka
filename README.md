funcland    mini lenguaje interpretado

Descripción breve:
Programa que lee un archivo de texto con definiciones de funciones y sentencias print, valida el contenido y ejecuta las expresiones.

Cómo ejecutar:
python funcland.py                 # hace que se lea  por defecto 'codigo.txt'
python funcland.py codigo_error.txt

Archivos del repositorio:
funcland.py                 Interprete (lexer, parser, evaluador)
codigo.txt                  Ejemplo correcto
codigo_error.txt            Ejemplos con error
funclan_informe_juan_camilo.md  Informe sencillo del trabajo
README.md                   Este archivo

Gramática:
<programa> ::= { <definicion_funcion> } { <print> }
<definicion_funcion> ::= func <id>( <param_list> ) = <expr> ;
<print> ::= print <llamada_funcion> ;
<param_list> ::= <id> { , <id> } | ε
<llamada_funcion> ::= <id>( <arg_list> )
<arg_list> ::= <expr> { , <expr> } | ε
<expr> ::= <term> { (+|-) <term> }*
<term> ::= <factor> { (*|/) <factor> }*
<factor> ::= <number> | <id> | ( <expr> ) | <llamada_funcion> | <factor> ^ <factor>

Tokens reconocidos:
func, print, identificadores, números, + - * / ^, paréntesis, coma, punto y coma, =

Reglas de validación:
1) Símbolo desconocido: error léxico con línea y columna.
2) Estructura inválida o paréntesis desbalanceados: error sintáctico.
3) Función usada sin estar definida antes: error semántico.
4) Cantidad de parámetros incorrecta: error semántico.
5) División por cero en ejecución: error en tiempo de ejecución.

Ejemplo correcto (archivo codigo.txt):
func suma(a, b) = a + b;
func cuadrado(x) = x * x;
func potencia(x, y) = x ^ y;
print suma(4, 5);
print cuadrado(3);
print potencia(2, 4);
print potencia(3, suma(2,2));

Salida esperada:
9
9
16
81

Ejemplo con errores (archivo codigo_error.txt):
func mult(a, b) = a * b;
print mult(5);
print potencia(2,3);

Salida esperada:
Error: número incorrecto de parámetros en mult (esperado 2, recibido 1)
Error: función no definida 'potencia'
