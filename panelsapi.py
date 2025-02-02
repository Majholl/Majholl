from mainrobot.models import v2panel , products , panelinbounds
import requests , uuid , json , datetime


#//TODO add try/exception for api


class marzban:

    def __init__(self , panel_id:int = None , panelurl =None , panelusername=None , panelpassword=None):
        if panel_id is not None:
            panel_ = v2panel.objects.get(id = panel_id)
            self.panel_url = panel_.panel_url
            self.panel_username = panel_.panel_username
            self.panel_password = panel_.panel_password
            self.reality_flow = panel_.reality_flow
        else:
            self.panel_url = panelurl
            self.panel_username = panelusername 
            self.panel_password = panelpassword


    def get_token_access(self ):
        panel_url = self.panel_url + '/api/admin/token'
        send_request = requests.post(panel_url , data={'username':self.panel_username , 'password' :self.panel_password})
        try :
            if send_request.status_code == 200:
                Token = json.loads(send_request.content)['access_token']
                header_info = {'Authorization': f"bearer {Token}"}
                return header_info
            else:
                return 'not_connected'
            
        except Exception as gettokenaccess_error:
            print(f'An ERROR occured in [panelsapi.py - CALLING MARZBAN API - LINE 34- FUNC get_token_access] \n\n\t Error-msg :{gettokenaccess_error} - {gettokenaccess_error.content}')



    def add_user(self , username , product_id , usernote=None):
        #- https://marzban:port/api/user
        product_ = products.objects.get(id = product_id)

        panel_url = self.panel_url + '/api/user'
        load_inbounds_db = json.loads(product_.panelinbounds_id.inbounds_selected)
        data_limit = float(product_.data_limit) * 1024 * 1024 * 1024
        expire_time = datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(days = product_.expire_date))
        reality = self.reality_flow if self.reality_flow else ""

        inbounds_ = {}
        for i in load_inbounds_db:
            inbounds_[i.strip()] = []
            for x in load_inbounds_db[i]:
                inbounds_[i.strip()].append(x.strip())

        proxy = {}
        for i in inbounds_:
            proxy[i.strip()] = {'id':str(uuid.uuid4())}
            if 'vless' in i :
                proxy[i.strip()] = {'id':str(uuid.uuid4()) , "flow":reality}
    
        proxy_dict ={
            "status": "active",
            "username": username,
            "proxies": proxy,
            "inbounds": inbounds_,
            "expire": expire_time,
            "data_limit": data_limit ,
            "note": usernote,
            "data_limit_reset_strategy": "no_reset",
            "on_hold_timeout": "2023-11-03T20:30:00",
            "on_hold_expire_duration": 0}
        try : 
            get_header = marzban.get_token_access(self)
            add_user_request = requests.post(panel_url , json=proxy_dict , headers=get_header)
            if add_user_request.status_code == 200:
                return json.loads(add_user_request.content)
            else :
                return False
            
        except Exception as adduser_error:
            print(f'api says : {adduser_error}')
            







    def put_user(self , user_name, product_id=None, usernote=None, uuid_sui=None , expire_date_sui=None, date_limit_sui=None, inbounds_sui=None, status_sui=None, reality_sui=None):

        panel_url = self.panel_url + f'/api/user/{user_name}'
        inbounds_ = {}
        if product_id is not None :
            product_ = products.objects.get(id = product_id)
            load_inbounds_db = json.loads(product_.panelinbounds_id.inbounds_selected)
            for i in load_inbounds_db:
                inbounds_[i.strip()] = []
                for x in load_inbounds_db[i]:
                    inbounds_[i.strip()].append(x.strip())


            data_limit = float(product_.data_limit) * 1024 * 1024 * 1024
            expire_time = datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(days = product_.expire_date))
            reality = self.reality_flow if self.reality_flow else ""
            status_config = 'active'.strip()

        else : 
            expire_time = expire_date_sui
            data_limit = date_limit_sui  
            inbounds_ = inbounds_sui
            uuidconfig = uuid_sui 
            reality = reality_sui
            status_config = status_sui.strip()  
        
        user_note =  usernote if usernote is not None else ''

        

        proxy_put = {}
        for i in inbounds_:
            proxy_put[i.strip()] = {'id':str(uuid.uuid4())}
            if 'vless' in i:
                proxy_put[i.strip()] = {'id':str(uuid.uuid4()) , "flow":reality}


        proxy_dict = {
                "proxies":  proxy_put,
                "inbounds": inbounds_ if inbounds_sui is None else inbounds_,
                "expire": expire_time, 
                "data_limit": data_limit,
                "data_limit_reset_strategy": "no_reset", "status": status_config,
                "note": user_note,
                "on_hold_timeout": "2023-11-03T20:30:00",
                "on_hold_expire_duration": 0}
        
        
        try : 
            get_header = marzban.get_token_access(self)
            put_user_requsts = requests.put(panel_url , json=proxy_dict , headers=get_header)
            
            if put_user_requsts.status_code == 200:
                return json.loads(put_user_requsts.content)
            else:
                return False
                
        except Exception as modifyinguser_error:
            print(f'An ERROR occured in [panelsapi.py - CALLING MARZBAN API - LINE 66-115 - FUNC put_user] \n\n\t Error-msg :{put_user_requsts.status_code} - {put_user_requsts.content} - {modifyinguser_error}')






    def get_inbounds(self):
        panel_url = self.panel_url + '/api/inbounds'
        get_headr = marzban.get_token_access(self)
        get_inbouns_requsts = requests.get(panel_url , headers=get_headr)
        return json.loads(get_inbouns_requsts.content)
    
    def get_all_users(self):
        panel_url = self.panel_url + '/api/users'
        get_header = marzban.get_token_access(self) 
        get_users_requsts = requests.get(panel_url , headers=get_header)
        if get_users_requsts.status_code ==200:
            return json.loads(get_users_requsts.content)


    def get_user(self , username):
        panel_url = self.panel_url + f'/api/user/{username}'
        get_header = marzban.get_token_access(self)
        get_user_request = requests.get(panel_url , headers=get_header)
        if get_user_request.status_code == 200 :
            return json.loads(get_user_request.content)
        else :
            return False
       
       
    def remove_user(self , username):
        panel_url = self.panel_url + f'/api/user/{username}'
        get_header = marzban.get_token_access(self)
        remove_user_request = requests.delete(panel_url , headers=get_header)
        if remove_user_request.status_code == 200:
            return True
        else:
            False



    def revoke_sub(self, username):
        panel_url = self.panel_url + f'/api/user/{username}/revoke_sub'
        get_header = marzban.get_token_access(self)
        revoke_sub = requests.post(panel_url , headers=get_header)
        if revoke_sub.status_code == 200:
            return json.loads(revoke_sub.content)
        else :
            return f'revoke {username} subscription failed'
        

    def get_user_bytoken_sub(self , Token):
        panel_url = self.panel_url + f'/sub/{Token}/'
        get_header = marzban.get_token_access(self)
        get_user_by_token_sub = requests.get(panel_url , headers=get_header)
        
        if get_user_by_token_sub.status_code == 200:
            return True
        
        return False
    


    def get_info_by_token(self , Token):
        panel_url = self.panel_url + f'/sub/{Token}/info'
        get_header = marzban.get_token_access(self)
        info_by_token = requests.get(panel_url , headers=get_header)
        if info_by_token.status_code == 200:
            return json.loads(info_by_token.content)
        else :
            return False


    #system-info / 08.28 
    def system_info(self):
        panel_url = self.panel_url + f'/api/system'
        get_header = marzban.get_token_access(self)
        system_by_token = requests.get(panel_url , headers=get_header)
        if system_by_token.status_code == 200:
            return json.loads(system_by_token.content)
        else:
            False