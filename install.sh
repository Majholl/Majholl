#! /bin/bash

sudo apt-get update -y ; 
sudo apt-get upgrade -y ;
sudo apt install pkg-config  ; 
sudo apt install pip -y ; 
sudo apt install python3 -y  ; 
sudo apt install python3.12-full -y ; 
sudo apt install python3-full -y ;
sudo apt install python3-venv -y  ; 
sudo apt install python3-distutils -y ; 
sudo apt install python3-dev build-essential -y ;

sudo apt install mysql-client -y  ;
sudo apt install mysql-server -y ; 
sudo apt install libmysqlclient-dev -y ; 
sudo apt install pkg-config ; 


alias  python = "python3" ; 
cd /root ; 
mkdir majhol ; 
cd /majhol ; 

python3 -m venv .venv ; 
source .venv/bin/activate ; 

pip install django ; 

git clone https://github.com/Noskheh/Majholl.git ;
cd Majholl ; 
python -m pip install --upgrade pip ; 
pip install --upgrade setuptools ; 
pip install --upgrade pip setuptools wheel ; 
pip install -r requirements.txt ; 