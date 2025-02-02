from mainrobot.models import v2panel , products , panelinbounds , inovices
from keybuttons import BotkeyBoard as botkb
import random , string , json , re
#this is functions that managing producs




# -------------- > Adding-Prodcuts < --------------
def add_product_database(call , bot , productname , productdatalimit , productdateexpire , productprice , panelid , inboundsid ):

    products_obejcts = [i.id for i in products.objects.all()] 
    sortid =max(products_obejcts)+1 if products_obejcts else 1    
    panel_ = v2panel.objects.get(id = int(panelid))
    panelinbounds_ = panelinbounds.objects.get(id = inboundsid)
    try:    
        product_=products.objects.create(product_name=productname , data_limit=productdatalimit ,
                                        expire_date=productdateexpire, product_price=productprice ,
                                        panel_id=panel_ , panelinbounds_id= panelinbounds_ , sort_id =sortid )
        
        Text_2='✅محصول با موفقیت اضافه شد'
        bot.edit_message_text(Text_2 , call.message.chat.id , call.message.message_id , reply_markup=botkb.products_management_menu_keyboard())
                
    except Exception as product_creation:
        print(f'An ERROR occured in [products.py  - LINE 24- FUNC add_product_database] \n\n\t Error-msg :{product_creation}')
        Text_1='❌یک مشکلی در هنگام اضافه کردن محصول به وجود امد\n مجدد امتحان کنید'
        bot.send_message(call.message.chat.id , Text_1)         




# -------------- > Removing_products < --------------

def remove_product_database(bot , call ,  product_id=None , panel_id=None , null_products=None):
    try:
        
        if product_id is not None:
            product_to_remove=products.objects.get(id = product_id)  
            inovice_ = inovices.objects.filter(product_id =product_to_remove)
            if inovice_.count() >=1:
                for updating_inovices in inovice_:
                    updating_inovices.product_id = None
                    updating_inovices.save()

            pro_name = product_to_remove.product_name        
            product_to_remove.delete()
            Text_2=f'محصول با موفقیت  پاک شد ✅\n\n  نام محصول حذف شده  : {pro_name}'
            no_products = botkb.product_managemet_remove_products(panelid=panel_id)
            if no_products =='no_products_to_remove':
                Text_3='📌پنلی را که میخواهید محصولات آن را مدیریت کنید انتخاب نمایید'
                bot.edit_message_text(Text_3 , call.message.chat.id , call.message.message_id , reply_markup=botkb.load_panel_add_product(remove_product=True))
            else: 
                bot.edit_message_text(Text_2 ,call.message.chat.id ,call.message.message_id , reply_markup=botkb.product_managemet_remove_products(panelid=panel_id))


        if null_products is not None:
            null_product_to_remove = products.objects.get(id = null_products)
            Text_4=f'محصول با موفقیت  پاک شد ✅\n\n  نام محصول حذف شده  : {null_product_to_remove.product_name}'
            null_product_to_remove.delete()

            no_products_null = botkb.product_managemet_remove_null_products()
            if no_products_null =='no_null_products_to_remove':
                Text_5='📌پنلی را که میخواهید محصولات آن را مدیریت کنید انتخاب نمایید'
                bot.edit_message_text(Text_5 , call.message.chat.id , call.message.message_id , reply_markup=botkb.load_panel_add_product(remove_product=True))
            else:
                bot.edit_message_text(Text_4 ,call.message.chat.id ,call.message.message_id , reply_markup=botkb.product_managemet_remove_null_products())

    except Exception as remove_product:
        print(f'An ERROR occured in [products.py  - LINE 69- FUNC remove_product_database] \n\n\t Error-msg :{remove_product}')




# -------------- > Managing_products < --------------


# ------------------------- < Product_Status >
def change_product_status(bot , call ,  product_id):
    try :
        product_ = products.objects.get(id = product_id)
        product_new_status = 1 if product_.product_status == 0 else 0 
        product_.product_status = product_new_status
        show_status = '🟢فعال ' if product_.product_status ==1 else "🔴 غیر فعال"
        product_.save() 
        Text_1=f'وضعیت محصول تغییر کرد \n وضعیت فعلی محصول : {show_status}'
        bot.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=botkb.product_changing_details(product_id))

    except Exception as change_product_status:
        print(f'An ERROR occured in [products.py  - LINE 90- FUNC change_product_status] \n\n\t Error-msg :{change_product_status}')
    

# ------------------------- < Product_Name >
def change_product_name(bot , message ,  product_id):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='🖋برای تغییر تنظیمات  محصول بر روی آن کلیک کنید'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.product_changing_details(product_id=product_id))
    else: 
        try: 
            if len(message.text) <= 64: 
                product_ = products.objects.get(id = product_id)
                product_new_name = message.text
                product_.product_name = product_new_name
                product_.save()

                Text_2='🖋برای تغییر تنظیمات  محصول بر روی آن کلیک کنید\n نام محصول تغییر کرد'
                bot.send_message(message.chat.id , Text_2 , reply_markup =botkb.product_changing_details(product_id = product_id))
            else :
                Text_3='اسم محصول نباید بیشتر از ۶۴ حرف یا کرکتر باشد \n مجدد امتحان نمایید'
                bot.send_message(message.chat.id , Text_3)
                bot.register_next_step_handler(message , lambda message : change_product_name(bot , message , product_id))   

        except Exception as change_prodcuct_name :
            print(f'An ERROR occured in [products.py  - LINE 109- FUNC change_product_name] \n\n\t Error-msg :{change_prodcuct_name}')


# ------------------------- < Product_DataLimit >
def change_product_datalimt(bot , message ,  product_id):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='🖋برای تغییر تنظیمات  محصول بر روی آن کلیک کنید'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.product_changing_details(product_id=product_id))
    else:
        try: 
                data_limit_checker = re.search(r'^\d+(\.\d{1,2})?$', message.text)
                if data_limit_checker: 
                    product_=products.objects.get(id = product_id)
                    product_new_datalimit = float(data_limit_checker.group(0))
                    product_.data_limit = product_new_datalimit
                    product_.save()        
                    Text_2='🖋برای تغییر تنظیمات هر محصول بر روی آن کلیک کنید\n حجم محصول تغییر کرد'
                    bot.send_message(message.chat.id , Text_2 ,reply_markup=botkb.product_changing_details(product_id=product_id))   
                else :
                    Text_3='فرمت ارسالی اشتباه میباشد مقادیر اعشاری را امتحان کنید \n مانند : 10.0 یا 20.00\n\nTO-CANCEL : /cancel'
                    bot.send_message(message.chat.id ,Text_3 , reply_markup = botkb.product_changing_details(product_id = product_id))       
                    bot.register_next_step_handler(message , lambda message : change_product_datalimt(bot , message , product_id))   
        except Exception as change_data_limit :
            print(f'An ERROR occured in [products.py  - LINE 137- FUNC change_product_datalimt] \n\n\t Error-msg :{change_data_limit}')

# ------------------------- < Product_Expire >
def change_prdocut_expiredate(bot , message ,  product_id):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='🖋برای تغییر تنظیمات  محصول بر روی آن کلیک کنید'
        bot.send_message(message.chat.id , Text_1 , reply_markup =botkb.product_changing_details(product_id =product_id))
    else :
        try : 
            if message.text.isdigit():
                product_ = products.objects.get(id = product_id)
                product_new_expiredate = message.text
                product_.expire_date = product_new_expiredate
                product_.save()
                Text_2='🖋برای تغییر تنظیمات  محصول بر روی آن کلیک کنید\n دوره محصول تغییر کرد'
                bot.send_message(message.chat.id , Text_2 , reply_markup=botkb.product_changing_details(product_id=product_id))
            else : 
                Text_3='مقدار ورود باید به صورت عدد باشد \n\nTO-CANCEL : /cancel'
                bot.send_message(message.chat.id , Text_3)                        
                bot.register_next_step_handler(message , lambda message : change_prdocut_expiredate(bot , message , product_id))   
        except Exception as change_expire_date :
                print(f'An ERROR occured in [products.py  - LINE 159- change_prdocut_expiredate] \n\n\t Error-msg :{change_expire_date}')


# ------------------------- < Product_Price >
def change_product_price(bot , message , product_id):
    if message.text=='/cancel' or message.text=='/cancel'.upper():
        Text_1='🖋برای تغییر تنظیمات هر محصول بر روی آن کلیک کنید'
        bot.send_message(message.chat.id , Text_1 , reply_markup=botkb.product_changing_details(product_id=product_id))
    else :  
        try : 
            if message.text.isdigit():
                product_ = products.objects.get(id = product_id)
                product_new_product_price = message.text
                product_.product_price = product_new_product_price
                product_.save()
                Text_2='🖋برای تغییر تنظیمات هر محصول بر روی آن کلیک کنید\n قیمت محصول تغییر کرد'
                bot.send_message(message.chat.id , Text_2 , reply_markup = botkb.product_changing_details(product_id = product_id)) 
            else : 
                Text_3='مقدار ورود باید به صورت عدد باشد \n\nTO-CANCEL : /cancel'
                bot.send_message(message.chat.id , Text_3)                        
                bot.register_next_step_handler(message , lambda message : change_product_price(bot , message , product_id))   

        except Exception as change_product_cost:
            print(f'An ERROR occured in [products.py  - LINE 181- change_product_cost] \n\n\t Error-msg :{change_product_cost}')





#- product_inbound 
def change_product_inbound(call , BOT , inbounds):
    if  (inbounds['inbounds'] is not None and call.data in inbounds['inbounds']):
        inbounds_list=inbounds['inbounds']
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
        for i in inbounds['inbounds']:
            if  '✅' in i:
                inbounds_checkmark.append(i.strip('✅'))
            Text_1=f"لیست اینباند های انتخابی:\n\n {inbounds_checkmark}"
        keyboard = botkb.change_inbounds(inbounds_list) 
        BOT.edit_message_text(Text_1 , call.message.chat.id , call.message.message_id , reply_markup=keyboard)


