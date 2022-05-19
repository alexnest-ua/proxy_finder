#Just in case kill previous copy of proxy_finder
echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Killing all old processes with proxy_finder..."
sleep 3s
sudo pkill -e -f finder.py
echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;35mAll old processes with proxy_finder killed\033[0;0m\n"

echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33mInstalling latest packages needed...\033[0;0m"
sleep 3s
sudo apt update -y
# Install git, python3, etc
sudo apt install --upgrade git python3 python3-pip -y
python3 -m pip install --upgrade pip
python3 -m pip install uvloop
ulimit -n 1048576

#Install latest version of proxy_finder
cd ~
git clone https://github.com/porthole-ascend-cinnamon/proxy_finder
cd ~/proxy_finder
sleep 3s
python3 -m pip install -r requirements.txt
echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;32mFiles installed successfully\033[1;0m\n\n"

restart_interval="60m"

ulimit -n 1048576

sudo chown -R ${USER}:${USER} ~/proxy_finder
sudo chown -R ${USER}:${USER} /home/${USER}/proxy_finder
sudo git config --global --add safe.directory /home/${USER}/proxy_finder

threads="${1:-5000}"
if ((threads < 2000));
then
	echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33m$threads is too LOW amount of threads - finder will be started with 2000 async threads\033[0;0m\n"
	threads=2000
elif ((threads > 15000));
then
	echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33m$threads is too HIGH amount of threads - finder will be started with 15000 async threads\033[0;0m\n"
	threads=15000
fi

num_of_copies="${2:-1}"
if ((num_of_copies < 1));
then
	num_of_copies=1
elif ((num_of_copies > 3));
then
	num_of_copies=3
elif ((num_of_copies != 1 && num_of_copies != 2 && num_of_copies != 3));
then
	num_of_copies=1
fi

echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;32mStarting proxy_finder with $threads threads...\033[1;0m\n\n"
sleep 4s

trap 'echo signal received!; ctrl_c' SIGINT SIGTERM

function ctrl_c() {
        echo "Exiting..."
  	sleep 3s
  	for i in ${PIDS[@]}; 
  	do 
    		sudo kill ${i} 
  	done 
  	for i in ${PIDS[@]};
  	do 
   		wait ${i} 
  	done
  	exit
  	echo "Exiting failed - close the window with terminal!!!"
  	sleep 60s
}
# Restarts attacks and update targets list every 20 minutes
while [ 1 == 1 ]
do	
	cd ~/proxy_finder
	num=$(sudo git pull origin main | grep -E -c 'Already|Уже|Вже')
	echo "$num"
   	
	if ((num == 1));
	then
		echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Running up to date proxy_finder\n\n"
	else
		echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Running updated proxy_finder\n\n"
		bash auto_runner_linux.sh $threads $num_of_copies # run new downloaded script 
		return 0 #terminate old script
	fi
	
	declare -a PIDS
	i=0
	while [ $i -lt $num_of_copies ]
	do
		python3 finder.py --threads $threads&
		PID="$!"
		PIDS[i]=${PID}
		i=$(( $i + 1 ))
	done
	
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;35mFinder is up and Running, next restart will be in $restart_interval...\033[1;0m\n\n"
  	sleep $restart_interval
  	clear
  
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Killing all old processes with proxy_finder\n\n"
  	sudo pkill -e -f finder.py
  	echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;35mAll old processes with proxy_finder killed\033[0;0m\n\n"


  	no_work_sleep="$(shuf -i 1-3 -n 1)m"
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[36mSleeping $no_work_sleep without proxy_finder to let your computer cool down...\033[0m\n"
  	sleep $no_work_sleep
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[42mRESTARTING\033[0m\n\n"
	#test
done
