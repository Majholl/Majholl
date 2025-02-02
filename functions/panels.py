from mainrobot.models import v2panel , products , inovices, subscriptions
from keybuttons import BotkeyBoard as botkb
import re
import panelsapi as panelsapi
#this is functions that managing panels





# -------------- > Adding-Panel < --------------


def add_panel_database(bot , message ,call,   panelname , panelurl , panelusername , panelpassword , paneltype):
    try :
        if paneltype == 'marzban':
            send_request = panelsapi.marzban(panelurl=panelurl , panelusername=panelusername , panelpassword=panelpassword).get_token_access()
            
            if send_request == 'not_connected':
                bot.edit_message_text('پنل متصل نمیباشد \n ممکن است اطلاعات وارده اشتباه باشد مجدد بررسی نمایید ', call.message.chat.id , call.message.message_id)  
            else:
                panel_=v2panel.objects.create(panel_name=panelname , panel_url=panelurl ,
                                            panel_username=panelusername , panel_password=panelpassword ,
                                            panel_type=paneltype , send_qrcode_mode=1 , send_links_mode=1)
            
                Text_1='✅پنل با موفقیت اضافه شد\n لطفا اینباند های پنل را تنظیم کنید \nساخت اینباند 👇🏻\n⚠️ شما در هر زمانی میتوانید با مراجعه به مدیریت پنل به مدیریت کردن ، حذف و یا اضافه کردن اینباند جدید اقدام کنید '
                bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup = botkb.inbounds_adding(panel_.pk))

    except Exception as panel_creation:
        print(f'An ERROR occured in [panels.py  - LINE 24- FUNC add_panel_database] \n\n\t Error-msg :{panel_creation}')
        Text_2='❌هنگام اضافه کردن پنل به دیتابیس مشکلی به وجود امد \n\n مجددا امتحان فرمایید یا لاگ را بررسی کنید'
        bot.send_message(message.chat.id , Text_2)





# -------------- > Removing_panel < --------------
def remove_panel_database(bot , call , panel_id , panel=None , product=None):
    try :  
        panel_to_remove = v2panel.objects.get(id = panel_id)
        products_ = products.objects.filter(panel_id = panel_id)
        inovices_ = inovices.objects.filter(panel_id = panel_to_remove)
        subscriptions_ = subscriptions.objects.filter(panel_id = panel_to_remove)

        if subscriptions_.count() >= 1 :
            bot.send_message(call.message.chat.id , 'اشتراک فعال از این پنل وجود دارد و نمیتوان آن را حذف کرد')
        else:
            if panel is not None :
                
                if inovices_.count() >=1:
                    for inovices_updating in inovices_:
                        inovices_updating.panel_id = None
                        inovices_updating.save()

                if products_.count() >= 1:
                    for products_updating in products_:
                        products_updating.panel_id = None
                        products_updating.save()

                panel_to_remove.delete()
                Text_1='✅پنل باموفقیت پاک شد'  
                if botkb.panel_management_remove_panel() =='no_panel_to_remove':
                    bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panels_management_menu_keyboard())
                else:
                    bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panel_management_remove_panel())


            
            if product is not None:
            
                if inovices_.count() >= 1:
                    for inovices_updating in inovices_:
                        inovices_updating.panel_id , inovices_updating.product_id = None , None
                        inovices_updating.save()

                for deleting_product in products_:
                    deleting_product.delete()

                panel_to_remove.delete()
                
                Text_2='✅پنل و تمامی محصولات مرتبط پاک شدند'  
                if botkb.panel_management_remove_panel() =='no_panel_to_remove':
                    bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panels_management_menu_keyboard())
                else:
                    bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panel_management_remove_panel())

    except Exception as removepanel_error:
        print(f'An ERROR occured in [panels.py  - LINE 89- FUNC remove_panel_database] \n\n\t Error-msg :{removepanel_error}')
        bot.send_message(call.message.chat.id , 'مشکلی در حذف کردن پنل به وجود امد')
        





# -------------- > Manage_panel < --------------

# ------------------------- < Panel-Stauts >

def change_panel_status(bot , call , panel_id):
    try :
        panel_ = v2panel.objects.get(id = panel_id)
        panel_new_status = 0 if panel_.panel_status == 1 else 1
        panel_.panel_status = panel_new_status
        panel_.save()
    except Exception as changeingstatus_error:
        print(f'An ERROR occured in [panels.py  - LINE 108- FUNC change_panel_status] \n\n\t Error-msg :{changeingstatus_error}')

    Text_1=f'🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\nوضعیت پنل تغییر کرد\nوضعیت فعلی:{"🟢فعال" if panel_.panel_status == 1 else "🔴غیر-فعال"}'
    Text_2=f'{"🟢فعال" if panel_.panel_status == 1 else "🔴غیر-فعال"}'
    bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_selected_panel(panel_pk = panel_id))      
    bot.answer_callback_query(call.id , Text_2)


# ------------------------- < Panel-Name >

def change_panel_name(bot , message , panel_id):     
    if  message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n تغییر نام پنل لغو شد '
        bot.send_message(message.chat.id , Text_1 ,reply_markup = botkb.manage_selected_panel(panel_pk=panel_id))   
    else:        
        try:
            panel_ = v2panel.objects.get(id = panel_id)
            panel_new_name = message.text 
            panel_.panel_name = panel_new_name
            panel_.save()
  
        except Exception as changepanelname_error:
            print(f'An ERROR occured in [panels.py  - LINE 130- FUNC change_panel_name] \n\n\t Error-msg :{changepanelname_error}')
        Text_2='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n اسم پنل تغییر کرد \n دقت کنید که این تغییر در هنگام خرید سرویس نمایش داده خواهد شد'
        bot.send_message(message.chat.id ,Text_2 , reply_markup=botkb.manage_selected_panel(panel_pk=panel_id))




# ------------------------- < Panel_Url >
CHANGE_panel_url_USERNAME_PASSWORD = {'change_panel_url':None , 'change_panel_username':None }

def change_panel_url(bot , message , panel_id):
    if  message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n تغییر ادرس پنل لغو شد'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.manage_selected_panel(panel_pk=panel_id))
    else :
        pattern=(r'^(http|https):\/\/' 
                r'('
                    r'[\w.-]+'
                    r'|'
                    r'(\d{1,3}\.){3}\d{1,3}'
                r')'
                r'(:\d{1,5})?$'
                )   
        http_or_https_chekcer = re.search(pattern , message.text)
    
        if http_or_https_chekcer:
            CHANGE_panel_url_USERNAME_PASSWORD['change_panel_url'] = http_or_https_chekcer.group(0)
            Text_2 = 'یوزر نیم پنل را ارسال کنید \n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_2)
            bot.register_next_step_handler(message , lambda message : change_username_on_panel_url(bot , message , panel_id))
        else:
            Text_3='ادرس پنل اشتباه است\n فرمت های صحیح :\n<b>http://panelurl.com:port</b>\n<b>https://panelurl.com:port</b>\n<b>http://ip:port</b>\n<b>https://ip:port</b>\n\n مجدد امتحان فرمایید'
            bot.send_message(message.chat.id , Text_3)
            bot.register_next_step_handler(message , lambda message : change_panel_url(bot , message , panel_id))



        
def change_username_on_panel_url(bot , message , panel_id):
    if  message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n تغییر ادرس پنل لغو شد'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.manage_selected_panel(panel_pk=panel_id))
    else :
        CHANGE_panel_url_USERNAME_PASSWORD['change_panel_username'] = message.text
        Text_2 = ' پسوورد پنل را ارسال کنید \n\nTO-CANCEL : /cancel'
        bot.send_message(message.chat.id , Text_2)
        bot.register_next_step_handler(message , lambda message : change_password_on_panel_url(bot , message , panel_id))



def change_password_on_panel_url(bot , message , panel_id):
    if  message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n تغییر ادرس پنل لغو شد'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.manage_selected_panel(panel_pk=panel_id))
    else:            
        try:
            panel_ = v2panel.objects.get(id=panel_id)
            send_request = panelsapi.marzban(panelurl=CHANGE_panel_url_USERNAME_PASSWORD['change_panel_url'] , panelusername=CHANGE_panel_url_USERNAME_PASSWORD['change_panel_username'] , panelpassword=message.text).get_token_access()
            if send_request !='not_connected':
                panel_new_url = CHANGE_panel_url_USERNAME_PASSWORD['change_panel_url']
                panel_.panel_url = panel_new_url
                panel_.save()
                Text_2='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n آدرس پنل تغییر کرد '
                bot.send_message(message.chat.id ,Text_2 ,reply_markup=botkb.manage_selected_panel(panel_pk= panel_id))
            else:
                bot.send_message(message.chat.id , 'پنل متصل نمیباشد \n ممکن است اطلاعات وارده اشتباه باشد مجدد بررسی نمایید ')  

        except Exception as changepanelurl_error:
                print(f'An ERROR occured in [panels.py  - LINE 198- FUNC change_password_on_panel_url] \n\n\t Error-msg :{changepanelurl_error}')
                bot.send_message(message.chat.id , 'امکان اتصال به لینک ارسالی وجود نداشت مجدد امتحان فرمایید\n این امکان وجود دارد که به علت عدم یکسان بودن یوزرنیم/پسورد اتصال به پنل به مشکل خورده است \n مجدد امتحان فرمایید\n\nTO-CANCEL : /cancel')
                bot.register_next_step_handler(message , lambda message : change_panel_url(bot , message , panel_id))
 


# ------------------------- < Panel_Reality >
def change_panel_realityflow(bot , call , panel_id , reality=None , none_reality=None):
    Text_0='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n ریلیتی - فلو پنل تغییر کرد '
    try: 
        if call.data.startswith('xtls-rprx-vision_') and reality is not None:
            panel_=v2panel.objects.get(id=panel_id)
            panel_new_reality=call.data.split('_')[0]
            panel_.reality_flow=panel_new_reality
            panel_.save()
            bot.edit_message_text(Text_0, call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_selected_panel(panel_pk=panel_id))

        if call.data.startswith('None_realityFlow_')and  none_reality is not None:
            
            panel_=v2panel.objects.get(id=panel_id)
            panel_new_reality=call.data.split('_')[0].lower()
            panel_.reality_flow=panel_new_reality
            panel_.save()
            bot.edit_message_text(Text_0 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_selected_panel(panel_pk=panel_id))

    except Exception as changepanelreality_error:
        print(f'An ERROR occured in [panels.py  - LINE 224- FUNC change_panel_realityflow] \n\n\t Error-msg :{changepanelreality_error}')



# ------------------------- < Panel_Capcity >                   
def change_panel_capcitymode(bot , call, panel_id):
    panel_=v2panel.objects.get(id=panel_id)
    try:
        if panel_.capcity_mode==0:
            new_capcity=1
            panel_.capcity_mode=new_capcity
            panel_.save()

        elif panel_.capcity_mode==1:
            new_capcity=2
            panel_.capcity_mode=new_capcity
            panel_.save()

        else :
            new_capcity=0
            panel_.capcity_mode=new_capcity
            panel_.save()
        Text_0='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n حالت ظرفیت  پنل تغییر کرد '
        bot.edit_message_text(Text_0,call.message.chat.id , call.message.message_id , reply_markup=botkb.changin_panel_capcity(panel_pk=panel_id))
    
    except Exception as changepanelcapcitymode_error :
        print(f'An ERROR occured in [panels.py  - LINE 250- FUNC change_panel_capcitymode] \n\n\t Error-msg :{changepanelcapcitymode_error}')



# ------------------------- < Panel_Salemode >   
def change_panel_salemode(bot , call , panel_id):
    panel_ = v2panel.objects.get(id=panel_id)
    try:
        if panel_.sale_mode==0:
            new_=1
            panel_.sale_mode=new_
            panel_.save()
            
        else: 
            new_=0
            panel_.sale_mode=new_
            panel_.save()

        Text_0='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n حالت فروش  پنل تغییر کرد '
        bot.edit_message_text(Text_0 , call.message.chat.id , call.message.message_id , reply_markup=botkb.changin_panel_capcity(panel_pk=panel_id))
            
    except Exception as changepanelsalemode_error :
        print(f'An ERROR occured in [panels.py  - LINE 272- FUNC change_panel_salemode] \n\n\t Error-msg :{changepanelsalemode_error}')



# ------------------------- < Panel_AllCapcity > 

def change_panel_allcapcity(bot , message ,panel_id):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n تغییر ظرفیت-کلی پنل لغو شد'  
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.changin_panel_capcity(panel_pk=panel_id))
    else:
        if message.text.isdigit():
            try: 
                panel_=v2panel.objects.get(id=panel_id)
                panel_new_all_capcity=message.text
                panel_.all_capcity=panel_new_all_capcity
                panel_.sold_capcity = 0
                panel_.save()

                Text_2='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n ظرفیت-کلی پنل تغییر کرد '        
                bot.send_message(message.chat.id , Text_2 , reply_markup=botkb.changin_panel_capcity(panel_pk=panel_id))

            except Exception as changeallcapcity_error :
                print(f'An ERROR occured in [panels.py  - LINE 295- FUNC change_panel_allcapcity] \n\n\t Error-msg :{changeallcapcity_error}')
        else: 
            Text_3='❌برای تغییر ظرفیت کلی پنل مقدار عددی ارسال کنید'
            bot.send_message(message.chat.id  , Text_3)  
            bot.register_next_step_handler(message , lambda message: change_panel_allcapcity(bot , message , panel_id))



# ------------------------- < Panel_QRcode > 
def change_panel_qrcode(bot , call , panel_id ):
    if call.data.startswith('qrcode_sending_'):
        panel_=v2panel.objects.get(id=panel_id)
        try:
            if panel_.send_qrcode_mode==0: 
                new_send_qrcode_moode=1 #/send subscriptions QR
                panel_.send_qrcode_mode=new_send_qrcode_moode 
                panel_.save()   

            elif panel_.send_qrcode_mode==1:
                new_send_qrcode_moode=2 #/send config QR
                panel_.send_qrcode_mode=new_send_qrcode_moode 
                panel_.save()    

            else:
                new_send_qrcode_moode=0 #/dont send any
                panel_.send_qrcode_mode=new_send_qrcode_moode 
                panel_.save()  

            Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n حالت ارسال کیوارکد پنل تغییر کرد '   
            bot.edit_message_text(Text_1,call.message.chat.id , call.message.message_id , reply_markup= botkb.how_to_send_links(panel_id))

        except Exception as changepanelqrcodemode_error:
            print(f'An ERROR occured in [panels.py  - LINE 327- FUNC change_panel_qrcode] \n\n\t Error-msg {changepanelqrcodemode_error}')



# ------------------------- < Panel_Config > 
def change_panel_config(bot , call , panel_id):
    if call.data.startswith('link_sending_'):
        panel_=v2panel.objects.get(id=panel_id)
        try:
            if panel_.send_links_mode==0:
                new_send_links_mode=1
                panel_.send_links_mode=new_send_links_mode
                panel_.save()    

            elif panel_.send_links_mode==1:
                new_send_links_mode=2
                panel_.send_links_mode=new_send_links_mode
                panel_.save()    

            else:
                new_send_links_mode=0
                panel_.send_links_mode=new_send_links_mode
                panel_.save()  

            Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید\n\n حالت ارسال کانفیگ پنل تغییر کرد '
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id ,reply_markup=botkb.how_to_send_links(panel_id))

        except Exception as changepanellinkmode_error:
            print(f'An ERROR occured in [panels.py  - LINE 355- FUNC change_panel_config] \n\n\t Error-msg :{changepanellinkmode_error}')
        

# ------------------------- < Panel_State > 
def panel_state (panel_id = int):
    panel_state = panelsapi.marzban(panel_id= int(panel_id)).system_info()
    total_mem = panel_state['mem_total'] / (1024 * 1024 * 1024)
    used_mem = panel_state['mem_used'] / (1024 * 1024 * 1024)
    incom = panel_state['incoming_bandwidth'] / (1024 * 1024 * 1024 * 1024)
    outcom = panel_state['outgoing_bandwidth'] / (1024 * 1024 * 1024 * 1024)
    panel_state_txt = f"""
─👥 کل کاربران : {panel_state['total_user']}
─ 🙌🏻کاربران فعال :‌{panel_state['users_active']}

  ┊─ 🔗هسته های پردازشگر : {panel_state['cpu_cores']} عدد
  ┊─ 🧮پردازشگر مصرفی : {panel_state['cpu_usage']} %

  ┊─ 📊کل حافظه : {round(total_mem , 2)} GB
  ┊─ 📈حافظه مصرفی : {round(used_mem , 2)} MB

  ┊─ ⬇️پهنای باند ورودی : {round(incom , 4)} TB
  ┊─ ⬆️پهنای باند خروجی :‌ {round(outcom , 4)} TB

┘ - 📍ورژن : ‌{panel_state['version']}

.        
        """
    return panel_state_txt



# ------------------------- < Check_Capcity > 
def check_capcity(panel_id = int):
    panels_ = v2panel.objects.get(id = panel_id)
    try : 
        if panels_.capcity_mode == 1:
            if panels_.all_capcity > 0 :
                panels_.all_capcity -= 1
                panels_.sold_capcity += 1

            if panels_.all_capcity == 0:
                panels_.capcity_mode = 0

            panels_.save()

    except Exception as checkcapcity_error:
        print(f'An ERROR occured in [PANEL_managing.py  - LINE 401 - FUNC check_capcity] \n\n\t Error-msg :{checkcapcity_error}')


