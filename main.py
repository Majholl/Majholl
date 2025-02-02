#all modules imported in here
import re, jdatetime, datetime, json
import telebot, BOTTOKEN, panelsapi

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, LinkPreviewOptions
from mainrobot.models import users, v2panel, panelinbounds, products, inovices, payments, subscriptions, shomarekart, admins, botsettings

from django.db.models import Max, Min, Sum, Count
from keybuttons import BotkeyBoard as botkb
from bottext import *


from functions.USERS_onstarts import *
from functions.panels import *
from functions.products import *
from functions.buy_services import * 
from functions.check_fun import *
from functions.showuserinfo import *
from functions.notif import *
from functions.admins_robot import *
from tools.QRcode_maker import *
from tools.entry_creator import *
from tools.pangnations import *

#------------------------------------------------------------

bot = telebot.TeleBot(token=BOTTOKEN.TOKEN[0], parse_mode="HTML", colorful_logs=True)


#= Welcomer
try:
    commands = [telebot.types.BotCommand('start' , 'استارت ربات' ),
                telebot.types.BotCommand('watchuserinfo' , 'مشاهده اطلاعات کاربر'),
                telebot.types.BotCommand('increseusercash' , 'اضافه کردن موجودی کاربر')]
    admins_ = admins.objects.values_list('user_id' , flat=True)
    for i in admins_:
        
        bot.set_my_commands(commands , telebot.types.BotCommandScopeChat(chat_id=int(i)) )
except Exception as err:
    print('err occured' , err)




@bot.message_handler(func=lambda message: '/start' in message.text)
def start_bot(message) :
    user_ = message.from_user 
    CHECKING_USER = CHECK_USER_EXITENCE(user_.id , user_.first_name , user_.last_name , user_.username , 0  , bot)

    if message.text :
        #bot status 
        if BOT_STATUS(user_.id) is True :
            #block phone number
            if PHONE_NUMBER(user_.id) is False: 
                #block or not
                if BLOCK_OR_UNBLOCK(UserId= user_.id) is False :
                    #check user is joined or not
                    if FORCE_JOIN_CHANNEL(UserId=user_.id , Bot=bot) == True :

                        #- Canceling operations : panels , product
                        for i in admins.objects.all():
                            if message.from_user.id == i.user_id:
                                USER_ADMIN_INFO['admin_name'] = False
                                USER_ADMIN_INFO['add_admin'] = False
                        #clear USER_BASKETS && TAMDID_BASKERS_USER 
                        clear_dict(USERS_ORDER_BASKET , message.from_user.id)
                        clear_dict(TAMDID_USERS_ORDER_BASKET , message.from_user.id)
                        #clear USER_STATE
                        clear_dict(USER_STATE , message.from_user.id)
                        
                        #clear USER_QUERY_SERVICE
                        clear_dict(USER_QUERY_SERVICE , message.from_user.id)


                        #clear TRANSFER_MONEY_USRTOUSR
                        clear_dict(TRANSFER_MONEY_USRTOUSR , message.chat.id)
                        # clear CHARGE_WALLET
                        #clear_dict(CHARGE_WALLET , message.from_user.id)
                        #clear INCREASE_DECREASE CAHS
                        clear_dict(USER_INCREASE_DECREASE_CASH , message.from_user.id)
                        #clear SHOW_USER_INFO
                        clear_dict(SHOW_USER_INFO , message.from_user.id)



                        bot.send_message(message.chat.id , welcome_msg , reply_markup= botkb.main_menu_in_user_side(message.from_user.id))

                    else :
                        bot.send_message(message.chat.id , text=force_channel_join_msg, reply_markup=botkb.load_channels(bot , user_.id))
                else :
                    bot.send_message(message.chat.id , text='⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')

            else:
                USER_PHONE_NUMBER[message.from_user.id] = {'get_number':True}
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True ,one_time_keyboard=True)
                button = KeyboardButton('ارسال شماره', request_contact=True )
                keyboard.add(button)
                Text_1 =  'پیش از ادامه کار با ربات لطفا شماره خود را ارسال نمایید'
                bot.send_message(message.chat.id , Text_1 , reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id ,'⚙️ربات در حال حاضر غیر فعال است ')




#- handles all incoming channels_joined call.data 
@bot.callback_query_handler(func=lambda call : call.data=='channels_joined')
def channels_joined(call):
    if call.data=='channels_joined':
        if FORCE_JOIN_CHANNEL(call.from_user.id , bot) == True:
            bot.edit_message_text(welcome_msg , call.message.chat.id , call.message.message_id , reply_markup= botkb.main_menu_in_user_side(call.message.from_user.id))
        else:
            Text_1='⚠️شما هنوز در چنل های ما جوین نشده اید⚠️'
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.load_channels(bot , call.from_user.id))



USER_PHONE_NUMBER = {}

#- get user contact 
@bot.message_handler(func= lambda message:  message.from_user.id in USER_PHONE_NUMBER and len(USER_PHONE_NUMBER)>=1 and USER_PHONE_NUMBER[message.from_user.id]['get_number'] ==True and message.content_type =='contact', content_types=['contact'])
def get_user_phone(message):
    if message.from_user.id in USER_PHONE_NUMBER and len(USER_PHONE_NUMBER)>=1 and USER_PHONE_NUMBER[message.from_user.id]['get_number'] ==True :
        patter = r'^([+98]|[+225]|[+7])+[0-9]{10}$'
        contact_msg = message.contact.phone_number
        check_phone_number = re.search(patter , contact_msg)
        if check_phone_number:
            
            try :
                if BLOCK_OR_UNBLOCK(UserId= message.from_user.id) is False :
                    if FORCE_JOIN_CHANNEL(UserId=message.from_user.id , Bot=bot) == True :
                        users_ = users.objects.get(user_id = message.from_user.id)
                        users_.phone_number = check_phone_number.group(0)
                        users_.save()
                        clear_dict(USER_PHONE_NUMBER , message.from_user.id)
                        bot.send_message(message.chat.id , 'اطلاعات شما با موفقیت دریافت شد' , reply_markup=ReplyKeyboardRemove())
                        notif_verify_number(bot , message.from_user.id)
                        time.sleep(1.5)
                        bot.send_message(message.chat.id , welcome_msg , reply_markup= botkb.main_menu_in_user_side(message.from_user.id))

                    else :

                        bot.send_message(message.chat.id , text=force_channel_join_msg, reply_markup=botkb.load_channels(bot , message.from_user.id))
                else :
                    bot.send_message(message.chat.id , text='⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')
            
            except Exception as phone_number_error:
                print(f'error while adding phone number to user: error_msg : {phone_number_error}')
        else:
            bot.send_message(message.chat.id , 'شماره های غیر ایرانی مجازی نمیباشد', reply_markup=ReplyKeyboardRemove())
        












# - 1 user-side
# --------------------------------------------------------------------------------------------------------------------------
# ------------------------- BUY-SERVICES -----------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------

#> ./buy_services : selecting all plans if olny have on panel

USER_STATE  = {}

USERS_ORDER_BASKET = {}
TAMDID_USERS_ORDER_BASKET = {}

USER_PAYCARD_FISH = {}
PAYMENT_product_price_ON_BUY = {}





@bot.callback_query_handler(func = lambda call: call.data in ['buy_service' , 'back_from_choosing_product_one_panel' , 'back_from_choosing_panels' , 'back_from_choosing_product_more_panels'])
def handler_buy_service_one_panel(call):   
    panels_count = v2panel.objects.all().count()
    
    #bot status 
    if BOT_STATUS(call.from_user.id) is True :
        #Verify-Phone-Number
        if PHONE_NUMBER(call.from_user.id) is False: 
            #Block-Unblock-InBot
            if BLOCK_OR_UNBLOCK(UserId= call.from_user.id) is False:
                #Force-Join-Channel
                if FORCE_JOIN_CHANNEL(call.from_user.id , bot) == True:
                    


                    if call.data == 'buy_service': 
                        #Load one panel products
                        if panels_count <=1 :
                            panels_products_loading = plans_loading_for_one_panel()
                            if panels_products_loading == 'panel_disable':
                                bot.send_message(call.message.chat.id , '⌛️پنل در حال بروزرسانی میباشد . لطفا بعدا مراجعه فرمایید')
                            else : 
                                if isinstance(panels_products_loading , InlineKeyboardMarkup):
                                
                                    if call.from_user.id not in USERS_ORDER_BASKET:
                                            USERS_ORDER_BASKET[call.from_user.id] = create_product_entry()

                                    bot.edit_message_text(buy_service_section_product_msg , call.message.chat.id , call.message.message_id , reply_markup = panels_products_loading)      

                            if panels_products_loading == 'sale_closed':
                                bot.send_message(call.message.chat.id , '⛔️فروش سرویس بسته میباشد ، بعدا مراجعه فرمایید')

                            if panels_products_loading == 'sale_open_no_zarfit':
                                bot.send_message(call.message.chat.id , '🪫ظرفیت فروش به اتمام رسیده است . بعدا مراجعه فرمایید')

                            if panels_products_loading == 'no_panel_product': 
                                bot.send_message(call.message.chat.id , '‼️متاسفیم ، هنوز هیچ سرور یا محصولی برای ارائه وجود ندارد' )

                        #Load two panel products
                        else:
                            bot.edit_message_text(buy_service_section_choosing_panel_msg , call.message.chat.id , call.message.message_id , reply_markup=botkb.choosing_panels_in_buying_section())

                    #-back - buttons - for one panel 
                    if call.data == 'back_from_choosing_product_one_panel': 
                        bot.edit_message_text(welcome_msg , call.message.chat.id , call.message.message_id , reply_markup = botkb.main_menu_in_user_side(call.from_user.id))
                    
                    #-back - button - choosing panels
                    if call.data == 'back_from_choosing_panels':
                        bot.edit_message_text(welcome_msg , call.message.chat.id , call.message.message_id , reply_markup = botkb.main_menu_in_user_side(call.from_user.id))


                    if call.data == 'back_from_choosing_product_more_panels':
                        bot.edit_message_text(buy_service_section_choosing_panel_msg , call.message.chat.id , call.message.message_id , reply_markup=botkb.choosing_panels_in_buying_section())



                else :
                    bot.send_message(call.message.chat.id , force_channel_join_msg , reply_markup=botkb.load_channels(bot , call.from_user.id))
            else :
                bot.send_message(call.message.chat.id , '⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')
        else:
            USER_PHONE_NUMBER[call.message.chat.id] = {'get_number':True}
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True ,one_time_keyboard=True)
            button = KeyboardButton('ارسال شماره', request_contact=True )
            keyboard.add(button)
            Text_1 =  'پیش از ادامه کار با ربات لطفا شماره خود را ارسال نمایید'
            bot.send_message(call.message.chat.id , Text_1 , reply_markup=keyboard)

    else:
        bot.send_message(call.message.chat.id ,'⚙️ربات در حال حاضر غیر فعال است ')







#> ./buy service : two panels buying / TBSpanel = TWO PANEL BUY SERVICE
@bot.callback_query_handler(func = lambda call : call.data.startswith('twopanelbuyservice_panelpk_'))
def handle_buy_service_two_panel(call):
    call_data = call.data.split('_')
    panels_products_loading = plans_loading_for_two_more_panel(panelid = call_data[-1])
    #bot status 
    if BOT_STATUS(call.from_user.id) is True :
        #Verify-Phone-Number
        if PHONE_NUMBER(call.from_user.id) is False: 
            #Block-Unblock-InBot
            if BLOCK_OR_UNBLOCK(UserId= call.from_user.id) is False:
                #Force-Join-Channel
                if FORCE_JOIN_CHANNEL(call.from_user.id , bot) == True:
                    

                    
                    if call.data.startswith('twopanelbuyservice_panelpk_'):

                        if panels_products_loading == 'panel_disable':
                            bot.send_message(call.message.chat.id , '⌛️پنل در حال بروزرسانی میباشد . لطفا بعدا مراجعه فرمایید')
                        else :
                            if isinstance(panels_products_loading , InlineKeyboardMarkup):
                                
                                if call.from_user.id not in USERS_ORDER_BASKET:
                                    USERS_ORDER_BASKET[call.from_user.id] = create_product_entry()

                                bot.edit_message_text(buy_service_section_product_msg , call.message.chat.id , call.message.message_id , reply_markup = panels_products_loading)

                        if panels_products_loading == 'sale_closed':
                            bot.send_message(call.message.chat.id , '⛔️فروش سرویس بسته میباشد ، بعدا مراجعه فرمایید')

                        if  panels_products_loading == 'sale_open_no_zarfit':
                            bot.send_message(call.message.chat.id , 'فروش به اتمام رسیده است . بعدا مراجعه فرمایید')

                        if panels_products_loading == 'no_products':
                            bot.send_message(call.message.chat.id , '‼️متاسفیم ، هنوز هیچ سرور یا محصولی برای ارائه وجود ندارد')



                else :
                    bot.send_message(call.message.chat.id , force_channel_join_msg , reply_markup=botkb.load_channels(bot , call.from_user.id))
            else :
                bot.send_message(call.message.chat.id , '⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')
        else:
            USER_PHONE_NUMBER[call.message.chat.id] = {'get_number':True}
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True ,one_time_keyboard=True)
            button = KeyboardButton('ارسال شماره', request_contact=True )
            keyboard.add(button)
            Text_1 =  'پیش از ادامه کار با ربات لطفا شماره خود را ارسال نمایید'
            bot.send_message(call.message.chat.id , Text_1 , reply_markup=keyboard)

    else:
        bot.send_message(call.message.chat.id ,'⚙️ربات در حال حاضر غیر فعال است ')











#> ./buy_services > selecting products plans
@bot.callback_query_handler(func = lambda call : call.data.startswith('buynewservice_'))
def handle_buyservice_select_productplan(call):
    #bot status 
    if BOT_STATUS(call.from_user.id) is True :    
        #Verify-Phone-Number
        if PHONE_NUMBER(call.from_user.id) is False: 
            #Block-Unblock-InBot
            if BLOCK_OR_UNBLOCK(UserId= call.from_user.id) is False:
                #Force-Join-Channel
                if FORCE_JOIN_CHANNEL(call.from_user.id , bot) == True:
                        
        
                    if call.data.startswith('buynewservice_'):
                        call_data = call.data.split("_")

                        if call.from_user.id in USERS_ORDER_BASKET:
                            
                            USERS_ORDER_BASKET[call.from_user.id]['product_id'] = call_data[1]
                            USERS_ORDER_BASKET[call.from_user.id]['statement'] = [call_data[2] , call_data[3]] 
                            
                            if call.from_user.id in USER_STATE and USER_STATE[call.from_user.id][0] in ('find_user_service' , 'charge_wallet'):
                                clear_dict(USER_QUERY_SERVICE , call.from_user.id)
                                clear_dict(CHARGE_WALLET , call.from_user.id)

                            USER_STATE[call.from_user.id] = ['buying_new_service' , time.time()]

                            bot.edit_message_text(buy_service_section_choosing_username_msg , call.message.chat.id , call.message.message_id)
                            bot.register_next_step_handler(call.message , get_username_for_config_name)

                else :
                    bot.send_message(call.message.chat.id , force_channel_join_msg , reply_markup=botkb.load_channels(bot , call.from_user.id))
            else :
                bot.send_message(call.message.chat.id , '⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')
        else:
            USER_PHONE_NUMBER[call.message.chat.id] = {'get_number':True}
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True ,one_time_keyboard=True)
            button = KeyboardButton('ارسال شماره', request_contact=True )
            keyboard.add(button)
            Text_1 =  'پیش از ادامه کار با ربات لطفا شماره خود را ارسال نمایید'
            bot.send_message(call.message.chat.id , Text_1 , reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id ,'⚙️ربات در حال حاضر غیر فعال است ')











#> ./buy_services > get user username 
def get_username_for_config_name(message):
    #bot status 
    if BOT_STATUS(message.from_user.id) is True :
        #Verify-Phone-Number
        if PHONE_NUMBER(message.from_user.id) is False: 
            #Block-Unblock-InBot
            if BLOCK_OR_UNBLOCK(UserId= message.from_user.id) is False :
                #Force-Join-Channel
                if FORCE_JOIN_CHANNEL(message.from_user.id , bot) == True :
                    
                        
                    if message.text == '/cancel' or message.text == '/cancel'.upper():
                        clear_dict(USERS_ORDER_BASKET , message.from_user.id)
                        bot.send_message(message.chat.id , welcome_msg , reply_markup=botkb.main_menu_in_user_side(message.from_user.id)) 
                        bot.clear_step_handler(message)
                    else: 
                        if make_username_for_panel(message , bot , USERS_ORDER_BASKET) != 'incorrect_username':
                            info = USERS_ORDER_BASKET[message.from_user.id]
                            
                            bot.send_message(message.chat.id , product_info_msg(info) , reply_markup=botkb.confirmation())              
                        else:
                            bot.send_message(message.chat.id , '⚠️نام کاربری انتخابی اشتباه است لطفا مجدد امتحان فرمایید \n دقت کنید که حروف فارسی مجاز نمیباشد \n مجدد امتحان فرمایید')


                else :
                    bot.send_message(message.message.chat.id , force_channel_join_msg , reply_markup=botkb.load_channels(bot , message.from_user.id))
            else :
                bot.send_message(message.message.chat.id , '⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')
        else:
            USER_PHONE_NUMBER[message.message.chat.id] = {'get_number':True}
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True ,one_time_keyboard=True)
            button = KeyboardButton('ارسال شماره', request_contact=True )
            keyboard.add(button)
            Text_1 =  'پیش از ادامه کار با ربات لطفا شماره خود را ارسال نمایید'
            bot.send_message(message.message.chat.id , Text_1 , reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id ,'⚙️ربات در حال حاضر غیر فعال است ')












#> ./buy_services > proccess selected product plan 
@bot.callback_query_handler(func = lambda call : call.data in ['verify_product' , 'pay_with_wallet' , 'pay_with_card' , 'back_from_confirmation' , 'back_from_payment'] )
def handle_selected_products(call) : 
    #bot status 
    if BOT_STATUS(call.from_user.id) is True :    
        #Verify-Phone-Number
        if PHONE_NUMBER(call.from_user.id) is False: 
            #Block-Unblock-InBot
            if BLOCK_OR_UNBLOCK(UserId= call.from_user.id) is False :
                #Force-Join-Channel
                if FORCE_JOIN_CHANNEL(call.from_user.id , bot) == True :
                    
                    #Verify-to-continue
                    if call.data == 'verify_product' :
                        bot.edit_message_text('⚪️ یک روش پرداخت را انتخاب نمایید' , call.message.chat.id , call.message.message_id , reply_markup=botkb.payby_in_user_side()) 
                


                    #pay wallet
                    if call.data == 'pay_with_wallet':
                        if call.from_user.id in USERS_ORDER_BASKET:
                            req = pay_with_wallet(call ,USERS_ORDER_BASKET)

                            if req == 'not_enough_money_inwallet':
                                bot.send_message(call.message.chat.id , '✣موجودی حساب شما کافی نمیباشد ⚠️\n ┊─ ابتدا موجودی خود را افزایش دهید و مجدد اقدام فرمایید .\n برای اضافه کردن :/add_money')
                            
                            elif req == 'requset_false':
                                    owner_id = admins.objects.values('user_id').get(is_owner=1)['user_id']
                                    bot.send_message(owner_id , f'یک مشکلی در هنگام ارسال درخواست کاربر برای ساخت اکانت به وجود امده \n\n{req}')
                                    print(f'An ERROR occured in sending request to the panel \n\n\t Error-msg :{req}')
                            else:
                                if isinstance(req , dict):
                                    bot.edit_message_text(paied_msg , call.message.chat.id , call.message.message_id)
                                    bot.send_chat_action(chat_id=call.message.chat.id , action='typing')
                                    time.sleep(2.5)
                                    how_to_send(req , USERS_ORDER_BASKET[call.from_user.id] , bot , call.from_user.id)
                                    notif_buy_new_service(bot , call.from_user.id , USERS_ORDER_BASKET[call.from_user.id]['product_id'] , USERS_ORDER_BASKET[call.from_user.id]['config_name'])
                                    clear_dict(USERS_ORDER_BASKET , call.from_user.id)  
                

                    #pay card
                    if call.data == 'pay_with_card':
                        if call.from_user.id in USERS_ORDER_BASKET:
                            pay_with_card(call , bot , USERS_ORDER_BASKET , USER_PAYCARD_FISH)




                    #back - buttons - confirm product selected
                    if call.data == 'back_from_confirmation':
                        bot.edit_message_text(welcome_msg , call.message.chat.id , call.message.message_id , reply_markup = botkb.main_menu_in_user_side(call.from_user.id))
                        bot.answer_callback_query(call.id , 'ادامه خرید محصول لغو شد')
                        clear_dict(USERS_ORDER_BASKET , call.from_user.id)


                    #back - buttons - payment 
                    if call.data == 'back_from_payment':
                        bot.edit_message_text(welcome_msg , call.message.chat.id , call.message.message_id , reply_markup= botkb.main_menu_in_user_side(call.from_user.id))
                        bot.answer_callback_query(call.id , 'پرداخت لغو شد')
                        clear_dict(USERS_ORDER_BASKET , call.from_user.id)


                else :
                    bot.send_message(call.message.chat.id , force_channel_join_msg , reply_markup=botkb.load_channels(bot , call.from_user.id))
            else :
                bot.send_message(call.message.chat.id , '⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')
        else:
            USER_PHONE_NUMBER[call.message.chat.id] = {'get_number':True}
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True ,one_time_keyboard=True)
            button = KeyboardButton('ارسال شماره', request_contact=True )
            keyboard.add(button)
            Text_1 =  'پیش از ادامه کار با ربات لطفا شماره خود را ارسال نمایید'
            bot.send_message(call.message.chat.id , Text_1 , reply_markup=keyboard)

    else:
        bot.send_message(call.message.chat.id ,'⚙️ربات در حال حاضر غیر فعال است ')











# ./buy_service > seding fish section
@bot.message_handler(func=lambda message:(len(USER_PAYCARD_FISH) > 0 and (message.from_user.id in USERS_ORDER_BASKET or message.from_user.id in TAMDID_USERS_ORDER_BASKET)), content_types=['photo' , 'text'])
def getting_fish_image(message):
    try :
        if message.from_user.id in USERS_ORDER_BASKET :
            user_unique_id = USERS_ORDER_BASKET[message.from_user.id]['user_fish_id']
        else :
            user_unique_id = TAMDID_USERS_ORDER_BASKET[message.from_user.id]['user_fish_id']
        user_fish_info = USER_PAYCARD_FISH[user_unique_id] 
        tamdid_nor = True if USER_PAYCARD_FISH[user_unique_id]['tamdid'] == True else False

        admins_ = admins.objects.all()
        product_= products.objects.get(id = USER_PAYCARD_FISH[user_unique_id]['product_id'])
        panel_ = v2panel.objects.get(id = product_.panel_id.pk)
        user_ = users.objects.get(user_id = message.from_user.id)  

        if user_fish_info['fish_send'] == True:
            #if user cancel his inovice
            if message.content_type  == 'text':
                
                if message.text =='/cancel' or message.text=='/cancel'.upper():
                    clear_dict(USERS_ORDER_BASKET , message.from_user.id)
                    clear_dict(TAMDID_USERS_ORDER_BASKET , message.from_user.id)
                    clear_dict(USER_PAYCARD_FISH , user_unique_id)
                    bot.send_message(message.chat.id , welcome_msg , reply_markup=botkb.main_menu_in_user_side(message.from_user.id))


            elif message.content_type == 'photo':
                     
                for i in admins_:
                    bot.send_photo(i.user_id , message.photo[-1].file_id , caption=send_user_buy_request_to_admins(user_fish_info , user_ , tamdid=tamdid_nor) , reply_markup=botkb.agree_or_disagree(user_unique_id , tamdid=tamdid_nor))
                bot.send_message(message.chat.id , send_success_msg_to_user)
                # 0 > unpaid , 1 > paid , 2 > waiting  , 3 > disagree

                tamdid = USER_PAYCARD_FISH[user_unique_id]['tamdid']
                    
                kindpay = 'buy' if tamdid is False else 'renew'
                inovivces_creations = create_inovices(user_ , panel_ , product_ , panel_.panel_name , product_.product_name , product_.data_limit , product_.expire_date ,product_.product_price ,  2 , kindpay , USER_PAYCARD_FISH[user_unique_id]['config_name'] , 'kbk' )
                USER_PAYCARD_FISH[user_unique_id]['inovice'] = inovivces_creations
                USER_PAYCARD_FISH[user_unique_id]['fish_send'] = False
                USER_PAYCARD_FISH[user_unique_id]['accpet_or_reject'] = True
                clear_dict(USERS_ORDER_BASKET , message.from_user.id)
                clear_dict(TAMDID_USERS_ORDER_BASKET , message.from_user.id)

        return            
    except Exception as useruniqueid_error:
        print(useruniqueid_error)











@bot.callback_query_handler(func = lambda call : call.data.startswith(('agree_' , 'disagree_', 'tamdidagree_' , 'tamdiddisagree_')))
def agree_or_disagree_kbk_payment(call):
    call_data = call.data.split('_')
    user_unique_id = f'{call_data[1]}_{call_data[2]}'

    try :
        info = USER_PAYCARD_FISH[user_unique_id]
        tamdid_nor = USER_PAYCARD_FISH[user_unique_id]['tamdid']
        user_ = users.objects.get(user_id = int(call_data[1]))
        product_ = products.objects.get(id = info['product_id'])
        panel_= v2panel.objects.get(id = product_.panel_id.pk)
        admins_ = admins.objects.all()
        sub_check = subscriptions.objects
        created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S') 

    except Exception as error:
        bot.answer_callback_query(call.id , 'این پرداخت از قبل بررسی شده')
        
    #agree section  
    if call.data.startswith(('agree_' , 'tamdidagree_')) and len(USER_PAYCARD_FISH) >=1 and (user_unique_id in USER_PAYCARD_FISH and USER_PAYCARD_FISH[user_unique_id]['accpet_or_reject']) == True:
        try:
            if tamdid_nor == True :
                note = f'renewed at {created_date} by {user_.user_id}'
                send_request = panelsapi.marzban(panel_.pk).put_user(info['config_name'] , info['product_id'] , usernote=note)
            else:
                note = f'renewd at {created_date} by {user_.user_id}'
                send_request = panelsapi.marzban(panel_.pk).add_user(info['config_name'] , product_.pk , usernote=note)


            if send_request:
                if sub_check.filter(user_subscription = info['config_name']).count() == 0:
                    subscription_creations = create_subscription(user_, info['config_name'] , product_ , panel_)   
                else:
                    load_sub = sub_check.get(user_subscription = info['config_name'])
                    load_sub.panel_id , load_sub.product_id , load_sub.created_date = panel_ , product_ , created_date
                    load_sub.save()


                inovice_ = inovices.objects.get(id = USER_PAYCARD_FISH[user_unique_id]['inovice'].id)
                inovice_.card_used = info['card_used']
                inovice_.paid_status = 1
                inovice_.save()
                payment_creations = create_payment(userid=user_ , amount=product_.product_price , paymenentstatus='accepted' , inoviceid=inovice_)
                panels.check_capcity(panel_.pk) if ('open' and 'zarfit') in info['statement'] else None


                
                bot.send_message(user_.user_id , paied_msg)
                time.sleep(3.5)
                bot.send_chat_action(int(call_data[1]) , action='typing')
                how_to_send(send_request , info , bot , user_.user_id)
                notif_buy_new_service(bot , call_data[1] , product_.pk , info['config_name'] , tamdid= tamdid_nor)

                for i in admins_:
                    if i.user_id != call.from_user.id:
                        Text_1 = f'✅درخواست پرداخت کاربر انجام شد\n🔻جزییات تراکنش\n|- ایدی کاربر: {user_.user_id}\n|- نام اکانت : {info["config_name"]}\n|- شماره فاکتور : {inovice_.pk}\n|- شماره پرداخت :‌ {payment_creations.pk}\n.'
                        bot.send_message(i.user_id , Text_1)
                bot.reply_to(call.message, Text_1)
                clear_dict(USER_PAYCARD_FISH , user_unique_id)


        except Exception as addusertopanell_error:
            print(f'An ERROR occured in [main.py  - LINE 546-641 - FUNC agree_or_disagree_kbk_payment] \n\n\t Error-msg :{addusertopanell_error}')
            



    #reject payment        
    if len(PAYMENT_product_price_ON_BUY) == 0:
        if call.data.startswith(('disagree_' , 'tamdiddisagree_')) and len(USER_PAYCARD_FISH) >=1 and (user_unique_id in USER_PAYCARD_FISH and USER_PAYCARD_FISH[user_unique_id]['accpet_or_reject']) == True:

            inovice_ = inovices.objects.get(id = info['inovice'].id)
            
            inovice_.card_used = info['card_used']
            inovice_.paid_status = 3 # paid_status = 03 / rejected
            inovice_.save()
            payments_ = create_payment(userid=user_ , amount=product_.product_price , paymenentstatus='rejected' , inoviceid=inovice_ )
            bot.send_message(call.message.chat.id , 'علت رد پرداخت را ارسال کنید')

            if int(call_data[1]) not in PAYMENT_product_price_ON_BUY :
                    PAYMENT_product_price_ON_BUY[int(call_data[1])] = payment_product_price_create()
            PAYMENT_product_price_ON_BUY[int(call_data[1])]['reason'] = True
            PAYMENT_product_price_ON_BUY[int(call_data[1])]['user_id'] = int(call_data[1])
            PAYMENT_product_price_ON_BUY[int(call_data[1])]['payment'] = payments_
            clear_dict(USER_PAYCARD_FISH , user_unique_id)
    else:
        bot.answer_callback_query(call.id , 'درخواست ها را جداگانه پردازش کنید')






# ./buy services > disagree of fish : getting reason
@bot.message_handler(func = lambda message:  len(PAYMENT_product_price_ON_BUY) ==1 )
def get_product_price_2(message) :

    admins_ = admins.objects.all()
    user_id = str
    for i in PAYMENT_product_price_ON_BUY.keys():
        user_id = i
    
    if PAYMENT_product_price_ON_BUY[user_id]['reason'] == True : 
        payments_ = payments.objects.get(id = PAYMENT_product_price_ON_BUY[int(user_id)]['payment'].id)
        payments_.product_price = message.text
        payments_.save()

        user_reject_reason = f"🔴درخواست شما رد شد \n┘ 🔻 علت : ‌ {message.text}."
        bot.send_message(user_id ,  user_reject_reason)
            
        admin_reject_reason= f"درخواست پرداخت رد شد ❌\n ¦─  یوزر درخواست کننده: ‌<code>{user_id}</code>\n ¦─  علت رد درخواست : ‌{message.text}\n ¦─  شماره فاکتور :‌ <code>{payments_.inovice_id.pk}</code>\n ¦─  شماره پرداخت :‌ <code>{payments_.pk}</code>\n."
        
        for i in admins_:
            if i.user_id != message.from_user.id:
                bot.send_message(i.user_id ,  admin_reject_reason)
        
        bot.reply_to(message , admin_reject_reason)
        #cleaning dicts
        clear_dict(PAYMENT_product_price_ON_BUY , user_id)








# - 2 user-side
# --------------------------------------------------------------------------------------------------------------------------
# ------------------------- RENEW-SERVICE ----------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------


@bot.callback_query_handler(func= lambda call : call.data in ['tamdid_service', 'tamdid_pay_with_wallet', 'tamdid_pay_with_card',   'verify_product_for_tamdid', 'back_from_user_tamdid_service', 'tamdid_back_two_panel', 'back_from_confirmation_tamdid', 'back_from_payment_tamdid' , 'back_from_choosing_product_one_panel_tamid' , 'back_from_choosing_product_more_panels_tamdid'] or call.data.startswith(('Tamidi:' , 'tamdid_panelid-' , 'tamdidservice_')))
def tamdid_service(call):
    panels_ = v2panel.objects.all()
    tamdid_panel_products_loading = plans_loading_for_one_panel(tamdid=True)

    #bot status 
    if BOT_STATUS(call.from_user.id) is True :
        #Verify-Phone-Number
        if PHONE_NUMBER(call.from_user.id) is False: 
            #Block-Unblock-InBot
            if BLOCK_OR_UNBLOCK(UserId= call.from_user.id) is False :
                #Force-Join-Channel
                if FORCE_JOIN_CHANNEL(call.from_user.id , bot) == True :
    


                    user_sub = botkb.show_user_subsctription(call.from_user.id)
                    if call.data == 'tamdid_service':
                        Text_1= ' ✢ برای تمدید سرویس اشتراکی را که میخواهید انتخاب نمایید '
                        if user_sub =='no_sub_user_have':
                            bot.answer_callback_query(call.id , 'شما هیچ سرویسی برای تمدید ندارید')
                        else:
                            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.show_user_subsctription(call.from_user.id))
                


                    if call.data.startswith('Tamidi:'):
                        call_data = call.data.split(":")
                        if panels_.count() <= 1: 
                            if tamdid_panel_products_loading == 'panel_disable' :
                                bot.send_message(call.message.chat.id , '⌛️پنل در حال بروزرسانی میباشد . لطفا بعدا مراجعه فرمایید')
                            else : 
                                if isinstance(tamdid_panel_products_loading , InlineKeyboardMarkup):
                                    if call.from_user.id not in TAMDID_USERS_ORDER_BASKET:
                                            TAMDID_USERS_ORDER_BASKET[call.from_user.id] = create_product_entry()
                                    TAMDID_USERS_ORDER_BASKET[call.from_user.id]['config_name'] = call_data[1]
                                    
                                    bot.edit_message_text(buy_service_section_product_msg , call.message.chat.id , call.message.message_id , reply_markup = tamdid_panel_products_loading)      
                                    
                            if tamdid_panel_products_loading == 'sale_closed' :
                                bot.send_message(call.message.chat.id , '⛔️فروش سرویس بسته میباشد ، بعدا مراجعه فرمایید')

                            if tamdid_panel_products_loading == 'sale_open_no_zarfit' :
                                bot.send_message(call.message.chat.id , '🪫ظرفیت فروش به اتمام رسیده است . بعدا مراجعه فرمایید')

                            if tamdid_panel_products_loading == 'no_panel_product' : 
                                bot.send_message(call.message.chat.id , '‼️متاسفیم ، هنوز هیچ سرور یا محصولی برای ارائه وجود ندارد' )

        
                        else :
                            subscriptions_name = call.data.split(':')[1]
                            keyboard = InlineKeyboardMarkup()
                            for i in panels_ :
                                button = InlineKeyboardButton(text=i.panel_name , callback_data=f'tamdid_panelid-{str(i.pk)}-{subscriptions_name}')
                                keyboard.add(button)
                            button_back_2more = InlineKeyboardButton(text='✤ - بازگشت به منوی قبلی - ✤', callback_data='tamdid_back_two_panel')
                            keyboard.add(button_back_2more)
                            bot.edit_message_text(buy_service_section_choosing_panel_msg , call.message.chat.id , call.message.message_id , reply_markup=keyboard)




                    if call.data.startswith('tamdid_panelid-') :
                        call_data = call.data.split('-')
                        tamdid_panels_products_loading = plans_loading_for_two_more_panel(panelid= int(call_data[1]) , tamdid=True)
                        
                        if tamdid_panels_products_loading == 'panel_disable':
                                bot.send_message(call.message.chat.id , '⌛️پنل در حال بروزرسانی میباشد . لطفا بعدا مراجعه فرمایید')
                        else :
                            if isinstance(tamdid_panels_products_loading , InlineKeyboardMarkup) :
                                if call.from_user.id not in TAMDID_USERS_ORDER_BASKET:
                                    TAMDID_USERS_ORDER_BASKET[call.from_user.id] = create_product_entry()
                                TAMDID_USERS_ORDER_BASKET[call.from_user.id]['config_name'] = call_data[2]

                                bot.edit_message_text(buy_service_section_product_msg , call.message.chat.id , call.message.message_id , reply_markup = tamdid_panels_products_loading)


                        if tamdid_panels_products_loading == 'sale_closed':
                            bot.send_message(call.message.chat.id , '⛔️فروش سرویس بسته میباشد ، بعدا مراجعه فرمایید')

                        if  tamdid_panels_products_loading == 'sale_open_no_capcity':
                            bot.send_message(call.message.chat.id , '🪫ظرفیت فروش به اتمام رسیده است . بعدا مراجعه فرمایید')

                        if tamdid_panels_products_loading == 'no_products':
                            bot.send_message(call.message.chat.id , '‼️متاسفیم ، هنوز هیچ سرور یا محصولی برای ارائه وجود ندارد')



                    if call.data.startswith('tamdidservice_'):
                        call_data = call.data.split("_")
                        TAMDID_USERS_ORDER_BASKET[call.from_user.id]['product_id'] = int(call_data[1])
                        TAMDID_USERS_ORDER_BASKET[call.from_user.id]['statement'] = [call_data[2] , call_data[3]]
                        
                        bot.edit_message_text(product_info_msg(TAMDID_USERS_ORDER_BASKET[call.from_user.id]) , call.message.chat.id , call.message.message_id ,  reply_markup=botkb.confirmation(tamdid=True))



                    if call.data =='verify_product_for_tamdid':
                        Text_2 ='⚪️ یک روش پرداخت را انتخاب نمایید'
                        bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.payby_in_user_side(tamdid=True))


                    if call.data =='tamdid_pay_with_wallet':
                        if call.from_user.id in TAMDID_USERS_ORDER_BASKET:
                            req = pay_with_wallet(call , TAMDID_USERS_ORDER_BASKET , tamdid=True)

                            if req == 'not_enough_money_inwallet':
                                bot.send_message(call.message.chat.id , '✣موجودی حساب شما کافی نمیباشد ⚠️\n ┊─ ابتدا موجودی خود را افزایش دهید و مجدد اقدام فرمایید .\n برای اضافه کردن :/add_money')
                            
                            elif req == 'requset_false':
                                print(f'An ERROR occured in sending request to the panel \n\n\t Error-msg :{req}')
                            
                            else:
                                if isinstance(req , dict):
                                    bot.edit_message_text(paied_msg , call.message.chat.id , call.message.message_id)
                                    bot.send_chat_action(chat_id=call.message.chat.id, action='typing')
                                    time.sleep(2.5)
                                    how_to_send(req , TAMDID_USERS_ORDER_BASKET[call.from_user.id] , bot , call.from_user.id)
                                    notif_buy_new_service(bot , call.from_user.id , TAMDID_USERS_ORDER_BASKET[call.from_user.id]['product_id'] , TAMDID_USERS_ORDER_BASKET[call.from_user.id]['config_name'] , tamdid=True)
                                    clear_dict(TAMDID_USERS_ORDER_BASKET , call.from_user.id)
        

                    if call.data =='tamdid_pay_with_card':
                        if call.from_user.id in TAMDID_USERS_ORDER_BASKET:
                            pay_with_card(call , bot , TAMDID_USERS_ORDER_BASKET , USER_PAYCARD_FISH , tamdid=True)
        



                    #back - buttons
                    if call.data in ['back_from_user_tamdid_service', 'tamdid_back_two_panel']:
                        clear_dict(TAMDID_USERS_ORDER_BASKET , call.from_user.id)
                        bot.edit_message_text(welcome_msg , call.message.chat.id , call.message.message_id , reply_markup=botkb.main_menu_in_user_side(call.from_user.id))        

                    #back - buttons
                    if call.data in ['back_from_confirmation_tamdid' , 'back_from_payment_tamdid']:
                        clear_dict(TAMDID_USERS_ORDER_BASKET , call.from_user.id)
                        bot.answer_callback_query(call.id , 'ادامه تمدید محصول لغو گردید')
                        bot.edit_message_text(welcome_msg , call.message.chat.id , call.message.message_id , reply_markup=botkb.main_menu_in_user_side(call.from_user.id))        
                    

                    if call.data == 'back_from_choosing_product_more_panels_tamdid' or call.data =='back_from_choosing_product_one_panel_tamid':
                        Text_back= ' ✢ برای تمدید سرویس اشتراکی را که میخواهید انتخاب نمایید '
                        bot.edit_message_text(Text_back , call.message.chat.id , call.message.message_id , reply_markup=botkb.show_user_subsctription(call.from_user.id))



                else :
                    bot.send_message(call.message.chat.id , force_channel_join_msg , reply_markup=botkb.load_channels(bot , call.from_user.id))
            else :
                bot.send_message(call.message.chat.id , '⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')
        else:
            USER_PHONE_NUMBER[call.message.chat.id] = {'get_number':True}
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True ,one_time_keyboard=True)
            button = KeyboardButton('ارسال شماره', request_contact=True )
            keyboard.add(button)
            Text_1 =  'پیش از ادامه کار با ربات لطفا شماره خود را ارسال نمایید'
            bot.send_message(call.message.chat.id , Text_1 , reply_markup=keyboard)


    else:
        bot.send_message(call.message.chat.id ,'⚙️ربات در حال حاضر غیر فعال است ')












# - 3 user-side
# --------------------------------------------------------------------------------------------------------------------------
# ------------------------- SERVICE-STATUS ---------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------


USER_QUERY_SERVICE = {}
USER_SUB_SHOW = {}

@bot.callback_query_handler(func= lambda call: call.data in ['service_status' , 'back_from_service_status' , 'back_from_user_service_status',  'service_not_inlist']  or call.data.startswith(('serviceshow.' ,'config_usage.' ,'get_config_link.' , 'get_qrcode_link.' , 'get_new_link.' , 'get_removing_account.')))
def show_services(call):

    Text_0 = 'برای نمایش وضعیت سرویس بر روی آن کلیک کنید'

    #bot status 
    if BOT_STATUS(call.from_user.id) is True :    
        #Verify-Phone-Number
        if PHONE_NUMBER(call.from_user.id) is False: 
            #Block-Unblock-InBot
            if BLOCK_OR_UNBLOCK(UserId= call.from_user.id) is False :
                #Force-Join-Channel
                if FORCE_JOIN_CHANNEL(call.from_user.id , bot) ==True :
                    

                    if call.data=='service_status':
                        bot.edit_message_text(Text_0 , call.message.chat.id , call.message.message_id , reply_markup=botkb.show_service_status(call.from_user.id))
                
                

                    if call.data.startswith('serviceshow.'):
                        call_data = call.data.split('.')
                        user_config_name =  call_data[-1].removeprefix("(").removesuffix(")")
                        subscriptions_ = subscriptions.objects.get(user_subscription = user_config_name)
                        request = panelsapi.marzban(subscriptions_.panel_id.pk).get_user(user_config_name) 
                        USER_SUB_SHOW[call.from_user.id] = {'user_sub':subscriptions_.pk , 'config_name':user_config_name , 'rm_sub':True , 'request':request }
                        Text_1 = user_service_status(user_config_name , request)
                        bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.user_service_status(request , call_data[-1]))



                    if call.data.startswith('get_config_link.'):
                        call_data = call.data.split('.')
                        user_config_name =  call_data[-1].removeprefix("(").removesuffix(")")
                        if user_config_name == USER_SUB_SHOW[call.from_user.id]['config_name']:
                            user_sub_link = USER_SUB_SHOW[call.from_user.id]['request']['subscription_url']
                            Text_2 = sub_link_user_service(user_sub_link)
                            bot.send_message(call.message.chat.id , Text_2)
                        else:
                            bot.answer_callback_query(call.id , 'نمیتوانید از این پیام استفاده کنید')
                            bot.send_message(call.message.chat.id , Text_0 , reply_markup=botkb.show_service_status(call.from_user.id))            


                    if call.data.startswith('get_qrcode_link.'):
                        call_data = call.data.split('.')
                        user_config_name =  call_data[-1].removeprefix("(").removesuffix(")")
                        Text_3 = USER_SUB_SHOW[call.from_user.id]['request']['subscription_url']
                        qr = QRcode_maker.make_qrcode(Text_3)
                        if user_config_name == USER_SUB_SHOW[call.from_user.id]['config_name']:
                            bot.send_photo(call.message.chat.id , qr , caption='─🧷نوع تصویر : حاوی لینک هوشمند \nاین تصویر حاوی اطلاعات حساب شما به صورت هوشمند میباشد')
                        else:
                            bot.answer_callback_query(call.id , 'نمیتوانید از این پیام استفاده کنید')
                            bot.send_message(call.message.chat.id , Text_0 , reply_markup=botkb.show_service_status(call.from_user.id))            
                            

                    if call.data.startswith('get_new_link.'):
                        call_data = call.data.split('.')
                        user_config_name = call_data[-1].removeprefix("(").removesuffix(")")   
                        user_name = USER_SUB_SHOW[call.from_user.id]['request']['username']
                        subscriptions_ = subscriptions.objects.get(user_subscription = user_name)
                        request = panelsapi.marzban(subscriptions_.panel_id.pk).revoke_sub(user_name)
                        if user_config_name == USER_SUB_SHOW[call.from_user.id]['config_name']:
                            USER_SUB_SHOW[call.from_user.id]['request'] = request
                            Text_4 = user_service_status(user_config_name , request)
                            bot.answer_callback_query(call.id , 'لینک قبلی اشتراک حذف شده و لینک جدید ایجاد شده ')
                            bot.send_message(call.message.chat.id , Text_4 , reply_markup=botkb.user_service_status(request , user_config_name))
                            bot.send_message(call.message.chat.id , request['subscription_url'])
                        else :
                            bot.answer_callback_query(call.id , 'نمیتوانید از این پیام استفاده کنید')
                            bot.send_message(call.message.chat.id , Text_0 , reply_markup=botkb.show_service_status(call.from_user.id))            




                    if call.data.startswith('get_removing_account.'):
                        call_data = call.data.split('.')
                        user_config_name = call_data[-1].removeprefix("(").removesuffix(")")  
                        if user_config_name == USER_SUB_SHOW[call.from_user.id]['config_name']:
                            bot.answer_callback_query(call.id ,'درحال حذف اشتراک شما ....' , cache_time=3)
                            time.sleep(1.5)
                            try:
                                user_subscription = USER_SUB_SHOW[call.from_user.id]['request']['username']
                                remove_subscription = subscriptions.objects.get(user_subscription =user_subscription)
                                remove_from_panel = panelsapi.marzban(remove_subscription.panel_id.pk).remove_user(user_subscription)
                                time.sleep(1)
                                remove_subscription.delete()
                            except Exception as any_error:
                                print(f'An ERROR occured in [main.py  - LINE 730-750 - FUNC show_services] \n\n\t Error-msg :{any_error}')

                            clear_dict(USER_SUB_SHOW , call.from_user.id)
                            bot.edit_message_text(Text_0 , call.from_user.id , call.message.message_id  , reply_markup=botkb.show_service_status(call.from_user.id))
                        else :
                            bot.answer_callback_query(call.id , 'نمیتوانید از این پیام استفاده کنید')
                            bot.send_message(call.message.chat.id , Text_0 , reply_markup=botkb.show_service_status(call.from_user.id))            





                    if call.data.startswith('config_usage.'):
                        call_data = call.data.split('.')
                        user_config_name = call_data[-1].removeprefix("(").removesuffix(")")  
                        if user_config_name == USER_SUB_SHOW[call.from_user.id]['config_name']:
                            traffic_data = USER_SUB_SHOW[call.from_user.id]['request']['data_limit']
                            if traffic_data is not None:
                                datalimit_math = traffic_data / (1024 * 1024 * 1024)
                                datalimit = f'حجم کلی اشتراک : {datalimit_math} Gb'
                            else:
                                datalimit = 'حجم اشتراک نامحدود میباشد'
                            bot.answer_callback_query(call.id , datalimit)
                        else :
                            bot.answer_callback_query(call.id , 'نمیتوانید از این پیام استفاده کنید')
                            bot.send_message(call.message.chat.id , Text_0 , reply_markup=botkb.show_service_status(call.from_user.id))            




                    if call.data =='service_not_inlist':
                        Text_5= text_not_inmy_list
                        USER_QUERY_SERVICE[call.from_user.id] = {'query':True}

                        if call.from_user.id in USER_STATE and USER_STATE[call.from_user.id][0] in ('buying_new_service' , 'charge_wallet'):
                            clear_dict(USERS_ORDER_BASKET , call.from_user.id)
                            clear_dict(CHARGE_WALLET , call.from_user.id)

                        USER_STATE[call.from_user.id] = ['find_user_service' , time.time()]

                        bot.edit_message_text(Text_5, call.message.chat.id , call.message.message_id)


                    if call.data =='back_from_service_status':
                        bot.edit_message_text(welcome_msg , call.message.chat.id , call.message.message_id , reply_markup=botkb.main_menu_in_user_side(call.from_user.id))


                    if call.data =='back_from_user_service_status':
                        clear_dict(USER_SUB_SHOW , call.from_user.id)
                        bot.edit_message_text(Text_0 , call.message.chat.id , call.message.message_id , reply_markup=botkb.show_service_status(call.from_user.id))

                else :
                    bot.send_message(call.message.chat.id , force_channel_join_msg , reply_markup=botkb.load_channels(bot , call.from_user.id))
            else :
                bot.send_message(call.message.chat.id , '⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')
        else:
            USER_PHONE_NUMBER[call.message.chat.id] = {'get_number':True}
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True ,one_time_keyboard=True)
            button = KeyboardButton('ارسال شماره', request_contact=True )
            keyboard.add(button)
            Text_1 =  'پیش از ادامه کار با ربات لطفا شماره خود را ارسال نمایید'
            bot.send_message(call.message.chat.id , Text_1 , reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id ,'⚙️ربات در حال حاضر غیر فعال است ')








@bot.message_handler(func=lambda message: (len(USER_SUB_SHOW) >= 1 and message.from_user.id in USER_SUB_SHOW and USER_SUB_SHOW[message.from_user.id]['rm_sub']==True))
def rm_mysub(message):

    if message.from_user.id in USER_SUB_SHOW and USER_SUB_SHOW[message.from_user.id]['rm_sub']==True:
        if message.text.startswith('/rm_mysub_'):
            sub_id = message.text.split('_')
            try :
                subscription_ = subscriptions.objects.get(id = sub_id[-1])
                if subscription_.user_id.user_id == message.from_user.id:
                    subscription_.delete()
                Text_0 = f'برای نمایش وضعیت سرویس بر روی آن کلیک کنید \n'
                bot.send_message(message.chat.id , Text_0 , reply_markup=botkb.show_service_status(message.from_user.id))
                clear_dict(USER_SUB_SHOW , message.from_user.id)

            except Exception as removingsub_error:
                print(f'An ERROR occured in [main.py  - LINE 802-820 - FUNC rm_mysub] \n\n\t Error-msg :{removingsub_error}')










@bot.message_handler(func=lambda message: (len(USER_QUERY_SERVICE) >= 1 and message.from_user.id in USER_QUERY_SERVICE and USER_QUERY_SERVICE[message.from_user.id]['query'] == True))
def query_for_user_service(message):
    if message.from_user.id in USER_QUERY_SERVICE and USER_QUERY_SERVICE[message.from_user.id]['query'] == True:

        if message.text == '/cancel' or message.text =='/cancel'.upper():
            clear_dict(USER_QUERY_SERVICE , message.from_user.id)
            Text_cancel = f'برای نمایش وضعیت سرویس بر روی آن کلیک کنید \n'
            bot.send_message(message.chat.id , Text_cancel, reply_markup=botkb.show_service_status(message.from_user.id))
        else:
            msg = message.text
            patt = r'^https?:\/\/[\d\w\.\-\_\/]+'
            if re.search(patt, msg) is not None:
                try:
                    sub_token = msg.split('/')[-1]
                    panels_id = [i.id for i in v2panel.objects.all()]
                    for i in panels_id:
                        try:
                            req = panelsapi.marzban(panel_id=int(i)).get_info_by_token(sub_token)
                            if req:
                                username = req["username"]
                                try:
                                    subscription_user = subscriptions.objects.get(user_subscription=str(username))

                                    if subscription_user.user_id.user_id != message.from_user.id:
                                        bot.send_message(message.chat.id, '⚠️این اشتراک متلعق به شما نیست⚠️')

                                    elif subscription_user  and subscription_user.user_id.user_id == message.from_user.id:
                                        bot.send_message(message.chat.id , '⚠️این اشتراک در لیست اشتراکهای شما قرار دارد⚠️')  

                                except subscriptions.DoesNotExist:
                                    user_ = users.objects.get(user_id=message.from_user.id)
                                    panel_id = v2panel.objects.get(id=int(i))
                                    subscription_creations = create_subscription(user_.user_id , username , panelid=panel_id.pk)
                                    Text_0 = f'برای نمایش وضعیت سرویس بر روی آن کلیک کنید \n ✅اشتراک شما بانام {username} با موفقیت اضافه شد'
                                    bot.send_message(message.chat.id, Text_0, reply_markup=botkb.show_service_status(message.from_user.id))

                                break
                            else:
                                bot.send_message(message.chat.id, 'اشتراکی با این توکن وجود ندارد')        
                        except Exception as findsubapi_error:
                            print(f'An ERROR occured in [main.py  - LINE 818-857 - FUNC query_for_user_service] \n\n\t Error-msg :{findsubapi_error}')
                                
                except Exception as usersubnotexists:  
                    bot.send_message(message.chat.id, 'همچین لینکی در سیستم وجود ندارد')
                clear_dict(USER_QUERY_SERVICE , message.from_user.id)

            else:
                try:
                    panels_id = [i.id for i in v2panel.objects.all()]
                    for i in panels_id:
                        req = panelsapi.marzban(panel_id=int(i)).get_user(username=str(message.text))
                        if req:
                            username = req['username']
                            try:
                                subscription_user_2 = subscriptions.objects.get(user_subscription=str(username))

                                if subscription_user_2.user_id.user_id != message.from_user.id:
                                    bot.send_message(message.chat.id, '⚠️این اشتراک متلعق به شما نیست⚠️')

                                elif subscription_user_2  and subscription_user_2.user_id.user_id == message.from_user.id:
                                        bot.send_message(message.chat.id , '⚠️این اشتراک در لیست اشتراکهای شما قرار دارد⚠️')  

                            except subscriptions.DoesNotExist:
                                panel_id = v2panel.objects.get(id=int(i))
                                user_ = users.objects.get(user_id=message.from_user.id)
                                subscription_creations_2  = create_subscription(user_.user_id , username , panelid=panel_id.pk)
                                Text_0 = f'برای نمایش وضعیت سرویس بر روی آن کلیک کنید \n ✅اشتراک شما با نام {username} با موفقیت اضافه شد'
                                bot.send_message(message.chat.id, Text_0, reply_markup=botkb.show_service_status(message.from_user.id))    
                            break
                        else:
                            bot.send_message(message.chat.id, 'همچین نامی وجود ندارد') 
                except Exception as usersubnotexists_2:
                    print(usersubnotexists_2)
                    bot.send_message(message.chat.id, 'همچین نامی در سیستم وجود ندارد')
                clear_dict(USER_QUERY_SERVICE, message.from_user.id)










# - 4 user-side
# --------------------------------------------------------------------------------------------------------------------------
# ------------------------- WALLET-PROFILE ---------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------


TRANSFER_MONEY_USRTOUSR  = {}




CHARGE_WALLET = {}
CHARGE_WALLET_QUEUE = {}
CHARGE_WALLET_REJECTED_REASON = {}



# ./wallet-profile
@bot.callback_query_handler(func = lambda call : call.data in ['wallet_profile' , 'back_from_wallet_profile' , 'user_id','username' , 'tranfert_money_from_wallet' ] or call.data.startswith(('charge_wallet_'))) 
def wallet_profile(call):
    #bot status 
    if BOT_STATUS(call.from_user.id) is True :
        #Verify-Phone-Number
        if PHONE_NUMBER(call.from_user.id) is False: 
            #Block-Unblock-InBot
            if BLOCK_OR_UNBLOCK(UserId= call.from_user.id) is False :
                #Force-Join-Channel
                if FORCE_JOIN_CHANNEL(call.from_user.id , bot) ==True :

                    if call.data=='wallet_profile':
                        Text_1 ='✤ - پروفایل من : '
                        bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup= botkb.wallet_profile(call.from_user.id))
                

                    if call.data=='user_id':
                        info_list_def = botkb.wallet_profile(call.from_user.id , True)
                        Text_2 = userid_text(info_list_def[0])
                        bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , parse_mode="HTML"  ,reply_markup= botkb.wallet_profile(call.from_user.id))


                    if call.data =='username':
                        info_list_def = botkb.wallet_profile(call.from_user.id , True)
                        Text_3 = username_text(info_list_def[1])
                        bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , parse_mode="HTML" , reply_markup= botkb.wallet_profile(call.from_user.id))
                        


                    if call.data.startswith('charge_wallet_'):
                        
                        clear_dict(CHARGE_WALLET , call.from_user.id)
                        if call.from_user.id not in CHARGE_WALLET:
                            CHARGE_WALLET[call.from_user.id] = charge_wallet_dict()

                        
                        CHARGE_WALLET[call.from_user.id]['charge_wallet'] = True
                        
                        if call.from_user.id in USER_STATE and USER_STATE[call.from_user.id] in ('buying_new_service' , 'find_user_service'):
                            clear_dict(USERS_ORDER_BASKET , call.from_user.id)
                            clear_dict(USER_QUERY_SERVICE , call.from_user.id)

                        USER_STATE[call.from_user.id] = ['charge_wallet' , time.time()]
                    
                        bot.send_message(call.message.chat.id ,'💰مبلغ مورد نظر را به تومان برای شارژ کیف پول خود را وارد نمایید \n\n برای کنسل کردن انتقال  : /CANCEL')



                    if call.data=='tranfert_money_from_wallet':
                        clear_dict(TRANSFER_MONEY_USRTOUSR , call.message.chat.id )
                        TRANSFER_MONEY_USRTOUSR[call.from_user.id] = transfer_money_usrtousr_dict()
                        TRANSFER_MONEY_USRTOUSR[call.from_user.id]['transfer_money_to_user'] = True
                        bot.send_message(call.message.chat.id , '🔻 لطفا ایدی عددی کاربر مقصد را وارد نمایید  \n\n برای کنسل کردن انتقال  : /CANCEL')



                    #back-button
                    if call.data=='back_from_wallet_profile':
                        bot.edit_message_text(welcome_msg , call.message.chat.id , call.message.message_id , reply_markup= botkb.main_menu_in_user_side(call.from_user.id))


                
                else :
                    bot.send_message(call.message.chat.id , force_channel_join_msg , reply_markup=botkb.load_channels(bot , call.from_user.id))
            else :
                bot.send_message(call.message.chat.id , '⚠️شما در ربات مسدود شده اید\n و امکان استفاده از ربات را ندارید ')
        else:
            USER_PHONE_NUMBER[call.message.chat.id] = {'get_number':True}
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True ,one_time_keyboard=True)
            button = KeyboardButton('ارسال شماره', request_contact=True )
            keyboard.add(button)
            Text_1 =  'پیش از ادامه کار با ربات لطفا شماره خود را ارسال نمایید'
            bot.send_message(call.message.chat.id , Text_1 , reply_markup=keyboard)

    else:
        bot.send_message(call.message.chat.id ,'⚙️ربات در حال حاضر غیر فعال است ')











# ./wallet-profile > charge - wallet
@bot.message_handler(func= lambda message: message.text =='/add_money'  or (len(CHARGE_WALLET) >= 1 and message.from_user.id in CHARGE_WALLET) and (CHARGE_WALLET[message.from_user.id]['charge_wallet'] == True or CHARGE_WALLET[message.from_user.id]['send_fish'] == True )  , content_types=['text' , 'photo'])
def charge_wallet_profilewallet(message):

    if message.text == '/add_money' and message.content_type =='text':
        CHARGE_WALLET[message.from_user.id] = charge_wallet_dict()
        CHARGE_WALLET[message.from_user.id]['charge_wallet'] = True
        bot.send_message(message.chat.id ,'💰مبلغ مورد نظر را به تومان برای شارژ کیف پول خود را وارد نمایید \n\n برای کنسل کردن انتقال  : /CANCEL')
        clear_dict(CHARGE_WALLET , message.from_user.id)
        return



    if CHARGE_WALLET[message.from_user.id]['charge_wallet'] == True:
        if message.text =='/cancel' or message.text =='/cancel'.upper():
            Text_1 ='✤ - پروفایل من : '
            bot.send_message(message.chat.id, Text_1 , reply_markup=botkb.wallet_profile(message.chat.id))
            clear_dict(CHARGE_WALLET,message.from_user.id)

        else:
            if message.text.isdigit(): 
                load_shomarekart = buy_service_section_cardtocard_msg(int(message.text))
                if load_shomarekart == 'هیچ شماره کارت فعالی وجود نداره':
                    bot.send_message(message.chat.id , 'هیچ شماره کارت فعالی وجود ندارد')
                    clear_dict(CHARGE_WALLET , message.from_user.id)
                else:
                    bot.send_message(message.chat.id , load_shomarekart)
                    user_ = users.objects.get(user_id = message.chat.id )
                    payments_creations = create_payment(user_ , int(message.text) , paymenentstatus='waiting' , paymenttype="charge-wallet")
                    CHARGE_WALLET[message.from_user.id]['charge_wallet'] = False
                    CHARGE_WALLET[message.from_user.id]['send_fish'] = True
                    CHARGE_WALLET[message.from_user.id]['amount'] = message.text
                    CHARGE_WALLET[message.from_user.id]['payment_ob'] = payments_creations
            else:
                bot.send_message(message.chat.id , 'لطفا مقدار عددی  وارد کنید \n\n برای لغو کردن انتقال :  /CANCEL')
        return
    


    if CHARGE_WALLET[message.from_user.id]['send_fish'] == True :
        if message.content_type =='text':
            if message.text =='/cancel' or message.text =='/cancel'.upper():
                Text_1 ='✤ - پروفایل من : '
                bot.send_message(message.chat.id, Text_1 , reply_markup=botkb.wallet_profile(message.chat.id))
                clear_dict(CHARGE_WALLET , message.from_user.id)
        
        elif message.content_type == 'photo':
                user_ = users.objects.get(user_id = message.from_user.id)
                amount = CHARGE_WALLET[message.from_user.id]['amount']
                Text_2 = f'✅درخواست شارژ کیف پول شما برای ادمین ارسال شد '
                chargewallettxt = charge_wallet_txt(user_.user_id  , amount)

                CHARGE_WALLET[message.from_user.id]['send_fish'] = False
                CHARGE_WALLET[message.from_user.id]['accpet_or_reject'] =True
                CHARGE_WALLET[message.from_user.id]['user_id'] = user_.user_id

                user_uniqe_id = f'{message.from_user.id}_{message.date}'
                CHARGE_WALLET_QUEUE[user_uniqe_id] = CHARGE_WALLET[message.from_user.id]

                bot.send_message(message.chat.id , Text_2)
                bot.send_photo((i.user_id for i in admins.objects.all()) , message.photo[-1].file_id, caption=chargewallettxt , reply_markup=botkb.wallet_accepts_or_decline(user_uniqe_id))
                clear_dict(CHARGE_WALLET , message.from_user.id)
        else:
            bot.send_message(message.chat.id , 'مورد ارسالی باید به صورت تصویر باشد\n مجدد امتحان فرمایید\n /add_money')
            clear_dict(CHARGE_WALLET , message.from_user.id)
    return
        





payments_decline = {'reason' : False  , 'userid':int}
# ./wallet-profile > charge - wallet : accpeting fish
@bot.callback_query_handler(func= lambda call : call.data.startswith(('wallet_accepts_' , 'wallet_decline_')))
def accepts_decline(call):
    try :
        userId = call.data.split('_')
        user_unique_id = f"{userId[2]}_{userId[3]}"
        info = CHARGE_WALLET_QUEUE[user_unique_id]
        user_ = users.objects.get(user_id = userId[2])
        payment_ = payments.objects.get(id = info['payment_ob'].id)
        user_old_wallet = user_.user_wallet
    except Exception as not_fount:
        
        bot.answer_callback_query(call.id , 'بررسی این پرداخت از قبل انجام شده است')



    if call.data.startswith('wallet_accepts_') and len(CHARGE_WALLET_QUEUE) >= 1 and user_unique_id in CHARGE_WALLET_QUEUE and CHARGE_WALLET_QUEUE[user_unique_id]['accpet_or_reject'] == True :
        payment_.payment_status = 'accepted'
        payment_.save()
        user_.user_wallet = user_.user_wallet + int(payment_.amount)
        user_.save()
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('مشاهده کیف پول' , callback_data='wallet_profile'))
        bot.reply_to(call.message ,  '✅درخواست شارژ کیف پول قبول شد')
        bot.send_message(userId[2] ,  '✅درخواست شارژ کیف پول شما با موفقیت انجام شد 👇🏻' , reply_markup=keyboard)
        notif_charge_wallet(bot ,  userId[2] , payment_.amount , user_old_wallet)
        clear_dict(CHARGE_WALLET_QUEUE , user_unique_id)


    if len(CHARGE_WALLET_REJECTED_REASON) == 0:
        if call.data.startswith('wallet_decline_') and len(CHARGE_WALLET_QUEUE) >= 1 and user_unique_id in CHARGE_WALLET_QUEUE and CHARGE_WALLET_QUEUE[user_unique_id]['accpet_or_reject'] ==True :
            if int(userId[2]) not in CHARGE_WALLET_REJECTED_REASON :
                CHARGE_WALLET_REJECTED_REASON[int(userId[2])] = {'reason':True , 'payment':payment_}
                clear_dict(CHARGE_WALLET_QUEUE , user_unique_id)
                bot.send_message(call.message.chat.id , 'علت رد پرداخت را ارسال کنید')
    else :
        bot.answer_callback_query(call.id , 'درخواست ها را جداگانه پردازش کنید')
    






# ./wallet-profile > charge - wallet : getting decline reason
@bot.message_handler(func = lambda message : len(CHARGE_WALLET_REJECTED_REASON) == 1)
def get_product_price(message):
    
    admins_ = admins.objects.all()
    user_id = str
    
    for i in CHARGE_WALLET_REJECTED_REASON.keys():
        user_id = i
    if CHARGE_WALLET_REJECTED_REASON[user_id]['reason'] == True:
        payments_ = payments.objects.get(id = CHARGE_WALLET_REJECTED_REASON[user_id]['payment'].id)
        payments_.payment_status = 'declined'
        payments_.product_price = message.text
        payments_.save()

        user_reject_reason = f"🔴درخواست شما رد شد \n┘ 🔻 علت : ‌ {message.text}."
        bot.send_message(user_id ,  user_reject_reason)

        admin_reject_reason= f"درخواست شارژ کیف رد شد ❌\n ¦─  یوزر درخواست کننده: ‌{user_id}\n ¦─  علت رد درخواست : ‌{message.text}\n ¦─  شماره پرداخت :‌ {payments_.pk}"
        for i in admins_:
            if i.user_id != message.from_user.id:
                bot.send_message(i.user_id ,  admin_reject_reason)
       
        bot.reply_to(message , admin_reject_reason)
        clear_dict(CHARGE_WALLET_REJECTED_REASON , user_id)






# ./wallet_profile > tranfert_money_from_wallet
@bot.message_handler(func= lambda message : (len(TRANSFER_MONEY_USRTOUSR) >= 1 and (TRANSFER_MONEY_USRTOUSR[message.from_user.id]['transfer_money_to_user'] == True or  TRANSFER_MONEY_USRTOUSR[message.from_user.id]['get_amount'] == True)))
def tranfert_money_from_wallet(message):

    if  TRANSFER_MONEY_USRTOUSR[message.from_user.id]['transfer_money_to_user'] == True:
        if message.text == '/cancel' or message.text == '/cancel'.upper():
            clear_dict(TRANSFER_MONEY_USRTOUSR , message.from_user.id)
            Text_1 ='✤ - پروفایل من : '
            bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.wallet_profile(message.from_user.id))
        else:
            if  message.text.isdigit():
                try :
                    user_search = users.objects.filter(user_id = int(message.text))
                    if user_search.exists() :
                        TRANSFER_MONEY_USRTOUSR[message.from_user.id]['transfer_money_to_user'] = False
                        TRANSFER_MONEY_USRTOUSR[message.from_user.id]['get_amount'] = True
                        TRANSFER_MONEY_USRTOUSR[message.from_user.id]['userid_to_transfer'] = message.text
                        bot.send_message(message.chat.id , '💰 مبلغ مورنظر را وارد نمایید \n\n برای کنسل کردن انتقال  : /CANCEL')
                    else :
                        bot.send_message(message.chat.id , '🔎 اکانتی با ایدی عددی ارسال شده وجود ندارد \n\n برای کنسل کردن انتقال  : /CANCEL')
                except users.DoesNotExist as error_users:
                    bot.send_message(message.chat.id , '🔎 اکانتی با ایدی عددی ارسال شده وجود ندارد \n\n برای کنسل کردن انتقال  : /CANCEL')
            else :
                bot.send_message(message.chat.id , '⚠️مقدار وارد شده باید عددی باشد⚠️ ')
        return


    if TRANSFER_MONEY_USRTOUSR[message.chat.id]['get_amount'] == True :
        if message.text == '/cancel' or message.text == '/cancel'.upper():
            clear_dict(TRANSFER_MONEY_USRTOUSR , message.from_user.id)
            Text_2 ='✤ - پروفایل من : '
            bot.send_message(message.chat.id , Text_2 , reply_markup = botkb.wallet_profile(message.from_user.id))
        else :
            if  not message.text.isdigit():
                bot.send_message(message.chat.id , '⚠️مقدار وارد شده باید عددی باشد⚠️\n\n برای کنسل کردن انتقال  : /CANCEL')
            else :
                
                users_want_to_transfer = users.objects.get(user_id = message.from_user.id)
                if users_want_to_transfer.user_wallet  == 0:
                    clear_dict(TRANSFER_MONEY_USRTOUSR , message.from_user.id)
                    bot.send_message(message.chat.id , '❌موجودی حساب شما برای انتقال کافی نمیباشد❌')
                else:
                    users_get_transfer = users.objects.get(user_id = TRANSFER_MONEY_USRTOUSR[message.from_user.id]['userid_to_transfer'])
                        
                    if users_want_to_transfer.user_wallet  >= int(message.text):
                        
                        #user gets the money
                        new_wallet = users_get_transfer.user_wallet + int(message.text)
                        users_get_transfer.user_wallet = new_wallet
                        users_get_transfer.save()

                        #user transer the money
                        new_wallet2 = users_want_to_transfer.user_wallet - int(message.text)
                        users_want_to_transfer.user_wallet = new_wallet2
                        users_want_to_transfer.save()

                        amount = format(int(message.text) , ',')
                        usr_wallet = format(int(users_want_to_transfer.user_wallet) , ',')
                                         
                        Text_who_transfer = text_transfer_money_to_usr(amount , TRANSFER_MONEY_USRTOUSR[message.from_user.id]["userid_to_transfer"] , usr_wallet)
                        Text_who_get = text_transfer_money_to_usr_2(amount)  
                        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('👁مشاهده حساب کاربری ' , callback_data='wallet_profile'))
                        bot.send_message(message.chat.id , Text_who_transfer , reply_markup= keyboard)
                        bot.send_message(TRANSFER_MONEY_USRTOUSR[message.from_user.id]['userid_to_transfer'] , Text_who_get ,reply_markup=keyboard)   
                        
                        notif_transfer_wallet(bot , users_want_to_transfer.user_id , users_get_transfer.user_id , int(message.text))
                        
                        clear_dict(TRANSFER_MONEY_USRTOUSR, message.from_user.id)
                    else:
                        bot.send_message(message.chat.id , '❌موجودی حساب شما برای انتقال کافی نمیباشد❌')

        return














# ---------------------------- MANAGEMENT ----------------------------------------------------------------------------------------


#> ./management
@bot.callback_query_handler(func=lambda call:call.data in ['robot_management' , 'back_from_management'])
def bot_mangement(call):
    
    if call.data=='robot_management':
        Text_1='به مدیریت ربات خوش امدید '
        bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.management_menu_in_admin_side(user_id = call.from_user.id))
    
    
    if call.data=='back_from_management':
        bot.edit_message_text(welcome_msg , call.message.chat.id ,call.message.message_id , reply_markup=botkb.main_menu_in_user_side(call.from_user.id))














# -----------------------------------------------------------------------------------#
# -------------------------PANEL MANAGEMENT----------------------------------------------------------------------#
# -----------------------------------------------------------------------------------#

#> ./Management > Panels 
@bot.callback_query_handler(func=lambda call: call.data in ['panels_management', 'back_from_panels_management', 'add_panel', 'remove_panel', 'manageing_panels', 'back_to_manageing_panels', 'back_to_manage_panel'] or call.data.startswith(('show_panel_remove' ,'show_panel_manage_')))
def handle_panel(call):
    
    Text_0='هیچ پنلی برای حذف کردن پیدا نشد \n\n برای اضافه کردن اولین پنل به ربات /add_panel رو بزنید'
    if check_admins(call.from_user.id , panel=True) == 'panel_access':
        
        if call.data=='panels_management' :
            Text_1='شما در حال مدیریت کردن بخش پنل ها هستید'
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panels_management_menu_keyboard())
    

        #- Adding Panels
        if call.data=='add_panel':
            Text_2='یک اسم برای پنل خود انتخاب کنید ؟\n⚠️.دقت کنید که این اسم مستقیما در قسمت خرید سرویس ها نمایش داده میشود\n\nمثال ها : \n سرویس هوشمند ، سرور مولتی لوکیشن \n\nTO-CANCEL : /cancel'
            bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , add_panel_name)





        #- Removing Panels
        if call.data=='remove_panel':
            no_panel = botkb.panel_management_remove_panel()
            Text_3 = '🚦برای حذف کردن پنلی که میخواهید بر روی اون کلیک کنید'
            if no_panel=='no_panel_to_remove':
                bot.send_message(call.message.chat.id , Text_0)
            else :
                bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panel_management_remove_panel())

        if call.data.startswith('show_panel_remove'):
            call_data = call.data.split('_')[-1]
            bot.edit_message_text('📌پنلی که میخواهید محصولات آن را حذف کنید را انتخاب نمایید' , call.message.chat.id , call.message.message_id , reply_markup=botkb.panel_management_remove_panel(page= int(call_data)))





        #- Manging Panels
        if call.data == 'manageing_panels':
            Text_4='شما در حال مدیریت کردن پنل ها هستید \n\n برای وارد شدن به پنل مدیریت :⚙️ '
            if botkb.panels_management_managing_panels() == 'no_panel_to_manage' :
                bot.send_message(call.message.chat.id , Text_0)
            else :
                bot.edit_message_text(Text_4 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panels_management_managing_panels())

        if call.data.startswith('show_panel_manage_'):
            call_data = call.data.split('_')[-1]
            bot.edit_message_text('شما در حال مدیریت کردن پنل ها هستید \n\n برای وارد شدن به پنل مدیریت :⚙️ ' , call.message.chat.id , call.message.message_id , reply_markup=botkb.panels_management_managing_panels(page= int(call_data)))




        #- Back-button -1
        if call.data=='back_from_panels_management':
            Text_5='به مدیریت ربات خوش امدید '
            bot.edit_message_text(Text_5 , call.message.chat.id , call.message.message_id , reply_markup=botkb.management_menu_in_admin_side(user_id = call.from_user.id))

        if call.data=='back_to_manage_panel':
            Text_6='شما در حال مدیریت کردن پنل ها هستید \n\n برای وارد شدن به پنل مدیریت :⚙️ '
            bot.edit_message_text(Text_6 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panels_management_managing_panels())
        
        if call.data == 'back_to_manageing_panels':
            bot.edit_message_text('شما در حال مدیریت کردن بخش پنل ها هستید' , call.message.chat.id , call.message.message_id , reply_markup=botkb.panels_management_menu_keyboard())
    
    
    else :
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')









#-------------ADD_panel-SECTION
PANEL_ADDING_DB = {'panel_adding_name':None , 'panel_adding_url':None ,
                   'panel_adding_username':None , 'panel_adding_password':None}

@bot.message_handler(commands=['add_panel'])
def handle_add_panel(message):
    if message.text =='/add_panel' :
        if check_admins(message.from_user.id , panel=True) == 'panel_access':
            Text_0='یک اسم برای پنل خود انتخاب کنید؟\n⚠️.دقت کنید که این اسم مستقیما در قسمت خرید سرویس ها نمایش داده میشود\n\nمثال ها : \n سرویس هوشمند ، سرور مولتی لوکیشن \n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_0)
            bot.register_next_step_handler(message , add_panel_name)
        else:
            bot.send_message(message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')
    


def add_panel_name(message):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        bot.send_message(message.chat.id , '✍🏻 اضافه کردن پنل لغو شد !!' , reply_markup=botkb.panels_management_menu_keyboard())
        bot.clear_step_handler(message)
    else:
        if len(message.text) < 124 :
            PANEL_ADDING_DB['panel_adding_name'] = message.text
            Text_1='✅.اسم پنل دریافت شد\n\n .ادرس پنل را ارسال کنید \n فرمت های صحیح :\n<b>http://panelurl.com:port</b> \n <b>https://panelurl.com:port</b> \n <b>http://ip:port</b> \n <b>https://ip:port</b>\n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_1)
            bot.register_next_step_handler(message , add_panel_url)
        else:
            Text_2='❌.اسم پنل نباید بیشتر از 124 حروف باشد\n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_2)
            bot.register_next_step_handler(message , add_panel_name)




def add_panel_url(message):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        bot.send_message(message.chat.id , '✍🏻 اضافه کردن پنل لغو شد !!' , reply_markup=botkb.panels_management_menu_keyboard())
        bot.clear_step_handler(message)
    else:
        pattern=(r'^(http|https):\/\/' 
                r'('
                    r'[\w.-]+'
                    r'|'
                    r'(\d{1,3}\.){3}\d{1,3}'
                r')'
                r'(:\d{1,5})?$'
                )
        http_or_https_chekcer=re.search(pattern , message.text)
        if http_or_https_chekcer: 
            PANEL_ADDING_DB['panel_adding_url']=http_or_https_chekcer.group(0)
            Text_1='✅آدرس پنل دریافت شد \n\n حالا یوزرنیم پنل رو برای ورود به پنل وارد کنید \n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_1)
            bot.register_next_step_handler(message , add_panel_username)
        else:
            Text_3='فرمت ادرس پنل اشتباه است.❌ \n\n فرمت درست به شکل زیر میباشد.\n\n <b>http://panelurl.com:port</b> \n <b>https://panelurl.com:port</b> \n <b>http://ip:port</b> \n <b>https://ip:port</b> '
            bot.send_message(message.chat.id ,Text_3) 
            bot.register_next_step_handler(message , add_panel_url)



def add_panel_username(message):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        bot.send_message(message.chat.id ,'✍🏻 اضافه کردن پنل لغو شد !!' , reply_markup=botkb.panels_management_menu_keyboard())
        bot.clear_step_handler(message)
    else:
        Text_1='✅یوزرنیم پنل دریافت شد.\n\n حالا پسورد پنل رو برای ورود به پنل وارد کنید.\n\nTO-CANCEL : /cancel'
        PANEL_ADDING_DB['panel_adding_username']= message.text
        bot.send_message(message.chat.id , Text_1)
        bot.register_next_step_handler(message , add_panel_password)



def add_panel_password(message):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        bot.send_message(message.chat.id , '✍🏻 اضافه کردن پنل لغو شد !!' , reply_markup=botkb.panels_management_menu_keyboard())
        bot.clear_step_handler(message)
    else:
        PANEL_ADDING_DB['panel_adding_password']= message.text
        Text_1 = '✅پسورد پنل دریافت شد\n\n نوع پنل را انتخاب نمایید\n'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.panel_type())



INBOUNDS_NAME = {'inbound_name':None , 'panelid':None , 'inboundsid':None, 'type':None , 'Inbounds':None}
@bot.callback_query_handler(func= lambda call: call.data in ['marzban_panel' , 'cancel_adding_panel'] or call.data.startswith(('add_inbounds_template_' ,'done_inbounds_' ,'back_from_inbounds_selecting_')) or (INBOUNDS_NAME['Inbounds'] is not None and call.data in INBOUNDS_NAME['Inbounds']))
def panel_type_handler(call):
    
    if call.data == 'marzban_panel':
        add_panel_database(bot , call.message , call,
                           panelname=PANEL_ADDING_DB['panel_adding_name'] , panelurl= PANEL_ADDING_DB['panel_adding_url'] , 
                           panelusername=PANEL_ADDING_DB['panel_adding_username'] , panelpassword= PANEL_ADDING_DB['panel_adding_password'] ,
                           paneltype='marzban')


    if call.data =='cancel_adding_panel':
        Text_1='شما در حال مدیریت کردن بخش پنل ها هستید'
        bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup= botkb.panels_management_menu_keyboard())



    if call.data.startswith('add_inbounds_template_'):
        call_data = call.data.split('_')[-1]
        INBOUNDS_NAME['panelid'] = call_data
        INBOUNDS_NAME['type'] = 'add_inbounds'
        bot.edit_message_text('یک نام برای تمپلیت اینباند خودانتخاب نمایید\n\nTO-CANCEL : /cancel' , call.message.chat.id , call.message.message_id)
        bot.register_next_step_handler(call.message , lambda message : inbound_template_name(message , call_data))




    if INBOUNDS_NAME['Inbounds'] is not None and call.data in INBOUNDS_NAME['Inbounds']:
        inbounds_list=INBOUNDS_NAME['Inbounds']
        for i in inbounds_list:
            if call.data==i:
                index_inboundlist=inbounds_list.index(call.data)
                if '✅' in i:
                    new_values=i.replace('✅', '❌')
                    inbounds_list[index_inboundlist]=new_values  
                elif '❌' in i:
                    new_values=i.replace('❌', '✅')
                    inbounds_list[index_inboundlist]=new_values  
                else:
                    values=i + '✅'
                    inbounds_list[index_inboundlist]=values  

            inbounds_checkmark=[]
            
            for i in INBOUNDS_NAME['Inbounds']:
                if  '✅' in i:
                    inbounds_checkmark.append(i.strip('✅'))
        if INBOUNDS_NAME['type'] == 'add_inbounds':
            keyboard = botkb.select_inbounds(inbounds_list , INBOUNDS_NAME['panelid'])
        else:
            keyboard = botkb.select_inbounds(inbounds_list , INBOUNDS_NAME['panelid'] , INBOUNDS_NAME['inboundsid'])
        Text_2=f"✅ نام تمپلیت اینباند دریافت شد\nلیست اینباند های انتخابی:\n\n {inbounds_checkmark}" 
        bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=keyboard)




    if call.data.startswith('done_inbounds_'):
        call_data = call.data.split('_')
        grouped_inbounds = {}
        for items in INBOUNDS_NAME['Inbounds']:
            key , value = items.split(':' , 1)
            if '✅' in value:
                if key not in grouped_inbounds:
                    grouped_inbounds[key]=[]
                grouped_inbounds[key].append(value.strip('✅').strip())

        if len(grouped_inbounds) > 0:
            if INBOUNDS_NAME['type'] =='add_inbounds':
                panel_ = v2panel.objects.get(id = call_data[2])
                panelinbounds_ = panelinbounds.objects.create(inbound_name = INBOUNDS_NAME['inbound_name'] , panel_id = panel_ , inbounds_selected = json.dumps(grouped_inbounds , indent=1))
                Text_1='تمپلیت اینباند با موفقیت اضافه شد\n برای مدیریت کردن تنظیمات پنل بروی گزینه بازگشت به منوی قبلی کلیک کنید'
                bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.inbounds_adding(call_data[2]))
                INBOUNDS_NAME.update({key:None for key in INBOUNDS_NAME.keys()})
            else:
                panelinbound_ = panelinbounds.objects.get(id =INBOUNDS_NAME['inboundsid'])
                panelinbound_.inbounds_selected = json.dumps(grouped_inbounds , indent=1)
                panelinbound_.save()
                bot.edit_message_text(inbound_info(panelinbound_.pk) , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_inbound_template(panelinbound_.pk))
        else:
            bot.answer_callback_query(call.id , 'اینباند محصول نمیتواند خالی باشد')
            INBOUNDS_NAME.update({key:None for key in INBOUNDS_NAME.keys()})



    if call.data.startswith('back_from_inbounds_selecting_'):
        call_data = call.data.split("_")
        if INBOUNDS_NAME['type'] =='edit_inbound':
            Text_1 = inbound_info(call_data[5])
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup= botkb.manage_inbound_template(call_data[5]))
        else:
            Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید'
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_selected_panel(panel_pk= call.data.split('_')[4]))

        

def inbound_template_name(message , panelid):
    if message.text == '/cancel' or message.text =='/cancel'.upper():
        Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.manage_selected_panel(panel_pk=panelid))
        bot.clear_step_handler(message)
    else:
        inbounds = panelsapi.marzban(panel_id=panelid).get_inbounds()
        INBOUNDS_NAME['inbound_name'] = message.text
        INBOUNDS_NAME['Inbounds'] = [f" {tag['protocol']} : {tag['tag']} " for outer in inbounds for tag in inbounds[outer]]
        Text_1=f"✅ نام تمپلیت اینباند دریافت شد\n 👇🏻 اینباند های انتخابی را از لیست زیر انتخاب نمایید" 
        keyboard = botkb.select_inbounds(INBOUNDS_NAME['Inbounds'] , panelid)
        bot.send_message(message.chat.id , Text_1 ,  reply_markup= keyboard)



#-------------REMOVE_panel-SECTION
#> ./Management > Panel > Remove_Panel 
@bot.callback_query_handler(func=lambda call:call.data.startswith(('remove_products_panel_' , 'remove_only_panel_' , 'panel_remove_')) or call.data in [ 'back_to_remove_panel_section'] )
def handle_removing_panels(call): 
    
    Text_0='هیچ پنلی برای حذف کردن پیدا نشد \n\n برای اضافه کردن اولین پنل به ربات /add_panel رو بزنید'
    if check_admins(call.from_user.id , panel=True) == 'panel_access':
        
        if call.data.startswith('panel_remove_'):
            panel_id= call.data.split('_')
            subscriptions_active = subscriptions.objects.filter(panel_id = panel_id[-1])
            Text_1 =f'''

عمل ترجیحی را انتخاب نمایید  

برای حذف کردن پنل به نکات زیر توجه فرمایید
درصورتی که برای پنل انتخابی  اشتراک فعالی وجود داشته باشد نمیتوانید آن را حذف کنید

در صورتی که فقط حذف پنل را انتخاب نمایید در فاکتور های مربوطه ارجاع به پنل پاک خواهد شد و همچنین محصولات به صورت بدون پنل در لیست محصولات نمایش داده خواهد شد
و میتوانید آن را به پنل جدید اختصاص دهید

اشتراک های فعال این پنل : {subscriptions_active.count()} عدد
'''
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panel_management_remove_panel(panel_id[-1] , kind=True))


        if call.data.startswith('remove_only_panel_'):
            panel_id = call.data.split("_")
            remove_panel_database(bot , call , panel_id[-1] , panel=True)


        if call.data.startswith('remove_products_panel_'):
            panel_id = call.data.split("_")
            remove_panel_database(bot , call , panel_id[-1] , product=True)


        #- Back-button -2 
        if call.data=='back_to_remove_panel_section':
            Text_back_2 = '🚦برای حذف کردن پنلی که میخواهید بر روی اون کلیک کنید'    
            bot.edit_message_text(Text_back_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.panel_management_remove_panel())

    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')



#-------------MANAGING_panel-SECTION

#> ./Management > Panel > Manageing_Panels(step-1)
@bot.callback_query_handler(func=lambda call:call.data.startswith(('managing_panel_' , 'panel_status_' , 'panel_name_' ,'panel_url_' ,
                                                                    'reality_flow_'  , 'xtls-rprx-vision_' , 'None_realityFlow_' ,
                                                                    'inbound_settings_', 'back_from_template_inbouds_' ,
                                                                    'panel_capacity_', 'capcity_mode_','sale_mode_' ,'all_capcity_', 'back_from_panel_capcity_list_' ,
                                                                    'send_config_', 'qrcode_sending_' , 'link_sending_' , 'back_from_panel_howtosend_list_',
                                                                    'panel_statics_' , 'panel_statics_' , 'updating_panel_' , 'back_from_panel_static_')))
def handle_panel_management(call):
    
    call_data=call.data.split('_')

    if check_admins(call.from_user.id , panel=True) == 'panel_access':
        
        if call.data.startswith('managing_panel_'):
            Text_1='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید'
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_selected_panel(panel_pk=call_data[-1]))


        #- Change-Status
        if call.data.startswith('panel_status_'):
            change_panel_status(bot , call , call_data[2])


        #- Change-Name
        if call.data.startswith('panel_name_'):
            Text_2=f'یک نام جدید برای پنل وارد کنید \n\nنام فعلی : {call_data[3]}\n\nTO-CANCEL : /cancel'
            bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , lambda message : change_panel_name(bot , message , call_data[2]))


        #- Change-Url
        if call.data.startswith('panel_url_'):
            Text_3=f' ادرس جدید پنل را وارد کنید\n\n ادرس فعلی : <code>{call_data[3]}</code> \n\nTO-CANCEL : /cancel'
            bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , lambda message : change_panel_url(bot , message , call_data[2]))



        #- Change-RealityFLow
        if call.data.startswith('reality_flow_'):
            Text_6='حالت ریلیتی - فلو برای کل اشتراک ها رواین پنل انتخاب کنید'
            bot.edit_message_text(Text_6 , call.message.chat.id , call.message.message_id , reply_markup=botkb.changin_reality_flow(call_data[2]))

        #- Reality - flow 
        if call.data.startswith('xtls-rprx-vision_'):
            change_panel_realityflow(bot , call , call_data[1] ,  reality=True)
            
        #-none Reality - flow 
        if call.data.startswith('None_realityFlow_'):
            change_panel_realityflow(bot , call , call_data[2] , none_reality=True)




        if call.data.startswith('inbound_settings_'):
            text = 'به بخش تنظیمات اینباند ها خوش امدید\n برای ادیت کردن هر اینباند بروی ان کلیک کنید'
            bot.edit_message_text(text , call.message.chat.id , call.message.message_id , reply_markup=botkb.inbounds_adding(call_data[-1]))

        if call.data.startswith('back_from_template_inbouds_'):
            Text='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید'
            bot.edit_message_text(Text , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_selected_panel(call_data[-1]))



        #- Change-Capcity 
        if call.data.startswith('panel_capacity_'):
            Text_9='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید'
            bot.edit_message_text(Text_9 , call.message.chat.id , call.message.message_id , reply_markup = botkb.changin_panel_capcity(panel_pk=call_data[2]))

        #- Capcity-mode
        if call.data.startswith('capcity_mode_'):
            change_panel_capcitymode(bot , call , call_data[2])

        #- Sale-mode
        if call.data.startswith('sale_mode_'):
            change_panel_salemode(bot , call , call_data[2])

        #- Change-Allcapcity
        if call.data.startswith('all_capcity_'):
            Text_10 = f'مقدار عددی ظرفیت کلی پنل را ارسال کنید \n ظرفیت فعلی :{call_data[3]}\n\nTO-CANCEL : /cancel'
            bot.send_message(call.message.chat.id , Text_10)
            bot.register_next_step_handler(call.message , lambda message : change_panel_allcapcity(bot , message , call_data[2]))


        if call.data.startswith('back_from_panel_capcity_list_') :
            Text_11='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید'
            bot.edit_message_text(Text_11 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_selected_panel(panel_pk=call_data[-1]))




        if call.data.startswith('send_config_'):
            Text_12='تعیین کنید هنگام خرید موفق اشتراک  لینک ها چگونه ارسال شوند ⁉️'
            bot.edit_message_text(Text_12 , call.message.chat.id , call.message.message_id , reply_markup=botkb.how_to_send_links(call_data[2]))

         #- QRcode
        if call.data.startswith('qrcode_sending_'):
            change_panel_qrcode(bot , call , call_data[-1])

        #- Config
        if call.data.startswith('link_sending_'):
            change_panel_config(bot , call , call_data[-1])

        #- Back button
        if call.data.startswith('back_from_panel_howtosend_list_'): 
            Text_13='🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید'
            bot.edit_message_text(Text_13 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_selected_panel(panel_pk=call_data[-1]))
        

        if call.data.startswith('panel_statics_'):
            bot.edit_message_text(panel_state(call_data[2]) , call.message.chat.id , call.message.message_id , reply_markup=botkb.updating_panel(call_data[2]))


        if call.data.startswith('updating_panel_'):
            bot.edit_message_text(panel_state(call_data[-1]) , call.message.chat.id , call.message.message_id , reply_markup=botkb.updating_panel(call_data[-1]))
        

        if call.data.startswith('back_from_panel_static_'):
            Text_14 = '🔗برای تغییر تنظیمات  بر روی دکمه ها کلیک کنید'
            bot.edit_message_text(Text_14 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_selected_panel(call_data[-1]))

    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')





@bot.callback_query_handler(func=lambda call:   call.data.startswith(('template_panel_', 'change_template_name_' , 'change_template_inbounds_' , 'remove_template_inbounts_' , 'back_from_inbound_chaning_')))
def handle_add_inbounts(call):
   

    if call.data.startswith('template_panel_'):
        call_data = call.data.split('_')
        Text_2 = inbound_info(call_data[-1])
        bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_inbound_template(call_data[-1]))


    if call.data.startswith('change_template_name_'):
        call_data = call.data.split('_')
        bot.edit_message_text('نام جدید تپملیت اینباند را ارسال نمایید\n\nTO-CANCEL : /cancel' , call.message.chat.id , call.message.message_id)
        bot.register_next_step_handler(call.message , lambda message: change_inbound_template_name(message , call_data[3]))



    if call.data.startswith('change_template_inbounds_'):
        call_data = call.data.split('_')
        Text_3 = 'بعد از انتخاب اینباند های ترجیحی بروی گزینه تایید و ذخیره بزنید'
        panelinbound_ = panelinbounds.objects.get(id = int(call_data[3]))
        inbounds = panelsapi.marzban(panel_id= panelinbound_.panel_id.pk).get_inbounds()
        INBOUNDS_NAME['Inbounds'] = [f" {tag['protocol']} : {tag['tag']} " for outer in inbounds for tag in inbounds[outer]]
        keyboard = botkb.select_inbounds(INBOUNDS_NAME['Inbounds'] , panelinbound_.panel_id.pk , panelinbound_.pk)
        bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , reply_markup=keyboard)
        INBOUNDS_NAME['type'] = 'edit_inbound'
        INBOUNDS_NAME['panelid'] = panelinbound_.panel_id.pk
        INBOUNDS_NAME['inboundsid'] = panelinbound_.pk


    if call.data.startswith('remove_template_inbounts'):
        panel_id = ''
        call_data = call.data.split('_')
        Text_4 = 'به بخش تنظیمات اینباند ها خوش امدید\n برای ادیت کردن هر اینباند بروی ان کلیک کنید'
        panelinbound_ = panelinbounds.objects.get(id = call_data[3])
        prodcuts_ = products.objects.filter(panelinbounds_id = panelinbound_)
        panel_id = panelinbound_.panel_id.pk 
        for i in prodcuts_:
            product_status = 0 if i.product_status == 1 else 0 
            i.product_status = product_status
            i.save()
        panelinbound_.delete()
        bot.edit_message_text(Text_4 , call.message.chat.id , call.message.message_id , reply_markup=botkb.inbounds_adding(panel_id))
        

    if call.data.startswith('back_from_inbound_chaning_'):
        call_data = call.data.split('_')[-1]
        Text_5 = 'به بخش تنظیمات اینباند ها خوش امدید\n برای ادیت کردن هر اینباند بروی ان کلیک کنید'
        bot.edit_message_text(Text_5 ,  call.message.chat.id , call.message.message_id , reply_markup=botkb.inbounds_adding(call_data)) 



def change_inbound_template_name(message , inbound_id):
    if message.text == '/cancel' or message.text =='/cancel'.upper():
        Text_1 = inbound_info(inbound_id)
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.manage_inbound_template(inbound_id))
    else:
        panelinbound_ = panelinbounds.objects.get(id = inbound_id)
        panelinbound_.inbound_name = message.text
        panelinbound_.save()
        Text_2 = inbound_info(inbound_id)
        bot.send_message(message.chat.id , Text_2 , reply_markup=botkb.manage_inbound_template(inbound_id))




















# -----------------------------------------------------------------------------------#
# -------------------------PRODUCTS MANAGEMENT----------------------------------------------------------------------#
# -----------------------------------------------------------------------------------#
#> ./Management > Product 
@bot.callback_query_handler(func=lambda call:call.data in [ 'products_management' , 'add_product' , 'remove_products' , 'manage_products' , 'back_from_products_managing'] or call.data.startswith('back_products') )
def handle_products(call) :

    panel_=v2panel.objects.all()
    Text_0='هیچ پنلی برای لود کردن وجود ندارد \n\n اولین پنل خود را اضافه کنید :/add_panel'
    
    if check_admins(call.from_user.id , product=True) == 'product_access':

        if call.data=='products_management':
            Text_1='✏️شما در حال مدیریت کردن بخش محصولات میباشید'
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.products_management_menu_keyboard())



        #- Adding products 
        if call.data=='add_product':
            no_panel=botkb.load_panel_add_product(add_product=True)
            if no_panel=='no_panel_add_product':
                bot.send_message(call.message.chat.id , Text_0)
            else:
                Text_3='📌یک پنل را برای اضافه کردن محصول به آن انتخاب کنید \n\n⚠️محصول زیر مجموعه پنل خواهد بود '
                bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , reply_markup=botkb.load_panel_add_product(add_product=True))
                


        #- Removing products
        if call.data == 'remove_products' :
            no_panel=botkb.load_panel_add_product(remove_product=True)
            if no_panel=='no_panel_add_product':
                bot.send_message(call.message.chat.id , Text_0)
            else:
                Text_4='📌پنلی که میخواهید محصولات آن را حذف کنید را انتخاب نمایید'
                bot.edit_message_text(Text_4, call.message.chat.id , call.message.message_id , reply_markup=botkb.load_panel_add_product(remove_product=True))
            


        #- Managing products
        if call.data=='manage_products':
            no_panel=botkb.load_panel_add_product(manage_product=True)
            if no_panel=='no_panel_add_product':
                bot.send_message(call.message.chat.id , Text_0)
            else:
                Text_5='📌پنلی را که میخواهید محصولات آن را مدیریت کنید انتخاب نمایید'
                bot.edit_message_text(Text_5 , call.message.chat.id , call.message.message_id , reply_markup=botkb.load_panel_add_product(manage_product=True))
   

        #Back - buttons
        if call.data=='back_from_products_managing':
            Text_2='به مدیریت ربات خوش امدید'
            bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.management_menu_in_admin_side(user_id = call.from_user.id))


        if call.data.startswith('back_products'):
            Text_5= '✏️شما در حال مدیریت کردن بخش محصولات میباشید'
            bot.edit_message_text(Text_5 , call.message.chat.id , call.message.message_id , reply_markup=botkb.products_management_menu_keyboard())

    else :
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')


                           

#-------------ADD_products-SECTION
PRODUCT_ADDING_DB ={'product_name_adding' : None , 'product_datalimit_adding' : None ,
                    'product_expire_adding' : None , 'product_price_adding' : None ,
                    'panel_id' : None , 'inboundsid':None}

#> ./Management > Product > Add_Product - Select_PanelId(step-1)
@bot.message_handler(commands=['add_product'])
def handle_add_product(message):
    if message.text =='/add_product':

        if check_admins(message.from_user.id , product=True) == 'product_access':
            Text_0='هیچ پنلی برای لود کردن وجود ندارد \n\n اولین پنل خود را اضافه کنید :/add_panel'
            no_panel=botkb.load_panel_add_product(add_product=True)
            if no_panel=='no_panel_add_product':
                bot.send_message(message.chat.id , Text_0)
            else:
                Text_3='📌یک پنل را برای اضافه کردن محصول به آن انتخاب کنید \n\n⚠️محصول زیر مجموعه پنل خواهد بود '
                bot.send_message(message.chat.id , Text_3 , reply_markup=botkb.load_panel_add_product(add_product=True))
        else :
            bot.send_message(message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')


@bot.callback_query_handler(func=lambda call:call.data.startswith('add_product_'))
def handle_incoming_product_panelId(call):
    if call.data.startswith('add_product_'): 
        call_data=call.data.split("_")
        PRODUCT_ADDING_DB['panel_id'] = call_data[-1]
        Text_1='📌یک نام برای محصول خود انتخاب نمایید \n\nTO-CANCEL : /cancel'
        bot.send_message(call.message.chat.id , Text_1)
        bot.register_next_step_handler(call.message , product_name)



def product_name(message):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='✍🏻اضافه کردن محصول لغو شد!!'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.products_management_menu_keyboard())
    else:
        if len(message.text)<=128:  
            PRODUCT_ADDING_DB['product_name_adding'] = message.text
            Text_2='🔋مقدار حجم محصول را ارسال کنید \n ⚠️ دقت کنید حجم محصول باید برحسب گیگابایت باشد \n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_2)
            bot.register_next_step_handler(message , product_datalimit)
        else:
            Text_3='❌نام محصول نباید بیشتر از 64 حرف/کرکتر باشد \n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_3)
            bot.register_next_step_handler(message , product_name)



def product_datalimit(message):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='✍🏻اضافه کردن محصول لغو شد!!'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.products_management_menu_keyboard())
    else :
        if message.text.isdigit():
            data_limit_checker = re.search(r'^\d+(\.\d{1,2})?$', message.text)
            if data_limit_checker:
                PRODUCT_ADDING_DB['product_datalimit_adding'] = float(data_limit_checker.group(0))
                Text_2='⌛️مقدار دوره محصول را ارسال کنید \n\n مثال :30,60 \n⚠️ این عدد در هنگام خرید محصول به عنوان روز در نظر گرفته میشود : مثلا 30 روز\n\nTO-CANCEL : /cancel'
                bot.send_message(message.chat.id , Text_2)
                bot.register_next_step_handler(message , product_expiredate)
            else:
                Text_3='❌فرمت حجم محصول اشتباه است\n\nفرمت صحیح میتواند با اعشار تمام شود \nمثلا:20,30 \n\nTO-CANCEL : /cancel'
                bot.send_message(message.chat.id , Text_3)
                bot.register_next_step_handler(message , product_datalimit)
        else:
            Text_4='❌متن ارسالی باید شامل عدد باشد نه حروف \n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_4)
            bot.register_next_step_handler(message , product_datalimit)



def product_expiredate(message):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='✍🏻 .اضافه کردن محصول لغو شد!!'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.products_management_menu_keyboard())
    else:
        if message.text.isdigit():
            PRODUCT_ADDING_DB['product_expire_adding'] = message.text
            Text_2='💵قیمت محصول را ارسال کنید \n⚠️قیمت محصول باید به تومان باشد\n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_2)
            bot.register_next_step_handler(message , product_price)
        else : 
            Text_3='❌متن ارسالی باید شامل عدد باشد نه حروف \n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_3)
            bot.register_next_step_handler(message , product_expiredate)


def product_price(message):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='✍🏻 .اضافه کردن محصول لغو شد!!'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.products_management_menu_keyboard())
    else :
        if not message.text.isdigit():
            Text_2='❌متن ارسالی باید شامل عدد باشد نه حروف \n\nTO-CANCEL : /cancel'
            bot.send_message(message.chat.id , Text_2 )
            bot.register_next_step_handler(message , product_price)
        else:
            PRODUCT_ADDING_DB['product_price_adding'] = message.text
            Text_3 = 'اینباند محصول را از لیست زیر انتخاب نمایید\n شما میتوانید در داخل تنظیمات هر پنل اقدام به تغییر اینباند ها کنید'
            bot.send_message(message.chat.id , Text_3 , reply_markup=botkb.loading_panles_inbounds_for_producs(PRODUCT_ADDING_DB['panel_id']))     
            

@bot.callback_query_handler(func=lambda call : call.data.startswith('inbound_number_'))
def handle_adding_products(call):
    if call.data.startswith('inbound_number_'):
        call_data = call.data.split('_')
        PRODUCT_ADDING_DB['inboundsid'] = call_data[-1]
        add_product_database(call , bot , PRODUCT_ADDING_DB['product_name_adding'] , PRODUCT_ADDING_DB['product_datalimit_adding'] , PRODUCT_ADDING_DB['product_datalimit_adding'] , PRODUCT_ADDING_DB['product_price_adding'] , PRODUCT_ADDING_DB['panel_id'] ,PRODUCT_ADDING_DB['inboundsid'])





#-------------REMOVE_products-SECTION

#> ./Management > Product > Remove-Product (step-1)
@bot.callback_query_handler(func=lambda call:call.data.startswith(('remove_products_' , 'delete_prodcut_' , 'show_product_remove_' ,'delete_null_prodcut_' , 'show_null_product_remove_')) or call.data in ['back_from_remove_products' , 'products_without_panel'])
def handle_removing_products(call):
    
    if check_admins(call.from_user.id , product=True) == 'product_access':
        #-load panels 
        if call.data.startswith('remove_products_'):
            call_data=call.data.split('_')
            if botkb.product_managemet_remove_products(panelid = call_data[-1]) == 'no_products_to_remove':
                Text_1='هیچ محصولی وجود ندارد \n محصولی اضافه  کنید\n\n /add_product'
                bot.send_message(call.message.chat.id , Text_1)
            else:
                Text_2='محصولی را که میخواهید حذف کنید را انتخاب کنید\n برای حذف کافیست بر روی آن کلیک کنید'
            
                bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.product_managemet_remove_products(panelid = call_data[-1]))
                

        #- delete product
        if call.data.startswith('delete_prodcut_'):
            call_data=call.data.split('_')
            remove_product_database(bot , call ,  call_data[2] , call_data[3])


        if call.data.startswith('show_product_remove_'):
            call_data = call.data.split('_')
            Text_3=f'محصولی را که میخواهید حذف کنید را انتخاب کنید\n برای حذف کافیست بر روی آن کلیک کنید \n صفحه :‌ {call_data[3]}'
            bot.edit_message_text(Text_3 , call.message.chat.id ,call.message.message_id ,reply_markup= botkb.product_managemet_remove_products(panelid=call_data[-1] , page= int(call_data[3])))
            


        if call.data =='products_without_panel':
            Text_4 = 'لیست محصولات بدون به صورت زیر میباشد در صورت تمایل برای حذف آن ها بر روی علامت مربوطه کلیک کنید'
            bot.edit_message_text(Text_4 , call.message.chat.id , call.message.message_id , reply_markup=botkb.product_managemet_remove_null_products())
        
        if call.data.startswith('delete_null_prodcut_'):
            call_data = call.data.split('_')
            remove_product_database(bot , call , null_products=int(call_data[-1]))


        if call.data.startswith('show_null_product_remove_'):
            call_data = call.data.split('_')
            Text_3=f'محصولی را که میخواهید حذف کنید را انتخاب کنید\n برای حذف کافیست بر روی آن کلیک کنید \n صفحه :‌ {call_data[-1]}'
            bot.edit_message_text(Text_3 , call.message.chat.id ,call.message.message_id ,reply_markup= botkb.product_managemet_remove_null_products(page=call_data[-1]))
            

        if call.data=='back_from_remove_products':
            Text_back_2='پنلی که میخواهید محصولات آن را حذف کنید را انتخاب نمایید'
            bot.edit_message_text(Text_back_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.load_panel_add_product(remove_product=True) )

    else :
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')



#-------------MANAGING_products-SECTION
#> ./Management > Products > Manage-Product(step-1)
@bot.callback_query_handler(func=lambda call:call.data.startswith(('managing_products_' , 'down_' , 'up_' , 'show_product_managements_' )) or call.data in ['back_from_manage_products_list_updown'])
def manage_product_choose_panel(call): 
    
    if check_admins(call.from_user.id , product=True) == 'product_access':        
        #- Listing product
        if call.data.startswith('managing_products_'):
            call_data =call.data.split('_')
            if botkb.products_list(call_data[-1])=='no_product_to_manage':
                Text_1='هیچ محصولی وجود ندارد ❌\n محصولی اضافه  کنید\n\n /add_product'
                bot.send_message(call.message.chat.id , Text_1)
            else:
                panel_=v2panel.objects.get(id=call_data[-1])
                Text_2=f'📝لیست تمام محصولات پنل <b>({panel_.panel_name})</b> به صورت زیر میباشد'
                bot.edit_message_text(Text_2 , call.message.chat.id ,call.message.message_id ,reply_markup= botkb.products_list(panelid=call_data[-1]) , parse_mode='HTML')
            

        #- down button
        if call.data.startswith('down_'):
            call_data=call.data.split('_')
            botkb.products_list(panelid=call_data[2] , down=int(call_data[1]) )
            Text_3='جایگاه محصول به پایین🔻 جابه جا شد \n ⚪️این جابه جایی در نحوه نمایش محصول هنگام خرید تاثیر خواهد گزاشت'
            bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , reply_markup=botkb.products_list(panelid=call_data[2] ,  page=int(call_data[-1])))

        #- up button
        if call.data.startswith('up_'):
            call_data=call.data.split('_')
            Text_3='جایگاه محصول به بالا🔺 جابه جا شد \n ⚪️این جابه جایی در نحوه نمایش محصول هنگام خرید تاثیر خواهد گزاشت'
            botkb.products_list(panelid=call_data[2] , up=int(call_data[1]) )
            bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , reply_markup=botkb.products_list(panelid=call_data[2] ,  page=int(call_data[-1])))
        
        #- Next button
        if call.data.startswith('show_product_managements_'):
            call_data=call.data.split('_')
            Text_4=f'بروی محصولی که میخواهید مدیریت کنید کلیک کنید\n 📂صفحه محصول بارگزاری شده :{int(call_data[3])}'
            bot.edit_message_text(Text_4 , call.message.chat.id , call.message.message_id , reply_markup=botkb.products_list(panelid=call_data[-1]  ,  page=int(call_data[3])))
            

        #- Back button 
        if call.data=='back_from_manage_products_list_updown':
            Text_back='📌پنلی را که میخواهید محصولات آن را مدیریت کنید انتخاب نمایید'
            bot.edit_message_text(Text_back , call.message.chat.id , call.message.message_id , reply_markup=botkb.load_panel_add_product(manage_product=True))


    else :
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')




#> ./Management > Products > Manage-Product(step-1)
@bot.callback_query_handler(func=lambda call:call.data.startswith(('detaling_product_' , '_pr_status_' , '_product_name_' , '_data_limit_', 'ـexpire_date_' , '_product_price_' , '_inbounds_product_' , 'change_inbound_to_', 'back_from_manage_product_changing_')))
def manage_products_base_id (call) : 
    if check_admins(call.from_user.id , product=True) == 'product_access':    
        #-start changing
        if call.data.startswith('detaling_product_') : 
            call_data =call.data.split('_')
            products_inbound_checking = products.objects.get(id = call_data[-1])
            panel_ = v2panel.objects.get(id = products_inbound_checking.panel_id.pk)
            inbouns_ = panelinbounds.objects.filter(panel_id = panel_)
            if products_inbound_checking.panelinbounds_id is not None:
                Text_1='🖋برای تغییر تنظیمات هر محصول بر روی دکمه های آن کلیک کنید'
                bot.edit_message_text(Text_1,call.message.chat.id ,call.message.message_id , reply_markup=botkb.product_changing_details(product_id=int(call_data[-1])))
            else:
                Text_2 = 'قبل از ادامه لطفا اینباند محصول را تعیین کنید '
                bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.change_products_inbounds(panel_ , products_inbound_checking.pk))


        #-product status
        if call.data.startswith('_pr_status_'):
            call_data = call.data.split('_')
            change_product_status(bot , call , call_data[-1])


        #-product name
        if call.data.startswith('_product_name_'):
            call_data = call.data.split("_")
            Text_3=f'🔗نام جدید محصول را وارد نمایید\n\nTO-CANCEL : /cancel'
            bot.send_message(call.message.chat.id , Text_3)
            bot.register_next_step_handler(call.message , lambda message : change_product_name(bot , message , int(call_data[-1])))   



        #- product data-limit
        if call.data.startswith('_data_limit_') :
            call_data = call.data.split('_')
            Text_4='🔗حجم جدید محصول را وارد نمایید\n\nTO-CANCEL : /cancel'
            bot.send_message(call.message.chat.id , Text_4)
            bot.register_next_step_handler(call.message , lambda message : change_product_datalimt(bot , message , int(call_data[-1])))   


        #- product expire-date
        if call.data.startswith('ـexpire_date_') :
            call_data = call.data.split('_')
            Text_5='🔗دوره جدید محصول را وارد نمایید \n\nTO-CANCEL : /cancel'
            bot.send_message(call.message.chat.id , Text_5)
            bot.register_next_step_handler(call.message , lambda message : change_prdocut_expiredate(bot , message , int(call_data[-1])))   


        #- product cost            
        if call.data.startswith('_product_price_') :
            call_data = call.data.split('_')
            Text_6='🔗قیمت جدید محصول را وارد نمایید \n\nTO-CANCEL : /cancel'
            bot.send_message(call.message.chat.id , Text_6)
            bot.register_next_step_handler(call.message , lambda message : change_product_price(bot , message , int(call_data[-1])))   


        #- product - inbounds
        if call.data.startswith('_inbounds_product_'):
            call_data = call.data.split('_')
            product_ = products.objects.get(id = call_data[-1])
            panel_id = product_.panel_id.pk
            Text_7=f'📥اینباند محصول را انتخاب نمایید و سپس گزینه اتمام را بزنید'
            bot.edit_message_text(Text_7 , call.message.chat.id , call.message.message_id , reply_markup=botkb.change_products_inbounds(panel_id , product_.pk))


        if call.data.startswith('change_inbound_to_'):
            call_data = call.data.split('_')
            Text_8='🖋برای تغییر تنظیمات هر محصول بر روی دکمه های آن کلیک کنید'
            product_ = products.objects.get(id = call_data[-1])
            panelinbound_ = panelinbounds.objects.get(id = call_data[3])
            if product_.panelinbounds_id is None:
                product_status = 0 if product_.product_status == 1 else 0
                product_.product_status = product_status
                product_.panelinbounds_id = panelinbound_
                product_.save()
            bot.edit_message_text(Text_8 , call.message.chat.id , call.message.message_id , reply_markup=botkb.product_changing_details(product_id=int(call_data[-1])))


        if call.data.startswith('back_from_manage_product_changing_'):
            call_data = call.data.split('_')
            panel_=v2panel.objects.get(id=call_data[-1])
            Text_back_2=f'📝لیست تمام محصولات پنل <b>({panel_.panel_name})</b> به صورت زیر میباشد'
            bot.edit_message_text(Text_back_2 , call.message.chat.id ,call.message.message_id ,reply_markup= botkb.products_list(panelid=panel_.pk) , parse_mode='HTML')
               
    else :
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')





        











    

#---------------------------------------------------------------------------------------------------------------------------------#
# -------------------------bot_statics------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------------------#



#//TODO add inline keyboard to this section > for example : which user buy the most , which product have been sold a lot , which panel has a lot user and other things in another versions

@bot.callback_query_handler(func= lambda call: call.data in ['bot_statics', 'back_from_bot_statics', 'users_static', 'products_static', 'panels_static', 'inovices_static', 'payments_static'])
def bot_statics(call):
    
    if check_admins(call.from_user.id , bot_static=True) == 'static_access': 
        if call.data =='bot_statics':
            user_ = users.objects.all().count()
            inovices_ = inovices.objects.all().count()
            payment_ = payments.objects.filter(payment_status = 'accepted').all().count()
            v2panel_ = v2panel.objects.all().count()
            product_ = products.objects.all().count()
            Text_1 = botStatics_1(user_ , v2panel_ , product_ , payment_ , inovices_)
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.bot_static())




        #- bot static - USERS
        if call.data == 'users_static':
            users_ = users.objects
            if users_.all().exists():
                Text_users = botStatics_2(users_)
                more_money = [i for i in users_.filter(user_wallet__gt = 25000).order_by('user_wallet').reverse()[:4]]
                users_static_list = []
                users_static_list.append(Text_users)
                for num , i in enumerate(more_money , 1):
                    user_money = f'\n {num} - 👤 : <code>{str(i.user_id)}</code> : {format(int(i.user_wallet), ",")} تومان'
                    users_static_list.append(user_money)
                users_static_list.append('\n.')
                users_static_text = ''.join(users_static_list)
            else :
                users_static_text = 'هنوز آماری برای ارائه وجود ندارد'
            bot.edit_message_text(users_static_text ,  call.message.chat.id , call.message.message_id , reply_markup=botkb.bot_static(users=True))




        #- bot static - PRODUCTS
        if call.data =='products_static':
            products_ = products.objects
            if products_.all().exists():
                Text_products = botStatics_3(products_)
                product_static_list = []
                product_static_list.append(Text_products)
                
                payments_accpeted_id = [i.inovice_id_id for i in  payments.objects.filter(payment_status= 'accepted' , inovice_id__isnull=False)]
                product_count_name = inovices.objects.filter(id__in = payments_accpeted_id).values('product_name').annotate(Count('product_name'))[:5]
                
                for num,i in enumerate(product_count_name ,1):
                    product_sold = f'\n {num}- 🛍 - <code>{i["product_name"]}</code>'
                    product_static_list.append(product_sold)
                product_static_list.append('\n.')
                product_static_text = ''.join(product_static_list)
            else:
                product_static_text = 'هنوز اطلاعاتی برای ارائه وجود ندارد'
            bot.edit_message_text(product_static_text , call.message.chat.id , call.message.message_id, reply_markup=botkb.bot_static(products=True))







        #- bot static - PANELS
        if call.data =='panels_static':
            panels_ = v2panel.objects
            if panels_.all().exists():
                Text_panels = botStatics_4(panels_)
                panel_id = [i.id for i in  v2panel.objects.all()]
                subs_count = subscriptions.objects.filter(panel_id__in = panel_id).values('panel_id').annotate(Count('panel_id'))
                panels_static_list = []
                panels_static_list.append(Text_panels)
                for num ,i in enumerate(subs_count ,1):
                    panel_name = v2panel.objects.get(id = i["panel_id"]).panel_name
                    panel_sub = f'\n {num}- 🎛 {panel_name} :  {i["panel_id__count"]} عدد'
                    panels_static_list.append(panel_sub)
                panels_static_list.append('\n.')
                panels_static_text = ''.join(panels_static_list)
            else:
                panels_static_text = 'هنوز اماری برای ارائه وجود ندارید'
            bot.edit_message_text(panels_static_text , call.message.chat.id , call.message.message_id , reply_markup=botkb.bot_static(panels=True))





        #- bot static - INOVICES
        if call.data =='inovices_static':
            inovices_ = inovices.objects
            if inovices_.all().exists():
                Text_inovices =botStatics_5(inovices_)
                inovices_static_list = []
                inovices_static_list.append(Text_inovices)

                most_bought_product = inovices_.values('product_name').annotate(Count('product_name'))
                for num,i in enumerate(most_bought_product , 1):
                    prod = f'\n {num}- 🔖 : <code>{i["product_name"]}</code> - {i["product_name__count"]} عدد'
                    inovices_static_list.append(prod)

                inovices_static_list.append('\n.')
                invoices_static_text = ''.join(inovices_static_list)
            else :
                invoices_static_text = 'هنوز آماری برای ارائه وجود ندارد '
            bot.edit_message_text(invoices_static_text, call.message.chat.id, call.message.message_id, reply_markup=botkb.bot_static(inovices=True))



        #- bot static - INOVICES
        if call.data =='payments_static':
            payments_ =payments.objects
            if payments_.all().exists():
                Text_payments = botStatics_6(payments_)
                bot.edit_message_text(Text_payments, call.message.chat.id, call.message.message_id , reply_markup=botkb.bot_static(payments=True))
            else:
                Text_payments = 'هنوز آماری برای ارائه وجود ندارد'
                bot.edit_message_text(Text_payments, call.message.chat.id, call.message.message_id , reply_markup=botkb.bot_static(payments=True))





        if call.data == 'back_from_bot_statics':
            bot.edit_message_text('به مدیریت ربات خوش امدید', call.message.chat.id , call.message.message_id , reply_markup= botkb.management_menu_in_admin_side(user_id = call.from_user.id))



    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')
















#---------------------------------------------------------------------------------------------------------------------------------#
# -------------------------admins_management------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------------------#

USER_ADMIN_INFO = {'page_item':1 ,}

@bot.callback_query_handler(func= lambda call  : call.data in ['admins_management', 'add_new_admin', 'back_from_admin_menu' , 'back_from_admin_access'] or call.data.startswith(('admin_pages_' ,'load_' , 'adminremove_' , 'adminaccess_', 'accpanels_','accproducts_' ,'accpbotseeting_' , 'accadmins_' , 'accusermanagment_' , 'accbotstaticts_')))
def admins_management(call):

    if check_admins(call.from_user.id , bot_static=True) == 'static_access': 
        
        if call.data == 'admins_management':
            bot.edit_message_text('برای مدیریت  ادمین ها بروی انها کلیک کنید ', call.message.chat.id , call.message.message_id , reply_markup=botkb.show_admins())
   


        if call.data.startswith('admin_pages_'):
            user_id = USER_ADMIN_INFO['user_id'] if USER_ADMIN_INFO['user_id'] is not None else None
            USER_ADMIN_INFO['page_item'] = int(call.data.split('_')[-1])
            page = call.data.split('_')[-1]
            bot.edit_message_text('برای مدیریت  ادمین ها بروی انها کلیک کیند ' , call.message.chat.id, call.message.message_id,  reply_markup= botkb.show_admins(who= user_id,page_items=int(page)))
        


        if call.data.startswith('load_'):
            USER_ADMIN_INFO['user_id'] = int(call.data.split('_')[-1])
            bot.edit_message_text('برای مدیریت  ادمین ها بروی انها کلیک کیند ' , call.message.chat.id, call.message.message_id,  reply_markup= botkb.show_admins(who=int(call.data.split('_')[-1]) , page_items= USER_ADMIN_INFO['page_item']))



        if call.data == 'add_new_admin':
            bot.edit_message_text('ایدی عددی ادمین را وارد کنید\n TO CANCEL :/cancel' , call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , addNewAdmin)



        if call.data.startswith('adminremove_'):
            call_data = call.data.split('_')
            try:
                admins_ = admins.objects.get(user_id = call_data[-1])
                if admins_.is_owner == 1 :
                    bot.answer_callback_query(call.id , 'شما نمیتوانید اونر بات را حذف کنید')
                else:
                    admins_.delete()   
                    bot.edit_message_text('✅یوزر با موفقیت از دیتابیس پاک  شد ' , call.message.chat.id , call.message.message_id , reply_markup= botkb.show_admins())

            except Exception as delete_admin_error:
                print(f'error while deleteing admin from db // error msg : {delete_admin_error}')



        if call.data.startswith('adminaccess_'):
            call_data = call.data.split('_')
            admins_ = admins.objects.get(user_id = call.from_user.id).is_owner 
            admins_2 = admins.objects.get(user_id= int(call_data[-1])).is_owner
            if admins_ == 1 :
                if admins_2 == 1 :
                    bot.send_message(call.message.chat.id , 'مدیریت کردن دسترسی های اونر مجاز نمیباشد')
                else: 
                    Text_1= f'به قسمت مدیریت دسترسی های ادمین خوش امدید'
                    bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_admin_acc(user_id= int(call_data[-1])))
            else:
                bot.send_message(call.message.chat.id ,'شما اجازه مدیریت کردن دسترسی ها را ندارید' )


        if call.data.startswith('accpanels_'):
            call_data = call.data.split('_')
            admins_ = admins.objects.get(user_id = int(call_data[-1]))
            new_acc_panels = 1 if admins_.acc_panels == 0 else  0 
            admins_.acc_panels = new_acc_panels
            admins_.save()
            Text_2= f'به قسمت مدیریت دسترسی های ادمین خوش امدید'
            bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_admin_acc(user_id= int(call_data[-1])))


        if call.data.startswith('accproducts_'):
            call_data = call.data.split('_')
            admins_ = admins.objects.get(user_id = int(call_data[-1]))
            new_acc_products = 1 if admins_.acc_products == 0 else  0 
            admins_.acc_products = new_acc_products
            admins_.save()
            Text_3= f'به قسمت مدیریت دسترسی های ادمین خوش امدید'
            bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_admin_acc(user_id= int(call_data[-1])))



        if call.data.startswith('accpbotseeting_'):
            call_data = call.data.split('_')
            admins_ = admins.objects.get(user_id = int(call_data[-1]))
            new_acc_botmanagment = 1 if admins_.acc_botmanagment == 0 else  0 
            admins_.acc_botmanagment = new_acc_botmanagment
            admins_.save()
            Text_4= f'به قسمت مدیریت دسترسی های ادمین خوش امدید'
            bot.edit_message_text(Text_4 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_admin_acc(user_id= int(call_data[-1])))




        if call.data.startswith('accadmins_'):
            call_data = call.data.split('_')
            admins_ = admins.objects.get(user_id = int(call_data[-1]))
            new_acc_admins = 1 if admins_.acc_admins == 0 else  0 
            admins_.acc_admins = new_acc_admins
            admins_.save()
            Text_5= f'به قسمت مدیریت دسترسی های ادمین خوش امدید'
            bot.edit_message_text(Text_5 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_admin_acc(user_id= int(call_data[-1])))



        if call.data.startswith('accusermanagment_'):
            call_data = call.data.split('_')
            admins_ = admins.objects.get(user_id = int(call_data[-1]))
            new_acc_users = 1 if admins_.acc_users == 0 else  0 
            admins_.acc_users = new_acc_users
            admins_.save()
            Text_5= f'به قسمت مدیریت دسترسی های ادمین خوش امدید'
            bot.edit_message_text(Text_5 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_admin_acc(user_id= int(call_data[-1])))



        if call.data.startswith('accbotstaticts_'):
            call_data = call.data.split("_")
            admins_ = admins.objects.get(user_id = int(call_data[-1]))
            new_acc_staticts = 1 if admins_.acc_staticts == 0 else 0
            admins_.acc_staticts = new_acc_staticts
            admins_.save()
            Text_6 = f'به قسمت مدیریت دسترسی های ادمین خوش امدید'
            bot.edit_message_text(Text_6 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_admin_acc(user_id= int(call_data[-1])))



        if call.data =='back_from_admin_access':
            Text_back = 'برای مدیریت  ادمین ها بروی انها کلیک کنید'
            bot.edit_message_text(Text_back , call.message.chat.id , call.message.message_id , reply_markup= botkb.show_admins())


        if call.data =='back_from_admin_menu':
            bot.edit_message_text('به مدیریت ربات خوش امدید' , call.message.chat.id , call.message.message_id , reply_markup= botkb.management_menu_in_admin_side(user_id = call.from_user.id))
    
    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')



def addNewAdmin(message):
    if message.text =='/cancel' or message.text=='/cancel'.upper():
        bot.send_message(message.chat.id , 'برای مدیریت  ادمین ها بروی انها کلیک کیند ', reply_markup=botkb.show_admins())
    else:
        if message.text.isdigit():
            try:
                userExist = users.objects.get(user_id = message.text)
                adminInfo = bot.get_chat(userExist.user_id)
                admins_ = admins.objects.create(admin_name=adminInfo.first_name or adminInfo.last_name, user_id=adminInfo.id,
                                                    is_admin=1, is_owner=0, acc_botmanagment=0, acc_panels=0, acc_products=0, acc_admins=0)
                bot.send_message(message.chat.id, 'کاربر به عنوان ادمین اضافه شد \n دسترسی های کاربر را مدیریت کنید‌!!' , reply_markup=botkb.manage_admin_acc(adminInfo.id))
            except Exception as err:
                bot.send_message(message.chat.id , ' امکان اضافه کردن این کاربر به عنوان ادمین وجود ندارد \n این کاربر  ربات را استارت نکرده است')
                bot.send_message(message.chat.id , 'برای مدیریت  ادمین ها بروی انها کلیک کنید ' , reply_markup=botkb.show_admins())
        else:
            bot.send_message(message.chat.id, 'ایدی باید به صورت عدد باشد نه حروف')

        














#---------------------------------------------------------------------------------------------------------------------------------#
# -------------------------bot_management-----------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------------------#


ADD_BANK_KARD = {}
def add_bankkard():
    add_bank_kard = {'chat_id':None , 
                      'bank_name_state' : False , 'bank_name' : str ,
                       'bank_kart_state': False , 'bank_kart' : str ,
                        'bank_ownername_state' : False , 'bank_ownername': str}
    return add_bank_kard



@bot.callback_query_handler(func= lambda call: call.data in ['bot_managment' , 'bot_enable_disable'])
def bot_managment(call):
    status_txt = lambda botstatus : '❌ غیر فعال' if botstatus == 0 else  '✅ فعال'
    if check_admins(call.from_user.id , bot_management=True) == 'botmanagement_access': 
        
        if call.data == 'bot_managment':
            bot.edit_message_text(bot_management_fisrt_TEXT , call.message.chat.id , call.message.message_id , reply_markup=botkb.bot_management())
    
        if call.data == 'bot_enable_disable':
            botsettings_ = botsettings.objects.first()
            new_bot_status = 1 if botsettings_.bot_status == 0 else 0
            botsettings_.bot_status = new_bot_status
            botsettings_.save()
            if botsettings_.bot_status == 0 :
                bot.answer_callback_query(call.id , 'از این پس دسترسی به ربات فقط از طرق اونر ممکن است' , show_alert=True)
            bot.edit_message_text(bot_management_fisrt_TEXT , call.message.chat.id , call.message.message_id , reply_markup= botkb.bot_management())
    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')






@bot.callback_query_handler(func= lambda call: call.data in ['manage_bank_cards' , 'walletpay_status' , 'kartbkart_status'  ,  'moneyusrtousr_status' , 'manage_shomare_kart' , 'back_to_management_menu' , 'back_from_mange_howtopay' , 'back_from_manage_shomare_kart' , 'back_from_manage_shomare_karts' , 'add_new_kart_number' , 'none_bnk_name' , 'none_owner_name'] or call.data.startswith(('mkart_' , 'changekardowner_name_' , 'changebankname_' , 'userin_pays_' , 'chstatus_shomarekart_' , 'rmkart_' )))
def bot_managment_payment(call):
    
    status_txt = lambda botstatus : '❌ غیر فعال' if botstatus == 0 else  '✅ فعال'
    bnk_inuse_txt = lambda bnk_inuse :  '👎🏻 عدم استفاده' if bnk_inuse == 0 else 'در حال استفاده 👍🏻'

    if check_admins(call.from_user.id , bot_management=True) == 'botmanagement_access': 
        
        if call.data == 'manage_bank_cards':
            bot.edit_message_text(bot_management_second_TEXT , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_howtopay())



        if call.data =='walletpay_status':
            botsettings_wallet_pay = botsettings.objects.first()
            if botsettings_wallet_pay:
                new_wallet_pay = 1 if botsettings_wallet_pay.wallet_pay == 0 else 0
                botsettings_wallet_pay.wallet_pay = new_wallet_pay
                botsettings_wallet_pay.save()
            Text_1 = f'{bot_management_second_TEXT}\n¦- 👝وضعیت پرداخت با کیف پول تغییر کرد\n┘ - وضعیت فعلی :{status_txt(botsettings_wallet_pay.wallet_pay)}\n .'
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_howtopay())



        if call.data =='kartbkart_status':
            botsettings_kartkart = botsettings.objects.first()
            if botsettings_kartkart:
                new_kartbkart_pay = 1 if botsettings_kartkart.kartbkart_pay == 0 else 0
                botsettings_kartkart.kartbkart_pay = new_kartbkart_pay
                botsettings_kartkart.save()
            Text_2 = f'{bot_management_second_TEXT}\n¦- 💳وضعیت پرداخت با کارت به کارت تغییر کرد\n┘ - وضعیت فعلی :{status_txt(botsettings_kartkart.kartbkart_pay)}\n .'
            bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_howtopay())



        if call.data == 'moneyusrtousr_status':
            botsettings_moneyusrtousr = botsettings.objects.first()
            if botsettings_moneyusrtousr:
                new_kartbkart_pay = 1 if botsettings_moneyusrtousr.moneyusrtousr == 0 else 0
                botsettings_moneyusrtousr.moneyusrtousr= new_kartbkart_pay
                botsettings_moneyusrtousr.save()
            Text_3 = f'{bot_management_second_TEXT}\n¦- 👥وضعیت انتقال وجه از کاربر به کاربر تغییر کرد\n┘ - وضعیت فعلی :{status_txt(botsettings_moneyusrtousr.moneyusrtousr)}\n .'
            bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_howtopay())



        
        if call.data =='manage_shomare_kart':
            bot.edit_message_text(bot_management_shomare_kart_TEXT_1, call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_shomarekart())




        if call.data.startswith('mkart_'):
            call_data = call.data.split('_')
            shomarekart_bypk = shomarekart.objects.get(bank_card= call_data[-1])
            card_user_times = inovices.objects.filter(card_used=shomarekart_bypk, payments__payment_status='accepted').aggregate(total_amount=Count('payments__amount'))['total_amount']
            Text_4 = bot_management_shomare_kart_TEXT_2(status_txt(shomarekart_bypk.bank_status) , shomarekart_bypk.ownername , shomarekart_bypk.bank_name , shomarekart_bypk.bank_card , bnk_inuse_txt(shomarekart_bypk.bank_inmsg) , card_user_times)
            bot.edit_message_text(Text_4 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_kart(call_data[-1]))


        if call.data.startswith('changekardowner_name_'):
            call_data = call.data.split('_')
            bot.edit_message_text('نام جدید صاحب کارت را وارد نمایید\n\n TO-CANCEL : /cancel' , call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , lambda message : change_owner_name(bot , message , call_data[-1]))


        if call.data.startswith('changebankname_'):
            call_data = call.data.split('_')
            bot.edit_message_text('نام جدید کارت را نام بانک وارد کنید \n\n TO_CANCEL : /cancel' , call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , lambda message : change_bank_name(bot , message , call_data[-1]))



        if call.data.startswith('userin_pays_'):
            call_data = call.data.split('_')
            shomarekart_bank_inuse = shomarekart.objects.get(bank_card = call_data[-1])
            new_use_status = 1 if shomarekart_bank_inuse.bank_inmsg == 0 else 0
            shomarekart_bank_inuse.bank_inmsg = new_use_status
            shomarekart_bank_inuse.save()
            card_user_times = inovices.objects.filter(card_used=shomarekart_bank_inuse, payments__payment_status='accepted').aggregate(total_amount=Count('payments__amount'))['total_amount']
            Text_5 = bot_management_shomare_kart_TEXT_2(status_txt(shomarekart_bank_inuse.bank_status) , shomarekart_bank_inuse.ownername , shomarekart_bank_inuse.bank_name , shomarekart_bank_inuse.bank_card , bnk_inuse_txt(shomarekart_bank_inuse.bank_inmsg), card_user_times)
            bot.edit_message_text(Text_5 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_kart(call_data[-1]))





        if call.data.startswith('chstatus_shomarekart_'):
            call_data = call.data.split("_")
            shomarekart_bank_status = shomarekart.objects.get(bank_card= call_data[-1])
            new_shomarekart_status = 1 if shomarekart_bank_status.bank_status == 0 else 0
            shomarekart_bank_status.bank_status = new_shomarekart_status
            shomarekart_bank_status.save()
            card_user_times = inovices.objects.filter(card_used= shomarekart_bank_inuse, payments__payment_status='accepted').aggregate(total_amount=Count('payments__amount'))['total_amount']
            Text_6 = bot_management_shomare_kart_TEXT_2(status_txt(shomarekart_bank_status.bank_status) , shomarekart_bank_status.ownername , shomarekart_bank_status.bank_name , shomarekart_bank_status.bank_card , bnk_inuse_txt(shomarekart_bank_status.bank_inmsg) , card_user_times)
            bot.edit_message_text(Text_6 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_kart(call_data[-1]))





        if call.data.startswith('rmkart_'):
            call_data = call.data.split('_')
            shomarekart_remove = shomarekart.objects.get(bank_card= call_data[-1]).delete()
            bot.edit_message_text(bot_management_shomare_kart_TEXT_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_shomarekart())



        if call.data =='add_new_kart_number':
            if call.from_user.id not in ADD_BANK_KARD:
                ADD_BANK_KARD[call.from_user.id] = add_bankkard()
            ADD_BANK_KARD[call.from_user.id]['chat_id'] = call.from_user.id
            ADD_BANK_KARD[call.from_user.id]['bank_name_state'] = True
            keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('ترجیحا خالی بماند' , callback_data = 'none_bnk_name'))
            bot.edit_message_text('ابتدا 🏦 نام بانک را ارسال نمایید\n  ↲ برای خالی گزاشتن نام بانک 👇🏻گزینه زیر را بزنید \n\n TO-CANCEL : /cancel' , call.message.chat.id , call.message.message_id , reply_markup = keyboard)



        if call.data =='none_bnk_name':
            ADD_BANK_KARD[call.from_user.id]['bank_name_state'] = False
            ADD_BANK_KARD[call.from_user.id]['bank_kart_state'] = True
            ADD_BANK_KARD[call.from_user.id]['bank_name'] = None
            bot.edit_message_text('لطفا 💳شماره کارت را ارسال نمایید\n\n TO-CANCEL : /cancel' , call.message.chat.id , call.message.message_id )



        if call.data =='none_owner_name':
            ADD_BANK_KARD[call.from_user.id]['bank_ownername_state'] = False
            ADD_BANK_KARD[call.from_user.id]['bank_ownername'] = None
            bank_name = None if ADD_BANK_KARD[call.from_user.id]['bank_name'] is None else ADD_BANK_KARD[call.from_user.id]['bank_name']
            bank_card = ADD_BANK_KARD[call.from_user.id]['bank_kart']
            ownername = None if ADD_BANK_KARD[call.from_user.id]['bank_ownername'] is None else ADD_BANK_KARD[call.from_user.id]['bank_ownername']
                    
            shomarekart.objects.create(bank_name = bank_name , bank_card = bank_card , ownername = ownername , bank_status = 0 , bank_inmsg = 0)
            clear_dict(ADD_BANK_KARD , call.from_user.id)
            bot.edit_message_text('✅ شماره کارت با موفقیت اضافه شد ' , call.message.chat.id , call.message.message_id , reply_markup = botkb.manage_shomarekart())
    



        #back-buttons 
        if call.data =='back_to_management_menu':
            bot.edit_message_text('به مدیریت ربات خوش امدید', call.message.chat.id , call.message.message_id , reply_markup= botkb.management_menu_in_admin_side(user_id = call.from_user.id))        

        if call.data =='back_from_mange_howtopay':
            bot.edit_message_text(bot_management_fisrt_TEXT, call.message.chat.id , call.message.message_id , reply_markup=botkb.bot_management())


        if call.data =='back_from_manage_shomare_karts':
            bot.edit_message_text(bot_management_second_TEXT , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_howtopay())


        if call.data == 'back_from_manage_shomare_kart':
            bot.edit_message_text(bot_management_shomare_kart_TEXT_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_shomarekart())


    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید ')    





def change_owner_name(bot , message , kard_number):

    if message.text == '/cancel' or message.text =='/cancel'.upper():
        kard_ = shomarekart.objects.get(bank_card = str(kard_number))
        card_user_times = inovices.objects.filter(card_used= kard_, payments__payment_status='accepted').aggregate(total_amount=Count('payments__amount'))['total_amount']
        Text_1 =bot_management_shomare_kart_TEXT_2(kard_.bank_status , kard_.ownername , kard_.bank_name , kard_.bank_card , kard_.bank_inmsg ,  card_user_times)
        bot.send_message(message.chat.id ,Text_1, reply_markup = botkb.manage_kart(kard_.bank_card) )
    else:
        kard_ = shomarekart.objects.get(bank_card = str(kard_number))
        kard_.ownername = message.text 
        kard_.save()
        card_user_times = inovices.objects.filter(card_used= kard_, payments__payment_status='accepted').aggregate(total_amount=Count('payments__amount'))['total_amount']
        Text_2 =bot_management_shomare_kart_TEXT_2(kard_.bank_status , kard_.ownername , kard_.bank_name , kard_.bank_card , kard_.bank_inmsg ,  card_user_times)
        bot.send_message(message.chat.id , Text_2 , reply_markup = botkb.manage_kart(kard_.bank_card))




def change_bank_name(bot , message , kard_number):

    if message.text == '/cancel' or message.text =='/cancel'.upper():
        kard_ = shomarekart.objects.get(bank_card = str(kard_number))
        card_user_times = inovices.objects.filter(card_used= kard_, payments__payment_status='accepted').aggregate(total_amount=Count('payments__amount'))['total_amount']
        Text_1 =bot_management_shomare_kart_TEXT_2(kard_.bank_status , kard_.ownername , kard_.bank_name , kard_.bank_card , kard_.bank_inmsg ,  card_user_times)
        bot.send_message(message.chat.id ,Text_1, reply_markup = botkb.manage_kart(kard_.bank_card))
    else:
        kard_ = shomarekart.objects.get(bank_card = str(kard_number))
        kard_.bank_name = message.text 
        kard_.save()
        card_user_times = inovices.objects.filter(card_used= kard_, payments__payment_status='accepted').aggregate(total_amount=Count('payments__amount'))['total_amount']
        Text_2 =bot_management_shomare_kart_TEXT_2(kard_.bank_status , kard_.ownername , kard_.bank_name , kard_.bank_card , kard_.bank_inmsg ,  card_user_times)
        bot.send_message(message.chat.id , Text_2 , reply_markup = botkb.manage_kart(kard_.bank_card))





@bot.message_handler(func= lambda message : len(ADD_BANK_KARD) >=1 and  message.from_user.id in ADD_BANK_KARD and  (ADD_BANK_KARD[message.from_user.id]['bank_name_state'] or ADD_BANK_KARD[message.from_user.id]['bank_kart_state'] or ADD_BANK_KARD[message.from_user.id]['bank_ownername_state'] or ADD_BANK_KARD[message.from_user.id]['bank_ownername_state'])==True and message.from_user.id == ADD_BANK_KARD[message.from_user.id]['chat_id'])
def handle_newbank_kard(message):

    if ADD_BANK_KARD[message.from_user.id]['bank_name_state']== True:
        if message.text == '/cancel' or message.text == '/cancel'.upper():
            clear_dict(ADD_BANK_KARD , message.from_user.id)
            bot.send_message(message.chat.id , bot_management_shomare_kart_TEXT_3 , reply_markup=botkb.manage_shomarekart())
        else:
            if not message.text.isdigit():
                ADD_BANK_KARD[message.from_user.id]['bank_name'] = message.text
                ADD_BANK_KARD[message.from_user.id]['bank_name_state'] = False
                ADD_BANK_KARD[message.from_user.id]['bank_kart_state'] = True
                bot.send_message(message.chat.id ,  'حالا 💳شماره کارت را ارسال نمایید\n\n TO-CANCEL : /cancel')
        return


    if ADD_BANK_KARD[message.from_user.id]['bank_kart_state'] == True:
        if message.text == '/cancel' or message.text == '/cancel'.upper():
            clear_dict(ADD_BANK_KARD , message.from_user.id)
            bot.send_message(message.chat.id , bot_management_shomare_kart_TEXT_3 , reply_markup=botkb.manage_shomarekart())
        else:
            if  message.text.isdigit():
                ADD_BANK_KARD[message.from_user.id]['bank_kart'] = message.text
                ADD_BANK_KARD[message.from_user.id]['bank_kart_state'] = False
                ADD_BANK_KARD[message.from_user.id]['bank_ownername_state'] = True
                keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('ترجیحا خالی بماند' , callback_data = 'none_owner_name'))
                bot.send_message(message.chat.id ,  'درنهایت 👤نام صاحب کارت  را ارسال نمایید\n  ↲ برای خالی گزاشتن نام صاحب کارت 👇🏻گزینه زیر را بزنید \n\n TO-CANCEL : /cancel' , reply_markup = keyboard)
        return



    if ADD_BANK_KARD[message.from_user.id]['bank_ownername_state'] == True:
        if message.text == '/cancel' or message.text == '/cancel'.upper():
            clear_dict(ADD_BANK_KARD , message.from_user.id)
            bot.send_message(message.chat.id , bot_management_shomare_kart_TEXT_3 , reply_markup=botkb.manage_shomarekart())
        else:
            if not message.text.isdigit():
                ADD_BANK_KARD[message.from_user.id]['bank_ownername'] = message.text
                ADD_BANK_KARD[message.from_user.id]['bank_ownername_state'] = False
                
                bank_name = None if ADD_BANK_KARD[message.from_user.id]['bank_name'] is None else ADD_BANK_KARD[message.from_user.id]['bank_name']
                bank_card = ADD_BANK_KARD[message.from_user.id]['bank_kart']
                ownername = None if ADD_BANK_KARD[message.from_user.id]['bank_ownername'] is None else ADD_BANK_KARD[message.from_user.id]['bank_ownername']
                
                shomarekart.objects.create(bank_name = bank_name , bank_card = bank_card , ownername = ownername , bank_status = 1 , bank_inmsg = 1)
                bot.send_message(message.chat.id , '✅ شماره کارت با موفقیت اضافه شد ' , reply_markup=botkb.manage_shomarekart())
                clear_dict(ADD_BANK_KARD , message.from_user.id)
        return











# ------------------------- < JoinChannel-Section > 

ADD_NEW_CHANNEL_FJ = {}
def add_newchannel():

    ADD_NEWCHANNEL_FJ = {'chat_id' : None ,
                        'ch_name_state' : False , 'ch_name' : str ,
                        'ch_id_state': False , 'ch_id' : str ,}
    
    return ADD_NEWCHANNEL_FJ


# force join channel 
@bot.callback_query_handler(func= lambda call : call.data in ['manage_force_channel_join' , 'forcechjoin' ,'manage_forcejoin', 'back_from_manage_force_ch' , 'back_from_managing_force_ch' , 'back_from_manage_channel' , 'add_new_force_channel' , 'use_channel_nameself'] or call.data.startswith(('mfch_' , 'change_chf_name_' , 'status_chf_' , 'rm_chf_')))
def manage_bot_join_ch(call):

    status_txt = lambda botstatus : '❌ غیر فعال' if botstatus == 0 else '✅ فعال'

    Text_main_1 = 'در این قسمت شما میتوانید جوین اجباری و چنل ها را مدیریت کنید .'
    if check_admins(call.from_user.id , bot_management=True) == 'botmanagement_access': 
        
        if call.data == 'manage_force_channel_join':
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_joinch())


        if call.data == 'forcechjoin':
            botsettings_forcechjoin = botsettings.objects.first()
            if botsettings_forcechjoin :
                new_status = 1 if botsettings_forcechjoin.forcechjoin == 0 else 0 
                botsettings_forcechjoin.forcechjoin = new_status
                botsettings_forcechjoin.save()
            Text_1 = f'{Text_main_1}\n¦- 🔐وضعیت جوین اجباری  تغییر کرد\n ┘ - وضعیت فعلی :‌{status_txt(botsettings_forcechjoin.forcechjoin)}\n .'
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup = botkb.manage_joinch())



        if call.data == 'manage_forcejoin':
            bot.edit_message_text(bot_management_join_ch_Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_channels())



        if call.data.startswith('mfch_'):
            call_data = call.data.split('_')
            channels_bypk= channels.objects.get(id = int(call_data[-1]))
            ch_url = bot.get_chat(channels_bypk.channel_id).invite_link
            Text_2 = bot_management_join_ch_Text_2(status_txt(channels_bypk.ch_status) , channels_bypk.channel_name , ch_url , channels_bypk.channel_id)
            bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_ch(channel_id= int(call_data[-1])) , link_preview_options=LinkPreviewOptions(is_disabled=True , url=ch_url))


        if call.data.startswith('change_chf_name_'):
            call_data = call.data.split('_')
            channels_bypk = channels.objects.get(id = int(call_data[-1]))
            bot.edit_message_text('نام جدید چنل را وارد نمایید \n\n TO-CANCEL : /cancel' , call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , lambda message : change_chf_name(bot , message , call_data[-1]))



        if call.data.startswith('status_chf_'):
            call_data = call.data.split("_")
            channels_bypk = channels.objects.get(id = int(call_data[-1]))
            new_status = 1 if channels_bypk.ch_status == 0 else 0 
            channels_bypk.ch_status = new_status
            channels_bypk.save()
            ch_url =  bot.get_chat(channels_bypk.channel_id).invite_link
            Text_3 = bot_management_join_ch_Text_2(status_txt(channels_bypk.ch_status) , channels_bypk.channel_name , ch_url , channels_bypk.channel_id)
            bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_ch(channel_id= int(call_data[-1])) , link_preview_options=LinkPreviewOptions(is_disabled=True , url=ch_url) )

    

        if call.data.startswith('rm_chf_'):
            call_data = call.data.split('_')
            channels_bypk = channels.objects.get(id = int(call_data[-1])).delete()  
            if channels.objects.all().count() < 1 :
                botsettings_ = botsettings.objects.first()
                botsettings_.forcechjoin = 0 
                botsettings_.save() 
            bot.edit_message_text(bot_management_join_ch_Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_channels())



        if call.data =='add_new_force_channel':
            if call.from_user.id not in ADD_NEW_CHANNEL_FJ:
                ADD_NEW_CHANNEL_FJ[call.from_user.id] = add_newchannel()
            ADD_NEW_CHANNEL_FJ[call.from_user.id]['chat_id'] = call.from_user.id
            ADD_NEW_CHANNEL_FJ[call.from_user.id]['ch_name_state'] = True
            keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('استفاده از نام خود چنل', callback_data='use_channel_nameself'))
            bot.edit_message_text('ابتدا🔈 نام چنل را ارسال نمایید\n  ↲ برای استفاده از نام خود چنل 👇🏻گزینه زیر را بزنید \n\n TO-CANCEL : /cancel' , call.message.chat.id , call.message.message_id , reply_markup=keyboard)



        if call.data == 'use_channel_nameself':
            ADD_NEW_CHANNEL_FJ[call.from_user.id]['ch_name'] = 'use_ch_name'
            ADD_NEW_CHANNEL_FJ[call.from_user.id]['ch_name_state'] = False
            ADD_NEW_CHANNEL_FJ[call.from_user.id]['ch_id_state'] = True
            bot.edit_message_text(bot_management_join_ch_Text_3 , call.message.chat.id , call.message.message_id)




        #back_button 
        if call.data =='back_from_manage_force_ch':
            bot.edit_message_text(bot_management_fisrt_TEXT , call.message.chat.id , call.message.message_id , reply_markup=botkb.bot_management())

        if call.data =='back_from_managing_force_ch':
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_joinch())

        if call.data =='back_from_manage_channel':
            bot.edit_message_text(bot_management_join_ch_Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_channels())


    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')





def change_chf_name(bot , message , channel_pk):
    status_txt = lambda botstatus : '❌ غیر فعال' if botstatus == 0 else '✅ فعال'

    if message.text == '/cancel' or message.text == '/cancel'.upper():
        channels_bypk = channels.objects.get(id = channel_pk)
        ch_url = bot.get_chat(channels_bypk.channel_id).invite_link
        Text_2 = bot_management_join_ch_Text_2(status_txt(channels_bypk.ch_status) , channels_bypk.channel_name , ch_url , channels_bypk.channel_id)
        bot.send_message(message.chat.id , Text_2 ,reply_markup=botkb.manage_ch(channel_id= int(channel_pk)) , link_preview_options= LinkPreviewOptions(is_disabled=True , url=ch_url))

    else:
        channels_bypk = channels.objects.get(id = channel_pk)
        channels_bypk.channel_name = message.text
        channels_bypk.save()
        ch_url = bot.get_chat(channels_bypk.channel_id).invite_link
        Text_2 = bot_management_join_ch_Text_2(status_txt(channels_bypk.ch_status) , channels_bypk.channel_name , ch_url , channels_bypk.channel_id)
        bot.send_message(message.chat.id , Text_2 ,reply_markup=botkb.manage_ch(channel_id= int(channel_pk)) , link_preview_options=LinkPreviewOptions(is_disabled=True , url=ch_url))






@bot.message_handler(func= lambda message : len(ADD_NEW_CHANNEL_FJ) >=1 and message.from_user.id in ADD_NEW_CHANNEL_FJ and  (ADD_NEW_CHANNEL_FJ[message.from_user.id]['ch_name_state'] or ADD_NEW_CHANNEL_FJ[message.from_user.id]['ch_id_state'])== True and message.from_user.id == ADD_NEW_CHANNEL_FJ[message.from_user.id]['chat_id'] )
def handle_add_ch(message):

    if ADD_NEW_CHANNEL_FJ[message.from_user.id]['ch_name_state'] == True:
        if message.text == '/cancel' or message.text == '/cancel'.upper():
            clear_dict(ADD_NEW_CHANNEL_FJ , message.from_user.id)
            bot.send_message(message.chat.id , bot_management_join_ch_Text_4 , reply_markup=botkb.manage_channels())
        else:
            if not message.text.isdigit():
                ADD_NEW_CHANNEL_FJ[message.from_user.id]['ch_name'] = message.text
                ADD_NEW_CHANNEL_FJ[message.from_user.id]['ch_name_state'] = False
                ADD_NEW_CHANNEL_FJ[message.from_user.id]['ch_id_state'] = True
                bot.send_message(message.chat.id , bot_management_join_ch_Text_5)
        return


    if ADD_NEW_CHANNEL_FJ[message.from_user.id]['ch_id_state'] == True:
        if message.text == '/cancel' or message.text == '/cancel'.upper():
            clear_dict(ADD_NEW_CHANNEL_FJ , message.from_user.id)
            bot.send_message(message.chat.id , bot_management_join_ch_Text_4 , reply_markup=botkb.manage_channels())
        else:
            ch_info = bot.get_chat(message.text)
            
            ch_name = ch_info.title if ADD_NEW_CHANNEL_FJ[message.from_user.id]['ch_name'] == 'use_ch_name' else ADD_NEW_CHANNEL_FJ[message.from_user.id]['ch_name']
            Text_2 = '✅چنل جدید با موفقیت اضافه شد'
            if  message.text.startswith('-'):
                ch_id = message.text 
                channels_id = channels.objects.create(channel_name = ch_name , channel_id = ch_id , ch_status = 1 , ch_usage = 'fjch' )
                bot.send_message(message.chat.id , Text_2 , reply_markup=botkb.manage_channels())
                clear_dict(ADD_NEW_CHANNEL_FJ , message.from_user.id)
            elif  message.text.startswith('@'):
                channels_url = channels.objects.create(channel_name = ch_name, channel_url = message.text , channel_id = ch_info.id , ch_status = 1 , ch_usage = 'fjch' )
                bot.send_message(message.chat.id , Text_2 , reply_markup=botkb.manage_channels())
                clear_dict(ADD_NEW_CHANNEL_FJ , message.from_user.id)
            else:
                bot.send_message(message.chat.id , 'فرمت ارسالی اشتباه است لطفا به توضیحات گفته شده توجه فرمایید')
        return
















# ------------------------- < logs-Section > 

ADD_NEW_CHANNEL_LOG = {}

def add_newchannel_logs():

    add_newchannel_log ={
                          'chat_id' : None , 
                          'chnl_id_state': False ,
                          'chnl_id' : str ,
                        }

    return add_newchannel_log


@bot.callback_query_handler(func = lambda call: call.data in ['manage_sending_logs' ,'who_reciving_notifs' , 'new_user_joined_notf' , 'charging_wallet_notf' , 'transfer_money_touser_notf' , 'buy_new_service_notf' , 'tamdid_service_notf' ,'verify_number_notf' , 'back_from_manage_logs' , 'add_new_log_channel'] or call.data.startswith('remove_log_channel_'))
def handle_logs(call):

    Text_main_1 = 'در این قسمت شما میتوانید ارسال وقایع را تنظیم کنید\n این قسمت مربوط به فعال کردن یا غیرفعال کردن اتفاقات داخل ربات میباشد '
    if check_admins(call.from_user.id , bot_management=True) == 'botmanagement_access': 
        if call.data == 'manage_sending_logs':
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_logs())


        if call.data == 'back_from_manage_logs':
            bot.edit_message_text(bot_management_fisrt_TEXT , call.message.chat.id , call.message.message_id , reply_markup=botkb.bot_management())


        if call.data == 'who_reciving_notifs':
            who_reciving_notifs = botsettings.objects.first()
            who_reciving_notifs.notif_mode = 1 if who_reciving_notifs.notif_mode == 0 else 0 
            who_reciving_notifs.save()
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_logs())



        if call.data =='new_user_joined_notf':
            botsettings_newuser_notf = botsettings.objects.first()
            new_user_joined_notf = 1 if botsettings_newuser_notf.newusers_notf == 0 else 0 
            botsettings_newuser_notf.newusers_notf = new_user_joined_notf
            botsettings_newuser_notf.save()
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_logs() )

    

        if call.data =='charging_wallet_notf':
            botsettings_chargingwallet_notf = botsettings.objects.first()
            new_charging_wallet_notf = 1 if botsettings_chargingwallet_notf.walletcharge_notf == 0 else 0 
            botsettings_chargingwallet_notf.walletcharge_notf = new_charging_wallet_notf
            botsettings_chargingwallet_notf.save()
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_logs() )



        if call.data =='transfer_money_touser_notf':
            botsettings_transfermoneytouser_notf = botsettings.objects.first()
            new_moneyusrtousr_notf = 1 if botsettings_transfermoneytouser_notf.moneyusrtousr_notf == 0 else 0 
            botsettings_transfermoneytouser_notf.moneyusrtousr_notf = new_moneyusrtousr_notf
            botsettings_transfermoneytouser_notf.save()
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_logs() )



        if call.data =='buy_new_service_notf':
            botsettings_buynewservice_notf = botsettings.objects.first()
            new_buynewservice_notf = 1 if botsettings_buynewservice_notf.buyservice_notf == 0 else 0 
            botsettings_buynewservice_notf.buyservice_notf = new_buynewservice_notf
            botsettings_buynewservice_notf.save()
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_logs() )



        if call.data =='tamdid_service_notf':
            botsettings_tamdidservice_notf = botsettings.objects.first()
            new_tamdidservice_notf = 1 if botsettings_tamdidservice_notf.tamdidservice_notf == 0 else 0 
            botsettings_tamdidservice_notf.tamdidservice_notf = new_tamdidservice_notf
            botsettings_tamdidservice_notf.save()
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_logs())


        if call.data =='verify_number_notf':
            botsettings_verify_number_notf = botsettings.objects.first()
            new_verify_number_notf = 1 if botsettings_verify_number_notf.verifynumber_notf == 0 else 0 
            botsettings_verify_number_notf.verifynumber_notf = new_verify_number_notf
            botsettings_verify_number_notf.save()
            bot.edit_message_text(Text_main_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_logs())



        if call.data == 'add_new_log_channel':
            channel_log = channels.objects.filter(ch_usage = 'logc').count()
            if channel_log <1 :
                if call.from_user.id not in ADD_NEW_CHANNEL_LOG:
                    ADD_NEW_CHANNEL_LOG[call.from_user.id] = add_newchannel_logs()
                ADD_NEW_CHANNEL_LOG[call.from_user.id]['chat_id'] = call.from_user.id
                ADD_NEW_CHANNEL_LOG[call.from_user.id]['chnl_id_state'] = True

                bot.edit_message_text(bot_management_log_ch_Text_1 , call.message.chat.id , call.message.message_id)
            else:
                bot.answer_callback_query(call.id , 'امکان اضافه کردن بیش از یک چنل وجود ندارد' , show_alert=True)
        
        
        if call.data.startswith('remove_log_channel_'):
            channel_log_pk = call.data.split('_')
            channel_log  = channels.objects.get(id = channel_log_pk[-1])
            channel_log.delete()
            Text_remove_ch = f'{Text_main_1} \n\n ❌ چنل لاگ پاک شد'
            bot.edit_message_text(Text_remove_ch , call.message.chat.id , call.message.message_id , reply_markup= botkb.manage_logs()) 


    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت رو ندارید')







@bot.message_handler(func= lambda message: len(ADD_NEW_CHANNEL_LOG) >=1 and message.from_user.id in ADD_NEW_CHANNEL_LOG and ADD_NEW_CHANNEL_LOG[message.from_user.id]['chnl_id_state'] == True and message.from_user.id == ADD_NEW_CHANNEL_LOG[message.from_user.id]['chat_id'] )
def handle_add_log_channel(message):
    Text_main_1 = 'در این قسمت شما میتوانید ارسال وقایع را تنظیم کنید\n این قسمت مربوط به فعال کردن یا غیرفعال کردن اتفاقات داخل ربات میباشد '

    if ADD_NEW_CHANNEL_LOG[message.from_user.id]['chnl_id_state'] == True:
        if message.text == '/cancel' or message.text == '/cancel'.upper():
            clear_dict(ADD_NEW_CHANNEL_LOG , message.from_user.id)
            bot.send_message(message.chat.id , Text_main_1 , reply_markup=botkb.manage_logs())
        else:
            if not message.text.isdigit() and message.text.startswith('-'):
                ch_info = bot.get_chat(message.text)
                channel_log = channels.objects.create(channel_name = ch_info.title, channel_url = ch_info.username  , channel_id = ch_info.id , ch_status = 1 , ch_usage = 'logc' )
                bot.send_message(message.chat.id ,  '✅چنل جدید با موفقیت اضافه شد' , reply_markup=botkb.manage_logs())
                clear_dict(ADD_NEW_CHANNEL_LOG , message.from_user.id)












































#---------------------------------------------------------------------------------------------------------------------------------#
# ------------------------- User-Management > p1
# --------------------------------------------------------------------------------------------------------------------------------#


@bot.callback_query_handler(func= lambda call : call.data in ['users_management', 'back_from_user_management'])
def manage_users(call):
    if check_admins(call.from_user.id , user_management=True) == 'usermanagment_access':
        if call.data == 'users_management':
            Text_1 = 'به قسمت مدیریت یوزر ها خوش امدید' 
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_users())
    

        if call.data =='back_from_user_management':
            Text_back = 'به مدیریت ربات خوش امدید'
            bot.edit_message_text(Text_back , call.message.chat.id , call.message.message_id , reply_markup=botkb.management_menu_in_admin_side(call.from_user.id))

    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')



#---------------------------------------------------------------------------------------------------------------------------------#
# ------------------------- User-Management > p2
# --------------------------------------------------------------------------------------------------------------------------------#




@bot.callback_query_handler(func= lambda call : call.data in ['ir_number' ,'verifying_users_by_hand', 'show_user_info' , 'increase_decrease_cash' ,'block_unblock_user' , 'send_msgs_to_users'])
def manage_users(call):

    if check_admins(call.from_user.id , user_management=True) == 'usermanagment_access':


        if call.data == 'ir_number':
            botsettings_ = botsettings.objects.first()
            botsettings_.irnumber = 1 if botsettings_.irnumber == 0 else 0 
            botsettings_.save()
            bot.edit_message_text('به قسمت مدیریت یوزر ها خوش امدید' , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_users())


        if call.data =='verifying_users_by_hand':
            bot.edit_message_text('ایدی عددی کاربر را برای تایید دستی ارسال نمایید\n\n TO-CANCEL : /cancel', call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , userid_for_verifying)
        

        if call.data == 'show_user_info':
            if call.from_user.id not in SHOW_USER_INFO:
                SHOW_USER_INFO[call.from_user.id] = show_user_info()

            Text_1 = '👁برای مشاهده اطلاعات کاربر ایدی عدد کاربر مورد نظر را ارسال نمایید \n\n TO-CANCEL : /cancel'
            bot.edit_message_text(Text_1, call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , handle_watchUserInfo)


        if call.data == 'increase_decrease_cash':
            bot.edit_message_text( '💸برای افزایش موجودی کاربر ایدی عدد کاربر مورد نظر را ارسال نمایید \n\n TO-CANCEL : /cancel', call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , getUserOperationsCashs)


        if call.data == 'block_unblock_user':
            Text_1 = 'ایدی عددی کاربری را که میخواهید مسدود یا رفع مسدودی کنید را وارد نمایید\n TO-CANCEL : /cancel'
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message ,getUserBlock)


        if call.data =='send_msgs_to_users':
            Text_1 = 'برای ارسال پیام به کاربران از گزینه های زیر استفاده نمایید'
            bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id, reply_markup=botkb.send_user_msg())


    else:
        bot.send_message(call.message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')










#----------------------------------------------------------------------------------------------------------------------------#
# -------------------------Phone verfing section-----------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------------#


# ---------------------------> Verifying-UserId
def userid_for_verifying(message):
    Text_1 = 'به قسمت مدیریت یوزر ها خوش امدیدبه قسمت مدیریت یوزر ها خوش امدید'
    if message.text == '/cancel' or message.text == '/cancel'.upper():
        bot.send_message(message.chat.id , Text_1, reply_markup=botkb.manage_users())
        bot.clear_step_handler(message)    
    else:
        if message.text.isdigit():
            user_ = users.objects.filter(user_id = message.text)
            if not user_:
                bot.send_message(message.chat.id , 'یوزری با این ایدی عددی وجود ندارد')
            else:
                if not user_[0].phone_number:
                    Text = f'برای وریفای کردن شماره تلفن این یوزر بروی دکمه های زیر کلیک کنید \n userId = {user_[0].user_id}' 
                    keyboard = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('وریفای کردن شماره تلفن' , callback_data=f'verifing_user_phone_{user_[0].user_id}') , InlineKeyboardButton('✤ - بازگشت به منوی قبلی - ✤', callback_data='back_from_verifying_user_phone'))
                    bot.send_message(message.chat.id , Text , reply_markup=keyboard)
                else:
                    Text_2 = 'این یوزر از قبل وریفای شده است'
                    bot.send_message(message.chat.id, Text_2)
                    bot.send_message(message.chat.id , Text_1, reply_markup=botkb.manage_users())
                    
        else:
            bot.send_message(message.chat.id , 'مقدار ارسالی باید به صورت عدد باشد')
            bot.register_next_step_handler(message , userid_for_verifying)




@bot.callback_query_handler(func=lambda call : call.data.startswith('verifing_user_phone_') or call.data in ['back_from_verifying_user_phone'])
def verifying_user_phone(call):
    if call.data.startswith('verifing_user_phone_'):
        user_ = users.objects.get(user_id = call.data.split('_')[-1])
        user_.phone_number = '+98'
        user_.save()
        bot.edit_message_text('یوزر وریفای شد ' , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_users())
    
    if call.data == 'back_from_verifying_user_phone':
        Text_1 = 'به قسمت مدیریت یوزر ها خوش امدیدبه قسمت مدیریت یوزر ها خوش امدید'
        bot.send_message(call.message.chat.id , Text_1, reply_markup=botkb.manage_users())



# ---------------------------> Verifying-UserId
@bot.callback_query_handler(func=lambda call: call.data.startswith('verfying_user_onstart_'))
def verfying_user_onstart(call):
    if call.data.startswith('verfying_user_onstart_'):
        user_= users.objects.get(user_id = call.data.split('_')[-1])
        if user_.phone_number is None:
            user_.phone_number = '+98'
            user_.save()
            bot.answer_callback_query(call.id , 'یوزر وریفای شد')
            bot.edit_message_reply_markup(call.message.chat.id , call.message.message_id , reply_markup=botkb.verfying_on_fist_join(user_.user_id , status=True) )
            bot.send_message(call.data.split('_')[-1],'شما با موفقیت وریفای شدید برای استفاده از ربات دستور زیر را ارسال کنید\n /start' , reply_markup=ReplyKeyboardRemove())
        else:
            bot.answer_callback_query(call.id , 'یوزر از قبل وریفای شده است')

            







#----------------------------------------------------------------------------------------------------------------------------#
# -------------------------Watch-user-info-----------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------------#

SHOW_USER_INFO = {}
def show_user_info():
    show_user_info = {'user_id':None, 'panel_id':None, 
                      'config_name':None, 'sub_request':None,
                      'data_limit_in':False, 'data_limit_de': False ,
                      'expire_in':False, 'expire_de':False,
                      'remove_service_money_back':False}
    
    return show_user_info


@bot.message_handler(commands=['watchuserinfo'])
def handle_watchUserIndo_command(message):
    if check_admins(message.from_user.id , user_management=True) == 'usermanagment_access':
        if message.text =='/watchuserinfo':
            Text_1 = '👁برای مشاهده اطلاعات کاربر ایدی عدد کاربر مورد نظر را ارسال نمایید \n\n TO-CANCEL : /cancel'
            if message.from_user.id not in SHOW_USER_INFO:
                SHOW_USER_INFO[message.from_user.id] = show_user_info()
            bot.send_message(message.chat.id , Text_1)
            bot.register_next_step_handler(message , handle_watchUserInfo)
    else:
        bot.send_message(message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')
    


@bot.callback_query_handler(func=lambda call : call.data in ['show_user_info_other', 'back_from_show_user_info', 'back_from_show_user_info_config'] or call.data.startswith(('showuserinfo' , 'suichstatus', 'suigetconfiglink', 'suigetqrcodelink', 'suiincreasedatalimit', 'suidecreasedatalimit', 'suiincreaseexpire' ,'suidecreaseexpire','suirevokesubscription' , 'suiremovepaneluser','suiremoveservicemoneyback')))
def watch_user_info(call):


    if call.data == 'show_user_info_other':
        if call.from_user.id not in SHOW_USER_INFO:
            SHOW_USER_INFO[call.from_user.id] = show_user_info()
        Text_1 = '👁برای مشاهده اطلاعات کاربر ایدی عدد کاربر مورد نظر را ارسال نمایید \n\n TO-CANCEL : /cancel'
        bot.delete_message(call.message.chat.id , call.message.message_id)
        bot.send_message(call.message.chat.id , Text_1)
        bot.register_next_step_handler(call.message , handle_watchUserInfo)


    if call.data =='back_from_show_user_info':
        clear_dict(SHOW_USER_INFO , call.from_user.id)
        Text_2 = 'به قسمت مدیریت یوزر ها خوش امدید'
        bot.delete_message(call.message.chat.id , call.message.message_id)
        bot.send_message(call.message.chat.id , Text_2 , reply_markup=botkb.manage_users())


    if call.data.startswith('showuserinfo'):
        call_data = call.data.split('.')
        config_name = call_data[-1].removeprefix('(').removesuffix(')')
        subscriptions_ = subscriptions.objects.get(user_subscription = config_name)
        request_user_config = panelsapi.marzban(panel_id = int(subscriptions_.panel_id.pk)).get_user(username = str(config_name))

        SHOW_USER_INFO[call.from_user.id]['sub_request'] = request_user_config
        SHOW_USER_INFO[call.from_user.id]['panel_id'] =  subscriptions_.panel_id.pk
        SHOW_USER_INFO[call.from_user.id]['config_name'] = config_name
        
        Text_3 = config_details(SHOW_USER_INFO, call)
        
        bot.delete_message(call.message.chat.id , call.message.message_id)
        bot.send_message(call.message.chat.id ,  Text_3,  parse_mode='HTML', reply_markup=botkb.show_user_info_subscription(user_id=call_data[1] , request_dict=request_user_config))


#//TODO add on_hold status 
    if call.data.startswith('suichstatus'):
       
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            panel_id = SHOW_USER_INFO[call.from_user.id]['panel_id']
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            config_name = call_data[-1].removeprefix('(').removesuffix(')')
            inbounds = request_dict['inbounds']
            expire_date = request_dict['expire']
            data_limit = request_dict['data_limit']
            reality = request_dict['proxies']['vless']['flow'] if request_dict['proxies']['vless']['flow'] else ''

            status_config = 'disabled' if request_dict['status'] ==  'active' else  'active'
            note = f'user status changed by {call.message.chat.id} - {datetime.datetime.now().strftime("%H:%M:%S-%Y/%m/%d")}'
            try :
                put_user_request = panelsapi.marzban(int(panel_id)).put_user(user_name=config_name, usernote=note,  expire_date_sui=expire_date,
                                                                            date_limit_sui=data_limit, inbounds_sui=inbounds, status_sui=status_config , reality_sui=reality)
                SHOW_USER_INFO[call.from_user.id]['sub_request'] = put_user_request

            except Exception as suichstatus_error :
                print(f'An ERROR occured in [main.py - CHNAGE USER CONFIG STATUS - LINE 3904-3239 - CALL DATA  suichstatus] \n\n\t Error-msg :{suichstatus_error} ')
            Text_4 = f"{config_details(SHOW_USER_INFO, call)}\n⚠️ وضعیت اشتراک کاربر تغییر کرد"
            bot.edit_message_text(Text_4, call.message.chat.id, call.message.message_id, reply_markup=botkb.show_user_info_subscription(user_id=call_data[1], request_dict=SHOW_USER_INFO[call.from_user.id]['sub_request']))    


    if call.data.startswith('suigetconfiglink'):
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            if call_data[-1].removeprefix('(').removesuffix(')') == request_dict['username']:
                Text_5 = f"🔗 لینک هوشمند اشتراک : {request_dict['username']} \n📌- <code>{request_dict['subscription_url']}</code>"
                bot.send_message(call.message.chat.id , Text_5)



    if call.data.startswith('suigetqrcodelink'):
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            if call_data[-1].removeprefix('(').removesuffix(')') == request_dict['username']:
                qrcode_img = QRcode_maker.make_qrcode(request_dict['subscription_url'])
                Text_6 = f"🔗 QRcode لینک هوشمند به صورت  :   {request_dict['username']}"
                bot.send_photo(call.message.chat.id , photo=qrcode_img , caption=Text_6)




    if call.data.startswith('suiincreasedatalimit'):
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            if call_data[-1].removeprefix('(').removesuffix(')') == request_dict['username']:
                SHOW_USER_INFO[call.from_user.id]['data_limit_in'] = True
                Text_7 = f'مقدار حجمی را که میخواهید به اشتراک کاربر اضافه کنید رابه صورت گیگابایت ارسال نمایید \n\n TO-CANCEL : /cancel'
                bot.edit_message_text(Text_7, call.message.chat.id , call.message.message_id)
                bot.register_next_step_handler(call.message , increaseDataLimit)


    if call.data.startswith('suidecreasedatalimit'):
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            if call_data[-1].removeprefix('(').removesuffix(')') == request_dict['username']:
                SHOW_USER_INFO[call.from_user.id]['data_limit_de'] = True
                Text_7 = f'مقدار حجمی را که میخواهید از اشتراک کاربر کم کنید را ارسال نمایید \n\n TO-CANCEL : /cancel'
                bot.edit_message_text(Text_7, call.message.chat.id , call.message.message_id)
                bot.register_next_step_handler(call.message , decreaseDataLimit)


    if call.data.startswith('suiincreaseexpire'):
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            if call_data[-1].removeprefix('(').removesuffix(')') == request_dict['username']:
                SHOW_USER_INFO[call.from_user.id]['expire_in'] = True
                Text_7 = f'مقدار زمانی را که میخواهید به اشتراک کاربر اضافه کنید را ارسال نمایید \n\n TO-CANCEL : /cancel'
                bot.edit_message_text(Text_7, call.message.chat.id , call.message.message_id)
                bot.register_next_step_handler(call.message , increaseExpireTime)


    if call.data.startswith('suidecreaseexpire'):
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            if call_data[-1].removeprefix('(').removesuffix(')') == request_dict['username']:
                SHOW_USER_INFO[call.from_user.id]['expire_de'] = True
                Text_7 = f'مقدار زمانی را که میخواهید از اشتراک کاربر کم کنید را ارسال نمایید \n\n TO-CANCEL : /cancel'
                bot.edit_message_text(Text_7, call.message.chat.id , call.message.message_id)
                bot.register_next_step_handler(call.message , decreaseExpireTime)




    if call.data.startswith('suirevokesubscription'):
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            if call_data[-1].removeprefix('(').removesuffix(')') == request_dict['username']:
                revoke_sub = panelsapi.marzban(SHOW_USER_INFO[call.from_user.id]['panel_id']).revoke_sub(request_dict['username'])
                SHOW_USER_INFO[call.from_user.id]['sub_request'] = revoke_sub
                Text_8 = f"🔗 لینک جدید اشتراک : {request_dict['username']} \n📌- <code>{request_dict['subscription_url']}</code>"
                bot.send_message(call.message.chat.id ,Text_8 )



    if call.data.startswith('suiremovepaneluser'):
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            if call_data[-1].removeprefix('(').removesuffix(')') == request_dict['username']:
                remove_user_from_panel = panelsapi.marzban(SHOW_USER_INFO[call.from_user.id]['panel_id']).remove_user(request_dict['username'])
                subscriptions.objects.get(user_subscription = request_dict['username']).delete()
                user_detaild(SHOW_USER_INFO[call.from_user.id]['user_id'] , bot , message = call.message)




    if call.data.startswith('suiremoveservicemoneyback'):
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            call_data = call.data.split('.')
            request_dict = SHOW_USER_INFO[call.from_user.id]['sub_request']
            if call_data[-1].removeprefix('(').removesuffix(')') == request_dict['username']:
                SHOW_USER_INFO[call.from_user.id]['remove_service_money_back'] = True
                Text_7 = f'لطفا مقدار وجهی را که میخواهید به حساب کاربر اضافه نمایید را وارد کنید\n\n TO-CANCEL : /cancel'
                bot.edit_message_text(Text_7, call.message.chat.id , call.message.message_id)
                bot.register_next_step_handler(call.message , removeConfigMoneyBack)




    if call.data == 'back_from_show_user_info_config':
        if call.from_user.id in SHOW_USER_INFO and len(SHOW_USER_INFO) >= 1 :
            user_ = users.objects
            user = user_.get(user_id = SHOW_USER_INFO[call.from_user.id]['user_id'])
            userphoto = bot.get_user_profile_photos(user.user_id)
            bot.delete_message(call.message.chat.id , call.message.message_id)
            user_detaild(user.user_id , bot , message = call.message)




def handle_watchUserInfo(message):
    if message.text == '/cancel' or message.text == '/cancel'.upper():
        Text_1 = 'به قسمت مدیریت یوزر ها خوش امدیدبه قسمت مدیریت یوزر ها خوش امدید'
        bot.send_message(message.chat.id , Text_1, reply_markup=botkb.manage_users())
        bot.clear_step_handler(message)
    else :
        user_ = users.objects
        if message.text.isdigit():
            try : 
                user = user_.get(user_id = message.text)
                if user:
                    user_detaild(user.user_id , bot , message = message)
                    SHOW_USER_INFO[message.from_user.id]['user_id'] = user.user_id
            except Exception as userNotFound :
                print(userNotFound)
                bot.send_message(message.chat.id , 'کاربری با این ایدی عددی وجود ندارید')
        else:
            bot.send_message(message.chat.id , 'فقط ایدی عددی مجازی میباشد')
            bot.register_next_step_handler(message , handle_watchUserInfo)
    return


def increaseDataLimit(message):
    
    if message.text == '/cancel' or message.text == '/cancel'.upper():
        Text_1 = config_details( SHOW_USER_INFO, message=message)
        bot.send_message(message.chat.id ,  Text_1 ,  parse_mode='HTML' , reply_markup=botkb.show_user_info_subscription(user_id=SHOW_USER_INFO[message.from_user.id]['user_id'] , request_dict=SHOW_USER_INFO[message.from_user.id]['sub_request']))
    else:
        if message.text.isdigit():
            info_dict = SHOW_USER_INFO[message.from_user.id]
            panelID = int(info_dict['panel_id'])
            request_dict = info_dict['sub_request']
            inBounds = request_dict['inbounds']
            userName = request_dict['username']
            expireDate = request_dict['expire']
            data_limit = int(message.text) * 1024 * 1024 * 1024
            newDatalimit = info_dict['sub_request']['data_limit'] + data_limit if info_dict['sub_request']['data_limit'] is not None else data_limit
            statusConfig = request_dict['status'] if request_dict['status'] == 'active' else 'active'
            realityConfig = request_dict['proxies']['vless']['flow'] if request_dict['proxies']['vless']['flow'] else ''
            note = f'DataLimit {message.text}GB increased  by {message.from_user.id} at {datetime.datetime.now().strftime("%H:%M:%S-%Y/%m/%d")}'
                

            increaseDataLimitreq = panelsapi.marzban(panelID).put_user(user_name=userName , usernote=note , expire_date_sui=expireDate ,
                                                                        date_limit_sui=newDatalimit , inbounds_sui=inBounds , status_sui=statusConfig ,
                                                                        reality_sui=realityConfig)
            
            
            
            SHOW_USER_INFO[message.from_user.id]['sub_request'] =increaseDataLimitreq
            SHOW_USER_INFO[message.from_user.id]['data_limit_in'] = False
            Text_2 = config_details(SHOW_USER_INFO , message)   
            bot.send_message(message.chat.id , Text_2 , reply_markup=botkb.show_user_info_subscription(user_id=info_dict['user_id'] , request_dict=increaseDataLimitreq))
        else:
            bot.send_message(message.chat.id , 'فقط  عدد مجاز میباشد')
            bot.register_next_step_handler(message , increaseDataLimit)
    return


def decreaseDataLimit(message):
    if message.text == '/cancel' or message.text == '/cancel'.upper():
        Text_1 = config_details( SHOW_USER_INFO, message=message )
        bot.send_message(message.chat.id ,  Text_1 ,  parse_mode='HTML' , reply_markup=botkb.show_user_info_subscription(user_id=SHOW_USER_INFO[message.from_user.id]['user_id'] , request_dict=SHOW_USER_INFO[message.from_user.id]['sub_request']))
    else :
        if message.text.isdigit():
            info_dict = SHOW_USER_INFO[message.from_user.id]
            panelID = int(info_dict['panel_id'])
            request_dict = info_dict['sub_request']
            inBounds = request_dict['inbounds']
            userName = request_dict['username']
            expireDate = request_dict['expire']
            data_limit = int(message.text) * 1024 * 1024 * 1024
            newDatalimit = info_dict['sub_request']['data_limit'] - data_limit if info_dict['sub_request']['data_limit'] is not None else data_limit
            statusConfig = request_dict['status'] if request_dict['status'] == 'active' else 'active'
            realityConfig = request_dict['proxies']['vless']['flow'] if request_dict['proxies']['vless']['flow'] else ''
            note = f'DataLimit {message.text}GB decreased  by {message.from_user.id} at {datetime.datetime.now().strftime("%H:%M:%S-%Y/%m/%d")}'
            
            decreaseDataLimitreq = panelsapi.marzban(panelID).put_user(user_name=userName , usernote=note , expire_date_sui=expireDate ,
                                                                        date_limit_sui=newDatalimit , inbounds_sui=inBounds , status_sui=statusConfig ,
                                                                        reality_sui=realityConfig)
            
            
            
            SHOW_USER_INFO[message.from_user.id]['sub_request'] = decreaseDataLimitreq
            SHOW_USER_INFO[message.from_user.id]['data_limit_de'] = False
            Text_3 = config_details(SHOW_USER_INFO , message)
            
            bot.send_message(message.chat.id , Text_3 , reply_markup=botkb.show_user_info_subscription(user_id=info_dict['user_id'] , request_dict=decreaseDataLimitreq))
        else:
            bot.send_message(message.chat.id , 'فقط  عدد مجاز میباشد')
            bot.register_next_step_handler(message , decreaseDataLimit)
    return


def increaseExpireTime(message):
    if message.text == '/cancel' or message.text == '/cancel'.upper():
        Text_1 = config_details( SHOW_USER_INFO, message=message )
        bot.send_message(message.chat.id ,  Text_1 ,  parse_mode='HTML' , reply_markup=botkb.show_user_info_subscription(user_id=SHOW_USER_INFO[message.from_user.id]['user_id'] , request_dict=SHOW_USER_INFO[message.from_user.id]['sub_request']))
    else :
        if message.text.isdigit():
            info_dict = SHOW_USER_INFO[message.from_user.id]
            panelID = int(info_dict['panel_id'])
            request_dict = info_dict['sub_request']
            inBounds = request_dict['inbounds']
            userName = request_dict['username']
            data_limit = request_dict['data_limit']
            statusConfig = request_dict['status'] if request_dict['status'] == 'active' else 'active'
            realityConfig = request_dict['proxies']['vless']['flow'] if request_dict['proxies']['vless']['flow'] else ''
            expire_fromtimestamp = datetime.datetime.fromtimestamp(request_dict['expire']) + datetime.timedelta(days= int(message.text))
            newExpireDate = datetime.datetime.timestamp(expire_fromtimestamp) 
            note = f'ExpireTime {message.text}days increased  by {message.from_user.id} at {datetime.datetime.now().strftime("%H:%M:%S-%Y/%m/%d")}'

            increaseExpireTimereq = panelsapi.marzban(panelID).put_user(user_name=userName , usernote=note , expire_date_sui=newExpireDate ,
                                                                    date_limit_sui=data_limit , inbounds_sui=inBounds , status_sui=statusConfig ,
                                                                    reality_sui=realityConfig)
            
            SHOW_USER_INFO[message.from_user.id]['sub_request'] = increaseExpireTimereq
            SHOW_USER_INFO[message.from_user.id]['expire_in'] = False
            Text_4 = config_details(SHOW_USER_INFO , message)
            bot.send_message(message.chat.id , Text_4 , reply_markup=botkb.show_user_info_subscription(user_id=info_dict['user_id'] , request_dict=increaseExpireTimereq))
        else:
            bot.send_message(message.chat.id , 'فقط  عدد مجاز میباشد')
            bot.register_next_step_handler(message , increaseExpireTime)
    return


def decreaseExpireTime(message):
    if message.text == '/cancel' or message.text == '/cancel'.upper():
        Text_1 = config_details( SHOW_USER_INFO, message=message )
        bot.send_message(message.chat.id ,  Text_1 ,  parse_mode='HTML' , reply_markup=botkb.show_user_info_subscription(user_id=SHOW_USER_INFO[message.from_user.id]['user_id'] , request_dict=SHOW_USER_INFO[message.from_user.id]['sub_request']))
    else :
        if message.text.isdigit():
            info_dict = SHOW_USER_INFO[message.from_user.id]
            panelID = int(info_dict['panel_id'])
            request_dict = info_dict['sub_request']
            inBounds = request_dict['inbounds']
            userName = request_dict['username']
            data_limit = request_dict['data_limit']
            statusConfig = request_dict['status'] if request_dict['status'] == 'active' else 'active'
            realityConfig = request_dict['proxies']['vless']['flow'] if request_dict['proxies']['vless']['flow'] else ''
            expire_fromtimestamp = datetime.datetime.fromtimestamp(request_dict['expire']) - datetime.timedelta(days= int(message.text))
            newExpireDate = datetime.datetime.timestamp(expire_fromtimestamp) 
            note = f'ExpireTime {message.text}days decreased  by {message.from_user.id} at {datetime.datetime.now().strftime("%H:%M:%S-%Y/%m/%d")}'

            decreaseExpireTimereq = panelsapi.marzban(panelID).put_user(user_name=userName , usernote=note , expire_date_sui=newExpireDate ,
                                                                    date_limit_sui=data_limit , inbounds_sui=inBounds , status_sui=statusConfig ,
                                                                    reality_sui=realityConfig)
            
            SHOW_USER_INFO[message.from_user.id]['sub_request'] = decreaseExpireTimereq   
            SHOW_USER_INFO[message.from_user.id]['expire_de'] = False  
            Text_5 = config_details(SHOW_USER_INFO , message)  
            bot.send_message(message.chat.id , Text_5 , reply_markup=botkb.show_user_info_subscription(user_id=info_dict['user_id'] , request_dict=decreaseExpireTimereq))
        else:
            bot.send_message(message.chat.id , 'فقط  عدد مجاز میباشد')
            bot.register_next_step_handler(message , decreaseExpireTime)
    return
   

def removeConfigMoneyBack(message):

    if message.text == '/cancel' or message.text == '/cancel'.upper():
        Text_1 = config_details( SHOW_USER_INFO, message=message )
        bot.send_message(message.chat.id ,  Text_1 ,  parse_mode='HTML' , reply_markup=botkb.show_user_info_subscription(user_id=SHOW_USER_INFO[message.from_user.id]['user_id'] , request_dict=SHOW_USER_INFO[message.from_user.id]['sub_request']))
    else:
        if message.text.isdigit():
            info = SHOW_USER_INFO[message.from_user.id]
            userID = info['user_id']
            panelId = int(info['panel_id'])
            userName = info['config_name']

            user_ = users.objects.get(user_id = userID)
            new_user_wallet = user_.user_wallet + decimal.Decimal(message.text)
            user_.user_wallet = new_user_wallet
            user_.save()
            remove_sub = subscriptions.objects.get(user_id=userID , user_subscription=userName).delete()
            remove_service = panelsapi.marzban(panelId).remove_user(userName)

            Text_6 = f"👤 کاربر گرامی اشتراک شما با نام {userName} از پنل و حساب کاربری شما حذف گردید ❌\n و همچنین مبلغ {str(format(int(message.text) , ','))} به حساب کیف پول شما واریز گردید" 
            bot.send_message(userID , Text_6)
            Text_7 = f"اشتراک کاربر با نام {userName} از پنل و سرویس کاربر حذف گردید "
            bot.send_message(message.chat.id , Text_7)
            user_detaild(userID , bot , message = message)
            SHOW_USER_INFO[message.from_user.id]['remove_service_money_back'] = False
        else:
            bot.send_message(message.chat.id , 'فقط  عدد مجاز میباشد')
            bot.register_next_step_handler(message , removeConfigMoneyBack)
    return






#----------------------------------------------------------------------------------------------------------------------------#
# -------------------------IN-DE crease cash section-----------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------------#

USER_INCREASE_DECREASE_CASH = {}
def operating():
    OPERATION_INCREASE_DECREASE  = {'operator': None ,'amount' : None, 'current_cash': None ,
                                    'verfiy_message': None , 'amount_wish': False , 'msg_wish':None,
                                    'operating': False, 'user_id' : int}
    return OPERATION_INCREASE_DECREASE


@bot.message_handler(commands=['increseusercash'])
def handle_watchUserIndo_command(message):
    if check_admins(message.from_user.id , user_management=True) == 'usermanagment_access':
        if message.text =='/increseusercash':
            Text_1 = '💸برای افزایش موجودی کاربر ایدی عدد کاربر مورد نظر را ارسال نمایید \n\n TO-CANCEL : /cancel'
            if message.from_user.id not in SHOW_USER_INFO:
                SHOW_USER_INFO[message.from_user.id] = show_user_info()
            bot.send_message(message.chat.id , Text_1)
            bot.register_next_step_handler(message , getUserOperationsCashs)
    else:
        bot.send_message(message.chat.id , 'شما اجازه دسترسی به این قسمت را ندارید')
    




@bot.callback_query_handler(func= lambda call : call.data in ['operator_mines' , 'operator_plus' , 'decrease_cash_to','increase_cash_to' , 'back_from_step_increase_decrease' , 'wish_amount' ,'wish_msg_cash', 'back_from_increase_decrease_cash'] or call.data.startswith(('amount_decrease' , 'amount_increase','verify_inde_')))
def increase_decrease_cahs(call):
    try:
        if call.from_user.id in USER_INCREASE_DECREASE_CASH :
            User_id = USER_INCREASE_DECREASE_CASH[call.from_user.id]['user_id'] 
            users_ = users.objects.get(user_id = int(User_id))
            Text_00 = getUserOperationsCashs_1(users_.user_id)


        if call.data =='operator_mines':
            if USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] == True and call.from_user.id in USER_INCREASE_DECREASE_CASH:
                USER_INCREASE_DECREASE_CASH[call.from_user.id]['operator'] = 'mines'
                operator = USER_INCREASE_DECREASE_CASH[call.from_user.id]['operator'] 
                amount_ = USER_INCREASE_DECREASE_CASH[call.from_user.id]['amount']
                currentCash = USER_INCREASE_DECREASE_CASH[call.from_user.id]['current_cash']
                op = "➕" if operator =="plus"  else "➖" if operator=="mines" else None  
                amount = amount_ if amount_ is not None else  int(1)
                current_cash = currentCash if currentCash is not None else '5000'

                bot.edit_message_text(Text_00 , call.message.chat.id , call.message.message_id , reply_markup=botkb.increase_or_decrease(user_id=int(User_id), amount_add= int(amount), operator=op , current_cash = int(current_cash)))
            else:
                bot.send_message(call.message.chat.id , 'انجام این عملیات برای این یوزر امکان پذیر نمیباشد')


        if call.data =='operator_plus':
            if USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] == True  and call.from_user.id in USER_INCREASE_DECREASE_CASH:
                USER_INCREASE_DECREASE_CASH[call.from_user.id]['operator'] = "plus"  
                operator = USER_INCREASE_DECREASE_CASH[call.from_user.id]['operator'] 
                amount_ = USER_INCREASE_DECREASE_CASH[call.from_user.id]['amount']
                currentCash = USER_INCREASE_DECREASE_CASH[call.from_user.id]['current_cash']
                op = "➕" if operator =='plus'  else '➖' if operator=='mines' else None  
                amount = amount_ if amount_ is not None else  int(1)
                current_cash = currentCash if currentCash is not None else '5000' 

                bot.edit_message_text(Text_00 , call.message.chat.id , call.message.message_id , reply_markup=botkb.increase_or_decrease(user_id=int(User_id),amount_add= int(amount) , operator=op, current_cash = int(current_cash)))
            
            else:
                bot.send_message(call.message.chat.id , 'انجام این عملیات برای این یوزر امکان پذیر نمیباشد')


        if call.data.startswith('amount_decrease'):
            if USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] == True  and call.from_user.id in USER_INCREASE_DECREASE_CASH:
                call_data = call.data.split("_")
                USER_INCREASE_DECREASE_CASH[call.from_user.id]['amount'] = int(call_data[-1])
                operator = USER_INCREASE_DECREASE_CASH[call.from_user.id]['operator']
                amount_ = USER_INCREASE_DECREASE_CASH[call.from_user.id]['amount'] 
                currentCash = USER_INCREASE_DECREASE_CASH[call.from_user.id]['current_cash']
                op = "➕" if operator =='plus'  else '➖' if operator=='mines' else None  
                amount = amount_ if amount_ is not None else int(call_data[-1])
                current_cash = currentCash if currentCash is not None else '5000'
                bot.edit_message_text(Text_00 , call.message.chat.id , call.message.message_id , reply_markup= botkb.increase_or_decrease(user_id=int(User_id), amount_add=amount, operator=op, current_cash=int(current_cash)))
            else:
                bot.send_message(call.message.chat.id , 'انجام این عملیات برای این یوزر امکان پذیر نمیباشد')


        if call.data.startswith('amount_increase'):
            if USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] == True  and call.from_user.id in USER_INCREASE_DECREASE_CASH:
                call_data = call.data.split("_")
                USER_INCREASE_DECREASE_CASH[call.from_user.id]['amount'] = int(call_data[-1])
                operator = USER_INCREASE_DECREASE_CASH[call.from_user.id]['operator']
                amount_ = USER_INCREASE_DECREASE_CASH[call.from_user.id]['amount'] 
                currentCash = USER_INCREASE_DECREASE_CASH[call.from_user.id]['current_cash']
                op = "➕" if operator =='plus'  else '➖' if operator=='mines' else None  
                amount = amount_ if amount_ is not None else int(call_data[-1])
                current_cash = currentCash if currentCash is not None else '5000'
                bot.edit_message_text(Text_00 , call.message.chat.id , call.message.message_id , reply_markup= botkb.increase_or_decrease(user_id=int(User_id), amount_add=amount, operator=op, current_cash=int(current_cash)))
            
            else:
                bot.send_message(call.message.chat.id , 'انجام این عملیات برای این یوزر امکان پذیر نمیباشد')



        if call.data.startswith('verify_inde_') :
            if USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] == True  and call.from_user.id in USER_INCREASE_DECREASE_CASH :  
                call_data = call.data.split('_')
                USER_INCREASE_DECREASE_CASH[call.from_user.id]['verfiy_message'] = call.data
                userDefindMsg = USER_INCREASE_DECREASE_CASH[call.from_user.id]['msg_wish']

                amount = format(int(call_data[2]), ',') 
                Text_0_2 = getUserOperationsCashs_2(amount) if userDefindMsg is None else userDefindMsg
                Text_0_3 = getUserOperationsCashs_3(amount) if userDefindMsg is None else userDefindMsg

                if call_data[3] == 'None':
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton(text='اضافه کردن وجه', callback_data='increase_cash_to') ,
                                InlineKeyboardButton(text='کم کردن وجه' , callback_data='decrease_cash_to') ,
                                InlineKeyboardButton(text='بازگشت↩️', callback_data='back_from_step_increase_decrease') ,row_width=1)
                    bot.edit_message_text('عملیات را انتخاب نمایید', call.message.chat.id , call.message.message_id , reply_markup=keyboard)
                
                

                if call_data[3] =='plus':
                    USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] = False
                    try :
                        user_ = users.objects.get(user_id = int(call_data[4]))
                        new_wallet = user_.user_wallet + decimal.Decimal(call_data[2])
                        user_.user_wallet = new_wallet
                        user_.save()
                        bot.delete_message(call.message.chat.id , call.message.message_id)
                        bot.send_message(call.message.chat.id , '✅مبلغ به کیف پول یوزر اضافه شد')
                        bot.send_message(int(call_data[-1]) , Text_0_2)
                        clear_dict(USER_INCREASE_DECREASE_CASH ,call.from_user.id)
                    except Exception as error_increase_cash :
                        print(f'error : {error_increase_cash}')


                if call_data[3] == 'mines':
                    USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] = False
                    try :
                        user_ = users.objects.get(user_id = int(call_data[4]))
                        if user_.user_wallet < 0 :
                            bot.send_message(call.message.chat.id , 'موجودی کیف پول مقصد صفر تومان است')
                        elif user_.user_wallet <= int(call_data[2]):
                            user_.user_wallet = 0 
                            user_.save()
                            bot.send_message(call.message.chat.id , 'موجودی کیف پول مقصد صفر خواهد شد')
                        else:
                            new_wallet = user_.user_wallet - decimal.Decimal(call_data[2])
                            user_.user_wallet = new_wallet
                            user_.save()
                            bot.delete_message(call.message.chat.id , call.message.message_id)
                            bot.send_message(call.message.chat.id , '✅مبلغ از کیف پول یوزر کسر شد')
                        bot.send_message(int(call_data[-1]) , Text_0_3)
                        clear_dict(USER_INCREASE_DECREASE_CASH , call.from_user.id)
                    except Exception as error_decrease_cash :
                        print(f'error : {error_decrease_cash}')
            else:
                bot.send_message(call.message.chat.id , 'انجام این عملیات برای این یوزر امکان پذیر نمیباشد')


        if call.data =='increase_cash_to':
            print(call.data)
            if USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] == True  and call.from_user.id in USER_INCREASE_DECREASE_CASH :  
                call_data = USER_INCREASE_DECREASE_CASH[call.from_user.id]['verfiy_message'].split("_")
                userDefindMsg = USER_INCREASE_DECREASE_CASH[call.from_user.id]['msg_wish']
                amount = format(int(call_data[2]) , ',')
                Text_0_4 = getUserOperationsCashs_2(amount) if userDefindMsg is None else userDefindMsg
                USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] = False
                try :
                    users_ = users.objects.get(user_id = int(call_data[4]))
                    new_wallet = users_.user_wallet + decimal.Decimal(call_data[2])
                    users_.user_wallet = new_wallet
                    users_.save()
                    bot.delete_message(call.message.chat.id , call.message.message_id)
                    bot.send_message(call.message.chat.id , '✅مبلغ به کیف پول یوزر اضافه شد')
                    bot.send_message(int(call_data[-1]) , Text_0_4)
                    clear_dict(USER_INCREASE_DECREASE_CASH , call.from_user)
                except Exception as error_next_increase:
                    print(f'error : {error_next_increase}')
            else:
                bot.send_message(call.message.chat.id , 'انجام این عملیات برای این یوزر امکان پذیر نمیباشد')


        if call.data =='decrease_cash_to':
            if USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] == True  and call.from_user.id in USER_INCREASE_DECREASE_CASH :  
                call_data = USER_INCREASE_DECREASE_CASH[call.from_user.id]['verfiy_message'].split("_")
                userDefindMsg = USER_INCREASE_DECREASE_CASH[call.from_user.id]['msg_wish']
                amount = format(int(call_data[2]) , ',')
                Text_0_5 = getUserOperationsCashs_3(amount) if userDefindMsg is None else userDefindMsg
                USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] = False
                try :
                    user_ = users.objects.get(user_id = int(call_data[4]))
                    if user_.user_wallet < 0 :
                        bot.send_message(call.message.chat.id , 'موجودی کیف پول مقصد صفر تومان است')
                    elif user_.user_wallet <= int(call_data[2]):
                        user_.user_wallet = 0 
                        user_.save()
                        bot.send_message(call.message.chat.id , 'موجودی کیف پول مقصد صفر خواهد شد')
                    else:
                        new_wallet = user_.user_wallet - decimal.Decimal(call_data[2])
                        user_.user_wallet = new_wallet
                        user_.save()
                        bot.send_message(call.message.chat.id , 'مبلغ از کیف پول یوزر کسر شد')
                    bot.delete_message(call.message.chat.id , call.message.message_id)   
                    bot.send_message(int(call_data[-1]) , Text_0_5)
                    clear_dict(USER_INCREASE_DECREASE_CASH , call.from_user.id)
                except Exception as error_decrease_cash :
                        print(f'error : {error_decrease_cash}')
            else:
                bot.send_message(call.message.chat.id , 'انجام این عملیات برای این یوزر امکان پذیر نمیباشد')


        if call.data=='wish_amount':
            if USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] == True  and call.from_user.id in USER_INCREASE_DECREASE_CASH : 
                bot.delete_message(call.message.chat.id , call.message.message_id) 
                bot.send_message(call.message.chat.id , 'مقدار دل خواه را وارد نمایید')
                bot.register_next_step_handler(call.message , changegetUserOperationsCashs)
            else:
            
                bot.send_message(call.message.chat.id , 'انجام این عملیات برای این یوزر امکان پذیر نمیباشد')



        if call.data =='wish_msg_cash':
            if USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] == True  and call.from_user.id in USER_INCREASE_DECREASE_CASH : 
                bot.delete_message(call.message.chat.id , call.message.message_id) 
                bot.send_message(call.message.chat.id , 'پیام دلخواه خود را وارد کنید\n\n TO-CANCEL : /cancel')
                bot.register_next_step_handler(call.message , changegetUserOperationsCashsMsg)
            else:
            
                bot.send_message(call.message.chat.id , 'انجام این عملیات برای این یوزر امکان پذیر نمیباشد')



        if call.data =='back_from_step_increase_decrease':
            USER_INCREASE_DECREASE_CASH[call.from_user.id]['operating'] = True
            userId = USER_INCREASE_DECREASE_CASH[call.from_user.id]['user_id']
            operator = USER_INCREASE_DECREASE_CASH[call.from_user.id]['operator'] 
            amount_ = USER_INCREASE_DECREASE_CASH[call.from_user.id]['amount']
            currentCash = USER_INCREASE_DECREASE_CASH[call.from_user.id]['current_cash']

            op = "➕" if operator =="plus"  else "➖" if operator=="mines" else None  
            amount = amount_ if amount_ is not None else  int(1)
            current_cash = currentCash if currentCash is not None else '5000'

            bot.edit_message_text(getUserOperationsCashs_1(userId) , call.message.chat.id , call.message.message_id , reply_markup=botkb.increase_or_decrease(user_id=int(userId), amount_add= int(amount), operator=op , current_cash =int(current_cash)))
        
        if call.data == 'back_from_increase_decrease_cash':
            clear_dict(USER_INCREASE_DECREASE_CASH , call.from_user.id)
            bot.edit_message_text('به قسمت مدیریت یوزر ها خوش امدید' , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_users())

    
    except Exception as err:
        pass




def getUserOperationsCashs(message):
    if message.text == '/cancel' or message.text == '/cancel'.upper():
        clear_dict(USER_INCREASE_DECREASE_CASH , message.from_user.id)
        bot.send_message(message.chat.id , 'عملیات لغو شد' , reply_markup=botkb.manage_users())
    else:
        if message.text.isdigit():
            try : 
                USER_INCREASE_DECREASE_CASH[message.from_user.id] = operating()
                users_ = users.objects.get(user_id = int(message.text))
                if users_:
                    USER_INCREASE_DECREASE_CASH[message.from_user.id]['user_id'] = users_.user_id
                    USER_INCREASE_DECREASE_CASH[message.from_user.id]['operating'] = True
                    Text_1 = getUserOperationsCashs_1(users_.user_id)
                    bot.send_message( message.chat.id , Text_1 , reply_markup=botkb.increase_or_decrease(user_id=users_.user_id))
            except users.DoesNotExist:
                bot.send_message(message.chat.id , 'یوزری با این ایدی یافت نشد')
        else:
            bot.send_message(message.chat.id , 'ایدی وارد شده باید به صورت عدد باشد')
            bot.register_next_step_handler(message , getUserOperationsCashs)
    return
    



def changegetUserOperationsCashs(message):
    if message.text.isdigit():
        USER_INCREASE_DECREASE_CASH[message.from_user.id]['current_cash'] = int(message.text)
        users_ = users.objects.get(user_id = USER_INCREASE_DECREASE_CASH[message.from_user.id]['user_id'])
        Text_2 = getUserOperationsCashs_1(users_.user_id)
        operator = USER_INCREASE_DECREASE_CASH[message.from_user.id]['operator']
        currentCash = USER_INCREASE_DECREASE_CASH[message.from_user.id]['current_cash']
        op = "plus" if operator =='plus'  else 'mines' if operator=='mines' else None
        current_cash = currentCash  if currentCash is not None else '5000'
        bot.send_message(message.chat.id , Text_2 , reply_markup=botkb.increase_or_decrease(user_id= users_.user_id, current_cash= int(current_cash), operator=op , amount_add= 1))
    else:
        bot.send_message(message.chat.id , 'ایدی وارد شده باید به صورت عدد باشد')
        bot.register_next_step_handler(message , changegetUserOperationsCashs)
    return
    



def changegetUserOperationsCashsMsg(message):
    if message.text == '/cancel' or message.text == '/cancel'.upper():
        bot.send_message(message.chat.id , 'پیام به صورت دیفالت تنظیم شد' , reply_markup=botkb.manage_users())
    else:
        USER_INCREASE_DECREASE_CASH[message.from_user.id]['msg_wish'] = str(message.text)
        users_ = users.objects.get(user_id = USER_INCREASE_DECREASE_CASH[message.from_user.id]['user_id'])
        Text_2 = getUserOperationsCashs_1(users_.user_id)
        operator = USER_INCREASE_DECREASE_CASH[message.from_user.id]['operator']
        currentCash = USER_INCREASE_DECREASE_CASH[message.from_user.id]['current_cash']
        op = "plus" if operator =='plus'  else 'mines' if operator=='mines' else None
        current_cash = currentCash  if currentCash is not None else '5000'
        bot.send_message(message.chat.id , Text_2 , reply_markup=botkb.increase_or_decrease(user_id= users_.user_id, current_cash= int(current_cash), operator=op , amount_add= 1))
        





#----------------------------------------------------------------------------------------------------------------------------#
# -------------------------user-blcok-unblcok-user management----------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------------#

BLOCK_UNBLOCK_USER = {}

def block_unblock_user():
    block_unblock_user_dict = {'get_userid':None, 'user_id':None,'block_unblock':None, 'get_reason':None, 'reason_msg':None }
    return block_unblock_user_dict


@bot.callback_query_handler(func= lambda call: call.data in ['back_from_block_unblock'] or call.data.startswith(('block_user_', 'unblock_user_', 'verify_sendmsg_')))
def handle_block_unblock(call):



    if call.data.startswith('block_user_'):
        users_ =users.objects.get(user_id = BLOCK_UNBLOCK_USER[call.from_user.id]['user_id'])
        if users_.block_status == 1 :
            Text_2 = 'یوزر از قبل مسدود میباشد'
            bot.send_message(call.message.chat.id , Text_2)
        else:
            Text_3 = 'علت مسدودی یوزر را وارد کنید\n TO-CANCEL : /cancel'
            bot.edit_message_text(Text_3, call.message.chat.id , call.message.message_id)
            bot.register_next_step_handler(call.message , getUserBlockReason)




    if call.data.startswith('unblock_user_'):
        users_ =users.objects.get(user_id = BLOCK_UNBLOCK_USER[call.from_user.id]['user_id'])
        if users_.block_status == 0 :
            Text_4 = 'یوزر از قبل مسدود نمیباشد'
            bot.send_message(call.message.chat.id , Text_4 )
        else:
            BLOCK_UNBLOCK_USER[call.from_user.id]['block_unblock'] = 0
            Text_5 = f"به قسمت مدیریت یوزر ها خوش امدید\n علت مسدودی یوزر دریافت شد\n ایدی یوزر : {BLOCK_UNBLOCK_USER[call.from_user.id]['user_id']}"
            bot.edit_message_text(Text_5 , call.message.chat.id , call.message.message_id , reply_markup=botkb.block_unblock(user_id=BLOCK_UNBLOCK_USER[call.from_user.id]['user_id'] , unblock=True))




    if call.data.startswith('verify_sendmsg_'):
        try :
            users_ = users.objects.get(user_id = BLOCK_UNBLOCK_USER[call.from_user.id]['user_id'])
            admins_ = admins.objects.filter(user_id = BLOCK_UNBLOCK_USER[call.from_user.id]['user_id'])
            if BLOCK_UNBLOCK_USER[call.from_user.id]['block_unblock'] == 1:
                if admins_.exists :
                    admins_.delete()
                users_.block_status = 1
                users_.block_reason = BLOCK_UNBLOCK_USER[call.from_user.id]['reason_msg']
                users_.save()
                Text_6 = f"شما در ربات مسدود شدید و امکان استفاده از امکانات ربات را نخواهید داشت\n علت مسدودی : {BLOCK_UNBLOCK_USER[call.from_user.id]['reason_msg']}"
                bot.send_message(BLOCK_UNBLOCK_USER[call.from_user.id]['user_id'] ,Text_6 )
            
            else:
                users_.block_status = 0 
                users_.block_reason = None
                users_.save()
                Text_7 = f"شما در ربات رفع انسداد شدید و امکان استفاده از امکانات ربات برای شما میسر شد"
                bot.send_message(BLOCK_UNBLOCK_USER[call.from_user.id]['user_id'] ,Text_7 )

        except Exception as block_unblock_status :
            print(f'error while changing user block_unblock status : error_msg : {block_unblock_status}')
        
        block_status_msg = 'مسدود' if users_.block_status == 1 else 'عدم انسداد'
        Text_8 = f'وضععیت انسداد یوزر تغییر پیدا کرد \n وضعیت فعلی :‌{block_status_msg} '
        bot.send_message(call.message.chat.id , Text_8)
        bot.edit_message_text('به قسمت مدیریت یوزر ها خوش امدید' , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_users())




    if call.data == 'back_from_block_unblock':
        clear_dict(BLOCK_UNBLOCK_USER , call.from_user.id)
        Text_0 = 'به قسمت مدیریت یوزر ها خوش امدید'
        bot.edit_message_text(Text_0 , call.message.chat.id , call.message.message_id , reply_markup=botkb.manage_users())
        
        






def getUserBlock(message):
    if message.text =='/cancel' or message.text == '/cancel'.upper():
        Text_1 = 'به قسمت مدیریت یوزر ها خوش امدید'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.manage_users())
    else:
        if message.text.isdigit():
            try :
                if message.from_user.id in BLOCK_UNBLOCK_USER :
                    clear_dict(BLOCK_UNBLOCK_USER , message.from_user.id)
                BLOCK_UNBLOCK_USER[message.from_user.id] = block_unblock_user()
                users_ = users.objects.get(user_id = int(message.text))
                BLOCK_UNBLOCK_USER[message.from_user.id]['user_id'] = int(message.text)
                Text_2 = f"برای اعمال محدودیت از منوی زیر اقدام نمایید\n ایدی یوزر : {users_.user_id}"
                bot.send_message(message.chat.id , Text_2 , reply_markup=botkb.block_unblock(user_id=users_.user_id))
            
            except users.DoesNotExist as user_doesnot_exist:
                clear_dict(BLOCK_UNBLOCK_USER , message.from_user.id)
                bot.send_message(message.chat.id , 'کاربری با این ایدی عددی یافت نشد')
        else:
            Text_3 = 'مقدار ارسالی باید به صورت عددی باشد'
            clear_dict(BLOCK_UNBLOCK_USER , message.from_user.id)
            bot.send_message(message.chat.id , Text_3)
    return 




def getUserBlockReason(message):
    if message.text =='/cancel' or message.text =='/cancel'.upper():
        clear_dict(BLOCK_UNBLOCK_USER , message.from_user.id)
        Text_4 = 'به قسمت مدیریت یوزر ها خوش امدید'
        bot.send_message(message.chat.id, Text_4, reply_markup=botkb.manage_users())
    else:
        BLOCK_UNBLOCK_USER[message.from_user.id]['reason_msg'] = str(message.text)
        BLOCK_UNBLOCK_USER[message.from_user.id]['block_unblock'] = 1
        Text_5 = f"به قسمت مدیریت یوزر ها خوش امدید\n علت مسدودی یوزر دریافت شد\n ایدی یوزر : {BLOCK_UNBLOCK_USER[message.from_user.id]['user_id']}\n علت مسدودی : {BLOCK_UNBLOCK_USER[message.from_user.id]['reason_msg']}"
        bot.send_message(message.chat.id , Text_5, reply_markup=botkb.block_unblock(user_id=BLOCK_UNBLOCK_USER[message.from_user.id]["user_id"] , block=True))
    return












#----------------------------------------------------------------------------------------------------------------------------#
# -------------------------Send-msg-to-users management----------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------------#



# //TODO add feature to send msg to users who  have not account or had accounts or having at least one account


SIND_SINGLE_MSG = {'user_id': False}
BOARDCATING = {'msg_to_store':None , 'admin_requested':None , 'msg_type':None , 'msg_caption':None}



@bot.callback_query_handler(func= lambda call: call.data in ['send_msg_single_user', 'send_msg_boardcasting' , 'verify_send_msg_to_all', 'cancel_send_msg_to_all' ,'send_msg_forwarding', 'back_from_send_msg'])
def handle_sending_users_msg(call):

    if call.data =='send_msg_single_user':
        Text_2 = '🆔ایدی عددی شخصی را که میخواهید پیام بدهید را ارسال نمایید\n TO-CANCEL : /cancel'
        bot.register_next_step_handler(call.message , sendMsgSingleUserUserId)
        bot.edit_message_text(Text_2, call.message.chat.id , call.message.message_id)



    if call.data =='send_msg_boardcasting':
        Text_3 = 'متنی را که میخواهید برای تمام اعضای ربات بفرستید را ارسال نمیایید\n فرمت های قابل پشتیبانی : متن ، تصویر ،‌ویدیو\n TO-CANCEL : /cancel'
        bot.edit_message_text(Text_3, call.message.chat.id , call.message.message_id)
        bot.register_next_step_handler(call.message , sendBoardcastingMsgToAll)



    if call.data == 'verify_send_msg_to_all':
        users_ = users.objects.all()
        owner_id = admins.objects.filter(is_owner =1).values_list('user_id' , flat=True)[0]
        time_to_send = (users_.count() * 1) / 60
        text_msg_status = f'یک پیام همگانی در حال ارسال برای همه اعضای ربات میباشد \nزمان تقریبی برای ارسال : {round(time_to_send,3)} دقیقه'

        if BOARDCATING['admin_requested'] is not None :
            bot.send_message(BOARDCATING['admin_requested'] , ' درخواست شما توسط اونر ربات تایید شد و در حال ارسال برای تمام اعضا میباشد')
            bot.send_message(BOARDCATING['admin_requested'], text_msg_status)

        bot.edit_message_text(text_msg_status, owner_id , call.message.message_id)
        admins_ = admins.objects.filter(is_admin =1).values('user_id')[0]['user_id']
        for userID in users_:
            if BOARDCATING['msg_type'] =='photo':
                if userID.user_id != owner_id or userID.user_id != admins_:
                    bot.send_photo(userID.user_id , photo=BOARDCATING['msg_to_store'][0].file_id , caption=BOARDCATING['msg_caption'])
                    time.sleep(1)

            elif BOARDCATING['msg_type'] =='video':
                if userID.user_id != owner_id or userID.user_id != admins_:
                    bot.send_video(userID.user_id , video=BOARDCATING['msg_to_store'].file_id , caption=BOARDCATING['msg_caption'])
                    time.sleep(1)     
            else:
                if userID.user_id != owner_id or userID.user_id != admins_ :
                    bot.send_message(userID.user_id , BOARDCATING['msg_to_store'])
                    time.sleep(1)



    if call.data =='cancel_send_msg_to_all':
        if BOARDCATING['admin_requested'] is not None :
            bot.send_message(BOARDCATING['admin_requested'] ,'درخواست ارسال پیام همگانی شما رد شد', reply_markup=botkb.send_user_msg())
        bot.send_message(call.message.chat.id ,'ارسال پیام همگانی لغو گردید' , reply_markup=botkb.send_user_msg())
        bot.delete_message(call.message.chat.id , call.message.message_id)
        BOARDCATING.update({key : None  for key in BOARDCATING.keys()})
        


    if call.data =='send_msg_forwarding':
        Text_4 = ' متنی را که میخواهید برای تمام اعضای ربات فوروارد نمیایید را ارسال نمایید \n ⚠️ با ارسال پیام عمل فوروارد کردن درجا آغاز میشود\n TO-CANCEL : /cancel'
        bot.edit_message_text(Text_4, call.message.chat.id , call.message.message_id)
        bot.register_next_step_handler(call.message , forwardMsgtoAll)



    if call.data =='back_from_send_msg':
        Text_back = 'به قسمت مدیریت یوزر ها خوش امدیدبه قسمت مدیریت یوزر ها خوش امدید'
        bot.edit_message_text(Text_back, call.message.chat.id, call.message.message_id, reply_markup=botkb.manage_users())





def sendMsgSingleUserUserId(message):
    if message.text == '/cancel' or message.text =='/cancel'.upper():
        bot.send_message(message.chat.id, 'برای ارسال پیام به کاربران از گزینه های زیر استفاده نمایید', reply_markup=botkb.send_user_msg())
    else:
        if message.content_type=='text' and  message.text.isdigit():
                user_ = users.objects.get(user_id = int(message.text))
                if  user_:
                    SIND_SINGLE_MSG['user_id'] = message.text
                    bot.send_message(message.chat.id, '📝متن پیام خود را برای ارسال به کاربر مورد نظر ارسال فرمایید\n فرمت های قابل پشتیبانی : متن ، تصویر ، ویدیو\n TO-CANCEL : /cancel')
                    bot.register_next_step_handler(message , sendMsgSingleUserSendMsg)
                else:
                    bot.send_message(message.chat.id , 'کاربری با این نام کاربری پیدا نشد')
        else:
            bot.send_message(message.chat.id , 'فقط ایدی عددی مجاز میباشد\n پیام ارسالی باید به صورت متن باشد')
        return



def sendMsgSingleUserSendMsg(message): 
    if message.text == '/cancel' or message.text =='/cancel'.upper():
        bot.send_message(message.chat.id, 'برای ارسال پیام به کاربران از گزینه های زیر استفاده نمایید', reply_markup=botkb.send_user_msg())
    else:
        if message.content_type in ['text' , 'photo' , 'video']:
            admins_ = admins.objects
            admin_info = admins_.get(user_id = message.from_user.id)
            userGetMsg = SIND_SINGLE_MSG['user_id']
            Text_2 = '✅ پیام شما با موفقیت ارسال گردید'  
            
            if message.content_type =='text':
                
                Text_1 = f'📧شما یک پیام دریافت کردید\nمتن پیام :\n {message.text}\n'
                
                bot.send_message( userGetMsg, Text_1)
                bot.send_message(message.chat.id , Text_2)

            if message.content_type =='photo':
                photo = message.photo[0].file_id
                photo_cap = message.caption if message.caption is not None else ' '
                bot.send_photo(userGetMsg , str(photo) , photo_cap)
                bot.reply_to(message , Text_2 )

            if message.content_type =='video':
                video = message.video.file_id
                video_cap = message.caption if message.caption is not None else ' '
                bot.send_video(userGetMsg , str(video) , caption=video_cap)
                bot.reply_to(message , Text_2)


            if admin_info.is_admin:
                owner_id = admins_.filter(is_owner =1).values('user_id')[0]['user_id']
                owner_msg_single_user_msg = f'یک پیام برای کاربر : {SIND_SINGLE_MSG["user_id"]} \n از طرف ادمین : {admin_info.user_id} با نام {admin_info.admin_name} \nارسال شد'
                bot.send_message(owner_id , owner_msg_single_user_msg)

            time.sleep(2)    
            bot.send_message(message.chat.id, 'برای ارسال پیام به کاربران از گزینه های زیر استفاده نمایید', reply_markup=botkb.send_user_msg())
            clear_dict(SIND_SINGLE_MSG)

        else:
            bot.send_message(message.chat.id , 'امکان ارسال این پیام وجود ندارد تنها فرمت های متن ،تصویر و ویدیو قابل ارسال است')

        
    return




def sendBoardcastingMsgToAll(message):
    if message.text =='/cancel' or  message.text =='/cancel'.upper():
        bot.send_message(message.chat.id, 'برای ارسال پیام به کاربران از گزینه های زیر استفاده نمایید', reply_markup=botkb.send_user_msg())
    else:
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('تایید✅',callback_data='verify_send_msg_to_all'),InlineKeyboardButton('لغو و بازگشت ❌',callback_data='cancel_send_msg_to_all'))
        if message.content_type =='photo':
            BOARDCATING['msg_to_store'] = message.photo
            BOARDCATING['msg_caption'] = message.caption
            BOARDCATING['msg_type'] = 'photo'
        elif message.content_type =='video':
            BOARDCATING['msg_to_store'] = message.video
            BOARDCATING['msg_caption'] = message.caption
            BOARDCATING['msg_type'] = 'video'
        else:
            BOARDCATING['msg_to_store'] = message.text
        
        admins_ = admins.objects
        request_admin = admins_.get(user_id = message.from_user.id)
        owner_id = admins_.filter(is_owner =1).values_list('user_id' , flat=True)[0]
        if request_admin.is_admin and request_admin.user_id == message.from_user.id:
            bot.send_message(request_admin.user_id, 'درخواست شما ثبت شد پس از تایید به اطلاع شما خواهد رسید')
            bot.send_message(owner_id,owner_msg, reply_markup=keyboard)
            BOARDCATING['admin_requested'] = request_admin.user_id
        else:
            owner_msg = f"🔖درخواست ارسال یک پیام همگانی در ربات ثبت شده است\n در صورت تایید گزینه ارسال را بزنید در غیر این صورت گزینه لغو را ارسال نمایید"
            bot.send_message(owner_id ,owner_msg, reply_markup=keyboard)
    return




def forwardMsgtoAll(message):
    if message.text =='/cancel' or  message.text =='/cancel'.upper():
        BOARDCATING.update({key:None for key in BOARDCATING.keys()})
        bot.send_message(message.chat.id, 'برای ارسال پیام به کاربران از گزینه های زیر استفاده نمایید', reply_markup=botkb.send_user_msg())
    else:
        admins_ = admins.objects
        request_admin = admins_.get(user_id = message.from_user.id)
        owner_id = admins_.filter(is_owner =1).values('user_id')[0]['user_id']
        text_msg_status = f'یک پیام همگانی در حال فوروارد برای همه اعضای ربات میباشد '
        if owner_id == message.from_user.id:
            bot.send_message(owner_id ,text_msg_status)
            users_ = users.objects.all()       
            for userId in users_:
                if userId.user_id != owner_id :
                    time.sleep(0.5)
                    bot.forward_message(userId.user_id, message.chat.id , message.message_id)
        else:
            bot.send_message(request_admin.user_id, 'شما امکان فوروارد کردن پیام همگانی را ندارید')
    return









































































"""

# this used to import django in to the code / scripting runing
import django 
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'TeleBot.settings'
django.setup()
prrint('Configured')


"""
@bot.callback_query_handler(func= lambda call : call.data)
def check_call(call):
    print(call.data)




