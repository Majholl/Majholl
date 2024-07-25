
<p align="center">
<strong >ربات فروشگاهی اشتراک های V2RAY </strong></br>
</p>
<hr>

<p>ربات هنوز به صورت کامل اماده نشده وهنوز در حال کد نویسی میباشد </p>
<p> شما میتونید هر نسخه ای از سورس کد رو که داخل گیت هاب قرار میدیدم رو ،‌ روی سیستم و یا روی سرور  شخصیتون کلون کنید و ران کنید  </p>

<br>
</hr>

</hr>


# ✅پنل های سازگار 
<ul>
    <li>
        این ربات با آخرین api پنل مرزبان هماهنگی دارد .
    </li>
    <li>
     .پنل سنایی به زودی اضافه خواهد شد 
    </li>
    - 🔗باقی پنل ها بر اساس درخواست های شما اضافه خواهد شد .

</hr>

## 🔖امکانات 
- فروش آسان اشتراک های v2ry
- استفاده آسان از ربات و کاربری راحت
- امکان شخصی سازی همه اجزای ربات
- امکان مدیریت اشتراک توسط یوزر 
- امکان تمدید اشتراک توسط یوزر
- امکان مدیریت پنل های v2ray  به همراه دسترسی بالا
- امکان مدیریت محصولات و شخصی سازی آنها  
- امکان احراز هویت افراد 
- جوین اجباری تک چنلی و چند چنلی 
- مدیریت راحت کاربران داخل ربات
- مدیریت کد تخفیف با تنوع بالای امکانات
- امکان خاموش و روشن کردن اجزای مختلف بات به دلخواه 
- امکان مدیریت دسترسی ادمین ها به بخش های مختلف ربات (⚠️به صورت کامل پیاده سازی نشده⚠️)
- ارائه آمار حرفه ای از ربات ، پنل ها و یوزر ها و محصولات (⚠️ به صورت کامل پیاده سازی نشده⚠️)
- امکان مدیریت نحوه پرداخت توسط اونر ربات (⚠️ به صورت کامل پیاده سازی نشده⚠️)
- 
- ارائه پنل وب برای اونر ربات برای مدیریت و دسترسی راحت  ( 📌 بعد از ارائه ورژن اول ربات اضافه خواهد شد )
- ارائه پنل وب برای مشتریان برای خرید و مدیریت اشتراک  ( 📌 بعد از ارائه ورژن اول ربات اضافه خواهد شد )
- پیاده سازی api ربات برای افراد دولوپر ( 📌 بعد از ارائه ورژن اول ربات اضافه خواهد شد )


<hr>

### 🎛 چگونه اجرا کنیم‌؟
- [ویندوز 🖥](####ویندوز)
- [لینوکس 💻](#####لینوکس)
<hr>

####  1️⃣ ویندوز

1- برای اجرا در ویندوز کافیست آخرین نسخه پایتون را از صفحه رسمی آن دانلود و نصب کنید

<a href='https://www.python.org/'>سایت رسمی پایتون </a>

2- سپس در داخل cmd خود دستور زیر را زده و یک محیط venv بسازید 

```bash 
 pip -m venv myvenv
 ```
3- بعد از ساخت محیط venv نیاز به فعال سازی محیط venv هست 

```bash 
./myvenv/Scripts/activate
```
4- در این مرحله شما نیاز به نصب zampp یا mysql client دارید که میتونید از سایت اونها دانلودشون کنید

5- و در نهایت با زدن دستور زیر در محیط venv پروژه رو کلون کنید

```bash 
git clone https://github.com/Noskheh/Majholl.git
```

6- با زدن دستور های زیر اقدام به ران کردن ربات کنید 
```bash 
python manage.py makemigrations 
python manage.py migrate 
python manage.py runbot
```
- ⚠️ توکن ربات رو باید به صورت دستی و داخل فایل زیر قرار بدید 
```bash 
BOTTOKEN.py
```

- این اموزش ممکنه ناقص باشه در اینده بروزرسانی میکنم 


<hr>

##### 2️⃣ لینوکس 
⚠️ بزودی 