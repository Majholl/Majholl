import time



def create_product_entry():
    product_entry = { 'product_id':0 ,'config_name':str , 
                     'statement':[] , 'user_fish_id': str}
    return product_entry


def create_paycard_fish(tamdid:bool =False):
    user_fish = {'fish_send':False , 'accpet_or_reject':False , 
                'inovice':None , 'product_id':None , 'card_used' : '', 
                'config_name':None , 'statement':None , 'tamdid':False}    
    return user_fish



def payment_product_price_create():
    payment_product_price_on_buy = {'reason' : False  , 'user_id' : int , 'payment':None}
    return payment_product_price_on_buy
   

def generate_unique_request_id(user_id):
    return f"{user_id}_{int(time.time())}"


def transfer_money_usrtousr_dict():
    transfer_money_usrtousr_dict = {'transfer_money_to_user':False, 'get_amount':False , 'userid_to_transfer':int}
    return transfer_money_usrtousr_dict



def charge_wallet_dict():
    charge_wallet_dict = {
                           'charge_wallet':False , 'send_fish':False , 'accpet_or_reject_wallet':False , 
                            'user_uniqe_id':int ,'amount':int , 'payment_ob':None}
    return charge_wallet_dict
