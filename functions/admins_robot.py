from mainrobot.models import *


def check_admins(userid , panel=None , product=None , bot_static=None , bot_management=None , user_management=None):
    try:
        admin_ = admins.objects.get(user_id=userid)
        
        if panel is not None and admin_ and (admin_.is_owner == 1 or (admin_.is_admin == 1 and admin_.acc_panels == 1)):
            return 'panel_access'
        
        elif product is not None and admin_ and (admin_.is_owner == 1 or (admin_.is_admin == 1 and admin_.acc_products == 1)):
            return 'product_access'
        
        elif bot_static is not None and admin_ and ((admin_.is_owner == 1) or (admin_.is_admin and admin_.acc_staticts == 1)):
            return 'static_access'
        
        elif bot_management is not None and admin_ and ((admin_.is_owner == 1 ) or (admin_.is_admin and admin_.acc_botmanagment ==1 )):
            return 'botmanagement_access'
        
        elif user_management is not None and admin_ and ((admin_.is_owner ==1) or (admin_.is_admin and admin_.acc_users ==1)):
            return 'usermanagment_access'
        
        else:
            return 'no_access'
    
    except admins.DoesNotExist:
        return 'not_admin'