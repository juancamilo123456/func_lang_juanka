Informe FuncLang (Parte 2 - Grupo B)

Objetivo
Implementar un mini lenguaje para definir y ejecutar funciones matematicas simples leidas desde un archivo de texto.

Diseño
El lexer reconoce: func, print, identificadores, numeros enteros, operadores + - * / ^, parentesis, coma, ; y =. Si aparece un simbolo raro, se informa linea y columna.

El parser es descendente recursivo y respeta precedencia: ^ es asociativo a la derecha; luego * y /; luego + y -. Se valida la gramatica indicada.
En semantica se exige que las funciones esten definidas antes de llamarlas, que la cantidad de parametros coincida y se marca redefinicion. Durante la evaluacion se detecta division por cero y uso de variable no definida.

La ejecucion guarda las funciones en una tabla simple y evalua expresiones sustituyendo parametros en un entorno local. Soporta recursion.

Errores detectados
Lexicos: simbolo desconocido con posicion.
Sintacticos: instruccion invalida o parentesis desbalanceados.
Semanticos tempranos: funcion no definida, aridad incorrecta, redefinicion.

De ejecucion: division por cero, variable no definida.

Uso
python funcland.py          (usa codigo.txt)
python funcland.py codigo_error.txt

Pruebas
Caso correcto:
suma(4,5) -> 9
cuadrado(3) -> 9
potencia(2,4) -> 16
potencia(3, suma(2,2)) -> 81
La salida del programa es: 9, 9, 16, 81 en lineas separadas.

Caso con errores:
mult definido con 2 parametros, pero se llama con 1 -> se reporta aridad incorrecta.

potencia no existe -> se reporta funcion no definida.

Decisiones y limites
Solo enteros en el lexer; la division devuelve real.
No hay variables globales; un identificador suelto solo puede ser parametro.

El parser intenta seguir despues de un error hasta el siguiente ';' para acumular mensajes.

Estructura
funcland.py (interprete), codigo.txt (ejemplo correcto), codigo_error.txt (ejemplos con error), README.md (guia).

Posibles mejoras
Unarios +/-, soporte de floats y algunas funciones internas como abs o max.
