from mainrobot.models import v2panel , products
import requests , uuid , json , datetime


#//TODO add try/exception for api

class marzban:

    def __init__(self , panel_id:int ):
        panel_ = v2panel.objects.get(id = panel_id)
        self.panel_url = panel_.panel_url
        self.panel_username = panel_.panel_username
        self.panel_password = panel_.panel_password
        self.reality_flow = panel_.reality_flow

    def get_token_acces(self ):
        panel_url = self.panel_url + '/api/admin/token'
        req = requests.post(panel_url , data={'username':self.panel_username , 'password' :self.panel_password})

        if req.status_code == 200:
            Token = json.loads(req.content)['access_token']
            header_info = {'Authorization': f"bearer {Token}"}
            return header_info
        else:
            return False


    def add_user(self , username , product_id):
        #- https://marzban:port/api/user

        panel_url = self.panel_url + '/api/user'
        product_ = products.objects.get(id = product_id)
        data_expire = product_.expire_date
        data_limit = float(product_.data_limit)
        inbounds = product_.inbounds_selected
        current_time = datetime.datetime.now()
        expire_time = current_time + datetime.timedelta(days = data_expire)
        reality = self.reality_flow if self.reality_flow else ""

        proxy_dict ={
            "username": username,
            "proxies": {"vmess": {"id": str(uuid.uuid4())},"vless": {'flow': reality}},
            "inbounds": json.loads(inbounds),
            "expire": datetime.datetime.timestamp(expire_time),
            "data_limit": data_limit * 1024 * 1024 * 1024,
            "data_limit_reset_strategy": "no_reset",
            "status": "active",
            "note": "",
            "on_hold_timeout": "2023-11-03T20:30:00",
            "on_hold_expire_duration": 0
                }
        try : 
            get_header = marzban.get_token_acces(self)
            add_user_request = requests.post(panel_url , json= proxy_dict , headers= get_header)
            
            if add_user_request.status_code == 200:
                return json.loads(add_user_request.content)
            else :
                return False
            
        except Exception as adduser_error:
            print(f'api says : {adduser_error}')
            


    def put_user(self , user_name , product_id):
        panel_url = self.panel_url + f'/api/user/{user_name}'
        
        product_ = products.objects.get(id = product_id)
        inbounds_database = json.loads(product_.inbounds_selected)
        data_limit = float(product_.data_limit)
        expire_time = datetime.datetime.now() + datetime.timedelta(days = product_.expire_date)

        inbound = {}
        for i in inbounds_database:
            inbound[i.strip()] = []
            for x in inbounds_database[i]:
                inbound[i.strip()].append(x.strip())

        proxy_dict = {
                    "proxies": {"vmess": {"id": str(uuid.uuid4())},"vless": {'flow':self.reality_flow if self.reality_flow else ""}},
                    "inbounds":inbound,
                    "expire": datetime.datetime.timestamp(expire_time),
                    "data_limit": data_limit,
                    "data_limit_reset_strategy": "no_reset",
                    "status": "active",
                    "note": f"renewed at :{datetime.datetime.now()} ",
                    "on_hold_timeout": "2023-11-03T20:30:00",
                    "on_hold_expire_duration": 0}
        
        try : 
            get_header = marzban.get_token_acces(self)
            put_user_requsts = requests.put(panel_url , json=proxy_dict , headers=get_header)

            if put_user_requsts.status_code == 200:
                return json.loads(put_user_requsts.content)
            else:
                return False
            
        except Exception as adduser_error:
            print(f'api says : {adduser_error}')
            




    def get_inbounds(self):
        panel_url = self.panel_url + '/api/inbounds'
        get_headr = marzban.get_token_acces(self)
        get_inbouns_requsts = requests.get(panel_url , headers=get_headr)
        return json.loads(get_inbouns_requsts.content)
    
    def get_all_users(self):
        panel_url = self.panel_url + '/api/users'
        get_header = marzban.get_token_acces(self) 
        get_users_requsts = requests.get(panel_url , headers=get_header)
        if get_users_requsts.status_code ==200:
            return json.loads(get_users_requsts.content)


    def get_user(self , username):
        panel_url = self.panel_url + f'/api/user/{username}'
        get_header = marzban.get_token_acces(self)
        get_user_request = requests.get(panel_url , headers=get_header)
        if get_user_request.status_code == 200 :
            return json.loads(get_user_request.content)
        else :
            return False
       
       
    def remove_user(self , username):
        panel_url = self.panel_url + f'/api/user/{username}'
        get_header = marzban.get_token_acces(self)
        remove_user_request = requests.delete(panel_url , headers=get_header)
        if remove_user_request.status_code == 200:
            return True
        else:
            False



    def revoke_sub(self, username):
        panel_url = self.panel_url + f'/api/user/{username}/revoke_sub'
        get_header = marzban.get_token_acces(self)
        revoke_sub = requests.post(panel_url , headers=get_header)
        if revoke_sub.status_code == 200:
            return json.loads(revoke_sub.content)
        else :
            return f'revoke {username} subscription failed'
        

    def get_user_bytoken_sub(self , Token):
        panel_url = self.panel_url + f'/sub/{Token}/'
        get_header = marzban.get_token_acces(self)
        get_user_by_token_sub = requests.get(panel_url , headers=get_header)
        
        if get_user_by_token_sub.status_code == 200:
            return True
        
        return False
    


    def get_info_by_token(self , Token):
        panel_url = self.panel_url + f'/sub/{Token}/info'
        get_header = marzban.get_token_acces(self)
        info_by_token = requests.get(panel_url , headers=get_header)
        if info_by_token.status_code == 200:
            return json.loads(info_by_token.content)
        else :
            return False


    #system-info / 08.28 
    def system_info(self):
        panel_url = self.panel_url + f'/api/system'
        get_header = marzban.get_token_acces(self)
        system_by_token = requests.get(panel_url , headers=get_header)
        if system_by_token.status_code == 200:
            return json.loads(system_by_token.content)
        else:
            False