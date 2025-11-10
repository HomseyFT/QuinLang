; String routines for '$'-terminated strings in DS
; rt_print_str: DS:DX -> '$' string, prints via int 21h/AH=09h
; rt_str_cmp:  DS:SI and DS:DI -> compare, returns AX: -1 if s1<s2, 0 if equal, 1 if s1>s2

global rt_print_str
rt_print_str:
    push ax
    mov ah, 0x09
    int 0x21
    pop ax
    ret

; Compare strings byte by byte until '$' or difference
; Uses AL, BL as current chars
; Returns AX = -1/0/1

global rt_str_cmp
rt_str_cmp:
    push bx
.next_char:
    mov al, [si]
    mov bl, [di]
    cmp al, bl
    jne .diff
    cmp al, '$'
    je .equal
    inc si
    inc di
    jmp .next_char
.diff:
    ; Determine order with unsigned compare
    jb .less
    ja .greater
.equal:
    xor ax, ax
    jmp .done
.less:
    mov ax, -1
    jmp .done
.greater:
    mov ax, 1
.done:
    pop bx
    ret