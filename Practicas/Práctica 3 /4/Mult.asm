// Inicializa R2 en 0
@R2
M=0  // R2 = 0, acumulador para almacenar la suma de R1 repetidamente

@R0
D=M  // Carga el valor de R0 en el registro D para comparar
@STEP
D;JGT  // Si R0 > 0, salta a STEP para realizar el bucle

// Si R0 <= 0, salta a END para detener la ejecución
@END
0;JMP

// Inicia el bucle de suma (STEP)
(STEP)
    @R2
    D=M  // Carga el valor actual de R2 en D
    @R1
    D=D+M  // Suma el valor de R1 al valor acumulado en D
    @R2
    M=D  // Guarda el resultado de la suma de R1 en el acumulador R2

    // Reduce el valor de R0 para controlar el número de iteraciones
    @R0
    D=M-1  
    M=D

    // Verifica si R0 > 0 para continuar el bucle saltando e STEP
    @STEP
    D;JGT

// Fin del programa (END)
(END)
    @END
    0;JMP  // Salta a END indefinidamente para detener la ejecución
