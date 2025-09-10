FuncLang - mini lenguaje interpretado

Como ejecutar:
python funcland.py                 # lee 'codigo.txt' por defecto
python funcland.py codigo_error.txt

Gramatica (resumen):
<programa> ::= { <definicion_funcion> } { <print> }
<definicion_funcion> ::= func <id>( <param_list> ) = <expr> ;
<print> ::= print <llamada_funcion> ;
<param_list> ::= <id> { , <id> } | ε
<llamada_funcion> ::= <id>( <arg_list> )
<arg_list> ::= <expr> { , <expr> } | ε
<expr> ::= <term> { (+|-) <term> }*
<term> ::= <factor> { (*|/) <factor> }*
<factor> ::= <number> | <id> | ( <expr> ) | <llamada_funcion> | <factor> ^ <factor>

Tokens: func, print, identificadores, numeros, + - * / ^, parentesis, coma, punto y coma, =
Chequeos: simbolos desconocidos, parentesis desbalanceados, definiciones antes de uso, cantidad de parametros, division por cero en ejecucion.

Ejemplos: programa correcto en codigo.txt y ejemplos con error en codigo_error.txt.
