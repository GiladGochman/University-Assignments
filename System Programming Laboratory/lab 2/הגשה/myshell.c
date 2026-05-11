#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <limits.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
#include <signal.h>
#include <fcntl.h>
#include "LineParser.h"

void execute_command(cmdLine *cmd, _Bool debug)
{
    if (strcmp("cd", cmd->arguments[0]) == 0)
    {
        if (cmd->argCount < 2)
        {
            fprintf(stderr, "Missing argument for cd\n");
        }
        else
        {
            if (chdir(cmd->arguments[1]) != 0)
            {
                perror("cd failed");
            }
        }
        return;
    }

    if (strcmp("alarm", cmd->arguments[0]) == 0)
    {
        if (cmd->argCount < 2)
        {
            fprintf(stderr, "Missing argument for alarm\n");
        }
        else
        {
            pid_t pid = atoi(cmd->arguments[1]);
            if (kill(pid, SIGCONT) == 0)
            {
                printf("Process %d continued\n", pid);
            }
            else
            {
                perror("alarm failed");
            }
        }
        return;
    }

    if (strcmp("blast", cmd->arguments[0]) == 0)
    {
        if (cmd->argCount < 2)
        {
            fprintf(stderr, "Missing argument for blast\n");
        }
        else
        {
            pid_t pid = atoi(cmd->arguments[1]);
            if (kill(pid, SIGKILL) == 0)
            {
                printf("Process %d terminated\n", pid);
            }
            else
            {
                perror("blast failed");
            }
        }
        return;
    }

    pid_t pid = fork();

    if (pid == -1)
    {
        perror("fork failed");
        _exit(1);
    }

    if (pid == 0)
    {
        if (debug)
        {
            fprintf(stderr, "PID: %d\n", getpid());
            fprintf(stderr, "Executing command: %s\n", cmd->arguments[0]);
        }

        if (cmd->inputRedirect != NULL)
        {
            int input_fd = open(cmd->inputRedirect, O_RDONLY);
            if (input_fd == -1)
            {
                perror("open input file failed");
                _exit(1);
            }
            if (dup2(input_fd, STDIN_FILENO) == -1)
            {
                perror("dup2 input redirection failed");
                close(input_fd);
                _exit(1);
            }
            close(input_fd);
        }

        if (cmd->outputRedirect != NULL)
        {
            int output_fd = open(cmd->outputRedirect, O_WRONLY | O_CREAT | O_TRUNC, 0644);
            if (output_fd == -1)
            {
                perror("open output file failed");
                _exit(1);
            }
            if (dup2(output_fd, STDOUT_FILENO) == -1)
            {
                perror("dup2 output redirection failed");
                close(output_fd);
                _exit(1);
            }
            close(output_fd);
        }

        execvp(cmd->arguments[0], cmd->arguments);
        perror("execvp failed");
        _exit(1);
    }
    else
    {
        if (cmd->blocking)
        {
            int status;
            waitpid(pid, &status, 0);
        }
    }
}

int main(int argc, char **argv)
{
    char cwd[PATH_MAX];
    char input[2048];
    cmdLine *parsed_cmd;
    _Bool debug = 0;

    for (int i = 0; i < argc; i++)
    {
        if (strcmp(argv[i], "-d") == 0)
        {
            debug = 1;
            break;
        }
    }

    while (1)
    {
        if (getcwd(cwd, sizeof(cwd)) != NULL)
        {
            printf("%s> ", cwd);
        }
        else
        {
            perror("failed getcwd()");
            return 1;
        }

        if (fgets(input, sizeof(input), stdin) == NULL)
        {
            perror("something wrong with fgets()");
            break;
        }

        input[strcspn(input, "\n")] = 0;

        parsed_cmd = parseCmdLines(input);

        if (parsed_cmd == NULL)
            continue;

        if (strcmp(parsed_cmd->arguments[0], "quit") == 0)
        {
            freeCmdLines(parsed_cmd);
            break;
        }

        execute_command(parsed_cmd, debug);
        freeCmdLines(parsed_cmd);
    }

    return 0;
}
