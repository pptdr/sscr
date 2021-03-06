#!/bin/bash 

NAME="smart_signal"                                 # Name of the apsuperplication
DJANGODIR=/home/ubuntu/ecubesolutions.in/venv/smart_signal            # Django project directory 
SOCKFILE=/home/ubuntu/ecubesolutions.in/venv/smart_signal/run/gunicorn.sock # we will communicte using this unix socket
#SOCKFILE=localhost:8000 # we will communicte using this unix socket
USER=ubuntu                                       # the user to run as 
GROUP=ubuntu                                    # the group to run as 
NUM_WORKERS=3                                    # how many worker processes should Gunicorn spawn 
DJANGO_SETTINGS_MODULE=smart_signal.settings            # which settings file should Django use 
DJANGO_WSGI_MODULE=smart_signal.wsgi                    # WSGI module name 

echo "Starting $NAME as `whoami`" 

# Activate the virtual environment 
cd $DJANGODIR 
source /home/ubuntu/ecubesolutions.in/venv/bin/activate 
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH 

# Create the run directory if it doesn't exist 
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn 
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon) 
exec gunicorn ${DJANGO_WSGI_MODULE}:application \ 
 --name $NAME \ 
 --workers $NUM_WORKERS \ 
 --user=$USER --group=$GROUP \ 
 --bind=$SOCKFILE \ 
 --log-level=debug \ 
 --log-file=- 
