; rt_print_num16
; Prints signed 16-bit integer in AX using DOS teletype (AH=02h)
; Inputs:
;   AX = value to print (signed)
; Preserves:
;   BX, CX, DX, SI (saved/restored); DS, ES, BP, SP not modified
; Clobbers:
;   AX (scratch during routine), FLAGS
;
; Note: prints '-' for negative, handles 0, and divides repeatedly by 10,
;       pushing remainders to stack, then outputs digits in correct order.

global rt_print_num16
rt_print_num16:
    push bx
    push cx
    push dx
    push si

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
    mov si, 10
.convert:
    xor dx, dx         ; DX:AX / SI
    mov ax, bx
    div si             ; unsigned divide since BX >= 0 here; AX=quotient, DX=remainder
    mov bx, ax         ; next value = quotient
    push dx            ; push remainder (0..9)
    inc cx
    cmp bx, 0
    jne .convert

.print:
    ; pop digits and print
    cmp cx, 0
    je .done
    pop dx            ; DL = digit
    add dl, '0'
    mov ah, 0x02
    int 0x21
    dec cx
    jmp .print

.done:
    pop si
    pop dx
    pop cx
    pop bx
    ret
