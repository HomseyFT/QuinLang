; Print signed 16-bit integer in AX using DOS teletype (AH=02h)
; Destroys AX,BX,CX,DX

global rt_print_num16
rt_print_num16:
    push bp
    mov bp, sp
    push bx
    push cx
    push dx

    mov bx, ax         ; value in BX for work
    cmp bx, 0
    jge .skip_neg
    ; print '-'
    mov dl, '-'
    mov ah, 0x02
    int 0x21
    neg bx
.skip_neg:
    ; convert to digits by pushing remainders on stack
    xor cx, cx         ; digit count
.convert:
    xor dx, dx
    mov ax, bx
    mov si, 10
    div si             ; AX=BX/10 DX=BX%10 (8086: use DIV with AX:DX/operand) but here BX fits in AX
    ; Correction: use DIV with AX by 10
    ; Using 16-bit unsigned division
    ; move quotient in bx, remainder in dx
    mov bx, ax
    push dx            ; push remainder
    inc cx
    cmp bx, 0
    jne .convert

.print:
    ; pop digits and print
    cmp cx, 0
    je .done
    pop dx
    add dl, '0'
    mov ah, 0x02
    int 0x21
    dec cx
    jmp .print

.done:
    pop dx
    pop cx
    pop bx
    mov sp, bp
    pop bp
    ret