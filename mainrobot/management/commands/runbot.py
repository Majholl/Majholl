from django.core.management.base import BaseCommand
from mainrobot.models import admins , botsettings
import getpass , os , time , main  , colorama


#/run the bot
class Command(BaseCommand):
    def handle(self , *args , **options):
        if not admins.objects.all().exists():
            
            print(colorama.Fore.GREEN + 'Database is Connected' + colorama.Style.RESET_ALL)

            self.stdout.write(self.style.HTTP_INFO('--- Creating Owner Bot !! ----\n \t Notice that this is done for first time next it will be loaded from db'))

            get_user_id = input(self.style.HTTP_INFO('stpe-1 : Send me OWNER user id >>? '))

            get_token_bot = input(self.style.HTTP_INFO('step-2 : Send me your token bot >>?'))

            get_user_passwd = getpass.getpass(self.style.HTTP_INFO('step-6 : Send me a password for owner >>? '))

            confirmation_passwd  = getpass.getpass(self.style.HTTP_INFO('step-7 : Send me password again >>?'))
                
            if get_user_passwd != confirmation_passwd :
                self.stdout.write(self.style.ERROR('Passwords do not match. Exiting...'))
                return
                
            time.sleep(2.5)

            admins.objects.create(user_id = get_user_id , is_admin = 0 , is_owner = 1 , password=get_user_passwd , admin_name ='Owner' , acc_botmanagment=0, acc_panels=0, acc_products=0, acc_admins=0 , acc_users=0, acc_staticts=0)
                
            botsettings.objects.create(wallet_pay = 0 , kartbkart_pay = 0 , forcechjoin = 0 , moneyusrtousr = 0 , irnumber = 0 , newusers_notf = 0 , walletcharge_notf = 0 , moneyusrtousr_notf = 0 , buyservice_notf=0 , tamdidservice_notf=0 , notif_mode = 0 , bot_status = 0)
                
            self.stdout.write(self.style.SUCCESS('Successfully !! Owner bot added to db'))
                
            write_token(get_token_bot)

            time.sleep(2.5)
                
            clear_console()

            main.bot.token = get_token_bot

            main.bot.send_message(get_user_id, 'بات شما با موفقیت نصب شد ✅ \n برای شروع دستور : /start را بفرستید')
                
            self.stdout.write(colorama.Fore.GREEN + '--! Bot is Running !--' + colorama.Style.RESET_ALL)
            main.bot.infinity_polling()
            #main.bot.polling(non_stop=True)
            
        else :
            clear_console()  
            i = 3
            while True:
                if i > 0 :
                    Text = f'Running in : {i}s'
                    text_3 = f'{Text} ...'
                    text_2 = f'{Text} ....'
                    text_1 = f'{Text} .....'
                    texts = text_3 if i ==3  else text_2 if i == 2  else text_1
                    self.stdout.write(colorama.Fore.CYAN + texts + colorama.Style.RESET_ALL)
                    time.sleep(1.5)
                    clear_console()
                    i -=1
                else :
                    break 
                
            time.sleep(2.5)
            clear_console()
                
            self.stdout.write(colorama.Fore.GREEN + '\t --! Bot is Running !-- \t' + colorama.Style.RESET_ALL)
           
            #main.bot.polling(non_stop=True)
            main.bot.infinity_polling()






#/ write token
def write_token(token):
    with open('BOTTOKEN.py' , 'w+') as f:
            f.write(f'TOKEN=["{token}"]')
            f.close()
            return




#/ clear console
def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
