section .data
    newline db 0x0A  ; newline character
section .text
global _start
global system_call
extern strlen
extern strncmp
 
_start:
    pop    dword ecx    ; ecx = argc
    mov    esi,esp      ; esi = argv
    ;; lea eax, [esi+4*ecx+4] ; eax = envp = (4*ecx)+esi+4
    mov     eax,ecx     ; put the number of arguments into eax
    shl     eax,2       ; compute the size of argv in bytes
    add     eax,esi     ; add the size to the address of argv 
    add     eax,4       ; skip NULL at the end of argv
    push    dword eax   ; char *envp[]
    push    dword esi   ; char* argv[]
    push    dword ecx   ; int argc

    call    main        ; int main( int argc, char *argv[], char *envp[] )

    mov     ebx,eax
    mov     eax,1
    int     0x80
    nop

main:

    ;argc
    mov edi, [esp + 4]
    ;argv
    mov esi, [esp + 8]
   

main_loop:
    ;length of argv[i]
    mov eax, [esi]  ;argv[0]
    push eax
    call strlen     ;eax = strlen(argv[i])

    ;print argv[i]
    mov edx, eax    ;str length
    mov eax, 4      
    mov ebx, 2      
    pop ecx         
    int 0x80        
    ;new line
    mov eax, 4      
    mov ebx, 2      
    mov ecx, newline    
    mov edx, 1      
    int 0x80        


loop_additions:
    add esi, 4      ;argv + 1
    dec edi
    jnz main_loop

        
system_call:
    push    ebp             ; Save caller state
    mov     ebp, esp
    sub     esp, 4          ; Leave space for local var on stack
    pushad                  ; Save some more caller state

    mov     eax, [ebp+8]    ; Copy function args to registers: leftmost...        
    mov     ebx, [ebp+12]   ; Next argument...
    mov     ecx, [ebp+16]   ; Next argument...
    mov     edx, [ebp+20]   ; Next argument...
    int     0x80            ; Transfer control to operating system
    mov     [ebp-4], eax    ; Save returned value...
    popad                   ; Restore caller state (registers)
    mov     eax, [ebp-4]    ; place returned value where caller can see it
    add     esp, 4          ; Restore caller state
    pop     ebp             ; Restore caller state
    ret                     ; Back to caller