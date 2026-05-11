#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <linux/limits.h>

int main() {
    int fd[2];
    pid_t pid;
    char buffer[1024];

    // Create the pipe
    if (pipe(fd) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }

    // Fork a child1 process
	fprintf(stderr, "parent_process forking\n");
    pid = fork();

    if (pid == -1) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) {
        // Child1 process
		fprintf(stderr, "child1 redirecting stdout to the write end of the pipe\n");
        close(STDOUT_FILENO); // Close unused read end
		int new_write = dup(fd[1]);
		close(fd[1]);
		fprintf(stderr, "child1 going to execute cmd\n");
		char *args[] = {"ls", "-l", NULL};
		if (execvp("ls", args) == -1) {
        // If execvp returns, an error occurred
        perror("execvp");
        }
        
    } else {
        // Parent process
		fprintf(stderr, "parent_process created process with id: %d\n", pid);
		fprintf(stderr, "parent_process waiting for child processes to terminate\n");
		waitpid(pid, NULL, 0);
		fprintf(stderr, "parent_process>closing the write end of the pipe\n");
        close(fd[1]); // Close unused write end
    }

	// Fork a child2 process
	pid_t pid2;
    pid2 = fork();

    if (pid2 == -1) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

	if(pid2==0){
		waitpid(pid, NULL, 0);
		fprintf(stderr, "child2 redirecting stdout to the write end of the pipe\n");
		close(STDIN_FILENO); // Close unused write end
		int new_read = dup(fd[0]);
		close(fd[0]);
		fprintf(stderr, "child2 going to execute cmd\n");
		char *args[] = {"tail", "-n", "2", NULL};
		if (execvp("tail", args) == -1) {
        // If execvp returns, an error occurred
        perror("execvp");
        }
	} else {
        // Parent process
		fprintf(stderr, "parent_process created process with id: %d\n", pid2);
		fprintf(stderr, "parent_process waiting for child processes to terminate\n");
		waitpid(pid2, NULL, 0);
		fprintf(stderr, "parent_process closing the read end of the pipe\n");
        close(fd[0]); // Close unused read end

    }

	fprintf(stderr, "parent_process exiting\n");
    return 0;
}