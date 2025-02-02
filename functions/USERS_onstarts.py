from mainrobot.models import users , admins , channels , botsettings
from keybuttons import BotkeyBoard as botkb
import re , jdatetime
from functions.notif import notif_new_user


#handles welcome functions



#= check user existence
def CHECK_USER_EXITENCE(UserId , UserFirstName , UserLastName , UserUserName , UserWallet , bot):
    try: 
        User_check = users.objects.get(user_id = UserId)
        if not User_check :
            return User_check , False   
        
    except users.DoesNotExist:
        User_create = users.objects.create(first_name=UserFirstName , last_name=UserLastName ,
                                           user_id=UserId , username=UserUserName , user_wallet=UserWallet) 
        notif_new_user(bot , UserId)

        return User_create , True 







#= check user in channel or not
def FORCE_JOIN_CHANNEL(UserId, Bot):
    Users_ = users.objects.get(user_id=UserId)
    Channels_ = channels.objects.filter(ch_usage = 'fjch').all()
    botsettings_forcech = botsettings.objects.all()[0].forcechjoin
    state = {}
    
    if botsettings_forcech == 1:  # Check only if force channel join is enabled
        for i in Channels_:
            if i.channel_url: 
                ch_id = Bot.get_chat(str(i.channel_url)).id

            Membership_ = Bot.get_chat_member(i.channel_id or ch_id, Users_.user_id).status
            state[i.channel_id or ch_id] = Membership_
        
        # Check all membership statuses
        for i in Channels_:
            if i.ch_status == 1:  # Check only active channels for forced joining
                if state.get(i.channel_id or ch_id) == 'left':
                    return botkb.load_channels(Bot, UserId)
    
    return True  # User is a member of all required channels or force join is disabled




# check user block or unblock status
def BLOCK_OR_UNBLOCK(UserId):
    users_ = users.objects.get(user_id = UserId)
    if users_.block_status == 1:
        return True
    
    return False



# check phone number 
def PHONE_NUMBER(user_id):
    botsettings_ = botsettings.objects.values_list('irnumber', flat=True).first()
    users_ = users.objects.get(user_id=user_id)

    if botsettings_ == 1 and not users_.phone_number:
        return True
    
    return False




def BOT_STATUS(user_id):
    botsettings_ = botsettings.objects.first()
    admins_ = admins.objects.filter(user_id = user_id , is_owner = 1)

    if botsettings_.bot_status == 0: #// bot is disable
        if admins_:
            return True
            
        return False 


    return True #// bot is enable


