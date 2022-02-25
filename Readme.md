# GDB image watch

## Setup

Some of the setup is specific to using these scripts in a docker container on MacOS. Running natively or in docker on Linux will be easier.

### XQuartz
XQuartz allows display of windows from a linux container on MacOS. 
1. Install XQuartz - an X.org X window system for MacOS. Logout and login required after install.
   - `brew install xquartz`

1. Change security settings
    - Launch XQuartz. 
    - Under the XQuartz menu, select Preferences
    - Go to the security tab and ensure "Allow connections from network clients" is checked.

1. Test. Run the following commands. You should see a Linux version of firefox running
    - Note: some instructions say to `xhost + 127.0.0.1`. This is not recommended.
```
xhost + $(hostname)
docker run -e DISPLAY=host.docker.internal:0 jess/firefox
```

1. The `DISPLAY` environment variable can be set in the docker compose file with this at the same level as `build`
```yml
    environment:
      - DISPLAY=host.docker.internal:0
```

### GDB Image watch
1. Install python dependencies in the container. We may add this to the docker image if it's found to be useful. 
    1. pip: `apt install python3-pip`
    1. The Tk backend works `apt install python3-tk`
    1. Matplotlib: `python3 -m pip install matplotlib`

1. Checkout https://github.com/cuekoo/GDB-ImageWatch. cv_imshow.py is the entirety of the needed code. 

1. .gdbinit files
Contents of /root/.gdbinit (we should not be using root as the user, in which case, this would be /home/<user>/.gdbinit)
```
add-auto-load-safe-path /usr/src/hue/.gdbinit
```

Example Local .gdbinit
```
source /path/to/cv_imshow.py

set args -t=1 -o="output/debug" -s="sars-cov-antigen" "input/FalsePositive"
```

## Usage
```sh
gdb bin/report
source /path/to/cv_imshow.py # if you did not set up .gdbinit

<set a breakpoint>
run
<hit breakpoint>
cv_imshow <image>
```

## Reference
There's also [OpenImageDebugger](https://github.com/openimagedebugger/openimagedebugger) which looks to require some compiling and install.


https://medium.com/@mreichelt/how-to-show-x11-windows-within-docker-on-mac-50759f4b65cb

https://github.com/cuekoo/GDB-ImageWatch

https://gist.github.com/paul-krohn/e45f96181b1cf5e536325d1bdee6c949

https://gist.github.com/CMCDragonkai/4e9464d9f32f5893d837f3de2c43daa4

https://stackoverflow.com/questions/12933335/tkagg-backend-problems
