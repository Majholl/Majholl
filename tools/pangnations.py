from telebot.types import InlineKeyboardButton , InlineKeyboardMarkup

def pangnations(keboard_before , item_per_page , call_data , max_page ,page=1):
    keboard = InlineKeyboardMarkup()

    total_pages = (max_page + item_per_page - 1) // item_per_page

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page-1) * item_per_page
    end = start + item_per_page

    pag_keyboard = []
    for i,ind in enumerate(keboard_before.keyboard,0):
        if start < i <= end:
            pag_keyboard.append(ind)

    keboard.add(*pag_keyboard)
    
    next_prev_buttons =[InlineKeyboardButton(text='صفحه بعدی ⏪' , callback_data =f'{call_data}_{page +1}') , 
                        InlineKeyboardButton(text='صفحه قبل ⏩' , callback_data =f'{call_data}_{page - 1}')]
        
        
    if page == 1 and total_pages > 1:
        keboard.add(next_prev_buttons[0])
    elif page > 1:
        if page < total_pages:
            keboard.add(*next_prev_buttons)
        else:
            keboard.add(next_prev_buttons[1]) 

    return keboard