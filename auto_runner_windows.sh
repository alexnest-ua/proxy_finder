#Just in case kill previous copy of proxy_finder
echo -e "[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Killing all old processes with finder..."
sleep 3s
taskkill -f -im python.exe
taskkill -f -im python3.8.exe
taskkill -f -im python3.9.exe
taskkill -f -im python3.10.exe
echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;35mAll old processes with finder killed\033[0;0m\n"

ulimit -n 1048576

#Install latest version of proxy_finder
cd ~
rm -rf proxy_finder
git clone https://github.com/alexnest-ua/proxy_finder
cd ~/proxy_finder
echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;33mInstalling latest requirements...\033[0;0m\n\n"
sleep 3s
python -m pip install -r requirements.txt

restart_interval="180m"

ulimit -n 1048576

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

echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;32mStarting finder with $threads threads...\033[1;0m\n\n"
sleep 4s



# Restarts attacks and update targets list every 20 minutes
while [ 1 == 1 ]
do	
	cd ~/proxy_finder
	num=$(git pull origin main | grep -P -c 'Already|Уже')
	echo "$num"
   	
	if ((num == 1));
	then
		echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Running up to date proxy_finder\n\n"
	else
		echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Running updated proxy_finder\n\n"
		bash auto_runner_windows.sh $threads # run new downloaded script 
		return 0 #terminate old script
	fi
	
	#run script
	python3 finder.py --threads $threads&
	
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[1;35mFinder is up and Running, next restart will be in $restart_interval...\033[1;0m\n\n"
  	sleep $restart_interval
  	clear
  
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - Killing all old processes with finder\n\n"
  	taskkill -f -im python.exe
	taskkill -f -im python3.8.exe
	taskkill -f -im python3.9.exe
	taskkill -f -im python3.10.exe
  	echo -e "\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[0;35mAll old processes with finder killed\033[0;0m\n\n"


  	no_work_sleep="$(shuf -i 1-3 -n 1)m"
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[36mSleeping $no_work_sleep without finder to let your computer cool down...\033[0m\n"
  	sleep $no_work_sleep
  	echo -e "\n\n[\033[1;32m$(date +"%d-%m-%Y %T")\033[1;0m] - \033[42mRESTARTING\033[0m\n\n"
	#test
done
