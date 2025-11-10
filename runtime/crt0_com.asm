; .COM program CRT0: set DS=CS and call main, then exit via int 21h/4C00h

global start
extern main

start:
    ; Establish DS = CS
    push cs
    pop ds

    call main

    mov ax, 0x4C00
    int 0x21