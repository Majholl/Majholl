from mainrobot.models import users,  v2panel ,panelinbounds , products , shomarekart , subscriptions 
import random , jdatetime , json
from django.db.models import Sum , Avg , Max , Min , Count
#-all editable messages 


#This is message when user send (/start)
welcome_msg = 'سلام به ربات ما خوش امدید😍🫠\n  فروشگاه ما به صورت ۲۴ ساعته اماده پشتیبانی از نیاز های شماست ❤️🙏🏻\n/start'


#Force user join channel 
force_channel_join_msg=f'♨️پیش از ادامه کار با ربات لطفا در چنل های ما جوین شوید'




#buy service section 
buy_service_section_product_msg = '✏️محصولی که میخواهید را انتخاب نمایید'
buy_service_section_choosing_panel_msg = '✏️سروری را که میخواهید انتخاب نمایید'
buy_service_section_choosing_username_msg = 'سرویس مورد نظر شما انتخاب شد ✅ \n 🟡 لطفا یک نام کاربری برای اشتراک خود انتخاب نمایید . \n   🔸نام کاربری باید به صورت حروف و اعداد اینگلیسی باشد \n نمونه : \n ali - ali_x - ali1234 \n TO-CANCEL : /cancel'




def product_info_msg(productinfo):
    product_ = products.objects.get(id = int(productinfo['product_id']))

    product_info_msg = f"""
<b>╮ ✣ سرویس شما انتخاب شد ✣ ╭</b>

┐<b>👤 نام کاربری</b>: <code>{productinfo['config_name']}</code>

 ┊─<b>🌐 نام سرور</b>: {product_.panel_id.panel_name}
 ┊─<b>📎 نام محصول</b>: {product_.product_name}
 ┊─<b>⌛️ زمان محصول</b>: {product_.expire_date} روز 
 ┊─<b>🔋 حجم محصول</b>: {int(product_.data_limit)} گیگ 
 ┊─<b>💸 قیمت محصول</b>: {format(int(product_.product_price) , ',')} تومان

┘ <b> در صورت تایید گزینه (تایید محصول✅) را زده و در صورت عدم تایید گزینه بازگشت را بزنید </b>

"""
    return product_info_msg

  






paied_msg = '✅پرداخت شما با موفقیت انجام شد \n محصول در حال اماده سازی و ارسال میباشد'




def buy_service_section_product_send(link_kind ,config_name , link=None , image_only=None):
    buy_service_section_product_send = f"""
┐🛍محصول شما حاضر شد
 ─🧷نوع لینک : {link_kind}
 ─✏️ نام اکانت:‌  <code>{config_name}</code>
┘  لینک شما :‌ \n<code>{link}</code> 
"""
    
    if image_only is not None:
        buy_service_section_product_image_send = f"""
┐🛍محصول شما حاضر شد
 ─🧷نوع لینک : <code>{link_kind}</code>
 ─✏️ نام اکانت:‌ {config_name}
""" 
        return buy_service_section_product_image_send
        
    return buy_service_section_product_send



def buy_service_section_cardtocard_msg(cost , user_basket = None): 
    bank = None
    bank_active_status = []
    try :
        shomarekart_ = shomarekart.objects.filter(bank_inmsg = 1)
        if len(shomarekart_) >= 1 :
            for i in shomarekart_:
                if i.bank_status == 1:
                    bank_active_status.append(i)
        else:
            return 'هیچ شماره کارت فعالی وجود نداره'
            
        if len(bank_active_status) >= 1:        
            random_shomarekart = random.choice(bank_active_status)
            bank = random_shomarekart
        else:
            bank = None

        if bank : 
            bank_kard = bank.bank_card
            bank_owner = bank.ownername
            bank_name = bank.bank_name
            kard = [str(bank_kard)[i : i+4] for i in range(0 , len(str(bank_kard)) , 4)]
            if user_basket is not None :
                user_basket['card_used'] = shomarekart.objects.get(bank_card = bank_kard)
            buy_service_section_card_to_card_msg = f"""
╮ برای  تکمیل خرید خود و دریافت لینک اشتراک خود  ╭

┤ 💸مبلغ : {format(cost , ',')}
به این شماره کارت واریز کرده و سپس فیش واریزی را همین جا ارسال کنید
▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐
               
┐  💳شماره کارت :‌  <code>{(",".join(kard))}</code>

─ ✍🏻 نام صاحب کارت : {bank_owner if  bank_owner is not None else ''}

 ┘  🏦بانک عامل : {bank_name if bank_name is not None else ''}

▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐
- لطفا از اسپم کردن پرهیز نمایید⚠️
┤ از ارسال رسید فیک اجتناب فرمایید ⚠️
- هرگونه واریزی اشتباه بر عهده شخص میباشد⚠️

TO-CANCEL : /cancel
.
"""
            
            return buy_service_section_card_to_card_msg
            
        else : 
            return 'هیچ شماره کارت فعالی وجود ندارد'

    except shomarekart.DoesNotExist as shomarekart_error :
        print(f'An ERROR occured in [bottext.py  - LINE 93-144 - FUNC buy_service_section_cardtocard_msg] \n\n\t Error-msg :{shomarekart_error}')


inovice_time_passed_msg = 'این صورت حساب باطل شده است مجدد صادر فرمایید \n تمامی صورت حساب هایی که ۳۰ دقیقه از مدت زمان انها گذشته باشند به صورت خودکار باطل خواهند شد'




def send_user_buy_request_to_admins(user_basket , user_info , tamdid:bool = False):
    info = user_basket
    product_ = products.objects.get(id =user_basket['product_id'])
    panel_ = v2panel.objects.get(id = product_.panel_id.pk)
    header_text = '【✣ درخواست خرید جدید در سیستم ثبت شده است ✣】' if tamdid is False else '【✣ درخواست تمدید سرویس در سیستم ثبت شده است ✣】'
    
    send_user_buy_request_to_admins = f'''
{header_text}
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
┐🧷نام اکانت : <code>{info['config_name']}</code>

┊──👤 ایدی عددی : {user_info.user_id}
┊──#️⃣ یوزرنیم تلگرام :‌ @‌{user_info.username}
┊──💰موجودی کیف پول :‌ {format(int(user_info.user_wallet) , ",")} تومان
┊──💸مبلغ خرید : {format(int(product_.product_price), ',')} تومان
┊──🔗نام محصول : {product_.product_name}

┘🔖 نام سرور : {panel_.panel_name}

¦─ در صورت تایید گزینه تایید پرداخت ✅ را بزنید در غیر این صورت رد پرداخت ❌  را بزنید
'''
    return send_user_buy_request_to_admins
 




send_success_msg_to_user= '👨🏻‍💻درخواست شما برای ادمین صادر شد در صورت تایید به اطلاع شما خواهد رسید \n  —🔸 پردازش درخواست شما ممکن است مدتی طول بکشید در این صورت از ارسال مجدد درخواست خودداری کنید❌'






def user_service_status(configname : str , request_sub = None):
    subscriptions_ = subscriptions.objects.get(user_subscription = configname)
    sub_name = subscriptions_.user_subscription

    if request_sub['expire'] is not None:
        expiredate = str(jdatetime.datetime.fromtimestamp(request_sub["expire"]).strftime('%H:%M:%S-%Y/%m/%d'))
        expire_date = expiredate if request_sub is not None else "-"
    else:
        expire_date = 'این اشتراک لایف تایم میباشد'

    if subscriptions_.product_id:
        product_name = subscriptions_.product_id.product_name 
        expire = str(subscriptions_.product_id.expire_date)
        product_price = format(subscriptions_.product_id.product_price , ',')
    else:
        product_name , expire , product_price = "-" , "-" , "-"

   
    if subscriptions_:
        Text =f"""
👀 وضعیت فعلی سرویس شما

── نام اشتراک : <code>{sub_name}</code>
   ↲ 💬نام بسته :‌ {product_name}
   ↲ 📅مدت زمان : {expire} روز
   ↲  💰قیمت محصول : {product_price} تومان

── تاریخ انقضا : {expire_date}

برای حذف کردن اشتراک از لیست خود:/rm_mysub_{subscriptions_.pk}

"""
        return Text
    
    else:
        return 'هیچ اطلاعاتی برای نمایش وجود ندارد'
    



def sub_link_user_service(user_sub_link):
    Text = f"""
─🧷نوع لینک : لینک هوشمند 
این لینک به صورت هوشمند میباشد و حاوی کانفیگ های اشتراک شما به همراه دیگر جزییات میباشد

<code>{user_sub_link}</code>
"""
    return Text







text_not_inmy_list =f"""
🚦برای اضافه کردن اشتراک خود در ربات یا دسترسی به اشتراک خود به دو طریق میتوانید عمل کنید

── 1️⃣ ارسال لینک هوشمند اشتراک 
    - در این روش دقت کنید که لینک کانفیگ را ارسال نکنید و تنها لینک هوشمندی که ابتدای آن دارای (https / http) هست را ارسال کنید

── 2️⃣ ارسال نام دقیق اشتراک 
    - در این روش نام اشتراک خود را ارسال نمایید . این نام همان نامی است که در هنگام خرید اشتراک وارد نمودید 

TO-CANCEL : /cancel
"""

userid_text = lambda userid : f'✤ - پروفایل من : \n  ┘ - آیدی عددی :‌ <code>{userid}</code>'
username_text = lambda useranme : f'✤ - پروفایل من :\n  ┘ - یوزرنیم : {useranme}'








def charge_wallet_txt(userid , amount):
    user_ = users.objects.get(user_id = userid)
    userwallet = format(int(user_.user_wallet) , ',')
    amount = format(int(amount) , ',')
    Text = f"""
【✣ درخواست شارژ کیف پول در سیستم ثبت شده است ✣】
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

┊──👤: ایدی عددی : <code>{user_.user_id}</code>
┊──#️⃣ یوزرنیم تلگرام :‌ @‌{user_.username}
┊──💰موجودی کیف پول :‌ {userwallet} تومان
┊──💸مبلغ شارژ : {amount} تومان

¦─ در صورت تایید گزینه تایید پرداخت ✅ را بزنید در غیر این صورت رد پرداخت ❌  را بزنید
"""
    return Text







def inbound_info(inboundid):
    panelinbounds_ = panelinbounds.objects.get(id= inboundid)
    text =f"""
┊──🏷نام اینباند : {panelinbounds_.inbound_name}
┊──📡پنل متصل : {panelinbounds_.panel_id.panel_name}

┊──🗳اینباند ها : 
{json.loads(panelinbounds_.inbounds_selected)}

""" 
    return text



text_transfer_money_to_usr = lambda amount , usr_id , usr_wallet : f'✅مبلغ مورد نظر با موفقیت انتقال یافت \n- شما مبلغ {amount} به شماره ایدی  {usr_id} ارسال کردید . \n - موجودی فعلی کیف پول شما : {usr_wallet} تومان'
text_transfer_money_to_usr_2 = lambda amount : f'💝 مبلغ {amount} به کیف پول شما منتقل شد\n - این انتقال توسط شخص  دیگری برای شما انجام شده است .'





bot_management_fisrt_TEXT = f"""<code> - به تنظیمات ربات خوش آمدید  - </code>

در این قسمت مدیریت کردن بخش های مختلف زیر امکان پذیر است 

¦- نحوه پرداخت +‌ مدیریت شماره کارت ها 
¦- مدیریت چنل های جوین اجباری 
¦- نحوه ارسال وقایع + تنظیم چنل ارسال وقایع 
.
"""



bot_management_second_TEXT= f'در این قسمت شما میتوانید نحوه پرداخت‌ها و همچنین شماره کارت‌ها را مدیریت کنید .'






bot_management_shomare_kart_TEXT_1 = f"""
<code>- به مدیریت شماره کارت خوش آمدید - </code>

در این قسمت مدیریت کردن بخش های مختلف زیر امکان پذیر است 

¦- مدیریت کردن شماره کارت‌ها + حذف شماره کارت + فعال /غیرفعال کردن 
¦-اضافه کردن شماره کارت 
.
"""



bot_management_shomare_kart_TEXT_2 = lambda bnk_status,bnk_owner,bnk_name,bnk_number,bnk_inuse , number_of_time_used: f"""
- در حال مشاهده و مدیریت کردن شماره کارت میباشید -

┐ - 📊وضعیت کارت :‌ {bnk_status}

┊─  👤نام صاحب کارت : {bnk_owner}
┊─  🏦 نام بانک : {bnk_name}
┊─  💳شماره کارت : {','.join([str(bnk_number)[i : i+4] for i in range(0 , len(str(bnk_number)) , 4)])}
┊─ #️⃣ تعداد استفاده شده در پرداخت ها : {number_of_time_used}

┘ - 💸وضعیت استفاده در پرداخت‌ها : {bnk_inuse}

<blockquote>⚠️ ⚠️ درصورتی که چندین شماره کارت به صورت فعال و استفاده در پرداخت‌ها باشد 
ربات به صورت سیستمی یکی از شماره کارت های فعال را به صورت رندوم (اتفاقی) عنوان شماره کارت برای هر  پرداخت انتخاب مینماید 
</blockquote>.
    """


bot_management_shomare_kart_TEXT_3 = f"""
<code>- به مدیریت شماره کارت خوش آمدید - </code>

در این قسمت مدیریت کردن بخش های مختلف زیر امکان پذیر است 

¦- مدیریت کردن شماره کارت‌ها + حذف شماره کارت + فعال /غیرفعال کردن 
¦-اضافه کردن شماره کارت 
.
"""
    



bot_management_join_ch_Text_1 = f"""
<code>- به مدیریت چنل‌های جوین اجباری خوش آمدید - </code>

در این قسمت مدیریت کردن بخش های مختلف زیر امکان پذیر است 

¦- مدیریت کردن چنل‌ها + حذف چنل‌ها + فعال /غیرفعال کردن 
¦-اضافه کردن  چنل‌ جدید
.
"""



bot_management_join_ch_Text_2 = lambda ch_status,ch_name,ch_url,ch_id : f"""
- شما در حال مشاهده و مدیریت کردن چنل جوین اجباری میباشید -

┐ - 📊وضعیت چنل :‌ {ch_status}

┊─🔈 نام چنل : {ch_name}
┊─🔗ادرس چنل : {ch_url}

┘ - #️⃣ایدی عددی چنل : {ch_id}

<blockquote>⚠️⚠️ دقت کنید که در صورتی که وضعیت چندین چنل به صورت فعال باشد همه چنل ها در جوین اجباری نمایش داده خواهد شد </blockquote>

"""



bot_management_join_ch_Text_3 = f"""
- در این مرحله برای وارد کردن صحیح چنل در ربات نکات زیر را مورد توجه قرار دهید - 

<blockquote> حتما ربات را در کانال هایی که اضافه میکند به صورت 
add as administrator 
اضافه کنید تا ربات بتواند کنترل جوین اجباری چنل را به صورت صحیح انجام دهد 
</blockquote>

<b> 1️⃣ روش  اول (پیشنهادی) </b>:‌ برای اینکه چنل به صورت صحیح وارد ربات شود و در عملکرد ربات اخلال ایجاد نکنید<b> یک پیام از چنل</b>را وارد ربات زیر یا هر رباتی با عملکرد یکسان با ربات زیر کنید 

#️⃣ @userinfobot 

در جواب پیام شما پیامی با محتوای زیر نمایش داده میشود 
Id: -1002148064457
Title: Dev-ch
که قسمت عددی آن به صورت -1002148064457 میباشد را ارسال نمایید تا ثبت شود ✅


2️⃣ روش دوم‌: در این روش ایدی عمومی کانال (نه لینک خصوصی ) را به همراه @ ارسال کنید تا ثبت شود ✅
نمونه : @channel

TO-CANCEL : /cancel
.
"""



bot_management_join_ch_Text_4 =f"""
<code>- به مدیریت چنل‌های جوین اجباری خوش آمدید - </code>

در این قسمت مدیریت کردن بخش های مختلف زیر امکان پذیر است 

¦- مدیریت کردن چنل‌ها + حذف چنل‌ها + فعال /غیرفعال کردن 
¦-اضافه کردن  چنل‌ جدید

.
"""



bot_management_join_ch_Text_5 = f"""
- در این مرحله برای وارد کردن صحیح چنل در ربات نکات زیر را مورد توجه قرار دهید - 

<blockquote> حتما ربات را در کانال هایی که اضافه میکند به صورت 
add as administrator 
اضافه کنید تا ربات بتواند کنترل جوین اجباری چنل را به صورت صحیح انجام دهد 
</blockquote>

<b> 1️⃣ روش  اول (پیشنهادی) </b>:‌ برای اینکه چنل به صورت صحیح وارد ربات شود و در عملکرد ربات اخلال ایجاد نکنید<b> یک پیام از چنل</b>را وارد ربات زیر یا هر رباتی با عملکرد یکسان با ربات زیر کنید 

#️⃣ @userinfobot 

در جواب پیام شما پیامی با محتوای زیر نمایش داده میشود 
Id: -100000000000
Title: Dev-ch
که قسمت عددی آن به صورت -100000000000 میباشد را ارسال نمایید تا ثبت شود ✅


2️⃣ روش دوم‌: در این روش ایدی عمومی کانال (نه لینک خصوصی ) را به همراه @ ارسال کنید تا ثبت شود ✅
نمونه : @channel

TO-CANCEL : /cancel
.
"""



bot_management_log_ch_Text_1 = f"""
- در این مرحله برای وارد کردن صحیح چنل در ربات نکات زیر را مورد توجه قرار دهید - 

<blockquote>
این چنل برای ارسال وقاع مختلف در داخل ربات میباشد 
</blockquote>
برای اینکه چنل به صورت صحیح وارد ربات شود و در عملکرد ربات اخلال ایجاد نکنید یک پیام از چنل را وارد ربات زیر یا هر رباتی با عملکرد یکسان با ربات زیر کنید 
#️⃣ @userinfobot 

در جواب پیام شما پیامی با محتوای زیر نمایش داده میشود 
Id: -100000000000
Title: Dev-ch
که قسمت عددی آن به صورت -100000000000 میباشد را ارسال نمایید تا ثبت شود ✅

TO-CANCEL : /cancel
    """



def getUserOperationsCashs_1(userId):
    users_ = users.objects.get(user_id = userId) 
    Text= f'''
عمل انتخابی خود را انتخاب نمایید 

👤: <code> {str(users_.user_id)} </code>
┊─  نام کاربری :‌{str(users_.first_name) } {str(users_.last_name)}
┊─  یوزر نیم : @{str(users_.username)}
┊─ موجودی کیف پول : {str(format(int(users_.user_wallet) , ','))}

.
'''
    return Text

getUserOperationsCashs_2 = lambda amnt:  f"""
┊─ مبلغ : {str(amnt)} تومان
به کیف پول شما اضافه شد ✅
.
"""

getUserOperationsCashs_3 = lambda amnt : f"""
┊─ مبلغ : {str(amnt)} تومان
به کیف پول شما کسر شد 
.
"""



botStatics_1 =  lambda user_ , v2panel_ , product_ , payment_ , inovices_ : f"""
    آمار ربات به صورت زیر میباشد
👤 تعداد کل یوزر های ربات: {user_}
🎛 تعداد کل پنل های متصل به ربات: {v2panel_}
🔖تعداد کل محصولات ربات : {product_}
🛍 تعداد کل پرداختی ها : {payment_}
📃 تعداد کل فاکتور های صادر شده : {inovices_}
"""


botStatics_2 = lambda users_ :  f"""
    📊- آمار کاربران 

── تعداد کل کاربران : {users_.all().count()} نفر
── تعداد کاربران بلاک شده : {users_.filter(block_status =1).count()} نفر 
── کل موجودی کیف پول کاربران : {format(int(users_.all().aggregate(Sum('user_wallet'))['user_wallet__sum']) , ',')} تومان
── بیشترین موجودی کیف پول کاربران : {format(int(users_.all().aggregate(Max('user_wallet'))['user_wallet__max']) ,',')} تومان

╣ - کاربران دارای بیشترین موجودی -

"""
            

botStatics_3 = lambda products_ : f"""
    📊- آمار محصولات

── تعداد کل محصولات : {products_.all().count()} عدد
── کمترین قیمت محصول : {format(products_.all().aggregate(Min('product_price'))['product_price__min'],',')} تومن
── بیشترین قیمت محصول : {format(products_.all().aggregate(Max('product_price'))['product_price__max'], ',')} تومن
── کمترین حجم محصول : {int(products_.all().aggregate(Min('data_limit'))['data_limit__min'])} گیگ
── بیشترین حجم محصول : {int(products_.all().aggregate(Max('data_limit'))['data_limit__max'])} گیگ

╣ - بیشترین محصولات فروش رفته - 
"""           

botStatics_4 = lambda panels_ : f"""
    📊- آمار پنل ها 

── تعداد کل پنل ها :‌ {panels_.all().count()}
── تعداد اشتراک های هر پنل: 
"""

botStatics_5 = lambda inovices_ :  f"""
    📊- آمار فاکتورها

── تعداد کل فاکتورها صادر شده : {inovices_.aggregate(Count('id'))['id__count']} عدد
── تعداد فاکتورها تمدید شده : {inovices_.filter(kind_pay ='Tamdid').aggregate(Count('id'))['id__count']} عدد
── تعداد فاکتورها اولین خرید  : {inovices_.filter(kind_pay = 'Buy').aggregate(Count('id'))['id__count']} عدد
── کل قیمت فاکتورها صادر شده : {format(int(inovices_.aggregate(Sum('product_price'))['product_price__sum']) ,',')} تومان
── کل حجم فاکتورها صادر شده : {inovices_.aggregate(Sum('data_limit'))['data_limit__sum']} Gb

╣ - بیشترین محصولات فاکتور شده - 
    """




botStatics_6 = lambda payments_ :  f"""
    📊- آمار پرداخت‌ها 

── تعداد کل پرداختی ها  : {payments_.aggregate(Count('id'))['id__count']} عدد
── تعداد کل پرداختی های موفق : {payments_.filter(payment_status ='accepted').aggregate(Count('id'))['id__count']} عدد
── تعداد کل پرداختی های ناموفق  : {payments_.filter(payment_status ='declined').aggregate(Count('id'))['id__count']} عدد
── کل پرداختی های موفق  : {format(int(payments_.filter(payment_status ='accepted').aggregate(Sum('amount'))['amount__sum']), ',')} تومان
.
"""