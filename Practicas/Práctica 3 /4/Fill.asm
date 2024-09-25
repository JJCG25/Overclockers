(RESTART)
@SCREEN
D=A
@0
M=D    // Se guarda la dirección de memoria inicial de la pantalla (RAM[16384]) en RAM[0]

// KBDCHECK: bucle para verificar si se presiona una tecla
(KBDCHECK)
@KBD
D=M    // Carga el valor de la dirección del teclado (RAM[24576]) en D.
// Si se presiona una tecla, RAM[24576] contiene un valor positivo.
// Si no se presiona ninguna tecla, RAM[24576] = 0.

@BLACK
D;JGT  // Si una tecla es presionada D > 0, salta a BLACK.

@WHITE
D;JEQ  // Si ninguna tecla es presionada D == 0, salta a WHITE.

@KBDCHECK
0;JMP  // Si no se cumple ninguna condición anterior, vuelve a KBDCHECK.

// BLACK: para pintar la pantalla de negro
(BLACK)
@1
M=-1   // Guarda en RAM[1] el valor -1, color negro

@CHANGE
0;JMP  // Salta a CHANGE, donde se aplica el color a la pantalla.


// WHITE: para pintar la pantalla de blanco
(WHITE)
@1
M=0    // Guarda en RAM[1] el valor 0, color blanco
@CHANGE
0;JMP  // Salta a CHANGE, donde se aplica el color a la pantalla.


// CHANGE: para aplicar el color en cada píxel de la pantalla
(CHANGE)
@1
D=M    // Carga en D el valor a aplicar, blanco o negro.

@0
A=M    // Obtiene la dirección de memoria actual de la pantalla desde RAM[0].
M=D    // Escribe el valor de D (color) en la dirección de memoria del píxel.

@0
M=M+1  // Incrementa RAM[0] para apuntar al siguiente píxel.

@24576
D=A
@0
D=D-M  // Calcula la diferencia entre la dirección de memoria del teclado (24576) y el siguiente píxel.

@CHANGE
D;JGT  // Si D > 0, todavía quedan píxeles por rellenar, por lo que vuelve a pintar el siguiente píxel.

// RESTART: vuelve al inicio para seguir verificando el teclado

@RESTART
0;JMP  // Reinicia el ciclo desde el inicio para seguir verificando el estado del teclado.
