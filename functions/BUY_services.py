from mainrobot.models import v2panel , products  , inovices , users  , payments , subscriptions , admins
from telebot.types import InlineKeyboardButton , InlineKeyboardMarkup , InputMediaPhoto
from tools import QRcode_maker , farsi_parser
import decimal , re , panelsapi as panelsapi , datetime , jdatetime , time
from functions import panels
from tools.entry_creator import *
from bottext import *




#- handling one panel
    #capcity_mode = 2 ظرفیت نامحدود / capcity_mode = 1 دارای ظرفیت / capcity_mode = 0 بدون ظرفیت
    #sale_mode = 0 فروش بسته / sale_mode 1 = فروش باز

def plans_loading_for_one_panel(tamdid:bool= False):
    
    keyboard = InlineKeyboardMarkup()
    panels_ = v2panel.objects
    products_ = products.objects
    panelid = panels_.values('id')[0]['id']
    load_panel = panels_.get(id = panelid)
    products_filter = products_.filter(panel_id = load_panel).order_by('sort_id')
    
    #PanelorProducts-Exists 
    if panels_.all().exists() and products_filter.exists():
        #Panel-Status : 1 = پنل روشن
        if load_panel.panel_status == 1:  
            #Sale-Mode : 1 = فروش باز
            if load_panel.sale_mode == 1:  
                #Capcity-Mode : 1 = دارای ظرفیت
                if load_panel.capcity_mode == 1:  
                    if load_panel.all_capcity > 0:
                        for product in products_filter: 
                            if product.product_status == 1:
                                call_data_1 = f"buynewservice_{product.pk}_open_zarfit" if tamdid is False else f"tamdidservice_{product.pk}_open_zarfit"
                                buttons = InlineKeyboardButton(text = product.product_name , callback_data = call_data_1)
                                keyboard.add(buttons) 

                #Capcity-Mode : 2 = ظرفیت نامحدود   
                elif load_panel.capcity_mode == 2 : # نوع ظرفیت :‌ نامحدود                 
                    for product in products_filter: 
                        if product.product_status ==1:
                            call_data_2 = f"buynewservice_{product.pk}_open_namahdod" if tamdid is False else f"tamdidservice_{product.pk}_open_namahdod"
                            buttons = InlineKeyboardButton(text = product.product_name , callback_data = call_data_2)
                            keyboard.add(buttons)         

                #Capcity-Mode : 0 = بدون ظرفیت
                else:
                    return 'sale_open_no_zarfit'  
            #Sale-Mode : 0 = فروش بسته        
            else: 
                return 'sale_closed'                
        #Panel-Status : 0 = پنل خاموش
        else :
            return 'panel_disable' 
    #PanelorProducts-Exists 
    else:
        return 'no_panel_product'

    button_back_ = InlineKeyboardButton(text = '✤ - بازگشت به منوی قبلی - ✤' , callback_data = 'back_from_choosing_product_one_panel' if tamdid is False else f'back_from_choosing_product_one_panel_tamid')
    keyboard.add(button_back_) 
    return keyboard                       





# handling two panel or more
def plans_loading_for_two_more_panel(panelid : int , tamdid:bool = False ):
    keyboard = InlineKeyboardMarkup()
    panels_loads = v2panel.objects.get(id = panelid)
    products_ = products.objects.filter(panel_id = panels_loads).order_by('sort_id')

    #Panel-Status : 1 = پنل روشن
    if panels_loads.panel_status == 1:
        #Products-Exists 
        if products_.exists():
            #Sale-Mode : 1 = فروش باز
            if panels_loads.sale_mode == 1:
                #Capcity-Mode : 1 = دارای ظرفیت
                if panels_loads.capcity_mode == 1:
                    if panels_loads.all_capcity > 0:
                        for product in products_:
                            if product.product_status == 1:
                                call_data_1 = f"buynewservice_{product.pk}_open_zarfit" if tamdid is False else f"tamdidservice_{product.pk}_open_zarfit"
                                buttons = InlineKeyboardButton(text= product.product_name , callback_data= call_data_1)
                                keyboard.add(buttons)

                #Capcity-Mode : 2 = ظرفیت نامحدود 
                if panels_loads.capcity_mode == 2 : 
                    for product in products_:
                        if product.product_status ==1 :
                            call_data_2 =  f"buynewservice_{product.pk}_open_namahdod" if tamdid is False else f"tamdidservice_{product.pk}_open_namahdod" 
                            buttons = InlineKeyboardButton(text= product.product_name , callback_data=call_data_2)
                            keyboard.add(buttons) 

                #Capcity-Mode : 0 = بدون ظرفیت
                else:
                    return 'sale_open_no_zarfit'
            #Sale-Mode : 0 = فروش بسته  
            else: 
                return 'sale_closed'
        #Products-Exists 
        else:
            return 'no_products'
    #Panel-Status : 0 = پنل خاموش
    else : 
        return 'panel_disable'


    button_back_more_panels = InlineKeyboardButton(text = '✤ - بازگشت به منوی قبلی - ✤' , callback_data = 'back_from_choosing_product_more_panels' if tamdid is False else 'back_from_choosing_product_more_panels_tamdid' )
    keyboard.add(button_back_more_panels)  
    return keyboard








#username in panel maker 
def make_username_for_panel(message , bot , user_basket : dict):
    products_panel_id = products.objects.get(id = user_basket[message.from_user.id]['product_id'])
    users_in_panel = panelsapi.marzban(products_panel_id.panel_id.pk).get_all_users()
    pattern = re.fullmatch(r'(\w|\d|\_)+', message.text)
    
    if farsi_parser.parse_farsi(message.text) == False:
        if pattern:
            
            if users_in_panel['total'] == 0:
                user_basket[message.from_user.id]['config_name'] = f'1_{message.text}'
                

            elif users_in_panel['total'] == 1:
                for i in users_in_panel['users']:
                    if '_' in i['username']:
                        new_number = i['username'].split("_")[0]
                        if new_number.isdigit():
                            user_basket[message.from_user.id]['config_name'] = f'{int(new_number) + 1}_{message.text}'
                        else:
                            user_basket[message.from_user.id]['config_name'] = f'1_{message.text}'
                    else:
                        user_basket[message.from_user.id]['config_name'] = f'1_{message.text}'



            elif users_in_panel['total'] > 1:
                users_with_hyphen = [i['username'] for i in users_in_panel['users'] if '_' in i['username']]
                users_with_number = []
                
                for i in users_with_hyphen:
                    userswithnumbersuffix = i.split("_")[0]
                    if userswithnumbersuffix.isdigit(): 
                        users_with_number.append(i)
                    new_number = users_with_hyphen[-1].split("_")[0]
                    user_basket[message.from_user.id]['config_name'] = f'{int(new_number) + 1}_{message.text}'
          
        
        else : 
            return 'incorrect_username'
    else :
        return 'incorrect_username'







#-pay with wallet
def pay_with_wallet(call ,  product_dict , tamdid = False):
    info = product_dict[call.from_user.id]
    product_ = products.objects.get(id = info['product_id'])
    user_ = users.objects.get(user_id = call.from_user.id)
    panel_ = v2panel.objects.get(id = product_.panel_id.pk)
    sub_check = subscriptions.objects
    product_price = product_.product_price
    created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S') 
    kindpay = 'buy' if tamdid is False else 'renew'

    if user_.user_wallet < decimal.Decimal(product_price):
        return 'not_enough_money_inwallet'
    
    if user_.user_wallet >= decimal.Decimal(product_price):
        try:
            
            if tamdid is False :
                note = f"created at {created_date} by {user_.user_id}"
                send_request = panelsapi.marzban(panel_.pk).add_user(info['config_name'] , product_.pk , usernote=note)    
            else: 
                note = f"renewed at {created_date} by {user_.user_id}"
                send_request = panelsapi.marzban(panel_.pk).put_user(info['config_name'] , product_.pk , usernote=note)

            if send_request :
                # 0 > unpaid , 1 > paid , 2 > waiting  , 3 > disagree
                inovivces_creations = create_inovices(user_, panel_ , product_ , panel_.panel_name ,product_.product_name , product_.data_limit , product_.expire_date , product_.product_price ,  1 , kindpay , info['config_name'] , 'wlt')
                payment_creations = create_payment(user_ , product_.product_price , 'accepted' , inovivces_creations)
                
                if sub_check.filter(user_subscription = info['config_name']).count() == 0:
                    subscription_creations = create_subscription(user_ , info['config_name'] , product_ , panel_)   
                else:
                    load_sub = sub_check.get(user_subscription = info['config_name'])
                    load_sub.panel_id , load_sub.product_id , load_sub.created_date = panel_ , product_ , created_date
                    load_sub.save()

                new_wallet = (user_.user_wallet) - decimal.Decimal(product_price)
                user_.user_wallet = new_wallet
                user_.save()
                panels.check_capcity(panel_.pk) if ('open' and 'zarfit') in info['statement'] else None

                return send_request 
            else:
                return 'requset_false'
            
        except Exception as paywithwallet_error:
            print(f'An ERROR occured in [buy_services.py  - LINE 219 - FUNC pay_with_wallet] \n\n\t Error-msg :{paywithwallet_error}')










#pay with card
def pay_with_card(call , bot , user_order_basket , user_paykard_fish , tamdid=False):
    
    info = user_order_basket[call.from_user.id]
    product_ = products.objects.get(id = info['product_id'])
    panel_ = v2panel.objects.get(id = product_.panel_id.pk)
    user_ = users.objects.get(user_id = call.from_user.id)
    admin_ = admins.objects.values('user_id').get(is_owner=1)['user_id']
    try:
        if buy_service_section_cardtocard_msg(product_.product_price , None) =='هیچ شماره کارت فعالی وجود نداره':
            bot.send_message(admin_ ,'هیچ شماره کارتی برای پرداختی ها وجود ندارد لطفا یک شماره کارت جدید اضافه کنید')
        else:
            
            unique_request_id = f'{call.from_user.id}_{call.message.date}'
                
            if unique_request_id not in user_paykard_fish:
                user_paykard_fish[unique_request_id] = create_paycard_fish()

            info['user_fish_id'] = unique_request_id

            user_paykard_fish[unique_request_id]['fish_send'] = True
            user_paykard_fish[unique_request_id]['product_id'] = info['product_id']
            user_paykard_fish[unique_request_id]['config_name'] = info['config_name']
            user_paykard_fish[unique_request_id]['statement'] = info['statement']

            if tamdid is True :
                user_paykard_fish[unique_request_id]['tamdid'] = True
            
            Text = buy_service_section_cardtocard_msg(product_.product_price , user_paykard_fish[unique_request_id])
            
            bot.send_message(call.message.chat.id , Text)
    
    except Exception as paywithcard_error : 
        print(f'An ERROR occured in [buy_services.py  - LINE 197-227 - FUNC pay_with_card] \n\n\t Error-msg :{paywithcard_error}')











#- this is dict clear
def clear_dict(op_on_dict , user_id:int=None):
    #clear the hole dict
    if user_id is None :
        op_on_dict.clear()
        return f'dict_cleared : {op_on_dict}'
    
    #pop user in dict
    elif user_id is not None and user_id in op_on_dict:
        op_on_dict.pop(user_id)
        return f'userid : {user_id} in {op_on_dict} poped out'







def how_to_send(request_ , info , BOT , call_userid):
    products_ = products.objects.get(id = info['product_id'])

    if products_.panel_id.send_qrcode_mode == 1 : #subscription QRcode
        
        sub_link = request_['subscription_url']
        qr_code_subscription = QRcode_maker.make_qrcode(sub_link)

        link = '\n'.join(request_['links'])
 
        if products_.panel_id.send_links_mode == 1: #subscription link 
            BOT.send_photo(call_userid, qr_code_subscription , buy_service_section_product_send('لینک هوشمند ' , request_['username'] ,  sub_link))
                    
        elif products_.panel_id.send_links_mode == 2: #config link  
            BOT.send_photo(call_userid , caption= buy_service_section_product_send('لینک هوشمند به همراه لینک کانفیگ' , request_['username'] , '👇🏻') , photo= qr_code_subscription)
            BOT.send_message(call_userid , f'<code>{link}</code>')

        elif products_.panel_id.send_links_mode == 0 : # dont using links in caption
            BOT.send_photo(call_userid , qr_code_subscription , buy_service_section_product_send('لینک هوشمند' , request_['username'] , image_only=True))




    elif products_.panel_id.send_qrcode_mode == 2 : #config link Qrcode
        config_link = request_['links']
        sub_link = request_['subscription_url'] 
        link = ' \n '.join(config_link)
        config_list = []

        for config in config_link :
            qr_code_config = QRcode_maker.make_qrcode(config) 
            config_list.append(InputMediaPhoto(qr_code_config))


        if products_.panel_id.send_links_mode == 1: # subsctrption link 
            config_list[-1] = InputMediaPhoto(config_list[-1].media  ,buy_service_section_product_send('qrcode کانفیگ به همراه لینک هوشمند' , request_['username'] , sub_link ) , parse_mode="HTML" )
            BOT.send_media_group(call_userid , config_list)
           
        if products_.panel_id.send_links_mode == 2: # config link 
            config_list[-1] = InputMediaPhoto(config_list[-1].media , buy_service_section_product_send('لینک کانفیگ به همراه qrcode کانفیگ ' , request_['username'] , '👇🏻') , parse_mode="HTML")
            BOT.send_media_group(call_userid,  config_list)
            BOT.send_message(call_userid ,link )

        if products_.panel_id.send_links_mode == 0 :
            config_list[-1] = InputMediaPhoto(config_list[-1].media , buy_service_section_product_send('qrcode کانفیگ ', request_['username'] , image_only= True) , parse_mode="HTML" )
            BOT.send_media_group(call_userid , config_list)










#------------------------------ creations db objects ---------------------------------------------------------
def create_inovices(userid  , panelid , productid ,panelname , productname , datalimit , expiredate , productprice ,  paidstatus , kindpay ,configname : None , paidmode : str ,kard_in_used = None ,  giftcode : int = None , discount : int = None): 
    created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S') 
    try :
        inovices_creations = inovices.objects.create(user_id=userid , panel_id=panelid , product_id=productid  , card_used_id = kard_in_used , 
                                                    panel_name=panelname , product_name=productname , data_limit=datalimit , expire_date=expiredate , product_price=productprice ,
                                                    gift_code=giftcode , discount=discount ,
                                                    config_name=configname ,  paid_status=paidstatus ,
                                                    paid_mode=paidmode , kind_pay=kindpay , 
                                                    created_date=created_date)   
        return inovices_creations
    
    except Exception as incovicescreations_error:
        print(f'An ERROR occured in [buy_services.py  - LINE 356 - FUNC create_inovices] \n\n\t Error-msg :{incovicescreations_error}')




def create_payment(userid , amount , paymenentstatus , inoviceid = None , paymenttype=None):
    created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S') 
    inoviceId = inoviceid if inoviceid is not None else None
    try:
        payment_creations =payments.objects.create(user_id=userid , inovice_id=inoviceId ,
                                                   amount=amount , payment_status=paymenentstatus ,
                                                   payment_type=paymenttype , created_date=created_date)
        return payment_creations
    
    except Exception as paymentcreations_error:
        print(f'An ERROR occured in [buy_services.py  - LINE 371 - FUNC create_payment] \n\n\t Error-msg :{paymentcreations_error}')




def create_subscription(userid , config_name , productid=None , panelid=None):
    created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    try:
        
        subscription_creations =subscriptions.objects.create(user_id=userid , product_id= productid , panel_id=panelid ,
                                                            user_subscription=config_name , created_date=created_date)       
        return subscription_creations
    
    except Exception as subscriptioncreations_error:
        print(f'An ERROR occured in [buy_services.py  - LINE 385 - FUNC create_subscription] \n\n\t Error-msg :{subscriptioncreations_error}')




