#Just in case kill previous copy of proxy_finder

set -e

echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Killing all old processes with proxy_finder..."
sleep 3
pkill -f finder.py || true
echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;35mAll old processes with proxy_finder killed\033[0;0m\n"

echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33mInstalling latest packages needed...\033[0;0m"
sleep 3

num=$(brew --version | grep -E -c "3.4|3.5" || true)
echo -e "$num"
if ((num == 1));
then	
	echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Brew is the latest version"
else
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/${USER}/.zprofile
	eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Install git, python3, etc
brew install coreutils git python@3.10
brew link --overwrite python@3.10
python3.10 -m pip install --upgrade pip
python3.10 -m pip install uvloop

ulimit -n 1048576

#Install latest version of proxy_finder
cd ~
rm -rf proxy_finder
git clone https://github.com/porthole-ascend-cinnamon/proxy_finder || true
cd ~/proxy_finder
echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33mInstalling latest requirements...\033[0;0m\n\n"
sleep 3
python3.10 -m pip install -r requirements.txt
echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;32mFiles installed successfully\033[1;0m\n\n"

#restart every 1 hour
restart_interval="3600"

ulimit -n 1048576


threads="${1:-2500}"
if ((threads < 2000));
then
	echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33m$threads is too LOW amount of threads - finder will be started with 2000 async threads\033[0;0m\n"
	threads=2000
elif ((threads > 10000));
then
	echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33m$threads is too HIGH amount of threads - finder will be started with 10000 async threads\033[0;0m\n"
	threads=10000
fi

echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;32mStarting proxy_finder with $threads threads...\033[1;0m\n\n"
sleep 4

trap 'echo signal received!; kill "${PID}"; wait "${PID}"; ctrl_c' SIGINT SIGTERM

function ctrl_c() {
        echo "Exiting..."
	sleep 3s
	exit
	echo "Exiting failed - close the window with terminal!!!"
	sleep 60s
}

# Restarts attacks and update targets list every 20 minutes
while [ 1 == 1 ]
do	
  	cd ~/proxy_finder

  	num=$(git pull origin main |  grep -E -c 'Already|Уже|Вже')
	echo "$num"
   	
	if ((num == 1));
	then
		echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Running up to date proxy_finder\n\n"
	else
		echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Running updated proxy_finder\n\n"
		bash auto_runner_mac.sh --threads $threads # run new downloaded script 
		exit #terminate old script
	fi
	
	#run script
	python3.10 finder.py --threads $threads&
	PID="$!"
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;35mFinder is up and Running, next restart will be in $restart_interval seconds...\033[1;0m\n\n"
  	sleep $restart_interval
  	clear
  
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Killing all old processes with proxy_finder\n\n"
  	pkill -f finder.py || true
  	echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;35mAll old processes with proxy_finder killed\033[0;0m\n\n"


  	no_work_sleep=`expr $(shuf -i 1-3 -n 1) \* 60`
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[36mSleeping $no_work_sleep seconds without proxy_finder to let your computer cool down...\033[0m\n"
  	sleep $no_work_sleep
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[42mRESTARTING\033[0m\n\n"
	#test
done
