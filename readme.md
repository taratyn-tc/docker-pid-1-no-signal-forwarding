# Docker + Shell Pid 1 Signal Problem

When using a shell script as your entrypoint in a docker container, your shell script will not pass the signal on to your service.

For example:

```
❯ docker build -t $(basename $(pwd)):problem -f Dockerfile.problem  .
Sending build context to Docker daemon  44.03kB
Step 1/6 : FROM python:3.7.1
 ---> 1e80caffd59e
Step 2/6 : RUN mkdir /app
 ---> Using cache
 ---> 2f38f75b4855
Step 3/6 : WORKDIR /app
 ---> Using cache
 ---> 2fef8f852cf4
Step 4/6 : ADD "entrypoint.problem.sh" /app
 ---> Using cache
 ---> d2061a143fe1
Step 5/6 : ADD "main.py" /app
 ---> Using cache
 ---> c31535bea6ea
Step 6/6 : ENTRYPOINT ["sh", "entrypoint.problem.sh"]
 ---> Using cache
 ---> 7e98afa6bde0
Successfully built 7e98afa6bde0
❯ docker run --detach --name problem  $(basename $(pwd)):problem 
600d819f665260067c576dd6524113ae9daa2fda95bf8736f02360bd5e39aa52
❯ time docker stop problem                                      
problem
docker stop problem  0.03s user 0.02s system 0% cpu 10.226 total
```

This takes 10 seconds to run because the default time out for `docker stop` is a [10s](https://docs.docker.com/engine/reference/commandline/stop/#options).

## Simple fix: use exec

If the last line of your bash script simply starts the process you can use `exec`. `exec` is a shell command that replaces the current process with the command that follows `exec`. So, `python main.py` becomes `exec python main.py`.

Let's check if this solves the problem:

```
❯ docker build -t $(basename $(pwd)):exec -f Dockerfile.exec .            
Sending build context to Docker daemon  45.57kB
Step 1/6 : FROM python:3.7.1
 ---> 1e80caffd59e
Step 2/6 : RUN mkdir /app
 ---> Using cache
 ---> 2f38f75b4855
Step 3/6 : WORKDIR /app
 ---> Using cache
 ---> 2fef8f852cf4
Step 4/6 : ADD "entrypoint.exec.sh" /app
 ---> fff72ff53c43
Step 5/6 : ADD "main.py" /app
 ---> 09a22257bfa1
Step 6/6 : ENTRYPOINT ["sh", "entrypoint.exec.sh"]
 ---> Running in df55254b3aef
Removing intermediate container df55254b3aef
 ---> 03a23a350917
Successfully built 03a23a350917
Successfully tagged docker-pid-1-no-signal-forward:exec
❯ docker run --detach --name exec  $(basename $(pwd)):exec   
2a6240f88e92914fc9be02c19549c8c66360280abb5e4e3c1e46ffd9173f5575
❯ time docker stop exec                                   
exec
docker stop exec  0.02s user 0.01s system 3% cpu 1.285 total
```

Now, stop exits immediately despite the exact same python code running. The difference is that `entrypoint.exec.sh` the shell is _replaced_ with the python process instead of spawning a new child process. This means that our service becomes PID 1, and gets all the signals.

## More complicated fix: use trap

A more complicated solution would be to use `trap` to catch the signals in your shell script and use `kill` to send those signals to the correct process.
