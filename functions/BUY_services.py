from mainrobot.models import v2panel , products  , inovices ,users  , payments
from telebot.types import InlineKeyboardButton , InlineKeyboardMarkup , InputMediaPhoto
from tools import QRcode_maker
import decimal , json , re
import panelsapi
import functions.check_fun as check_fun
from bottext import *




#- handling one panel
def plans_loading_for_one_panel() :
    
    #capcity_mode = 2 ظرفیت نامحدود / capcity_mode = 1 دارای ظرفیت / capcity_mode = 0 بدون ظرفیت
    #sale_mode = 0 فروش بسته / sale_mode 1 = فروش باز
    keyboard = InlineKeyboardMarkup()
    panels_ = v2panel.objects
    products_ = products.objects
    if not panels_.all().exists() or not products_.all().exists():
        return 'no_panel_product'
    panel_id =  [i.id for i in panels_.all()]
    products_filter = products_.filter(panel_id = panel_id[-1] ).order_by('sort_id')
    for i in panels_.all() :
        #panel_status = 1 enable
        if i.panel_status == 1:
            #sale_mode = 0 فروش بسته 
            if i.panel_sale_mode == 0 :              
                return 'sale_closed'
            #sale_mode 1 = فروش باز
            elif i.panel_sale_mode == 1 :

                if i.capcity_mode == 0:  # نوع ظرفیت :‌ بدون ظرفیت 
                    return 'sale_open_no_zarfit'
                                            
                elif i.capcity_mode == 1:  # نوع ظرفیت : دارای ظرفیت
                    if i.all_capcity > 0 :
                        for product in products_filter : 
                                if product.product_status == 1 :
                                    buttons = InlineKeyboardButton(text = product.product_name , callback_data =  f"buyservice_{product.id}_salemode_open_withcapcity")
                                    keyboard.add(buttons) 
                        button_back_1more = InlineKeyboardButton(text = 'بازگشت به منوی اصلی🔙' , callback_data = 'back_mainmenu_from_one_panels')
                        keyboard.add(button_back_1more) 
                        return keyboard
                    else :
                        return 'sale_open_no_zarfit'
                elif i.capcity_mode == 2 : # نوع ظرفیت :‌ نامحدود                 
                    for product in products_filter : 
                            if product.product_status ==1:
                                buttons = InlineKeyboardButton(text = product.product_name , callback_data = f"buyservice_{product.id}_salemode_open_freecapcity")
                                keyboard.add(buttons ) 
                    button_back_1more = InlineKeyboardButton(text = 'بازگشت به منوی اصلی🔙', callback_data = 'back_mainmenu_from_one_panels')
                    keyboard.add(button_back_1more) 
                    return keyboard
        #panel_status = 0 disable
        else :
            return 'panel_disable' 











# handling two panel or more
def plans_loading_for_two_more_panel(panel_pk : int ) :

    keyboard = InlineKeyboardMarkup()
    panels_ = v2panel.objects.filter(id = panel_pk)
    
    for i in panels_ :

        if i.panel_status == 1:
            if not products.objects.filter(panel_id = panel_pk ).exists():
                return 'no_products'
            
            if i.panel_sale_mode == 0: # فروش : بسته
                return 'sale_closed'


            elif i.panel_sale_mode == 1: #فروش : باز 

                if i.capcity_mode == 0 : # ظرفیت : بدون ظرفیت
                    return 'sale_open_no_capcity'
                

                elif i.capcity_mode == 1 :
                        if i.all_capcity > 0: # ظرفیت : دارای ظرفیت
                            for product in products.objects.filter(panel_id = panel_pk).order_by('sort_id'):
                                if product.product_status == 1:
                                    buttons = InlineKeyboardButton(text= product.product_name , callback_data= f"buyservice_{product.id}_salemode_open_withcapcity")
                                    keyboard.add(buttons)
                            button_back_2more = InlineKeyboardButton(text = 'بازگشت به منوی اصلی🔙' , callback_data = 'back_to_main_menu_for_two_panels')
                            keyboard.add(button_back_2more)  
                            return keyboard
                        else :
                            return 'sale_open_no_capcity'



                elif i.capcity_mode == 2 : # ظرفیت :نامحدود
                        for product in products.objects.filter(panel_id = panel_pk).order_by('sort_id'):
                            if product.product_status ==1 :
                                buttons = InlineKeyboardButton(text= product.product_name , callback_data= f"buyservice_{product.id}_salemode_open_freecapcity")
                                keyboard.add(buttons)
                        button_back_2more = InlineKeyboardButton(text = 'بازگشت به منوی اصلی🔙' , callback_data = 'back_to_main_menu_for_two_panels')
                        keyboard.add(button_back_2more)  
                        return keyboard

        else : 
            return 'panel_disable'
























#-pay with wallet
def pay_with_wallet( call , bot , product_dict , panel_loaded ):
    info = product_dict[call.from_user.id]
    user_ = users.objects.get(user_id = call.from_user.id)
    panel_ = v2panel.objects.get(id = info['panel_number'])
    product_price = info['pro_cost']

    if user_.user_wallet < product_price :
        bot.send_message(call.message.chat.id , '⚠️موجودی حساب شما کافی نمیباشد ')

    elif user_.user_wallet >= product_price :
        new_wallet = (user_.user_wallet) - decimal.Decimal(product_price)
        try :
            user_.user_wallet = new_wallet
            user_.save()
                
            if panel_loaded['one_panel'] == True :
                if  ('open' and 'withcapcity') in info['statement'] :
                    check_fun.check_capcity(panel_loaded['one_panel_id'])

            else :
                if panel_loaded['two_more_panels'] == True :
                    if  ('open' and 'withcapcity')  in info['statement']:
                        check_fun.check_capcity(panel_loaded['two_panel_id'])

        except Exception as error_1:
            print(f'an error eccured  when updating user wallet: \n\t {error_1}')
        
        
        inovivces_ = create_inovices(user_id= user_ , user_username=call.from_user.username ,
                                        panel_name = panel_.panel_name , product_name= info['product_name'],
                                        data_limit= info['data_limit'] , expire_date= info['expire_date'] ,
                                        pro_cost= info['pro_cost'] , config_name = info['usernameforacc'] ,
                                        paid_status = 1 , # 0 > unpaid , 1 > paid , 2 > waiting  , 3 > disagree 
                                        paid_mode= 'wlt')
            
        inovivces2_ = inovices.objects.filter(user_id = user_).latest('created_date')
        payments_ = payments.objects.create(user_id = user_ , amount = info['pro_cost'] ,payment_stauts = 'accepted' , inovice_id = inovivces2_)
        send_request = panelsapi.marzban(info['panel_number']).add_user(info['usernameforacc'] , info['product_id'])
        if send_request is False :
            return 'requset_false'
        else :
            return send_request 















def create_paycard_fish():
    user_fish = { 'fish_send' : False , 'accpet_or_reject':False}
    return user_fish

#pay with card

def pay_with_card(call , bot , product_dict , user_fish ):
    info = product_dict[call.from_user.id]
    panel_id = products.objects.get(id = info['product_id']).panel_id

    panel_name = v2panel.objects.get(id=panel_id ).panel_name
    users_ = users.objects.get(user_id=call.from_user.id )

    inovivces_ = create_inovices(user_id= users_ , user_username=call.from_user.username ,
                                panel_name = panel_name , product_name= info['product_name'],
                                data_limit= info['data_limit'] , expire_date= info['expire_date'] ,
                                pro_cost= info['pro_cost'] , config_name = info['usernameforacc'] ,
                                paid_status= 2 , # 0 > unpaid , 1 > paid , 2 > waiting  , 3 > disagree
                                paid_mode= 'kbk')
    
    
    if call.from_user.id not in user_fish :
        user_fish[call.from_user.id] = create_paycard_fish()

    user_fish[call.from_user.id]['fish_send'] = True
    bot.send_message(chat_id = call.message.chat.id , text = buy_service_section_card_to_card_msg(info['pro_cost']))





























def create_inovices(user_id  , panel_name , product_name , data_limit , expire_date , pro_cost ,  paid_status ,config_name : None , paid_mode : str , gift_code : int = None , discount : int = None , user_username : str = None):
     
     
    try :
        inovices_ = inovices.objects.create(user_id = user_id ,
                            user_username = user_username ,
                            panel_name = panel_name ,
                            product_name=product_name ,
                            data_limit=data_limit ,
                            expire_date = expire_date ,
                            pro_cost = pro_cost ,
                            gift_code = gift_code ,
                            discount = discount ,
                            config_name = config_name , 
                            paid_status = paid_status ,
                            paid_mode = paid_mode )   
        return 'done'   
    except Exception as error:
        print(f'an error eccoured when adding inovices : {error}')












def how_to_send(request_ , panel_id , BOT , call_userid):
    panel_ = v2panel.objects.get(id= panel_id)

    if panel_.send_qrcode_mode == 1 : #subscription QRcode
        sub_link = request_['subscription_url']
        
        qr_code_subscription = QRcode_maker.make_qrcode(sub_link)
        link = '\n'.join(request_['links'])
 

        if panel_.send_links_mode == 1: #subscription link 
            BOT.send_photo(call_userid, qr_code_subscription , buy_service_section_product_send('لینک هوشمند ' ,  sub_link))
                    

        elif panel_.send_links_mode == 2: #config link  
            BOT.send_photo(call_userid , caption= buy_service_section_product_send('لینک هوشمند به همراه لینک کانفیگ' , '👇🏻') , photo= qr_code_subscription)
            BOT.send_message(call_userid , f'<code> {link} </code>')


        elif panel_.send_links_mode == 0 : # dont using links in caption
            BOT.send_photo(call_userid , qr_code_subscription , buy_service_section_product_send('لینک هوشمند' , image_only=True))



    elif panel_.send_qrcode_mode == 2 : #config link Qrcode
        config_link = request_['links']
        sub_link = request_['subscription_url'] 
        link = ' \n '.join(config_link)
        config_list = []

        for config in config_link :
            qr_code_config = QRcode_maker.make_qrcode(config) 
            config_list.append(InputMediaPhoto(qr_code_config))


        if panel_.send_links_mode == 1: # subsctrption link 
            config_list[-1] = InputMediaPhoto(config_list[-1].media  ,buy_service_section_product_send('qrcode کانفیگ به همراه لینک هوشمند' , sub_link ) , parse_mode="HTML" )
            BOT.send_media_group(call_userid , config_list)
           
                        


        if panel_.send_links_mode == 2: # config link 
            config_list[-1] = InputMediaPhoto(config_list[-1].media , buy_service_section_product_send('لینک کانفیگ به همراه qrcode کانفیگ ' , '👇🏻') , parse_mode="HTML")
            BOT.send_media_group(call_userid,  config_list)
            BOT.send_message(call_userid ,link )



        if panel_.send_links_mode == 0 :
            config_list[-1] = InputMediaPhoto(config_list[-1].media , buy_service_section_product_send('qrcode کانفیگ ', image_only= True) , parse_mode="HTML" )
            BOT.send_media_group(call_userid , config_list)

