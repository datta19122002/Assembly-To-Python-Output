


section .data 
    r1 dd 11
    r2 dd 16
    r3 db "datta"
section .bss
     

section .text
    global main
main:
    ABC 10, 20 
    mov edi, eax
    mov eax, esp
    mov eax, 21 
    mov edi, 10 
    mov esp, 12
    mov edi, edi
    xor eax, 10
    add eax, 10 
    add edi, edi
    add eax, eax 
    add eax, esp
    sub eax, esp 
    cmp edi, eax 
    or eax, eax 
    adc edi, eax 
    sbb eax, edi 
    xor edi, edi 
    mov edi, [eax+edi*8]
    mov [eax+edi*8], edi
    add edi, [eax+edi*8]
    add [eax+eax*4], eax
    sub edi, [eax+edi*8]
    sub [eax+eax*4], eax
    xor edi, [eax+edi*8]
    xor [eax+eax*4], eax
    cmp edi, [eax+edi*8]
    cmp [eax+eax*4], eax
    or edi, [eax+edi*8]
    or [eax+eax*4], eax
    adc edi, [eax+edi*8]
    adc [eax+eax*4], eax
    sbb edi, [eax+edi*8]
    sbb [eax+eax*4], eax
    inc eax
    inc ecx
    inc edx
    inc ebx
    inc edi
    dec eax
    dec ecx
    dec edx
    dec ebx
    dec edi
    sbb [eax+eax*4], eax
    sub [eax+eax*4], edi
