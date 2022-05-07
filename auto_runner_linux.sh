#Just in case kill previous copy of proxy_finder
echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Killing all old processes with finder..."
sleep 5s
sudo pkill -e -f finder
echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;35mAll old processes with finder killed\033[0;0m\n"

echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33mInstalling latest packages needed\033[0;0m"
sudo apt update -y
# Install git, python3, etc
sudo apt install --upgrade git python3 python3-pip -y
sudo -H pip3 install --upgrade pip
ulimit -n 1048576

#Install latest version of proxy_finder
cd ~
git clone https://github.com/alexnest-ua/proxy_finder
cd ~/proxy_finder
echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33mInstalling latest requirements\033[0;0m"
sudo pip3 install -r requirements.txt

restart_interval="180m"

ulimit -n 1048576

sudo git config --global --add safe.directory /home/${USER}/proxy_finder

threads="${1:-5000}"
if ((threads < 2000));
then
	echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33m$threads is too LOW amount of threads - finder will be started with 2000 async threads\033[0;0m\n"
	threads=2000
elif ((threads > 10000));
then
	echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33m$threads is too HIGH amount of threads - finder will be started with 10000 async threads\033[0;0m\n"
	threads=10000
fi

echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;32mStarting finder with $threads threads...\033[1;0m"
sleep 4s



# Restarts attacks and update targets list every 20 minutes
while [ 1 == 1 ]
do	
	cd ~/proxy_finder
	

	num=$(sudo git pull origin main | grep -P -c 'Already|Уже')
  echo "$num"
   	
  if ((num == 1));
  then	
		echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Running up to date proxy_finder"
	else
		echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Running updated proxy_finder"
		bash auto_runner_linux.sh $threads& # run new downloaded script 
		return 0 #terminate old script
	fi
  
  #run script
  python3 finder.py --threads $threads
	
  echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;35mFinder is up and Running, next restart will be in $restart_interval...\033[1;0m"
  sleep $restart_interval
  clear
  
  echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Killing all old processes with finder"
  sudo pkill -e -f finder
  echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;35mAll old processes with finder killed\033[0;0m\n"


  no_ddos_sleep="$(shuf -i 1-3 -n 1)m"
  echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[36mSleeping $no_ddos_sleep without finder to let your computer cool down...\033[0m\n"
  sleep $no_ddos_sleep
  echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[42mRESTARTING\033[0m\n"
done
