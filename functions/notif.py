from mainrobot.models import users , v2panel , products ,  admins , botsettings , channels
import datetime , jdatetime , time
from keybuttons import BotkeyBoard as botkb







# ------------------------- < Newuser-Notif > 
def notif_new_user(bot , userid : int = None):
    user_ = users.objects.get(user_id = userid)
    botsetting_ = botsettings.objects.values('newusers_notf')[0]['newusers_notf']
    created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S') 

    Text = f"""
🎊 یک کاربر جدید به ربات اضافه شد

▼ ایدی عددی : ‌{user_.user_id}
 • نام کاربری :  @{user_.username}
 • تاریخ عضویت‌ : {created_date}
.

"""
    if botsetting_ == 1 :
        logchannel = channels.objects.filter(ch_usage = 'logc')
        if  logchannel :
            if logchannel[0].ch_status == 1  :
                bot.send_message(logchannel[0].channel_id , Text , reply_markup= botkb.verfying_on_fist_join(user_.user_id))
        else :
            admins_to_notf = admins.objects
            botsettings_ = botsettings.objects.first()
            if botsettings_.notif_mode == 0 :
                ownerid = admins_to_notf.filter(is_owner = 1)
                bot.send_message(ownerid[0].user_id , Text , reply_markup= botkb.verfying_on_fist_join(user_.user_id))
            else:
                for id in admins_to_notf.all():
                    bot.send_message(id.user_id , Text , reply_markup= botkb.verfying_on_fist_join(user_.user_id))









# ------------------------- < verifyNumber-Notif > 
def notif_verify_number(bot , userid:int=None):

    user_ = users.objects.get(user_id = userid)
    botsetting_ = botsettings.objects.values('verifynumber_notf')[0]['verifynumber_notf']
    created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S') 

    Text = f"""
کاربر زیر احراز هویت با شماره تلفن شد ✅

▼ ایدی عددی : ‌{user_.user_id}
 • نام کاربری : @{user_.username}
 • شماره تلفن: {user_.phone_number}
.
"""
    if  botsetting_ == 1 :
        logchannel = channels.objects.filter(ch_usage = 'logc')
        if  logchannel :
            if logchannel[0].ch_status == 1  :
                bot.send_message(logchannel[0].channel_id , Text)
        else :
            admins_to_notf = admins.objects
            botsettings_ = botsettings.objects.first()
            if botsettings_.notif_mode == 0 :
                ownerid = admins_to_notf.filter(is_owner = 1)
                bot.send_message(ownerid[0].user_id , Text)
            else:
                for id in admins_to_notf.all():
                    bot.send_message(id.user_id , Text)












# ------------------------- < BuyService-Notif > 
def notif_buy_new_service(bot , userid : int = None , productid : int = None , config_name : str = None  , tamdid = None):
    user_ = users.objects.get(user_id = userid)
    product_ = products.objects.get(id = productid)
    values_botsetting = 'buyservice_notf' if tamdid is None else 'tamdidservice_notf'
    botsetting_ = botsettings.objects.values(values_botsetting)[0][values_botsetting]
    created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S') 

    header_title = '🔄 یک تمدید سرویس انجام شد' if tamdid is not  None and tamdid is True else '🛍یک خرید جدید انجام شد'

    Text = f"""
{header_title}
┐ ایدی عددی: <code>{user_.user_id}</code>
  ↲👤 نام کاربری: @{user_.username}
   ↲👝 موجودی کیف پول: {str(format(int(user_.user_wallet) , ','))} تومان 

 ▬📡نام محصول: {product_.product_name}
 ▬🎛نام پنل: {product_.panel_id.panel_name}
 ▬💰‌قیمت محصول: {str(format(int(product_.product_price) , ','))} تومان
 ▬📅 تاریخ خرید: {created_date}

┘ نام اکانت: ‌‌<code>{config_name}</code>
"""
    if  botsetting_ == 1 :
        logchannel = channels.objects.filter(ch_usage = 'logc')
        if  logchannel :
            if logchannel[0].ch_status == 1  :
                bot.send_message(logchannel[0].channel_id , Text)
        else :
            admins_to_notf = admins.objects
            botsettings_ = botsettings.objects.first()
            if botsettings_.notif_mode == 0 :
                ownerid = admins_to_notf.filter(is_owner = 1)
                bot.send_message(ownerid[0].user_id , Text)
            else:
                for id in admins_to_notf.all():
                    bot.send_message(id.user_id , Text)







def notif_charge_wallet(bot , userid , chargeamount , user_oldwallet):
    user_ = users.objects.get(user_id = userid)
    charge = str(format(int(chargeamount) , ','))
    created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    user_pld_wallet = format(int(user_oldwallet) , ',')

    Text_charge_wallet_notf = f"""
💰 یک کاربر شارژ کیف پول انجام شد

┐ ایدی عددی: {user_.user_id}
   ↲👤 نام کاربری: @{user_.username}
    ↲👝 موجودی کیف پول: {user_pld_wallet} تومان

 ▬ 💸مبلغ شارژ : {charge} تومان
 ▬ 📆تاریخ شارژ : {created_date}
.
"""
    if botsettings.objects.values('walletcharge_notf')[0]['walletcharge_notf'] == 1 :
        logchannel = channels.objects.filter(ch_usage = 'logc')
        if logchannel:
            if logchannel[0].ch_status == 1  :
                bot.send_message(logchannel[0].channel_id, Text_charge_wallet_notf)
        else :
            admins_to_notf = admins.objects
            botsettings_ = botsettings.objects.first()
            if botsettings_.notif_mode == 0 :
                ownerid = admins_to_notf.filter(is_owner = 1)
                bot.send_message(ownerid[0].user_id , Text_charge_wallet_notf)
            else:
                for id in admins_to_notf.all():
                    bot.send_message(id.user_id , Text_charge_wallet_notf)








def notif_transfer_wallet(bot , userid_transferer , userid_transfered , chargeamount):
    user_id_transferer = users.objects.get(user_id = userid_transferer)
    user_id_transfered = users.objects.get(user_id = userid_transfered)

    charge = str(format(int(chargeamount) , ','))

    created_date = jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    user_id_transferer_wallet = format(int(user_id_transferer.user_wallet) , ',')
    user_id_transfered_wallet = format(int(user_id_transfered.user_wallet) , ',')
    
    Text_charge_wallet_notf = f"""
📥یک کاربر مبلغ کیف پول را به حساب کاربر دیگری واریز نمود
مشخصات منتقل کننده :
┐🙎🏻‍♂️ ایدی عددی: {user_id_transferer.user_id}
   ↲👤 نام کاربری: @{user_id_transferer.username}
   ↲👝 موجودی کیف پول: {user_id_transferer_wallet} تومان

مشخصات گیرنده :‌
┐🙋🏻‍♂️ ایدی عددی: {user_id_transfered.user_id}
   ↲👤 نام کاربری: @{user_id_transfered.username}
   ↲👝 موجودی کیف پول: {user_id_transfered_wallet} تومان

 ▬ 💸مبلغ شارژ : {charge} تومان
 ▬ 📆تاریخ شارژ : {created_date}
.
"""
    
    if botsettings.objects.values('moneyusrtousr_notf')[0]['moneyusrtousr_notf'] == 1 :
        logchannel = channels.objects.filter(ch_usage = 'logc')
        if logchannel:
            if logchannel[0].ch_status == 1:
                bot.send_message(logchannel[0].channel_id, Text_charge_wallet_notf)   
        else:
            admins_to_notf = admins.objects
            botsettings_ = botsettings.objects.first()
            if botsettings_.notif_mode == 0 :
                ownerid = admins_to_notf.filter(is_owner = 1)
                bot.send_message(ownerid[0].user_id , Text_charge_wallet_notf)
            else:
                for id in admins_to_notf.all():
                    bot.send_message(id.user_id , Text_charge_wallet_notf)


