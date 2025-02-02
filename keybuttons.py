from telebot.types import InlineKeyboardMarkup , InlineKeyboardButton , WebAppInfo
from mainrobot.models import v2panel ,panelinbounds ,products , admins , users , channels , subscriptions , botsettings , shomarekart
import re ,  datetime , jdatetime



class BotkeyBoard:


# ------------------------------------------------------------
# -----------------------------------------------------------------
# ----------------------------------------------------------------------
# ---------------------------------------------------------------------------
#--------------------------------------- User-Side -----------------------------------------------#
# ---------------------------------------------------------------------------
# ----------------------------------------------------------------------
# -----------------------------------------------------------------
# ------------------------------------------------------------



    @staticmethod
    def main_menu_in_user_side(userId : int) :
        keyboard = InlineKeyboardMarkup()
        #web_app_url = 'https://59c1-188-215-166-184.ngrok-free.app/products/'
        #webappinfo = WebAppInfo(url = web_app_url)
        user_side_ui_buttom = [[InlineKeyboardButton('🚀 خرید سرویس جدید' , callback_data ='buy_service')] ,
                               [InlineKeyboardButton('📡 وضعیت سرویس' , callback_data ='service_status'), InlineKeyboardButton('🔄 تمدید سرویس ' , callback_data ='tamdid_service')] ,
                               [InlineKeyboardButton('📖 حساب کاربری',callback_data ='wallet_profile')]
                              ]
        
        for rows in user_side_ui_buttom:
            keyboard.add(*rows)

        #button_webapp = InlineKeyboardButton('خرید از وبسایت', web_app=webappinfo)
        #keyboard.add(button_webapp)

        for i in admins.objects.all() :
            if userId == i.user_id and (i.is_owner == 1 or i.is_admin == 1) :
                button_robot_management = InlineKeyboardButton(text = '⚙️ مدیریت ربات',callback_data = 'robot_management')
                keyboard.add(button_robot_management)

        return keyboard
    


# ------------------------------------------------------------------------------------------
# ------------------------- Buy-Section --------------------------------------------------------------------------------------->
# ------------------------------------------------------------------------------------------

    @staticmethod 
    def choosing_panels_in_buying_section():
        keyboard = InlineKeyboardMarkup()
        panels_ = v2panel.objects.all()

        buttons_panel_list = []
        if panels_.count() >= 2:
            for i in panels_:
                if i.panel_status == 1:
                    button = InlineKeyboardButton(text= str(i.panel_name), callback_data=f'twopanelbuyservice_panelpk_{str(i.pk)}')
                    buttons_panel_list.append(button)
            button_back = InlineKeyboardButton(text='✤ - بازگشت به منوی قبلی - ✤' , callback_data='back_from_choosing_panels')
        keyboard.add(*buttons_panel_list , button_back , row_width=1)

        return keyboard



    @staticmethod
    def confirmation(tamdid = False):
        keyboard = InlineKeyboardMarkup()
        verify_data = 'verify_product' if tamdid is False else 'verify_product_for_tamdid'
        verify_data_back = 'back_from_confirmation' if tamdid is False else 'back_from_confirmation_tamdid'
        
        button_1 = InlineKeyboardButton('✅ تایید محصول ' , callback_data = verify_data)
        button_2 = InlineKeyboardButton('✤ - بازگشت به منوی قبلی - ✤' , callback_data = verify_data_back)
       
        keyboard.add(button_1 , button_2 , row_width = 1)
        
        return keyboard



    @staticmethod 
    def payby_in_user_side(tamdid:bool= False):
        keyboard = InlineKeyboardMarkup()
        botsettings_ = botsettings.objects.values('wallet_pay' , 'kartbkart_pay')[0]

        data_wallet = 'pay_with_wallet' if tamdid is False else 'tamdid_pay_with_wallet'
        data_card = 'pay_with_card' if tamdid is False else 'tamdid_pay_with_card'
        back_data = 'back_from_payment' if tamdid is False else 'tamdid_back_from_payment'

        pay_options = []

        if botsettings_['wallet_pay'] == 1 and botsettings_['kartbkart_pay'] == 1:
            pay_options.append(('👝 پرداخت با کیف پول' , data_wallet))
            pay_options.append(('💳پرداخت کارت به کارت' , data_card))

        elif botsettings_['wallet_pay'] == 1:
            pay_options.append(('👝 پرداخت با کیف پول' , data_wallet))    

        elif botsettings_['kartbkart_pay'] == 1:
            pay_options.append(('💳پرداخت کارت به کارت' , data_card))

        for text , data in pay_options:
            buttons = InlineKeyboardButton(text = text , callback_data = data)
            keyboard.add(buttons , row_width = 1)
        
        back_button = InlineKeyboardButton('✤ - بازگشت به منوی قبلی - ✤', callback_data=back_data)
        keyboard.add(back_button)

        return keyboard
    



    @staticmethod 
    def agree_or_disagree(user_id , tamdid:bool=False):
        keyboard = InlineKeyboardMarkup()
        data_agree =  f'agree_{user_id}' if tamdid is False else   f'tamdidagree_{user_id}'
        data_disagree = f'disagree_{user_id}' if tamdid is False else  f'tamdiddisagree_{user_id}'

        rows = [InlineKeyboardButton(text ='✅ تایید پرداخت ', callback_data = data_agree),
                InlineKeyboardButton(text ='❌ رد پرداخت ', callback_data = data_disagree)]
        keyboard.add(*rows)
        
        return keyboard    
    


# ------------------------- < Tamdid-Section > 
    
    @staticmethod
    def show_user_subsctription(user_id):
        keyboard = InlineKeyboardMarkup()
        user_ = users.objects.get(user_id = user_id)
        subscriptions_ = subscriptions.objects.filter(user_id = user_)
        
        if subscriptions_.count() >= 1:
            for i in subscriptions_.order_by('created_date').reverse():
                buttons = InlineKeyboardButton(text= i.user_subscription , callback_data= f'Tamidi:{i.user_subscription}:{i.user_id.user_id}')
                keyboard.add(buttons)
        else :
            return 'no_sub_user_have'
        back_button = InlineKeyboardButton('✤ - بازگشت به منوی قبلی - ✤' , callback_data='back_from_user_tamdid_service')
        keyboard.add(back_button)

        return keyboard
    



# ------------------------------------------------------------------------------------------
# ------------------------- Service-Status --------------------------------------------------------------------------------------->
# ------------------------------------------------------------------------------------------

# ------------------------- < ShowService-Section > 
    @staticmethod
    def show_service_status(user_id , show_user_info = None):
        keyboard = InlineKeyboardMarkup()
        users_ = users.objects.get(user_id = user_id)
        subscriptions_ = subscriptions.objects.filter(user_id = users_).order_by('created_date').reverse()
        back_button_data = 'back_from_service_status' if show_user_info is None else "back_from_show_user_info"
        
        
        buttons_list = []
        for i in subscriptions_:
            user_sub_data = f'serviceshow.{users_.user_id}.({i.user_subscription})' if show_user_info is None else f'showuserinfo.{users_.user_id}.({i.user_subscription})'
            buttons = InlineKeyboardButton(text= i.user_subscription , callback_data=user_sub_data)
            buttons_list.append(buttons)


        button_notinlist = InlineKeyboardButton(text='🚦 سرویس من در لیست نیست 🚦'  , callback_data='service_not_inlist')
        button_showuserinfo_other = InlineKeyboardButton(text='👀جست و جوی کاربر دیگری 👀'  , callback_data='show_user_info_other')
        button_back = InlineKeyboardButton(text='✤ - بازگشت به منوی قبلی - ✤'  , callback_data=back_button_data)


        if show_user_info is None :
            keyboard.add(*buttons_list, button_notinlist, button_back, row_width=1)
        else :
            keyboard.add(*buttons_list, button_showuserinfo_other, button_back, row_width=1)

        return keyboard
    


# ------------------------- < ServiceInfo-Section > 
    @staticmethod 
    def user_service_status(request , config_name = None):
        keyboard = InlineKeyboardMarkup( )
        
        service_status = '✅ فعال' if request['status'] == 'active' else '❌ غیر فعال'
        used_traffic = request['used_traffic'] / ( 1024 * 1024 * 1024)


        online_at = request['online_at'] if request['online_at'] is not None else 'empty'
        if online_at != 'empty':
            dt = datetime.datetime.strptime(online_at.split('.')[0] , '%Y-%m-%dT%H:%M:%S')
            last_online = jdatetime.datetime.fromgregorian(datetime=dt)
        else:
            last_online = 'بدون اتصال'

        serviceinfo_rawbuttons = [
                                [(f'{service_status}' , 'en_di_service') , ('وضعیت سرویس ' , 'en_di_service')], 
                                [(f'{round(used_traffic , 2)} گیگ ' , f'config_usage.{config_name}') , ('🔋حجم مصرفی' , f'config_usage.{config_name}')],
                                [(f'{str(last_online)}' , 'last_connection') , ('👁‍🗨زمان آخرین اتصال' , 'last_connection')],
                                [('📥 دریافت لینک اشتراک' , f'get_config_link.{config_name}') , ('🖼 دریافت QRcode اشتراک' , f'get_qrcode_link.{config_name}')],
                                [('❌ حذف لینک فعلی و دریافت لینک جدید ❌' ,  f'get_new_link.{config_name}')],
                                [('❌ حذف کامل اشتراک ❌' , f'get_removing_account.{config_name}')],
                                [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_user_service_status')],
                                ]   
        
        for row in serviceinfo_rawbuttons:
            button_list = []
            for text , data in row:
                buttons = InlineKeyboardButton(text = text , callback_data = data)
                button_list.append(buttons)
            keyboard.add(*button_list)


        return keyboard

# ------------------------------------------------------------------------------------------
# ------------------------- Wallet-Profile --------------------------------------------------------------------------------------->
# ------------------------------------------------------------------------------------------


    @staticmethod 
    def wallet_profile(user_id , info  = False):
        keyboard = InlineKeyboardMarkup()        
        user_ = users.objects.get(user_id = user_id)
        botsettings_ = botsettings.objects.values('moneyusrtousr')

        info_box = []     
        userid = user_.user_id
        username = f"@{user_.username}" if user_.username else '-'
        user_wallet = format(int(user_.user_wallet) , ',') + ' تومان '
        first_last_name = user_.first_name  if user_.first_name else '-' + user_.last_name if user_.last_name else '-'
        
        userinfo_rawbutton =[ 
                            [(first_last_name , 'fist_last_name') , ('👤- نام ' , 'fist_last_name')] ,
                            [(userid , 'user_id') , ('#️⃣ - ایدی عددی ' , 'user_id')] , 
                            [(username , 'username') , ('🌀- یوزرنیم' , 'username')] , 
                            [(user_wallet, 'wallet') , ('👝- کیف پول' , 'wallet')] , 
                            # place for moneyusrtousr
                            [('شارژ کیف پول 💰' , f'charge_wallet_{userid}')],
                            [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_wallet_profile' )]
                            ]
            
        info_box.append(userid)
        info_box.append(username)
        

        if botsettings_[0]['moneyusrtousr'] == 1 :
                userinfo_rawbutton.insert(4 , [('انتقال وجه به کاربر 💸 ' , 'tranfert_money_from_wallet')])


        for i in userinfo_rawbutton :
            buttons_list = []
            for text , data in i:
                button = InlineKeyboardButton(text= text , callback_data=  data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)


        if info == False :
            return keyboard
        else :
            return info_box 
        

    @staticmethod 
    def wallet_accepts_or_decline(user_unique_id):
        keyboard = InlineKeyboardMarkup()

        rows = [InlineKeyboardButton(text ='✅ تایید پرداخت ', callback_data= f'wallet_accepts_{user_unique_id}'),
                InlineKeyboardButton(text ='❌ رد پرداخت ', callback_data =f'wallet_decline_{user_unique_id}')]
        keyboard.add(*rows)
        
        return keyboard  
    













# ------------------------------------------------------------
# -----------------------------------------------------------------
# ----------------------------------------------------------------------
# ---------------------------------------------------------------------------
#--------------------------------------- admin-side -----------------------------------------------#
# ---------------------------------------------------------------------------
# ----------------------------------------------------------------------
# -----------------------------------------------------------------
# ------------------------------------------------------------







# ------------------------------------------------------------------------------------------
# ------------------------- Panel-Management --------------------------------------------------------------------------------------->
# ------------------------------------------------------------------------------------------

    @staticmethod
    def panels_management_menu_keyboard(): 
        keyboard = InlineKeyboardMarkup()
        raw_buttons =[[('➖ حذف کردن پنل ' , 'remove_panel') , ('➕ اضافه کردن پنل' , 'add_panel')] ,
                      [('🔩 مدیریت پنل ','manageing_panels')] ,
                      [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_panels_management')]]
        
        for i in raw_buttons:
            buttons_list = []
            for text , data in i:
                buttom = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(buttom)
            keyboard.add(*buttons_list)

        return keyboard
    

    
# ------------------------- < Add-Panel > 
    @staticmethod
    def panel_type():
        keyboard = InlineKeyboardMarkup()
        button_1 = InlineKeyboardButton(text='مرزبان' , callback_data='marzban_panel')
        back_button = InlineKeyboardButton(text='✤ - بازگشت به منوی قبلی - ✤' , callback_data='cancel_adding_panel')
        keyboard.add(button_1 , back_button , row_width=1)

        return keyboard


    @staticmethod 
    def inbounds_adding(panel_id = None):
        keyboard = InlineKeyboardMarkup()
        panel_ = v2panel.objects.get(id = panel_id)
        panelinbounds_ = panelinbounds.objects.filter(panel_id = panel_)

        raw_buttons= []
        if panelinbounds_.count() >= 1:
            for i in panelinbounds_:
                buttons = [(str(i.inbound_name) , f'template_panel_{i.pk}')]
                raw_buttons.append(buttons)
            
        raw_buttons.append([('اضافه کردن تمپلت اینباند' , f'add_inbounds_template_{panel_.pk}')])
        raw_buttons.append([('✤ - بازگشت به منوی قبلی - ✤' , f'back_from_template_inbouds_{panel_.pk}')])

        for i in raw_buttons:
            buttons_list = []
            for text , data in i:
                button = InlineKeyboardButton(text=text ,callback_data=data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)
        
        return keyboard



    @staticmethod 
    def select_inbounds(inbound_selected:any=None , panelid=None , inbound_id=None):
        keyboard=InlineKeyboardMarkup(row_width=1)
        buttons_list=[]

        if inbound_selected is not None:
            for i in inbound_selected:
                button = InlineKeyboardButton(text=i  , callback_data=i)
                buttons_list.append(button)
        keyboard.add(*buttons_list)

        done_buttons = InlineKeyboardButton('اتمام و ذخیره  🧷' , callback_data=f'done_inbounds_{panelid}_{inbound_id}')
        back_buttons = InlineKeyboardButton(' بازگشت و لغو ثبت  ↪️ ' , callback_data=f'back_from_inbounds_selecting_{panelid}_{inbound_id}')
        keyboard.add(done_buttons , back_buttons)
        return keyboard 
        


# ------------------------- < Remove-Panel > 
    @staticmethod 
    def panel_management_remove_panel(panel_pk:int=None , kind=False , page =1 , item_per_page=6):
        keyboard = InlineKeyboardMarkup()
        keyboard_2 = InlineKeyboardMarkup()
        panels_ = v2panel.objects.all() 

        raw_buttons = [[('حذف ' , 'remove_actions') , ('ادرس پنل' , 'panel_removal_url') , ('نام پنل ' , 'panel_removal_name')]]

        if not panels_.exists():
            return 'no_panel_to_remove'
        else : 
            for i in panels_:
                call_back_data= f'panel_remove_{i.pk}'
                panel_url_shows= re.sub(r'(http|https)://' , '' , i.panel_url)
                panel_raw_buttons= [('❌' , call_back_data ) , (panel_url_shows , call_back_data) , (i.panel_name , call_back_data)]
                raw_buttons.append(panel_raw_buttons)


        panel_number = panels_.count()
        total_pages = (panel_number + item_per_page - 1) // item_per_page

        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        start = (page-1) * item_per_page
        end = start + item_per_page

        for ind , row   in enumerate(raw_buttons , 0):
            button_list =[]
            if start < ind <= end:
                for text , data in row:
                    button = InlineKeyboardButton(text=text , callback_data=data)
                    button_list.append(button)
                keyboard.add(*button_list)
        
        next_prev_buttons =[InlineKeyboardButton(text='صفحه بعدی ⏪' , callback_data =f'show_panel_remove_{page +1}') , 
                            InlineKeyboardButton(text='صفحه قبل ⏩' , callback_data =f'show_panel_remove_{page - 1}')]
        
        
        if page == 1 and total_pages > 1:
            keyboard.add(next_prev_buttons[0])
        elif page > 1:
            if page < total_pages:
                keyboard.add(*next_prev_buttons)
            else:
                keyboard.add(next_prev_buttons[1]) 

        
        back_button_manage_panel = InlineKeyboardButton('✤ - بازگشت به منوی قبلی - ✤' , callback_data = 'back_to_manage_panel')
        keyboard.add(back_button_manage_panel)



        raw_buttons =[[('حذف پنل و تمامی محصولات مرتبط', f'remove_products_panel_{panel_pk}') , ('فقط حذف پنل ' , f'remove_only_panel_{panel_pk}')] , 
                        [('✤ - بازگشت به منوی قبلی - ✤' , 'back_to_remove_panel_section')]]
       
        for row in raw_buttons:
            button_list=[]
            for text , data in row:
                button=InlineKeyboardButton(text=text , callback_data=data)
                button_list.append(button)
            keyboard_2.add(*button_list)


        if kind is False :
            return keyboard
        else :
            return keyboard_2
        



# ------------------------- < managing-Panel >

    @staticmethod 
    def panels_management_managing_panels(page = 1 , item_per_page = 6):
        keyboard = InlineKeyboardMarkup()
        panels_ = v2panel.objects.all()

        raw_buttons = [[('مدیریت پنل' , 'manage_panel_') , ('وضعیت پنل' , 'panel_status') , ('نام پنل', 'panel_name')]]
        
        panel_number = panels_.count()
        total_pages = (panel_number + item_per_page - 1) // item_per_page

        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        start = (page-1) * item_per_page
        end = start + item_per_page

        if not panels_.exists() : 
            return 'no_panel_to_manage'
        else :
            for i in panels_:
                panel_status_out='🟢فعال' if i.panel_status==1 else '🔴غیرفعال'
                panel_id=f'managing_panel_{i.pk}'
                panels_raw_buttons=[('⚙️' , panel_id) , (panel_status_out , panel_id) , (i.panel_name , panel_id)]
                raw_buttons.append(panels_raw_buttons)

        for inx , row  in enumerate(raw_buttons , 0):
            bottom_row=[]
            if start < inx <= end:
                for text , data in row:
                    bottom_row_buttons=InlineKeyboardButton(text=text , callback_data=data )
                    bottom_row.append(bottom_row_buttons)
                keyboard.add(*bottom_row)

        next_prev_buttons =[InlineKeyboardButton(text='صفحه بعدی ⏪' , callback_data =f'show_panel_manage_{page +1}') , 
                            InlineKeyboardButton(text='صفحه قبل ⏩' , callback_data =f'show_panel_manage_{page - 1}')]
            
        if page == 1 and total_pages > 1:
            keyboard.add(next_prev_buttons[0])
        elif page > 1:
            if page < total_pages:
                keyboard.add(*next_prev_buttons)
            else:
                keyboard.add(next_prev_buttons[1]) 

        back_button = InlineKeyboardButton('✤ - بازگشت به منوی قبلی - ✤' , callback_data = 'back_to_manageing_panels')   
        keyboard.add(back_button) 

        return keyboard
        


    @staticmethod
    def manage_selected_panel(panel_pk:int , passwd:bool=False , username:bool=False):
        keyboard = InlineKeyboardMarkup()

        panel_ = v2panel.objects.get(id = panel_pk)
        panel_status_out= '🟢فعال' if panel_.panel_status == 1 else  '🔴غیرفعال'
        panel_reality_flow_out='None' if panel_.reality_flow=='' else panel_.reality_flow  
        panel_url_shows=re.sub(r'(http|https)://' , '' , panel_.panel_url)

        raw_buttons=[[(str(panel_status_out) , f'panel_status_{panel_.pk}' ) , ('وضعیت پنل' , f'panel_status_{panel_.pk}')] ,
                    [(str(panel_.panel_name) , f'panel_name_{panel_.pk}_{panel_.panel_name}') , ('نام پنل ' , f'panel_name_{panel_.pk}_{panel_.panel_name}')] , 
                    [(str(panel_url_shows) , f'panel_url_{panel_.pk}_{panel_url_shows}') , ('ادرس پنل' , f'panel_url_{panel_.pk}_{panel_url_shows}')] ,   

                    [((str(panel_.panel_type)) , f'panel_type_{panel_.pk}') , ('نوع پنل ' , f'panel_type_{panel_.pk}')],
                    [(str(panel_reality_flow_out) , f'reality_flow_{panel_.pk}') , ('reality-flow💡' , f'reality_flow_{panel_.pk}')],
                    [('🧷 تنظیمات اینباندها' , f'inbound_settings_{panel_.pk}'), ('🔖نوع ارسال اشتراک ' ,  f'send_config_{panel_.pk}')],

                    [('⚙️' , f'panel_capacity_{panel_.pk}') , ('🧮ظرفیت پنل' ,  f'panel_capacity_{panel_.pk}')],
                    [('📊آمار پنل ' , f'panel_statics_{panel_.pk}')],
                    [('✤ - بازگشت به منوی قبلی - ✤' , 'back_to_manage_panel')]]
        
        for row in raw_buttons:
            buttons_list = []
            for text , data in row :
                button = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(button)
            keyboard.add(*buttons_list )

        return keyboard
    

    @staticmethod
    def changin_reality_flow(panelpk = None):
        keyboard=InlineKeyboardMarkup()
        raw_buttons =[[('xtls-rprx-vision' , f'xtls-rprx-vision_{panelpk}') , ('None' , f'None_realityFlow_{panelpk}')]]
        for i in raw_buttons:
            buttons_list=[]
            for text,data in i:
                buttons=InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(buttons)
            keyboard.add(*buttons_list )
    
        return keyboard



    @staticmethod 
    def changin_panel_capcity(panel_pk):
        keyboard=InlineKeyboardMarkup()
        #= sale-mode 0 : باز \ sale-mode 1 : بسته 
        #= capcity-mode 0 : بدون ظرفیت \ capcity-mode : 1 ظرفیت نامحدود \ sale-mode : 2 دارای ظرفیت

        panel_ = v2panel.objects.get(id=panel_pk)

        capcity_mode = 'بدون ظرفیت' if panel_.capcity_mode == 0 else 'دارای ظرفیت' if panel_.capcity_mode == 1 else 'ظرفیت نامحدود'
        sale_mode = 'بسته' if panel_.sale_mode ==  0 else 'باز'
        
        all_capcity =  int(panel_.all_capcity) if panel_.all_capcity > 0  else 0
        sold_capcity = panel_.sold_capcity if panel_.sold_capcity > 0 else 0
        remaing_capacity= (int(all_capcity) - int(panel_.sold_capcity)) if panel_.all_capcity > 0 else 0


        raw_buttons= [[(capcity_mode , f'capcity_mode_{panel_.pk}') , ('🎚نوع ظرفیت ' , f'capcity_mode_{panel_.pk}')] ,
                    [(sale_mode , f'sale_mode_{panel_.pk}') , ('💸حالت فروش' , f'sale_mode_{panel_.pk}')] ,

                    [(f"{abs(all_capcity)} عدد" , f'all_capcity_{panel_.pk}_{panel_.all_capcity}') , ('🔋ظرفیت کلی' , f'all_capcity_{panel_.pk}_{panel_.all_capcity}')] ,
                    [(f"{abs(sold_capcity)} عدد" , 'sold_capcity') , ('💰ظرفیت فروش رفته' , 'sold_capcity')],

                    [(f"{abs(remaing_capacity)} عدد" , 'remaining_capcity') , ('⏳ظرفیت باقی مانده ' , 'remaining_capcity')] ,
                    [('✤ - بازگشت به منوی قبلی - ✤' , f'back_from_panel_capcity_list_{panel_.pk}')]]
        
        for row in raw_buttons:
            buttons_list=[]
            for text, callback_data in row:
                button = InlineKeyboardButton(text=text , callback_data=callback_data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)

        return keyboard



    @staticmethod 
    def manage_inbound_template(templateid):
        keyboard = InlineKeyboardMarkup()
        panelinbound_ = panelinbounds.objects.get(id = templateid)
        raw_buttons = [[('تغییر نام' , f'change_template_name_{panelinbound_.pk}_{panelinbound_.panel_id.pk}')],
                       [('تغییر اینباند' , f'change_template_inbounds_{panelinbound_.pk}_{panelinbound_.panel_id.pk}') , ('حذف اینباند' , f'remove_template_inbounts_{panelinbound_.pk}_{panelinbound_.panel_id.pk}')],
                       [('✤ - بازگشت به منوی قبلی - ✤' , f'back_from_inbound_chaning_{panelinbound_.pk}_{panelinbound_.panel_id.pk}')]
                       ]

        for row in raw_buttons:
            buttons_list = []
            for text , data in row:
                button= InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)
        
        return keyboard


    @staticmethod
    def how_to_send_links(panel_pk):
        keyboard=InlineKeyboardMarkup()
        panel_=v2panel.objects.get(id=panel_pk)

        send_link = 'عدم ارسال' if panel_.send_links_mode == 0 else 'لینک هوشمند' if panel_.send_links_mode == 1 else 'لینک کانفیگ'
        send_qrcode = 'عدم ارسال' if panel_.send_qrcode_mode == 0 else 'لینک هوشمند' if panel_.send_qrcode_mode == 1 else 'لینک کانفیگ'

        raw_buttons = [[('👇🏻QR-code نوع ارسال' , f'qrcode_sending_{panel_.pk}') , ('👇🏻نوع لینک ارسالی' , f'link_sending_{panel_.pk}')] ,
                       [(send_qrcode , f'qrcode_sending_{panel_.pk}') , (send_link , f'link_sending_{panel_.pk}')] , 
                       [('✤ - بازگشت به منوی قبلی - ✤' , f'back_from_panel_howtosend_list_{panel_.pk}')]]
        
        for i in raw_buttons:
            buttons_list=[]
            for text , data in i:
                button = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)

        return keyboard
    

    @staticmethod 
    def updating_panel (panel_id=int):
        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton('بروزرسانی 🔄' , callback_data=f'updating_panel_{panel_id}')
        button_back = InlineKeyboardButton('✤ - بازگشت به منوی قبلی - ✤' , callback_data=f'back_from_panel_static_{panel_id}')
        keyboard.add(button , button_back , row_width=1)
        return keyboard






# -------------------------Products-Management -----------------------------------------------------------------------------


    @staticmethod
    def products_management_menu_keyboard():
        keyboard =InlineKeyboardMarkup()
        raw_buttons = [[('➖حذف کردن محصول' , 'remove_products') , ('➕اضافه کردن محصول' , 'add_product')],
                       [('🔩مدیریت محصولات'  , 'manage_products')],
                       [('✤ - بازگشت به منوی قبلی - ✤'  , 'back_from_products_managing' )]]
        
        for i in raw_buttons: 
            buttons_list=[]
            for text , data in i:
                buttom = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(buttom)
            keyboard.add(*buttons_list)
        return keyboard
    


    @staticmethod
    def load_panel_add_product(add_product=False , remove_product=False , manage_product=False):
        keyboard=InlineKeyboardMarkup()
        panel_=v2panel.objects.all()

        if not panel_.exists():
            return "no_panel_add_product"
        else:
            if add_product is not False:
                call_data = "add_product"

            elif remove_product is not False:
                call_data = "remove_products"

            elif manage_product is not False :
                call_data = 'managing_products'

            for i in panel_:
                buttons= InlineKeyboardButton(text=i.panel_name , callback_data = f'{call_data}_{i.pk}')
                keyboard.add(buttons)

            product_no_panel = products.objects.filter(panel_id__isnull=True).all().count() 
            if remove_product is not False and product_no_panel >=1 :
                keyboard.add(InlineKeyboardButton('محصولات بدون پنل' , callback_data='products_without_panel'))
            back_button_add = InlineKeyboardButton(text = '✤ - بازگشت به منوی قبلی - ✤'  , callback_data = f'back_products{call_data}')
            keyboard.add(back_button_add)

            return keyboard
           


# ------------------------- < Adding-proudcts >
    @staticmethod 
    def loading_panles_inbounds_for_producs(panelid=None):
        keyboard=InlineKeyboardMarkup()
        panels_ = v2panel.objects.get(id = panelid)
        panelinbounds_ = panelinbounds.objects.filter(panel_id = panels_)

        for i in panelinbounds_:
            button= InlineKeyboardButton(text=i.inbound_name , callback_data=f'inbound_number_{i.pk}')
            keyboard.add(button)

            
        return keyboard
    

# ------------------------- < Removing-proudcts >

    @staticmethod 
    def product_managemet_remove_products(panelid = None , page:int=1 , item_per_page:int=8) :
        keyboard=InlineKeyboardMarkup()
        panels_ = v2panel.objects.get(id = panelid)
        products_=products.objects.filter(panel_id= panels_)
 

        raw_buttons = [[('حذف' , 'remove_actions') , ('آدرس پنل' , 'related_panel_url') , ('نام محصول' , 'product_removal_name')]]        

        product_number = products_.count()
        total_pages = (product_number + item_per_page  -1 ) // item_per_page
        
        if page < 1:
            page = 1 
        elif page > total_pages:
            page = total_pages

        start = (page-1) * item_per_page
        end = start + item_per_page

        if not products_.exists():
            return 'no_products_to_remove'
        else:
            for i , product in enumerate(products_ , 1): 
                if  start < i <= end:
                    panelurl=re.sub(r'(http|https)://' , '' ,  panels_.panel_url)
                    product_id=f'delete_prodcut_{product.pk}_{panels_.pk}'
                    products_buttons = [('❌' , product_id) , (panelurl , product_id) , (product.product_name , product_id)]
                    raw_buttons.append(products_buttons)

        for row in raw_buttons:
                bottos_list=[]
                for text , data in row:
                    buttos = InlineKeyboardButton(text = text , callback_data = data)
                    bottos_list.append(buttos)
                keyboard.add(*bottos_list)


        next_prev_buttons = [InlineKeyboardButton(text='صفحه بعدی ⏪' , callback_data = f'show_product_remove_{page +1}_{panels_.pk}') , 
                            InlineKeyboardButton(text='صفحه قبل ⏩' , callback_data = f'show_product_remove_{page - 1}_{panels_.pk}')]
        
        if page ==1 and total_pages >1:
            keyboard.add(next_prev_buttons[0])
        elif page>1:
            if page<total_pages:
                keyboard.add(*next_prev_buttons)
            else:
                keyboard.add(next_prev_buttons[1])


        back_button=InlineKeyboardButton(text ='✤ - بازگشت به منوی قبلی - ✤' , callback_data='back_from_remove_products')  
        keyboard.add( back_button )

        return keyboard


    @staticmethod 
    def product_managemet_remove_null_products(page:int=1 , item_per_page:int=8) :
        keyboard=InlineKeyboardMarkup()
        products_=products.objects.filter(panel_id__isnull=True)

        raw_buttons = [[('حذف' , 'remove_actions') , ('آدرس پنل' , 'related_panel_url') , ('نام محصول' , 'product_removal_name')]]        
        product_number = products_.count()
        total_pages = (product_number + item_per_page  -1 ) // item_per_page
        
        if page < 1:
            page = 1 
        elif page > total_pages:
            page = total_pages

        start = (page-1) * item_per_page
        end = start + item_per_page

        if not products_.exists():
            return 'no_null_products_to_remove'
        else:
            for i , product in enumerate(products_ , 1): 
                if  start < i <= end:
                    panelurl='بدون پنل'
                    product_id=f'delete_null_prodcut_{product.pk}'
                    products_buttons = [('❌' , product_id) , (panelurl , product_id) , (product.product_name , product_id)]
                    raw_buttons.append(products_buttons)

        for row in raw_buttons:
                bottos_list=[]
                for text , data in row:
                    buttos = InlineKeyboardButton(text = text , callback_data = data)
                    bottos_list.append(buttos)
                keyboard.add(*bottos_list)


        next_prev_buttons = [InlineKeyboardButton(text='صفحه بعدی ⏪' , callback_data = f'show_null_product_remove_{page +1}') , 
                            InlineKeyboardButton(text='صفحه قبل ⏩' , callback_data = f'show_null_product_remove_{page - 1}')]
        
        if page ==1 and total_pages >1:
            keyboard.add(next_prev_buttons[0])
        elif page>1:
            if page<total_pages:
                keyboard.add(*next_prev_buttons)
            else:
                keyboard.add(next_prev_buttons[1])


        back_button=InlineKeyboardButton(text ='✤ - بازگشت به منوی قبلی - ✤' , callback_data='back_from_remove_products')  
        keyboard.add( back_button )

        return keyboard




    @staticmethod
    def products_list(panelid , up:int=None , down:int=None , page:int=1 , item_per_page:int=5):
        keyboard=InlineKeyboardMarkup()
        panel_ = v2panel.objects.get(id = panelid)
        filtered_products=products.objects.filter(panel_id=panel_).order_by('sort_id')

        raw_buttons = [[('🔻پایین' , 'down') , ('🔺بالا' , 'up') , ('محصول' , 'product')]]

        sorted_filtered_list=[(prod.sort_id, prod.id) for prod in filtered_products]

        if up is not None:
            for pro_sortId , pro_id in sorted_filtered_list:
                if pro_id==sorted_filtered_list[up - 1][1]:
                    before_sort_id=sorted_filtered_list[up - 2][0]
                    after_sort_id=sorted_filtered_list[up - 1][0]
                    try:
                        product=products.objects.get(id=sorted_filtered_list[up - 1][1])
                        new_sort_id = before_sort_id 
                        product.sort_id = new_sort_id
                        product.save()
                        product2 = products.objects.get(id=sorted_filtered_list[up - 2][1])
                        new_sort_id_2=after_sort_id
                        product2.sort_id=new_sort_id_2
                        product2.save()
                    except Exception as up_error:
                        print(f'something wentwrong \\\ up section-1 \\\:{up_error}')



        if down is not None:
            for pro_sortId , pro_id in sorted_filtered_list:
                if pro_id==sorted_filtered_list[down - 1][1]:      
                    if down<=len(sorted_filtered_list) - 1: 
                        before_sort_id=sorted_filtered_list[down - 1][0]
                        after_sort_id=sorted_filtered_list[down][0]
                        try:
                            productـmain=products.objects.get(id=sorted_filtered_list[down - 1][1])
                            new_sort_id=after_sort_id 
                            productـmain.sort_id=new_sort_id
                            productـmain.save()
                            product2 = products.objects.get(id=sorted_filtered_list[down][1])
                            new_sort_id_2=before_sort_id
                            product2.sort_id=new_sort_id_2
                            product2.save() 
                        except Exception as down_error_1:
                            print(f'something wentwrong \\\ down seciotn-1 \\\ :{down_error_1}')     
                    elif down>=len(sorted_filtered_list)-1:
                        before_sort_id = sorted_filtered_list[down - 1][0]
                        after_sort_id = sorted_filtered_list[down - down][0]
                        try :
                            productـmain=products.objects.get(id=sorted_filtered_list[down - 1][1])
                            new_sort_id=after_sort_id 
                            productـmain.sort_id=new_sort_id
                            productـmain.save()

                            product2=products.objects.get(id=sorted_filtered_list[down - down][1])
                            new_sort_id_2=before_sort_id
                            product2.sort_id=new_sort_id_2
                            product2.save()   
                        except Exception as down_error_2:
                            print(f'something wentwrong \\\ down section-2 \\\ :{down_error_2}')

        product_number = filtered_products.count()
        total_pages = (product_number + item_per_page  - 1 ) // item_per_page
        
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        start = (page - 1) * item_per_page
        end = start + item_per_page
        
        if not filtered_products.exists():
            return 'no_product_to_manage'
        else:
            for num , (sort_id, produ_id) in enumerate(sorted_filtered_list):
                if start < num+1 <= end : 
                    product=products.objects.get(id=produ_id)
                    num=num+1 
                    bottom_row = [('👇🏻' , f'down_{num}_{panel_.pk}_{page}') ,('👆🏻' , f'up_{num}_{panel_.pk}_{page}') ,
                                  (product.product_name , f'detaling_product_{product.id}')]
                    raw_buttons.append(bottom_row)

        for row in raw_buttons:
            buttons_list = []
            for text , data in row:
                button = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)


        next_prev_buttons =[InlineKeyboardButton(text='صفحه بعدی ⏪' , callback_data =f'show_product_managements_{page +1}_{panel_.pk}') , 
                            InlineKeyboardButton(text='صفحه قبل ⏩' , callback_data =f'show_product_managements_{page - 1}_{panel_.pk}')]


        if page ==1 and total_pages > page:
            keyboard.add(next_prev_buttons[0])
        elif page > 1:
            if page > total_pages:
                keyboard.add(*next_prev_buttons)
            else:
                keyboard.add(next_prev_buttons[1])

        back_button = InlineKeyboardButton(text = '✤ - بازگشت به منوی قبلی - ✤' ,  callback_data = 'back_from_manage_products_list_updown')  
        keyboard.add( back_button , row_width = 1)

        return keyboard





    @staticmethod
    def product_changing_details(product_id:int):
        keyboard = InlineKeyboardMarkup()
        product_ =products.objects.get(id = int(product_id))
        data_limit_str = str(product_.data_limit) if product_.data_limit else 'N/A'
        product_price = format(product_.product_price , ',') + ' تومان'
        product_status='🟢' if product_.product_status == 1 else '🔴'

        raw_buttons=[[(product_status , f'_pr_status_{product_.pk}') , ('وضعیت محصول ' , f'_pr_status_{product_.pk}') ] ,
                    [(product_.product_name  , f"_product_name_{product_.pk}" ) , ('📝نام محصول' , f"_product_name_{product_.pk}")], 
                    [(data_limit_str + ' گیگ ', f'_data_limit_{product_.pk}') , ('🔋حجم محصول' , f'_data_limit_{product_.pk}')] ,
                    [(str(product_.expire_date) + ' روز ', f'ـexpire_date_{product_.pk}') , ('⏳مدت زمان ' , f'ـexpire_date_{product_.pk}')] ,
                    [(product_price , f'_product_price_{product_.pk}') , ('💸قیمت محمصول' , f'_product_price_{product_.pk}')],
                    [(product_.panelinbounds_id.inbound_name ,  f'_inbounds_product_{product_.pk}') , ('📡اینباند های محصول' , f'_inbounds_product_{product_.pk}')]]
            

        for  rows in raw_buttons:
            buttons_list = []
            for text , data in rows:
                button = InlineKeyboardButton(text = text , callback_data= data)
                buttons_list.append(button)
            keyboard.add(*buttons_list )

        back_button = InlineKeyboardButton(text =  '✤ - بازگشت به منوی قبلی - ✤' ,  callback_data = f'back_from_manage_product_changing_{product_.panel_id.pk}')  
        keyboard.add( back_button)


        return keyboard



    @staticmethod 
    def change_products_inbounds(panel_realated_inbound_id = None , product_id=None):
        keyboard=InlineKeyboardMarkup()
        panelinbounds_ = panelinbounds.objects.filter(panel_id = panel_realated_inbound_id)

        raw_buttons=[]
        for i in panelinbounds_:
            button = InlineKeyboardButton(text=i.inbound_name , callback_data=f'change_inbound_to_{i.pk}_{product_id}')
            raw_buttons.append(button)

        keyboard.add(*raw_buttons , row_width=1)

        return keyboard 





















# ------------------------- Admin-Side -------------------------------------------------------------------------------------

    @staticmethod 
    def management_menu_in_admin_side(user_id = None) :
        keyboard = InlineKeyboardMarkup()
        admins_ = admins.objects.get(user_id = user_id)


        admin_side_ui_buttom = [
                                [('🖥 مدیریت پنل ها ' , 'panels_management') , ('🎛مدیریت فروشگاه' , 'products_management')] ,
                                [('📈آمار ربات' , 'bot_statics')] , 
                                [('👤مدیریت کاربران', 'users_management'), ('🧑🏼‍💻مدیریت ادمین ها' , 'admins_management')] ,
                                [('🤖تنظیمات ربات ', 'bot_managment')]
                                ]
        
        if admins_.is_owner == 1 or (admins_.is_owner == 1 and admins_.is_admin ==1 ):
            admin_side_ui_buttom = admin_side_ui_buttom

        
        if admins_.is_admin == 1 and admins_.is_owner == 0:

            if admins_.acc_botmanagment == 0 :
                bot_setting = ('🤖تنظیمات ربات ', 'bot_managment')
                for inner in admin_side_ui_buttom:
                    if bot_setting in inner :
                        inner.remove(bot_setting)

            if admins_.acc_panels == 0 :
                panels_managements = ('🖥 مدیریت پنل ها ' , 'panels_management')
                for inner in admin_side_ui_buttom :
                    if panels_managements in inner:
                        inner.remove(panels_managements)

            if admins_.acc_products == 0 :
                product_managemets = ('🎛مدیریت فروشگاه' , 'products_management')
                for inner in admin_side_ui_buttom :
                    if product_managemets in inner:
                        inner.remove(product_managemets)


            if admins_.acc_admins == 0 :
                admins_managements = ('🧑🏼‍💻مدیریت ادمین ها' , 'admins_management')
                for inner in admin_side_ui_buttom :
                    if admins_managements in inner:
                        inner.remove(admins_managements)

            if admins_.acc_users == 0 :
                users_managemet = ('👤مدیریت کاربران', 'users_management')
                for inner in  admin_side_ui_buttom :
                    if users_managemet in inner:
                        inner.remove(users_managemet)


            if admins_.acc_staticts == 0:
                acc_staticts = ('📈آمار ربات' , 'bot_statics')
                for inner in admin_side_ui_buttom :
                    if acc_staticts in inner:
                        inner.remove(acc_staticts)


        for row in admin_side_ui_buttom :
            row_buttons = []
            for text , data in row :
                buttons = InlineKeyboardButton(text = text , callback_data = data)
                row_buttons.append(buttons)
            keyboard.add(*row_buttons)       



        back_button = InlineKeyboardButton(text='بازگشت به منوی اصلی 🏘' , callback_data='back_from_management')  
        keyboard.add(back_button) 
        return keyboard
    


# ------------------------- User-Settings ----------------------------------------------------------------------------------

    @staticmethod 
    def manage_users():
        keyboard = InlineKeyboardMarkup()
        
        botsettings_ = botsettings.objects.values('irnumber')[0]['irnumber']
        ir_number = lambda txt : '✅' if txt == 1 else '❌'
        buttons_raw = [ [(ir_number(botsettings_) , 'ir_number'),('احراز هویت با شماره' , 'ir_number')],
                        [('⏏️ تایید دستی کاربر' , 'verifying_users_by_hand')],
                        [('👁 مشاهده اطلاعات کاربر ' , 'show_user_info')],
                        [('⬇️⬆️ موجودی کاربر ' , 'increase_decrease_cash'), ('🔴🟢 انسداد کاربر ', 'block_unblock_user')],
                        [('📨ارسال پیام به کاربران', 'send_msgs_to_users')] , 
                        [('✤ - بازگشت به منوی قبلی - ✤','back_from_user_management')]
                        ]


        for row in buttons_raw:
            buttons_list = []
            for text , data in row:
                buttons = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(buttons)
            keyboard.add(*buttons_list)

        return keyboard

# ------------------------- verification-msg-on-first-join ----------------------------------------------------------------------------------
    @staticmethod
    def verfying_on_fist_join(user_id , status=None):
        keyboard = InlineKeyboardMarkup()
        st_ = 'وریفای کردن یوزر ' if status is None else '✅یوزر وریفای شده است'
        buttons_raw = [[(st_ , f'verfying_user_onstart_{user_id}')]]
        for row in buttons_raw:
            buttons_list = []
            for text , data in row:
                buttons = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(buttons)
            keyboard.add(*buttons_list)
        
        return keyboard
            
# ------------------------- Channels ---------------------------------------------------------------------------------------

    @staticmethod
    def load_channels(bot , Userid):
        keyboard = InlineKeyboardMarkup()
        channels_ = channels.objects.filter(ch_usage = 'fjch').all()
        channel_list = []
        for i in channels_:
            user_joined = bot.get_chat_member(i.channel_url or i.channel_id  , Userid).status
            if user_joined == 'left':
                if i.ch_status == 1 : 
                    channel_url = bot.get_chat(str(i.channel_id) or str(i.channel_url)).invite_link
                    button = InlineKeyboardButton(i.channel_name , callback_data=channel_url  , url=channel_url)
                    channel_list.append(button)

        button_start=InlineKeyboardButton('✅جوین شدم' , callback_data='channels_joined')
        keyboard.add(*channel_list , button_start ,  row_width=1)
        return keyboard























# ------------------------- Admin-Section -----------------------------------------------------------------------------------


#//TODO improve this section
    @staticmethod 
    def show_admins(who = None , num_toshow_items:int=2 , page_items:int=1):

        keyboard = InlineKeyboardMarkup()

        try :
            if who is None: 
                admins_ = admins.objects.filter(is_owner=1).first()
                admin_name_id = f'{admins_.admin_name}-{admins_.user_id}'
                admin_id = f'{str(admins_.user_id)}'
            else:
                admins_who = admins.objects.get(user_id = int(who))
                admin_name_id = f'{admins_who.admin_name}-{admins_who.user_id}'
                admin_id = f'{str(admins_who.user_id)}'
        except Exception as notfounding :
            print(f'user not found in admin db // error msg : {notfounding}')
  

             
        buttons_row_list = [[(f'🟢{admin_name_id}', f'loads_{admin_id}')],
                            [('❌حذف کردن ادمین ' ,f'adminremove_{admin_id}') , ('🕹مدیریت دسترسی ها' , f'adminaccess_{admin_id}')],]
        

        admins_list = admins.objects.filter(is_admin = 1)
        
        start = (page_items - 1) * num_toshow_items
        end = start + num_toshow_items


        users_list = []
        for indx , items in enumerate(admins_list , 0):
            if start <= indx < end:
                admin = [(f'{admins_list[indx].admin_name}-{admins_list[indx].user_id}' , f'load_{admins_list[indx].user_id}')]
                users_list.append(admin)

        for row in buttons_row_list:
            buttons_add_list = []
            for text , data in row:
                button = InlineKeyboardButton(text , callback_data=data)
                buttons_add_list.append(button)
            keyboard.add(*buttons_add_list)


        listOFUsers = []
        for row in users_list :
            for text , data in row:
                button = InlineKeyboardButton(text=text , callback_data=data)
                listOFUsers.append(button)

        keyboard.add(*listOFUsers , row_width=2)
        
        next_prev_buttons =[InlineKeyboardButton(text='صفحه بعدی ⏪' , callback_data =f'admin_pages_{page_items +1}') , 
                            InlineKeyboardButton(text='صفحه قبل ⏩' , callback_data =f'admin_pages_{page_items - 1}')]


        total_page = (admins_list.count() + num_toshow_items - 1 ) // num_toshow_items
        if page_items ==1 and total_page > page_items:
            keyboard.add(next_prev_buttons[0])
        elif page_items > 1:
            if page_items > total_page:
                keyboard.add(*next_prev_buttons)
            else:
                keyboard.add(next_prev_buttons[1])


        back_admin_buttons = InlineKeyboardButton('✤ - بازگشت به منوی قبلی - ✤' , callback_data='back_from_admin_menu')
        admin_add = InlineKeyboardButton('➕اضافه کردن ادمین ' , callback_data='add_new_admin')
        keyboard.add(admin_add , back_admin_buttons ,  row_width=1)

        return keyboard 





    @staticmethod
    def manage_admin_acc(user_id = None):
        keyboard = InlineKeyboardMarkup()
        admins_ = admins.objects.get(user_id = user_id)
        status_txt = lambda txt : "❌" if txt == 0 else '✅'

        buttons_raw  = [[(status_txt(admins_.acc_panels) , f'accpanels_{str(admins_.user_id)}') , ('دسترسی به تنظیمات پنل ها' , f'accpanels_{str(admins_.user_id)}')],
                       [(status_txt(admins_.acc_products) , f'accproducts_{str(admins_.user_id)}') , ('دسترسی به تنظیمات محصولات ها' , f'accproducts_{str(admins_.user_id)}')],
                       [(status_txt(admins_.acc_botmanagment) , f'accpbotseeting_{str(admins_.user_id)}') , ('دسترسی به تنظیمات مدیریت بات' , f'accpbotseeting_{str(admins_.user_id)}')],
                       [(status_txt(admins_.acc_admins) , f'accadmins_{str(admins_.user_id)}') , ('دسترسی به تنظیمات ادمین ها ', f'accadmins_{str(admins_.user_id)}')],
                       [(status_txt(admins_.acc_users) , f'accusermanagment_{str(admins_.user_id)}') , ('دسترسی به مدیریت یوزر ها', f'accusermanagment_{str(admins_.user_id)}')],
                       [(status_txt(admins_.acc_staticts) , f'accbotstaticts_{str(admins_.user_id)}') , ('دسترسی به آمار ربات', f'accbotstaticts_{str(admins_.user_id)}')]]

        for row in buttons_raw:
            buttons_list = []
            for text , data in row:
                button = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)
        back_button= InlineKeyboardButton('✤ - بازگشت به منوی قبلی - ✤' , callback_data='back_from_admin_access')
        keyboard.add(back_button)
        return keyboard









# ------------------------- Increase-Decrease-Section -----------------------------------------------------------------------
    @staticmethod 
    def increase_or_decrease(amount_add = 1, user_id = None , current_cash = 5000 , operator = None ,):
        keyboard = InlineKeyboardMarkup()
        if amount_add == None :
            amount_add =1 
        elif amount_add  == 0:
            current_cash = current_cash * amount_add
        elif amount_add > 0 :
            current_cash = current_cash *  amount_add
        elif amount_add < 0:
            amount_add = 0
            current_cash = current_cash * amount_add
            
        operator_verify = 'plus' if operator == '➕' else 'mines' if operator == '➖' else None
        operator_ = '➕' if operator == '➕' else '➖' if operator == '➖' else '='

        raw_buttons = [[(format(current_cash , ',') , 'current_cash')], 
                       [('➖' , 'operator_mines') , (str(operator_) , 'operator'), ('➕' , 'operator_plus')],
                       [(f'{str(5000)} کاهش' , f'amount_decrease_{str(amount_add - 1 )}') , (f'{str(5000)} افزایش' , f'amount_increase_{str(amount_add + 1)}')],
                       [('مبلغ دلخواه🔖' , 'wish_amount') , ('📨پیام دلخواه' ,'wish_msg_cash')],
                       [('تایید عملیات ✅' , f'verify_inde_{current_cash}_{operator_verify}_{user_id}')],
                       [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_increase_decrease_cash')],]
        
        for row in raw_buttons:
            buttons_list = []
            for text , data in row:
                button = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)

        return keyboard


# ------------------------- Block-Unblock-Section ---------------------------------------------------------------------------
    @staticmethod
    def block_unblock(user_id = None , block = None , unblock = None):
        keyboard = InlineKeyboardMarkup()
        user_id = str(user_id)
        users_ =users.objects.get(user_id=user_id)


        blockSatus = '✅مسدود کردن' if block is not None else 'مسدود کردن'
        unBlockStatus = '✅ رفع مسدودی' if unblock is not None else 'رفع مسدودی'
        block_unblock_txt = 'مسدود' if users_.block_status == 1 else 'عدم مسدودی'


        raw_button = [[(f'وضعیت یوزر :‌ {block_unblock_txt}' , f'userid_{user_id}')],
                    [(blockSatus , f'block_user_{user_id}'), (unBlockStatus , f'unblock_user_{user_id}')],
                    [('📍تایید و ارسال پیام به یوزر', f'verify_sendmsg_{user_id}')],
                    [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_block_unblock')],]
        
        for raw in raw_button:
            button_list = []
            for text , data in raw:
                button = InlineKeyboardButton(text=text , callback_data=data)
                button_list.append(button)
            keyboard.add(*button_list)

        return keyboard
    





# ------------------------- Msg-Section ---------------------------------------------------------------------------
    @staticmethod
    def send_user_msg():
        keyboard = InlineKeyboardMarkup()
        raw_buttons = [[('👤ارسال پیام به کاربر' , 'send_msg_single_user')],
                        [('📢ارسال پیام همگانی' , 'send_msg_boardcasting'), ('↪️ فروارد همگانی ' , 'send_msg_forwarding')],
                        [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_send_msg')]]
        for raw in raw_buttons:
            button_list = []
            for text,data in raw:
                button = InlineKeyboardButton(text=text, callback_data=data)
                button_list.append(button)
            keyboard.add(*button_list)

        return keyboard
    
        

    








# ------------------------- Bot-Static-Section ------------------------------------------------------------------------------
    @staticmethod
    def bot_static(users = None, products = None, panels =None, inovices=None, payments=None):
        keyboard = InlineKeyboardMarkup()
        users_choose = '👥 -کاربران ' if users is None else '👥- کاربران☑️ '
        products_choose = '🛍 -محصولات ' if products is None else '🛍- محصولات☑️'
        panels_choose = '🎛 -پنل‌ها' if panels is None else '🎛- پنل‌ها☑️'
        inovices_choose = '📑-فاکتورها' if inovices is None else '📑- فاکتورها☑️'
        payments_choose = '💰- پرداخت‌ها ' if payments is None else "💰- پرداخت‌ها☑️"
        raw_buttons = [
                        [   
                            (panels_choose, 'panels_static'),
                            (products_choose , 'products_static'),
                            (users_choose, 'users_static'),
                            (inovices_choose, 'inovices_static'),
                            (payments_choose, 'payments_static'),
                            #('کارت ها ', 'karts_static'),
                        ],
                        [
                            ('بازگشت به منوی قبلی↪️', 'back_from_bot_statics')
                        ]
                    ]
        
        for row in raw_buttons:
            buttons_list = []
            for text , data in row :
                button = InlineKeyboardButton(text=text , callback_data=data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)
        return keyboard
    





# ------------------------- Show-User-Info ---------------------------------------------------------------------------
    @staticmethod
    def show_user_info_subscription(user_id , request_dict):
        keyboard = InlineKeyboardMarkup()
        subscriptions_ = subscriptions.objects
        users_ = users.objects

        user_info = users_.get(user_id = user_id)
        subscriptions_config = subscriptions_.get(user_subscription = request_dict['username'])
        status_txt = lambda msg : '✅ فعال ' if msg == 1 else '❌ غیرفعال '
        status_config = '✅ فعال ' if  request_dict['status'] == 'active' else '❌ غیرفعال ' if request_dict['status'] == 'disabled' else '🕯 درانتظار اتصال'

        raw_buttons = [
            [(status_config , f'suichstatus.{user_info.user_id}.({subscriptions_config.user_subscription})') , ('وضعیت سرویس', f'suichstatus.{user_info.user_id}.({subscriptions_config.user_subscription})')] ,
            [('🔗 دریافت لینک اشتراک', f'suigetconfiglink.{user_info.user_id}.({subscriptions_config.user_subscription})') , ('🖼 دریافت QRcode اشتراک' , f'suigetqrcodelink.{user_info.user_id}.({subscriptions_config.user_subscription})')],        
            [('➕ افزایش حجم اشتراک' , f'suiincreasedatalimit.{user_info.user_id}.{subscriptions_config.user_subscription}'), ('➖ کاهش حجم اشتراک' , f'suidecreasedatalimit.{user_info.user_id}.({subscriptions_config.user_subscription})')], 
            [('⏳افزایش زمان اشتراک ' , f'suiincreaseexpire.{user_info.user_id}.{subscriptions_config.user_subscription}'), ('⌛️ کاهش زمان اشتراک ' , f'suidecreaseexpire.{user_info.user_id}.({subscriptions_config.user_subscription})')], 
            [('❌ حذف لینک فعلی اشتراک ' , f'suirevokesubscription.{user_info.user_id}.{subscriptions_config.user_subscription}')],
            [('❌حذف اشتراک ازپنل وحساب کاربر ' , f'suiremovepaneluser.{user_info.user_id}.({subscriptions_config.user_subscription})')],
            [('📨حذف اشتراک و عودت وجه ' , f'suiremoveservicemoneyback.{user_info.user_id}.{subscriptions_config.user_subscription}')],
            #[('✂️ سلب امتیاز از کاربر ' , f'suideprivationconfig.{user_info.user_id}.{subscriptions_config.user_subscription}'), ('🖇 اعطای اشتراک به کاربر دیگر', f'suigiveconfigtoother.{user_info.user_id}.{subscriptions_config.user_subscription}')], 
            ]

        for row in raw_buttons:
            button_list = []
            for text , data in row:
                button = InlineKeyboardButton(text=text , callback_data=data) 
                button_list.append(button)
            keyboard.add(*button_list , row_width=2 )

        back_button = InlineKeyboardButton(text='✤ - بازگشت به منوی قبلی - ✤' , callback_data= 'back_from_show_user_info_config')
        
        keyboard.add(back_button , row_width= 1)

        return keyboard
    













# ------------------------------------------------------------------------------------------
# ------------------------- Bot-Settings --------------------------------------------------------------------------------------->
# ------------------------------------------------------------------------------------------
    @staticmethod
    def bot_management():
        keyboard = InlineKeyboardMarkup()
        botsettings_ = botsettings.objects.first()
        status_txt = lambda botstatus : '❌ غیر فعال' if botstatus == 0 else  '✅ فعال'

        botmangement_rawbuttons =[
                                  [(status_txt(botsettings_.bot_status) , 'bot_enable_disable') , ('🤖 - وضعیت ربات ' , 'bot_enable_disable')],
                                  [('🔒مدیریت جوین اجباری ' , 'manage_force_channel_join') , ('💸 مدیریت نحوه پرداخت' , 'manage_bank_cards')],
                                  [('📄مدیریت ارسال گزارشات' , 'manage_sending_logs')],
                                  [('✤ - بازگشت به منوی قبلی - ✤' , 'back_to_management_menu')],
                                ]

        for row in botmangement_rawbuttons:
            buttons_list = []
            for text , data in row:
                button = InlineKeyboardButton(text = text , callback_data = data)
                buttons_list.append(button)
            
            keyboard.add(*buttons_list)
  
        return keyboard





# ------------------------- < Payment-Section > 
    @staticmethod 
    def manage_howtopay():
        keyboard = InlineKeyboardMarkup()
        botsettings_ = botsettings.objects.values('wallet_pay' , 'kartbkart_pay' , 'moneyusrtousr')[0]
        status_txt = lambda botstatus : '❌ غیر فعال' if botstatus == 0 else  '✅ فعال'

        botsettings_wallet_pay = status_txt(botsettings_['wallet_pay'])
        botsettings_kartbkart_pay = status_txt(botsettings_['kartbkart_pay'])
        botsettings_mineyusrtousr = status_txt(botsettings_['moneyusrtousr'])

        payments_rawbuttons =[
                              [(botsettings_wallet_pay , 'walletpay_status') , ('👝 - پرداخت با کیف پول','walletpay_status')],
                              [(botsettings_kartbkart_pay , 'kartbkart_status') , ('💳 - پرداخت با کارت به کارت' , 'kartbkart_status')],
                              [(botsettings_mineyusrtousr , 'moneyusrtousr_status') , ('👥 - انتقال وجه یوزر به یوزر' , 'moneyusrtousr_status')],
                              [('⚙️ مدیریت شماره کارت‌‌ها ' , 'manage_shomare_kart')],
                              [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_mange_howtopay')] 
                            ]

        for row in payments_rawbuttons:
            buttons_list = []
            for text , data in row:
                button = InlineKeyboardButton(text = text , callback_data = data)
                buttons_list.append(button)

            keyboard.add(*buttons_list)

        return keyboard    
    




# ------------------------- < ManageShomareKart-Section > 
    @staticmethod
    def manage_shomarekart():
        keyboard = InlineKeyboardMarkup()
        shomarekart_all = shomarekart.objects.all()
        
        manageshomarekart_rawbuttons =[[('مدیریت کارت' ,'mangene') , ('شماره کارت','kart_number') , ('نام بانک' , 'bank_name')],]
        
        for i in shomarekart_all:
            button_karts =[('⚙️' , f'mkart_{str(i.bank_card)}') , (f'{str(i.bank_card)}' , f'mkart_{str(i.bank_card)}') , (f'{str(i.bank_name)}' , f'mkart_{str(i.bank_card)}')]
            manageshomarekart_rawbuttons.append(button_karts)
    
        finall_button =[
                        [('➕ اضافه کردن شماره کارت جدید' , 'add_new_kart_number')],
                        [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_manage_shomare_karts')],
                       ]

        manageshomarekart_rawbuttons.extend(finall_button)

        for row in manageshomarekart_rawbuttons:
            buttons_list =[]
            for text , data in row:
                button = InlineKeyboardButton(text = text , callback_data = data)
                buttons_list.append(button)

            keyboard.add(*buttons_list)
        
        return keyboard




    @staticmethod 
    def manage_kart(kart_number):
        keyboard = InlineKeyboardMarkup()
        shomarekart_loads = shomarekart.objects.get(bank_card= int(kart_number))

        kart_status = '✅فعال کردن ' if shomarekart_loads.bank_status == 0 else '❌غیرفعال کردن'
        kart_inuse = '👍🏻استفاده در پرداخت ها' if shomarekart_loads.bank_inmsg == 0 else '👎🏻عدم استفاده در پرداخت‌ها'

        buttons =[ [('👤 تغییر نام صاحب کارت' , f'changekardowner_name_{str(kart_number)}')] , 
                   [('💳 تغییر نام بانک' , f'changebankname_{str(kart_number)}')] , 
                   [(kart_inuse , f'userin_pays_{str(kart_number)}') , (kart_status , f'chstatus_shomarekart_{str(kart_number)}')],
                   [('❌حذف شماره کارت' , f'rmkart_{str(kart_number)}')],
                   [('✤ - بازگشت به منوی قبلی - ✤' ,'back_from_manage_shomare_kart')]
                  ]
                     
        for row in buttons:
            buttons_list =[]
            for text , data in row:
                button = InlineKeyboardButton(text = text , callback_data = data)
                buttons_list.append(button)

            keyboard.add(*buttons_list)

        return keyboard
    




# ------------------------- < JoinChannel-Section > 
    @staticmethod 
    def manage_joinch():
        keyboard = InlineKeyboardMarkup()
        botsettings_forcechjoin = botsettings.objects.values('forcechjoin')[0]
        status_txt = lambda botstatus : '❌ غیر فعال' if botstatus == 0 else  '✅ فعال'

        forcechjoin_rawbuttons =[
                                  [(status_txt(botsettings_forcechjoin['forcechjoin']) , 'forcechjoin') , ('🔐 - جوین اجباری' , 'forcechjoin')],
                                  [('⚙️مدیریت کردن چنل‌ها' , 'manage_forcejoin')],
                                  [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_manage_force_ch')]
                                ]
        for row in forcechjoin_rawbuttons:
            buttons_list =[]
            for text , data in row:
                button = InlineKeyboardButton(text = text , callback_data = data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)

        return keyboard
    





    @staticmethod
    def manage_channels():
        keyboard = InlineKeyboardMarkup()
        channels_forcejoin = channels.objects.filter(ch_usage= 'fjch').all()
        managefch_rawbuttons =[[('مدیریت چنل' , 'mangene') , ('ایدی چنل' , 'ch_url') , ('نام چنل' , 'ch_name')],]
        for i in channels_forcejoin:
            buttons = [('⚙️' , f'mfch_{str(i.id)}') , (i.channel_url or i.channel_id ,  f'mfch_{str(i.id)}') , (i.channel_name , f'mfch_{str(i.id)}')]
            managefch_rawbuttons.append(buttons)

        finall_button = [
                         [('➕اضافه کردن چنل جدید' , 'add_new_force_channel')],
                         [('✤ - بازگشت به منوی قبلی - ✤' ,'back_from_managing_force_ch')]
                        ]
        
        managefch_rawbuttons.extend(finall_button)

        for row in managefch_rawbuttons:
            buttons_list = []
            for text , data in row:
                button = InlineKeyboardButton(text = text , callback_data = data)
                buttons_list.append(button)

            keyboard.add(*buttons_list)

        return keyboard





    @staticmethod 
    def manage_ch(channel_id):
        keyboard = InlineKeyboardMarkup()
        channel_loads = channels.objects.get(id = int(channel_id))
        status_txt = lambda botstatus : '❌ غیر فعال کردن' if botstatus == 1 else  '✅ فعال کردن'

        buttons = [ [('تغییر نام چنل 🔈' , f'change_chf_name_{channel_loads.pk}')] , 
                    [('❌ حذف کردن چنل ' , f'rm_chf_{str(channel_loads.pk)}') , (status_txt(channel_loads.ch_status) , f'status_chf_{str(channel_loads.pk)}')],
                    [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_manage_channel')]
                   ]

        for row in buttons:
            button_list =[]
            for text , data in row:
                button = InlineKeyboardButton(text = text , callback_data = data)
                button_list.append(button)

            keyboard.add(*button_list)

        return keyboard
    







# ------------------------- < logs-Section > 
    @staticmethod 
    def manage_logs():
        keyboard = InlineKeyboardMarkup()
        status_txt = lambda botstatus : '❌غیر فعال' if botstatus == 0 else  '✅فعال'
        botsettings_logs = botsettings.objects.values('newusers_notf' , 'walletcharge_notf' , 'moneyusrtousr_notf' , 'buyservice_notf' , 'tamdidservice_notf' ,'verifynumber_notf', 'notif_mode')[0]
        channel_log = channels.objects.filter(ch_usage = 'logc')
        chlog = channel_log.all().first()
        who_reciving_notifs = '👤 فقط مالک ' if botsettings_logs['notif_mode'] == 0 else '👥 مالک و ادمین ها '
        botsettingslogs_rawbuttons =[
                                      [(status_txt(botsettings_logs['newusers_notf']) , 'new_user_joined_notf') , ('اعلان کاربر جدید ' , 'new_user_joined_notf')], 
                                      [(status_txt(botsettings_logs['walletcharge_notf']) , 'charging_wallet_notf') , ('اعلان شارژ کیف پول' , 'charging_wallet_notf')], 
                                      [(status_txt(botsettings_logs['moneyusrtousr_notf']) , 'transfer_money_touser_notf') , ('اعلان‌انتقال‌وجه‌کاربر‌به‌کاربر' , 'transfer_money_touser_notf')], 
                                      [(status_txt(botsettings_logs['buyservice_notf']) , 'buy_new_service_notf') , ('اعلان خرید اشتراک جدید' , 'buy_new_service_notf')], 
                                      [(status_txt(botsettings_logs['tamdidservice_notf']) , 'tamdid_service_notf') , ('اعلان تمدید اشتراک' , 'tamdid_service_notf')],
                                      [(status_txt(botsettings_logs['verifynumber_notf']) , 'verify_number_notf') , ('اعلان تایید‌شماره‌کاربر' , 'verify_number_notf')],
                                      [('✤ - بازگشت به منوی قبلی - ✤' , 'back_from_manage_logs')]
                                    ]
        

        if channel_log.count() <1:
            botsettingslogs_rawbuttons.insert(len(botsettingslogs_rawbuttons) -1 , [(who_reciving_notifs , 'who_reciving_notifs') , ('ارسال اعلان ها برای ' , 'who_reciving_notifs')] ,)
            botsettingslogs_rawbuttons.insert(len(botsettingslogs_rawbuttons) - 1  ,  [('➕اضافه کردن چنل وقایع' , 'add_new_log_channel')],)
        else:
            botsettingslogs_rawbuttons.insert(len(botsettingslogs_rawbuttons) - 1 , [('❌ حذف کردن چنل لاگ' , f'remove_log_channel_{str(channel_log[0].pk)}')],)


        for row in botsettingslogs_rawbuttons:
            buttons_list =[]
            for text , data in row:
                button = InlineKeyboardButton(text = text , callback_data = data)
                buttons_list.append(button)
            keyboard.add(*buttons_list)

        return keyboard 


