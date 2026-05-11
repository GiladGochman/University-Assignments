#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <linux/limits.h>
#include "LineParser.h"

#define TERMINATED  -1
#define RUNNING 1
#define SUSPENDED 0

typedef struct process{
    cmdLine* cmd;         /* the parsed command line*/
    pid_t pid; 		      /* the process id that is running the command*/
    int status;           /* status of the process: RUNNING/SUSPENDED/TERMINATED */
    struct process *next  /* next process in chain */
} process;

//functions declerations
void addProcess(process** process_list, cmdLine* cmd, pid_t pid);
void printProcessList(process** process_list);


// process* list_append(process* process_list, cmdLine *cmd, pid_t pid) {
//     process* newProcess = (process*)malloc(sizeof(process));
//     if (newProcess == NULL) {
//         perror("Failed to allocate memory for new process");
//         return process_list; // Return original list on failure
//     }
//     newProcess->cmd = cmd;
//     newProcess->pid = pid;
//     newProcess->status = RUNNING;
//     newProcess->next = NULL;

//     if (process_list == NULL) {
//         return newProcess; // Return new node if list is empty
//     }

//     process* last = process_list;
//     while (last->next != NULL) {
//         last = last->next;
//     }
//     last->next = newProcess;
//     return process_list; // Return updated list
// }

void addProcess(process **process_list, cmdLine *cmd, pid_t pid) {
    process* newProcess = (process*)malloc(sizeof(process));
    if (newProcess == NULL) {
        perror("Failed to allocate memory for new process");
        exit(EXIT_FAILURE);
    }
    newProcess->cmd = cmd;
    newProcess->pid = pid;
    newProcess->status = RUNNING;
    newProcess->next = *process_list;

    *process_list = newProcess;
}


void printProcessList(process **process_list) {
    int index = 0;
    process* current = *process_list;

    while (current != NULL) {
        printf("index: %d\n", index);
        printf("PID: %d\n", current->pid);
        printf("STATUS: %d\n", current->status);
        printf("Command: %s\n", current->cmd->arguments[0]);

        current = current->next;
        index++;
    }

    printf("Number of processes: %d\n", index);
}



// void freeCmdLine(cmdLine *pCmdLine) {
//     while (pCmdLine != NULL) {
//         for (int i = 0; i < pCmdLine->argCount; i++) {
//             if (pCmdLine->arguments[i] != NULL) {
//                 free(pCmdLine->arguments[i]);
//             }
//         }

//         if (pCmdLine->inputRedirect != NULL) {
//             free((char *)pCmdLine->inputRedirect);
//         }

//         if (pCmdLine->outputRedirect != NULL) {
//             free((char *)pCmdLine->outputRedirect);
//         }

//         cmdLine *nextCmdLine = pCmdLine->next;

//         free(pCmdLine);
//         free(process_list);

//         pCmdLine = nextCmdLine;
//     }
// }

void freeCmdLine(cmdLine *pCmdLine) {
    while (pCmdLine != NULL) {
        for (int i = 0; i < pCmdLine->argCount; i++) {
            if (pCmdLine->arguments[i] != NULL) {
                free(pCmdLine->arguments[i]);
            }
        }

        if (pCmdLine->inputRedirect != NULL) {
            free((char *)pCmdLine->inputRedirect);
        }

        if (pCmdLine->outputRedirect != NULL) {
            free((char *)pCmdLine->outputRedirect);
        }

        cmdLine *nextCmdLine = pCmdLine->next;
        free(pCmdLine); // Free the command line structure itself

        pCmdLine = nextCmdLine;
    }

}

void freeProcessList (process *process_list){
      // Free the process list
    process* current = process_list;
    while (current != NULL) {
        process* next = current->next;
        free(current);
        current = next;
    }
    process_list = NULL; // Reset the process list pointer
}


void execute2childs(cmdLine *pCmdLine1, cmdLine *pCmdLine2, process *process_list) {
    int fd[2];
    pid_t pid;

    // Create the pipe
    if (pipe(fd) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }

    // Fork the first child process
    pid = fork();
    if (pid == -1) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) {
        // Child 1 process: Set up input redirection and pipe to Child 2
        if (pCmdLine1->inputRedirect != NULL) {
            freopen(pCmdLine1->inputRedirect, "r", stdin);
        }

        close(fd[0]); // Close unused read end
        dup2(fd[1], STDOUT_FILENO); // Redirect stdout to pipe
        close(fd[1]); // Close original write end

        if (execvp(pCmdLine1->arguments[0], pCmdLine1->arguments) == -1) {
            perror("execvp");
            exit(EXIT_FAILURE);
        }
    } else {
        // Fork the second child process
        pid_t pid2 = fork();
        if (pid2 == -1) {
            perror("fork");
            exit(EXIT_FAILURE);
        }

        if (pid2 == 0) {
            // Child 2 process: Set up pipe from Child 1 and output redirection
            if (pCmdLine2->outputRedirect != NULL) {
                freopen(pCmdLine2->outputRedirect, "w", stdout);
            }

            close(fd[1]); // Close unused write end
            dup2(fd[0], STDIN_FILENO); // Redirect stdin from pipe
            close(fd[0]); // Close original read end

            if (execvp(pCmdLine2->arguments[0], pCmdLine2->arguments) == -1) {
                perror("execvp");
                exit(EXIT_FAILURE);
            }
        } else {
            // Parent process: Close pipe and wait for both children to finish
            addProcess(&process_list, pCmdLine1, pid);
            close(fd[0]);
            close(fd[1]);
            waitpid(pid, NULL, 0);
            waitpid(pid2, NULL, 0);
        }
    }
}


void execute(cmdLine *pCmdLine, char* buffer, process *process_list) {
    char *pipe_pos = strchr(buffer, '|');

    if(pipe_pos != NULL) {
        // Calculate the length of the command before and after the pipe
        size_t before_pipe_len = pipe_pos - buffer;

        // Allocate memory for the two commands (+1 for the null terminator)
        char *before_pipe = (char *)malloc(before_pipe_len + 1);

        if (before_pipe == NULL) {
            fprintf(stderr, "Error: Memory allocation failed.\n");
            return;
        }


        // Copy the parts into the new strings
        strncpy(before_pipe, buffer, before_pipe_len);
        before_pipe[before_pipe_len] = '\0';  // Null-terminate the string

        char * index = pipe_pos + 1;
        while(strncmp(index, " ", 1) == 0){
            index++;
        }

        size_t after_pipe_len = strlen(index + 1);
        char *after_pipe = (char *)malloc(after_pipe_len + 1);

         if (after_pipe == NULL) {
            fprintf(stderr, "Error: Memory allocation failed.\n");
            return;
        }

        strcpy(after_pipe, index);  // Skip the '|' character and copy the rest
        while (*after_pipe == ' ') after_pipe++;  // Skip leading spaces in after_pipe
        

        cmdLine *pCmdLine1 = parseCmdLines(before_pipe);
        cmdLine *pCmdLine2 = parseCmdLines(after_pipe);

        execute2childs(pCmdLine1, pCmdLine2, process_list);

        // Free allocated memory
        freeCmdLine(pCmdLine1);
        freeCmdLine(pCmdLine2);
        free(before_pipe);
        free(after_pipe);

    } else {
        // Normal execution without pipe
        pid_t pid = fork();  // Create a new process

        if (pid == -1) {
            perror("Error forking");
            exit(1);
        } else if (pid == 0) {
            // In the child process
            fprintf(stderr, "PID: %d Executing command: %s \n", pid, buffer); //task1a

            //task3
            if(pCmdLine->inputRedirect != NULL){
                freopen(pCmdLine->inputRedirect, "r", stdin);
            }

            if(pCmdLine->outputRedirect != NULL){
                freopen(pCmdLine->outputRedirect, "w", stdout);
            }

            if (execvp(pCmdLine->arguments[0], pCmdLine->arguments) == -1) {// I checked in the Internet what are execv's arguments
                perror("Error executing command");
                exit(1);
            }

        } else {
            // In the parent process
            addProcess(&process_list, pCmdLine, pid);
            if(pCmdLine->blocking == 1){
                waitpid(pid, NULL, 0);  // Wait for the child process to complete, task1b
            }
        }
    }

    freeCmdLine(pCmdLine);
}



int debug(int argc, char *argv[]){

    int debug_mode = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-d") == 0) {
            debug_mode = 1; // Turn on debug mode
            break;
        } 
    }

    return debug_mode;

}

int main(int argc, char *argv[]) {

	int max_input_size = 2048;
    char cwd[PATH_MAX];
	char buffer[max_input_size];
    int debug_mode = debug(argc, argv);

    process *process_list = NULL;

    while(strcmp(buffer, "quit\n") != 0){

        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            printf("Current working directory: %s\n", cwd);
            } else {
                perror("getcwd() error");
            }

        if (fgets(buffer, max_input_size, stdin) != NULL) {
		    cmdLine *parsedLine = parseCmdLines(buffer);
            if(strcmp(parsedLine ->arguments[0], "cd") == 0){//task1c
                if(chdir(parsedLine->arguments[1]) == -1){
                    fprintf(stderr, "cd operation failed");
                }
            }else if(strcmp(parsedLine ->arguments[0], "alarm") == 0){//task2
                kill(atoi(parsedLine ->arguments[1]), SIGCONT);
            }else if(strcmp(parsedLine ->arguments[0], "blast") == 0){//task2
                kill(atoi(parsedLine ->arguments[1]), SIGINT);
            }else if(strcmp(parsedLine ->arguments[0], "procs") == 0){
                printf("got to procs!\n");
                printProcessList(&process_list);

            }else{
                execute(parsedLine, buffer, process_list);
            }
        } else {
            perror("fgets error");
        }

        if(debug_mode == 1){
            fprintf(stderr,"Debug: %s", buffer);
        }

    }

    freeProcessList (process_list);
    exit(0);    
    return 0;
}

