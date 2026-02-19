"""
SocialPay Web App v3.0
- OTP Email Verification
- 3 Languages: English, Arabic, Hausa
- Auto Admin Account
- PalmPay-style Mobile UI
- Full Admin & User Features

Install: pip install flask
Run: python app.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json, os, hashlib, secrets, smtplib, random, string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

_HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            template_folder=os.path.join(_HERE, "templates"),
            static_folder=os.path.join(_HERE, "static"))
app.secret_key = os.environ.get("SECRET_KEY", "socialpay_secret_key_2024_xk9z")

# ============================================================
# CONFIG
# ============================================================
APP_NAME = "SocialPay"
VERSION = "3.0"

# EMAIL CONFIG (Gmail SMTP)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "socialpay.app.ng@gmail.com"
EMAIL_PASS = "qjpu jvtt kyat xlmx"
EMAIL_FROM = f"{APP_NAME} <{EMAIL_USER}>"

# AUTO ADMIN ACCOUNT (created automatically on first run)
ADMIN_EMAIL = "socialpay.app.ng@gmail.com"
ADMIN_PASSWORD = "@ Ahmerdee4622"
ADMIN_NAME = "SocialPay Admin"

# OTP Settings
OTP_EXPIRE_MINUTES = 10

# ============================================================
# DATA DIRECTORY (absolute paths for Railway/production)
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "logs"), exist_ok=True)

def dp(f): return os.path.join(DATA_DIR, f)

USERS_FILE       = dp("users.json")
WALLETS_FILE     = dp("wallets.json")
TASKS_FILE       = dp("tasks.json")
SUBMISSIONS_FILE = dp("submissions.json")
BANK_FILE        = dp("bank_details.json")
WITHDRAWALS_FILE = dp("withdrawals.json")
EXCHANGES_FILE   = dp("exchanges.json")
TRANSFERS_FILE   = dp("transfers.json")
PINS_FILE        = dp("pins.json")
REFERRALS_FILE   = dp("referrals.json")
OTP_FILE         = dp("otps.json")
NOTIF_FILE       = dp("notifications.json")
SETTINGS_FILE    = dp("settings.json")
AUDIT_FILE       = dp("logs/audit.json")

# ============================================================
# TRANSLATIONS
# ============================================================
TRANSLATIONS = {
    "en": {
        "app_name": "SocialPay",
        "tagline": "Earn Money via Social Media Tasks",
        "login": "Login",
        "register": "Register",
        "email": "Email Address",
        "password": "Password",
        "full_name": "Full Name",
        "confirm_password": "Confirm Password",
        "referral_code": "Referral Code (Optional)",
        "create_account": "Create Account",
        "login_now": "Login Now",
        "otp_title": "Enter OTP Code",
        "otp_desc": "We sent a 6-digit code to your email.",
        "otp_placeholder": "Enter 6-digit code",
        "verify_otp": "Verify OTP",
        "resend_otp": "Resend OTP",
        "welcome_back": "Welcome back",
        "total_balance": "Total Balance",
        "tasks": "Tasks",
        "balance": "Balance",
        "transfer": "Transfer",
        "referrals": "Referrals",
        "withdraw": "Withdraw",
        "exchange": "Exchange",
        "profile": "Profile",
        "history": "History",
        "notifications": "Notifications",
        "logout": "Logout",
        "available_tasks": "Available Tasks",
        "my_earnings": "My Earnings",
        "completed_tasks": "Completed Tasks",
        "pending_tasks": "Pending",
        "send_proof": "Submit Proof",
        "proof_placeholder": "Link, username, screenshot URL...",
        "submit": "Submit for Review",
        "withdraw_money": "Withdraw Money",
        "exchange_currency": "Exchange Currency",
        "send_money": "Send Money",
        "receiver_id": "Receiver's User ID",
        "amount": "Amount",
        "pin": "4-digit PIN",
        "send_now": "Send Now",
        "cancel": "Cancel",
        "save": "Save",
        "set_pin": "Set PIN",
        "change_pin": "Change PIN",
        "bank_details": "Bank / Payment Details",
        "bank_name": "Bank Name",
        "account_number": "Account Number",
        "account_name": "Account Name",
        "payment_type": "Payment Type",
        "referral_link": "Your Referral Link",
        "copy": "Copy",
        "share_whatsapp": "WhatsApp",
        "share_telegram": "Telegram",
        "how_referral_works": "How Referrals Work",
        "reward": "Reward",
        "status": "Status",
        "pending": "Pending",
        "approved": "Approved",
        "rejected": "Rejected",
        "no_tasks": "No Tasks Available",
        "no_tasks_desc": "Check back soon! Admin will add new tasks.",
        "no_notifications": "No Notifications",
        "admin_panel": "Admin Panel",
        "total_users": "Total Users",
        "active_tasks": "Active Tasks",
        "pending_approvals": "Pending Approvals",
        "pending_withdrawals": "Pending Withdrawals",
        "manage_users": "Users",
        "manage_tasks": "Tasks",
        "approve_tasks": "Approvals",
        "manage_withdrawals": "Withdrawals",
        "broadcast": "Broadcast",
        "settings": "Settings",
        "logs": "Logs",
        "transfers_log": "Transfers",
        "ban_user": "Ban User",
        "unban_user": "Unban User",
        "adjust_balance": "Adjust Balance",
        "reset_pin": "Reset PIN",
        "make_admin": "Make Admin",
        "send_message": "Send Message",
        "approve": "Approve",
        "reject": "Reject",
        "reverse": "Reverse Transfer",
        "create_task": "Create Task",
        "delete_task": "Delete Task",
        "task_title": "Task Title",
        "task_desc": "Description",
        "platform": "Platform",
        "task_type": "Task Type",
        "link": "Link",
        "max_users": "Max Users",
        "currency": "Currency",
        "maintenance_mode": "Maintenance Mode",
        "fee_percent": "Withdrawal Fee (%)",
        "min_withdrawal": "Min Withdrawal",
        "max_withdrawal": "Max Withdrawal",
        "exchange_rate": "Exchange Rate ($1 = ₦)",
        "referral_bonus": "Referral Bonus (₦)",
        "referral_tasks": "Tasks Needed for Referral Bonus",
        "save_settings": "Save Settings",
        "my_id": "My User ID",
        "edit_profile": "Edit Profile",
        "old_password": "Current Password",
        "new_password": "New Password",
        "total_earned": "Total Earned",
        "total_withdrawn": "Total Withdrawn",
        "referral_earned": "Referral Bonus Earned",
        "select_language": "Language",
        "wrong_email_or_password": "Wrong email or password",
        "account_banned": "Your account has been banned. Contact support.",
        "email_exists": "This email is already registered",
        "fill_all_fields": "Please fill all required fields",
        "password_short": "Password must be at least 6 characters",
        "otp_sent": "OTP code sent to your email!",
        "otp_invalid": "Invalid or expired OTP code",
        "otp_verified": "Email verified successfully!",
        "task_submitted": "Task submitted! Awaiting admin review.",
        "already_submitted": "You already submitted this task",
        "insufficient_balance": "Insufficient balance",
        "withdraw_min": "Minimum withdrawal is",
        "pin_required": "You need to set a PIN first",
        "pin_wrong": "Wrong PIN",
        "pin_set": "PIN set successfully!",
        "pin_4digits": "PIN must be exactly 4 digits",
        "profile_updated": "Profile updated!",
        "bank_saved": "Bank details saved!",
        "balance_adjusted": "Balance adjusted!",
        "user_banned": "User has been banned",
        "user_unbanned": "User has been unbanned",
        "pin_reset": "PIN has been reset",
        "message_sent": "Message sent!",
        "task_created": "Task created!",
        "task_deleted": "Task deleted!",
        "submission_approved": "Submission approved! Payment added.",
        "submission_rejected": "Submission rejected.",
        "withdrawal_approved": "Withdrawal approved!",
        "withdrawal_rejected": "Withdrawal rejected. Funds refunded.",
        "transfer_reversed": "Transfer reversed!",
        "broadcast_sent": "Broadcast sent!",
        "settings_saved": "Settings saved!",
        "money_sent": "Money sent successfully!",
        "exchanged": "Currency exchanged!",
        "user_not_found": "User not found",
        "cannot_send_self": "Cannot send to yourself",
        "admin_notice": "Admin Notice",
        "from_admin": "From Admin",
        "referral_bonus_earned": "Referral bonus earned!",
        "withdrawal_request": "Withdrawal request submitted!",
        "days": "days",
        "ago": "ago",
        "just_now": "just now",
    },
    "ar": {
        "app_name": "سوشيال باي",
        "tagline": "اكسب المال عبر مهام وسائل التواصل الاجتماعي",
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "full_name": "الاسم الكامل",
        "confirm_password": "تأكيد كلمة المرور",
        "referral_code": "رمز الإحالة (اختياري)",
        "create_account": "إنشاء الحساب",
        "login_now": "تسجيل الدخول الآن",
        "otp_title": "أدخل رمز OTP",
        "otp_desc": "أرسلنا رمزاً مكوناً من 6 أرقام إلى بريدك الإلكتروني.",
        "otp_placeholder": "أدخل الرمز المكون من 6 أرقام",
        "verify_otp": "تحقق من الرمز",
        "resend_otp": "إعادة إرسال الرمز",
        "welcome_back": "مرحباً بعودتك",
        "total_balance": "إجمالي الرصيد",
        "tasks": "المهام",
        "balance": "الرصيد",
        "transfer": "تحويل",
        "referrals": "الإحالات",
        "withdraw": "سحب",
        "exchange": "تبادل",
        "profile": "الملف الشخصي",
        "history": "التاريخ",
        "notifications": "الإشعارات",
        "logout": "تسجيل الخروج",
        "available_tasks": "المهام المتاحة",
        "my_earnings": "أرباحي",
        "completed_tasks": "المهام المكتملة",
        "pending_tasks": "قيد الانتظار",
        "send_proof": "إرسال الدليل",
        "proof_placeholder": "رابط، اسم مستخدم، رابط لقطة الشاشة...",
        "submit": "إرسال للمراجعة",
        "withdraw_money": "سحب الأموال",
        "exchange_currency": "تبادل العملات",
        "send_money": "إرسال المال",
        "receiver_id": "معرّف المستلم",
        "amount": "المبلغ",
        "pin": "رمز PIN المكون من 4 أرقام",
        "send_now": "إرسال الآن",
        "cancel": "إلغاء",
        "save": "حفظ",
        "set_pin": "تعيين PIN",
        "change_pin": "تغيير PIN",
        "bank_details": "تفاصيل البنك / الدفع",
        "bank_name": "اسم البنك",
        "account_number": "رقم الحساب",
        "account_name": "اسم صاحب الحساب",
        "payment_type": "نوع الدفع",
        "referral_link": "رابط الإحالة الخاص بك",
        "copy": "نسخ",
        "share_whatsapp": "واتساب",
        "share_telegram": "تيليغرام",
        "how_referral_works": "كيف تعمل الإحالات",
        "reward": "المكافأة",
        "status": "الحالة",
        "pending": "قيد الانتظار",
        "approved": "مقبول",
        "rejected": "مرفوض",
        "no_tasks": "لا توجد مهام متاحة",
        "no_tasks_desc": "تحقق لاحقاً! سيضيف المسؤول مهام جديدة.",
        "no_notifications": "لا توجد إشعارات",
        "admin_panel": "لوحة الإدارة",
        "total_users": "إجمالي المستخدمين",
        "active_tasks": "المهام النشطة",
        "pending_approvals": "الموافقات المعلقة",
        "pending_withdrawals": "عمليات السحب المعلقة",
        "manage_users": "المستخدمون",
        "manage_tasks": "المهام",
        "approve_tasks": "الموافقات",
        "manage_withdrawals": "السحوبات",
        "broadcast": "رسالة جماعية",
        "settings": "الإعدادات",
        "logs": "السجلات",
        "transfers_log": "التحويلات",
        "ban_user": "حظر المستخدم",
        "unban_user": "رفع الحظر",
        "adjust_balance": "تعديل الرصيد",
        "reset_pin": "إعادة تعيين PIN",
        "make_admin": "ترقية لمسؤول",
        "send_message": "إرسال رسالة",
        "approve": "قبول",
        "reject": "رفض",
        "reverse": "عكس التحويل",
        "create_task": "إنشاء مهمة",
        "delete_task": "حذف المهمة",
        "task_title": "عنوان المهمة",
        "task_desc": "الوصف",
        "platform": "المنصة",
        "task_type": "نوع المهمة",
        "link": "الرابط",
        "max_users": "الحد الأقصى للمستخدمين",
        "currency": "العملة",
        "maintenance_mode": "وضع الصيانة",
        "fee_percent": "رسوم السحب (%)",
        "min_withdrawal": "الحد الأدنى للسحب",
        "max_withdrawal": "الحد الأقصى للسحب",
        "exchange_rate": "سعر الصرف ($1 = ₦)",
        "referral_bonus": "مكافأة الإحالة (₦)",
        "referral_tasks": "المهام المطلوبة لمكافأة الإحالة",
        "save_settings": "حفظ الإعدادات",
        "my_id": "معرّف المستخدم",
        "edit_profile": "تعديل الملف الشخصي",
        "old_password": "كلمة المرور الحالية",
        "new_password": "كلمة مرور جديدة",
        "total_earned": "إجمالي الأرباح",
        "total_withdrawn": "إجمالي المسحوب",
        "referral_earned": "مكافأة الإحالة المكتسبة",
        "select_language": "اللغة",
        "wrong_email_or_password": "البريد الإلكتروني أو كلمة المرور خاطئة",
        "account_banned": "تم حظر حسابك. تواصل مع الدعم.",
        "email_exists": "هذا البريد الإلكتروني مسجل بالفعل",
        "fill_all_fields": "يرجى ملء جميع الحقول المطلوبة",
        "password_short": "يجب أن تكون كلمة المرور 6 أحرف على الأقل",
        "otp_sent": "تم إرسال رمز OTP إلى بريدك الإلكتروني!",
        "otp_invalid": "رمز OTP غير صالح أو منتهي الصلاحية",
        "otp_verified": "تم التحقق من البريد الإلكتروني بنجاح!",
        "task_submitted": "تم إرسال المهمة! في انتظار مراجعة المسؤول.",
        "already_submitted": "لقد أرسلت هذه المهمة بالفعل",
        "insufficient_balance": "رصيد غير كافٍ",
        "withdraw_min": "الحد الأدنى للسحب هو",
        "pin_required": "تحتاج إلى تعيين PIN أولاً",
        "pin_wrong": "PIN خاطئ",
        "pin_set": "تم تعيين PIN بنجاح!",
        "pin_4digits": "يجب أن يكون PIN مكوناً من 4 أرقام بالضبط",
        "profile_updated": "تم تحديث الملف الشخصي!",
        "bank_saved": "تم حفظ تفاصيل البنك!",
        "balance_adjusted": "تم تعديل الرصيد!",
        "user_banned": "تم حظر المستخدم",
        "user_unbanned": "تم رفع الحظر عن المستخدم",
        "pin_reset": "تم إعادة تعيين PIN",
        "message_sent": "تم إرسال الرسالة!",
        "task_created": "تم إنشاء المهمة!",
        "task_deleted": "تم حذف المهمة!",
        "submission_approved": "تمت الموافقة! تم إضافة الدفع.",
        "submission_rejected": "تم رفض الطلب.",
        "withdrawal_approved": "تمت الموافقة على السحب!",
        "withdrawal_rejected": "تم رفض السحب. تم استرداد الأموال.",
        "transfer_reversed": "تم عكس التحويل!",
        "broadcast_sent": "تم إرسال الرسالة الجماعية!",
        "settings_saved": "تم حفظ الإعدادات!",
        "money_sent": "تم إرسال المال بنجاح!",
        "exchanged": "تم تبادل العملة!",
        "user_not_found": "المستخدم غير موجود",
        "cannot_send_self": "لا يمكنك الإرسال لنفسك",
        "admin_notice": "إشعار من الإدارة",
        "from_admin": "من الإدارة",
        "referral_bonus_earned": "تم كسب مكافأة الإحالة!",
        "withdrawal_request": "تم تقديم طلب السحب!",
        "days": "أيام",
        "ago": "منذ",
        "just_now": "الآن",
    },
    "ha": {
        "app_name": "SocialPay",
        "tagline": "Samu Kuɗi ta Hanyar Ayyukan Social Media",
        "login": "Shiga",
        "register": "Ƙirƙiri Account",
        "email": "Adireshin Email",
        "password": "Password",
        "full_name": "Cikakken Suna",
        "confirm_password": "Tabbatar da Password",
        "referral_code": "Lambar Kiran Aboki (zaɓi)",
        "create_account": "Ƙirƙiri Account Yanzu",
        "login_now": "Shiga Yanzu",
        "otp_title": "Shigar da Lambar OTP",
        "otp_desc": "Mun aika lamba mai lamba 6 zuwa email ɗinka.",
        "otp_placeholder": "Shigar da lambar lamba 6",
        "verify_otp": "Tabbatar da OTP",
        "resend_otp": "Sake Aika OTP",
        "welcome_back": "Barka da dawowa",
        "total_balance": "Jimillar Kuɗi",
        "tasks": "Ayyuka",
        "balance": "Kuɗi",
        "transfer": "Aika",
        "referrals": "Kiraye",
        "withdraw": "Cire",
        "exchange": "Canza",
        "profile": "Profile",
        "history": "Tarihi",
        "notifications": "Sanarwa",
        "logout": "Fita",
        "available_tasks": "Ayyukan da Samu",
        "my_earnings": "Kuɗaɗena",
        "completed_tasks": "Ayyuka Kammala",
        "pending_tasks": "Jira",
        "send_proof": "Aika Shaida",
        "proof_placeholder": "Link, username, ko hanyar screenshot...",
        "submit": "Aika don Bincike",
        "withdraw_money": "Fitar da Kuɗi",
        "exchange_currency": "Canza Kuɗi",
        "send_money": "Aika Kuɗi",
        "receiver_id": "ID na Mai Karɓa",
        "amount": "Adadi",
        "pin": "PIN haruffa 4",
        "send_now": "Aika Yanzu",
        "cancel": "Soke",
        "save": "Ajiye",
        "set_pin": "Saita PIN",
        "change_pin": "Canza PIN",
        "bank_details": "Bayanin Banku / Kuɗi",
        "bank_name": "Sunan Banku",
        "account_number": "Lambar Akwatin Kuɗi",
        "account_name": "Suna a Banku",
        "payment_type": "Nau'in Kuɗi",
        "referral_link": "Hanyar Kiran Ku",
        "copy": "Kwafa",
        "share_whatsapp": "WhatsApp",
        "share_telegram": "Telegram",
        "how_referral_works": "Yadda Ake Samun Lada",
        "reward": "Lada",
        "status": "Yanayi",
        "pending": "Jira",
        "approved": "An Amince",
        "rejected": "An Ƙi",
        "no_tasks": "Babu Ayyuka a Yanzu",
        "no_tasks_desc": "Duba baya! Admin zai ƙara ayyuka sabon.",
        "no_notifications": "Babu Sanarwa",
        "admin_panel": "Panel na Admin",
        "total_users": "Jimla Masu Amfani",
        "active_tasks": "Ayyuka Active",
        "pending_approvals": "Jiran Amince",
        "pending_withdrawals": "Ficewa Jira",
        "manage_users": "Masu Amfani",
        "manage_tasks": "Ayyuka",
        "approve_tasks": "Amince",
        "manage_withdrawals": "Ficewa",
        "broadcast": "Sanarwa",
        "settings": "Settings",
        "logs": "Logs",
        "transfers_log": "Transfers",
        "ban_user": "Hana User",
        "unban_user": "Kwato User",
        "adjust_balance": "Gyara Balance",
        "reset_pin": "Share PIN",
        "make_admin": "Bai Admin",
        "send_message": "Aika Saƙo",
        "approve": "Amince",
        "reject": "Ƙi",
        "reverse": "Mayar Transfer",
        "create_task": "Ƙirƙiro Aiki",
        "delete_task": "Goge Aiki",
        "task_title": "Suna na Aiki",
        "task_desc": "Bayani",
        "platform": "Platform",
        "task_type": "Nau'in Aiki",
        "link": "Hanyar Link",
        "max_users": "Mafi Yawan Masu Amfani",
        "currency": "Kuɗi",
        "maintenance_mode": "Yanayin Gyarawa",
        "fee_percent": "Kudin Ficewa (%)",
        "min_withdrawal": "Mafi Ƙarancin Ficewa",
        "max_withdrawal": "Mafi Yawan Ficewa",
        "exchange_rate": "Rate ($1 = ₦)",
        "referral_bonus": "Lada Kira (₦)",
        "referral_tasks": "Ayyuka don Lada Kira",
        "save_settings": "Ajiye Settings",
        "my_id": "ID na",
        "edit_profile": "Gyara Profile",
        "old_password": "Tsohon Password",
        "new_password": "Sabon Password",
        "total_earned": "Jimlar Samun",
        "total_withdrawn": "Jimlar Ficewa",
        "referral_earned": "Lada Kira da Aka Samu",
        "select_language": "Harshe",
        "wrong_email_or_password": "Email ko password ba daidai ba",
        "account_banned": "An hana account dinku. Tuntuɓi support.",
        "email_exists": "Email din nan an riga an yi rajistar da shi",
        "fill_all_fields": "Cika duk filayen da ake bukata",
        "password_short": "Password ya zama akalla haruffa 6",
        "otp_sent": "Lambar OTP an aika zuwa email ɗinka!",
        "otp_invalid": "Lambar OTP ba ta daidai ko ta ƙare",
        "otp_verified": "Email an tabbatar da shi cikin nasara!",
        "task_submitted": "Aiki an aika! Ana jiran amincewa admin.",
        "already_submitted": "Kun riga kun aika wannan aiki",
        "insufficient_balance": "Kudinka ba ya isawa",
        "withdraw_min": "Mafi ƙarancin ficewa shine",
        "pin_required": "Kana buƙatar saita PIN da farko",
        "pin_wrong": "PIN ba daidai ba",
        "pin_set": "PIN an saita cikin nasara!",
        "pin_4digits": "PIN dole ne ya zama lamba 4",
        "profile_updated": "Profile an sabunta!",
        "bank_saved": "Bayanin banku an ajiye!",
        "balance_adjusted": "Balance an gyara!",
        "user_banned": "User an hana shi",
        "user_unbanned": "An sake bude account",
        "pin_reset": "PIN an share",
        "message_sent": "Saƙo an aika!",
        "task_created": "Aiki an ƙirƙira!",
        "task_deleted": "Aiki an goge!",
        "submission_approved": "An amince! Kuɗi an ƙara.",
        "submission_rejected": "An ƙi buƙatar.",
        "withdrawal_approved": "Ficewa an amince!",
        "withdrawal_rejected": "Ficewa an ƙi. Kuɗi an mayar.",
        "transfer_reversed": "Transfer an mayar!",
        "broadcast_sent": "Sanarwa an aika!",
        "settings_saved": "Settings an ajiye!",
        "money_sent": "Kuɗi an aika cikin nasara!",
        "exchanged": "An canza kuɗi!",
        "user_not_found": "User ba ya wanzu",
        "cannot_send_self": "Ba za ka iya aika wa kanka ba",
        "admin_notice": "Sanarwa daga Admin",
        "from_admin": "Daga Admin",
        "referral_bonus_earned": "Lada kira an samu!",
        "withdrawal_request": "Buƙatar ficewa an aika!",
        "days": "kwanaki",
        "ago": "da suka wuce",
        "just_now": "yanzu haka",
    }
}

def t(key, lang=None):
    """Get translation for current language"""
    if lang is None:
        lang = session.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

app.jinja_env.globals["t"] = t
app.jinja_env.globals["session"] = session

# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def load(f):
    if not os.path.exists(f):
        return {}
    try:
        with open(f, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except:
        return {}

def save(f, data):
    with open(f, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)

def now_str():
    return datetime.now().isoformat()

def short_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def hash_pw(pw):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000)
    return f"{salt}${h.hex()}"

def verify_pw(pw, stored):
    try:
        salt, sh = stored.split('$')
        h = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000)
        return h.hex() == sh
    except:
        return False

def get_settings():
    d = {"referral_bonus": 30, "referral_tasks_needed": 10,
         "withdrawal_fee_percent": 5, "min_withdrawal": 500,
         "max_withdrawal": 100000, "exchange_rate": 1500,
         "site_name": "SocialPay", "maintenance": False,
         "announcement": ""}
    d.update(load(SETTINGS_FILE))
    return d

def add_notif(user_id, message, ntype="info"):
    n = load(NOTIF_FILE)
    if user_id not in n:
        n[user_id] = []
    n[user_id].insert(0, {"id": short_id(), "message": message,
                           "type": ntype, "time": now_str(), "read": False})
    n[user_id] = n[user_id][:50]
    save(NOTIF_FILE, n)

def log_audit(action, uid, detail="", amount=0):
    logs = load(AUDIT_FILE)
    lid = f"log_{int(datetime.now().timestamp())}_{secrets.token_hex(3)}"
    logs[lid] = {"action": action, "user_id": uid, "detail": detail,
                  "amount": amount, "time": now_str()}
    save(AUDIT_FILE, logs)

def get_wallet(uid):
    w = load(WALLETS_FILE)
    uid = str(uid)
    if uid not in w:
        w[uid] = {"naira": 0.0, "dollar": 0.0, "completed_tasks": 0,
                  "pending_tasks": 0, "referral_count": 0,
                  "referral_bonus_earned": 0.0, "total_earned": 0.0,
                  "total_withdrawn": 0.0, "created": now_str()}
        save(WALLETS_FILE, w)
    return w[uid]

def upd_wallet(uid, field, amount, absolute=False):
    w = load(WALLETS_FILE)
    uid = str(uid)
    if uid not in w:
        get_wallet(uid)
        w = load(WALLETS_FILE)
    if absolute:
        w[uid][field] = amount
    else:
        w[uid][field] = w[uid].get(field, 0) + amount
        if w[uid][field] < 0:
            w[uid][field] = 0
    save(WALLETS_FILE, w)

# ============================================================
# EMAIL / OTP
# ============================================================
def send_email(to_email, subject, html_body):
    """Send email via Gmail SMTP"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.sendmail(EMAIL_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def save_otp(email, otp, purpose="verify"):
    otps = load(OTP_FILE)
    otps[email] = {
        "otp": otp,
        "purpose": purpose,
        "expires": (datetime.now() + timedelta(minutes=OTP_EXPIRE_MINUTES)).isoformat(),
        "used": False
    }
    save(OTP_FILE, otps)

def verify_otp(email, otp):
    otps = load(OTP_FILE)
    rec = otps.get(email)
    if not rec:
        return False
    if rec.get("used"):
        return False
    if datetime.now() > datetime.fromisoformat(rec["expires"]):
        return False
    if rec["otp"] != otp:
        return False
    otps[email]["used"] = True
    save(OTP_FILE, otps)
    return True

def otp_email_html(otp, name, lang="en"):
    if lang == "ar":
        title = "رمز التحقق الخاص بك"
        body = f"مرحباً {name}،"
        desc = "أدخل رمز OTP أدناه للتحقق من حسابك."
        expire = f"ينتهي هذا الرمز خلال {OTP_EXPIRE_MINUTES} دقائق."
        footer = "إذا لم تطلب هذا، تجاهل هذه الرسالة."
    elif lang == "ha":
        title = "Lambar OTP Ɗinka"
        body = f"Sannu {name},"
        desc = "Shigar da wannan lambar OTP don tabbatar da account ɗinka."
        expire = f"Wannan lambar za ta ƙare bayan minti {OTP_EXPIRE_MINUTES}."
        footer = "Idan ba kai ne ka nema ba, ka yi watsi da wannan email."
    else:
        title = "Your OTP Verification Code"
        body = f"Hello {name},"
        desc = "Enter the OTP code below to verify your account."
        expire = f"This code expires in {OTP_EXPIRE_MINUTES} minutes."
        footer = "If you didn't request this, please ignore this email."

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f0f4ff;font-family:'Segoe UI',Arial,sans-serif">
  <div style="max-width:480px;margin:40px auto;background:white;border-radius:20px;overflow:hidden;box-shadow:0 8px 40px rgba(10,36,99,0.12)">
    <div style="background:linear-gradient(135deg,#0A2463,#1a3a8f);padding:32px 24px;text-align:center">
      <div style="font-size:32px;font-weight:900;color:white;letter-spacing:-1px">Social<span style="color:#ffd166">Pay</span></div>
      <div style="color:rgba(255,255,255,0.7);font-size:13px;margin-top:6px">{title}</div>
    </div>
    <div style="padding:32px 24px">
      <p style="font-size:15px;color:#333;margin-bottom:8px">{body}</p>
      <p style="font-size:14px;color:#666;margin-bottom:24px">{desc}</p>
      <div style="background:#f0f4ff;border-radius:16px;padding:24px;text-align:center;margin:24px 0">
        <div style="font-size:42px;font-weight:900;letter-spacing:10px;color:#0A2463">{otp}</div>
      </div>
      <p style="font-size:13px;color:#999;text-align:center">{expire}</p>
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0">
      <p style="font-size:12px;color:#bbb;text-align:center">{footer}</p>
    </div>
  </div>
</body>
</html>
"""

# ============================================================
# AUTH DECORATORS
# ============================================================
def login_required(f):
    @wraps(f)
    def deco(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return deco

def admin_required(f):
    @wraps(f)
    def deco(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        users = load(USERS_FILE)
        if not users.get(session["user_id"], {}).get("is_admin"):
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return deco

# ============================================================
# AUTO CREATE ADMIN ON STARTUP
# ============================================================
def ensure_admin():
    """Create admin account automatically if not exists"""
    users = load(USERS_FILE)
    # Check if admin already exists
    for uid, u in users.items():
        if u.get("email", "").lower() == ADMIN_EMAIL.lower() and u.get("is_admin"):
            return  # Admin already exists
    # Create admin
    admin_id = "SP00000001"
    users[admin_id] = {
        "id": admin_id,
        "name": ADMIN_NAME,
        "email": ADMIN_EMAIL,
        "password": hash_pw(ADMIN_PASSWORD),
        "is_admin": True,
        "banned": False,
        "verified": True,
        "created": now_str(),
        "last_login": now_str(),
        "referral_code": admin_id,
        "referred_by": None,
        "lang": "en"
    }
    save(USERS_FILE, users)
    get_wallet(admin_id)
    print(f"[SETUP] Admin account created: {ADMIN_EMAIL}")

# ============================================================
# LANGUAGE
# ============================================================
@app.route("/set_lang/<lang>")
def set_lang(lang):
    if lang in ["en", "ar", "ha"]:
        session["lang"] = lang
        if "user_id" in session:
            users = load(USERS_FILE)
            if session["user_id"] in users:
                users[session["user_id"]]["lang"] = lang
                save(USERS_FILE, users)
    return redirect(request.referrer or url_for("index"))

# ============================================================
# MAIN ROUTES
# ============================================================
@app.route("/")
def index():
    if "user_id" in session:
        users = load(USERS_FILE)
        if users.get(session["user_id"], {}).get("is_admin"):
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        lang = session.get("lang", "en")

        users = load(USERS_FILE)
        uid = None
        udata = None
        for k, v in users.items():
            if v.get("email", "").lower() == email:
                uid = k; udata = v; break

        if not udata:
            return jsonify({"success": False, "message": t("wrong_email_or_password", lang)})
        if not verify_pw(password, udata.get("password", "")):
            return jsonify({"success": False, "message": t("wrong_email_or_password", lang)})
        if udata.get("banned"):
            return jsonify({"success": False, "message": t("account_banned", lang)})

        # ADMIN: skip OTP
        if udata.get("is_admin"):
            session["user_id"] = uid
            session["user_name"] = udata.get("name", "Admin")
            session["is_admin"] = True
            session["lang"] = udata.get("lang", "en")
            users[uid]["last_login"] = now_str()
            save(USERS_FILE, users)
            log_audit("login", uid)
            return jsonify({"success": True, "redirect": url_for("admin_dashboard")})

        # Direct login - no OTP (Railway SMTP issues)
        lang = udata.get("lang", "en")
        session["lang"] = lang
        session["user_id"] = uid
        session["user_name"] = udata.get("name", "User")
        session["is_admin"] = False
        users[uid]["last_login"] = now_str()
        save(USERS_FILE, users)
        log_audit("login", uid)
        return jsonify({"success": True, "redirect": url_for("dashboard")})

    lang = session.get("lang", "en")
    return render_template("login.html", lang=lang)

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp_route():
    lang = session.get("lang", "en")
    if request.method == "POST":
        otp_code = request.form.get("otp", "").strip()
        pending = session.get("pending_login") or session.get("pending_register")

        if not pending:
            return jsonify({"success": False, "message": t("otp_invalid", lang)})

        email = pending.get("email")
        if not verify_otp(email, otp_code):
            return jsonify({"success": False, "message": t("otp_invalid", lang)})

        # OTP OK
        if "pending_register" in session:
            data = session.pop("pending_register")
            users = load(USERS_FILE)
            uid = data["uid"]
            users[uid] = data["user_data"]
            users[uid]["verified"] = True
            save(USERS_FILE, users)
            get_wallet(uid)
            # Handle referral
            ref_code = data.get("ref_code")
            if ref_code and ref_code != uid:
                for ref_uid, ref_data in users.items():
                    if ref_data.get("referral_code") == ref_code or ref_uid == ref_code:
                        users[uid]["referred_by"] = ref_uid
                        refs = load(REFERRALS_FILE)
                        if ref_uid not in refs:
                            refs[ref_uid] = []
                        refs[ref_uid].append({"referred_id": uid, "time": now_str(),
                                               "bonus_paid": False, "tasks_done": 0})
                        save(REFERRALS_FILE, refs)
                        upd_wallet(ref_uid, "referral_count", 1)
                        break
            save(USERS_FILE, users)
            add_notif(uid, f"🎉 Welcome to {APP_NAME}!", "success")
            session["user_id"] = uid
            session["user_name"] = data["user_data"]["name"]
            session["is_admin"] = False
        else:
            session.pop("pending_login", None)
            uid = pending["uid"]
            users = load(USERS_FILE)
            users[uid]["last_login"] = now_str()
            save(USERS_FILE, users)
            session["user_id"] = uid
            session["user_name"] = users[uid].get("name", "User")
            session["is_admin"] = False

        log_audit("otp_verified", uid)
        return jsonify({"success": True, "message": t("otp_verified", lang),
                        "redirect": url_for("dashboard")})

    return render_template("otp.html", lang=lang)

@app.route("/resend_otp", methods=["POST"])
def resend_otp():
    lang = session.get("lang", "en")
    pending = session.get("pending_login") or session.get("pending_register")
    if not pending:
        return jsonify({"success": False, "message": t("otp_invalid", lang)})

    email = pending.get("email")
    name = pending.get("name", "User")
    otp = generate_otp()
    save_otp(email, otp, "resend")
    send_email(email, f"[{APP_NAME}] Your OTP Code",
               otp_email_html(otp, name, lang))
    return jsonify({"success": True, "message": t("otp_sent", lang)})

@app.route("/register", methods=["GET", "POST"])
def register():
    lang = session.get("lang", "en")
    # If already logged in, redirect away
    if "user_id" in session:
        if session.get("is_admin"):
            return redirect(url_for("admin_dashboard")) if request.method == "GET" else jsonify({"success": False, "message": "Already logged in as admin"})
        return redirect(url_for("dashboard")) if request.method == "GET" else jsonify({"success": False, "message": "Already logged in"})
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        name = request.form.get("name", "").strip()[:100]
        ref_code = request.form.get("ref", "").strip()

        if not email or not password or not name:
            return jsonify({"success": False, "message": t("fill_all_fields", lang)})
        if len(password) < 6:
            return jsonify({"success": False, "message": t("password_short", lang)})
        if "@" not in email:
            return jsonify({"success": False, "message": t("fill_all_fields", lang)})

        users = load(USERS_FILE)
        for u in users.values():
            if u.get("email", "").lower() == email:
                return jsonify({"success": False, "message": t("email_exists", lang)})

        uid = f"SP{short_id()}"
        user_data = {
            "id": uid, "name": name, "email": email,
            "password": hash_pw(password), "is_admin": False,
            "banned": False, "verified": False,
            "created": now_str(), "last_login": now_str(),
            "referral_code": uid, "referred_by": None, "lang": lang
        }

        # Direct register - no OTP needed
        users[uid] = user_data
        users[uid]["verified"] = True
        save(USERS_FILE, users)
        get_wallet(uid)
        # Handle referral
        if ref_code and ref_code != uid:
            for ref_uid, ref_d in users.items():
                if ref_d.get("referral_code") == ref_code or ref_uid == ref_code:
                    users[uid]["referred_by"] = ref_uid
                    refs = load(REFERRALS_FILE)
                    if ref_uid not in refs:
                        refs[ref_uid] = []
                    refs[ref_uid].append({"referred_id": uid, "time": now_str(),
                                           "bonus_paid": False, "tasks_done": 0})
                    save(REFERRALS_FILE, refs)
                    save(USERS_FILE, users)
                    upd_wallet(ref_uid, "referral_count", 1)
                    break
        # Only set session if not already logged in (e.g. admin creating account)
        if "user_id" not in session:
            session["user_id"] = uid
            session["user_name"] = name
            session["is_admin"] = False
        add_notif(uid, f"🎉 Welcome to {APP_NAME}! Start earning today.", "success")
        log_audit("register", uid)
        redir = url_for("admin_dashboard") if session.get("is_admin") else url_for("dashboard")
        return jsonify({"success": True, "redirect": redir, "message": f"Account created for {name}"})

    return render_template("login.html", lang=lang, tab="register")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ============================================================
# USER ROUTES
# ============================================================
@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    users = load(USERS_FILE)
    user = users.get(uid, {})
    if user.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
    wallet = get_wallet(uid)
    notifs = load(NOTIF_FILE).get(uid, [])
    unread = sum(1 for n in notifs if not n.get("read"))
    # Count pending withdrawals for this user
    wds = load(WITHDRAWALS_FILE)
    pending_wd = sum(1 for w in wds.values() if w.get("user_id")==uid and w.get("status")=="pending")
    # Get announcements (from settings)
    settings = get_settings()
    announcement = settings.get("announcement", "")
    lang = session.get("lang", "en")
    return render_template("dashboard.html", user=user, wallet=wallet,
                            unread=unread, pending_wd=pending_wd,
                            announcement=announcement, lang=lang)

@app.route("/tasks")
@login_required
def tasks_page():
    uid = session["user_id"]
    tasks = load(TASKS_FILE)
    subs = load(SUBMISSIONS_FILE)
    available = []
    for tid, t_data in tasks.items():
        if t_data.get("status") != "active": continue
        done = any(s.get("user_id") == uid and s.get("task_id") == tid for s in subs.values())
        if not done:
            cb = t_data.get("completed_by", [])
            if len(cb) < t_data.get("max_users", 999999):
                tc = dict(t_data); tc["id"] = tid
                available.append(tc)
    lang = session.get("lang", "en")
    return render_template("tasks.html", tasks=available, lang=lang)

@app.route("/submit_task", methods=["POST"])
@login_required
def submit_task():
    uid = session["user_id"]
    task_id = request.form.get("task_id")
    proof = request.form.get("proof", "").strip()
    lang = session.get("lang", "en")
    # Handle screenshot upload (base64)
    screenshot = request.form.get("screenshot", "")
    if screenshot:
        proof = proof + ("\n[SCREENSHOT]" if proof else "[SCREENSHOT]")
    if not task_id or (not proof and not screenshot):
        return jsonify({"success": False, "message": t("fill_all_fields", lang)})
    tasks = load(TASKS_FILE)
    if task_id not in tasks:
        return jsonify({"success": False, "message": "Task not found"})
    subs = load(SUBMISSIONS_FILE)
    for s in subs.values():
        if s.get("user_id") == uid and s.get("task_id") == task_id:
            return jsonify({"success": False, "message": t("already_submitted", lang)})
    sid = f"SUB_{short_id()}"
    task = tasks[task_id]
    subs[sid] = {"id": sid, "user_id": uid, "task_id": task_id,
                 "proof": proof[:1000], "screenshot": screenshot[:50000] if screenshot else "",
                 "status": "pending",
                 "reward": task.get("reward", 0), "currency": task.get("currency", "naira"),
                 "submitted_at": now_str(), "reviewed_at": None, "note": ""}
    save(SUBMISSIONS_FILE, subs)
    upd_wallet(uid, "pending_tasks", 1)
    add_notif(uid, f"✅ {t('task_submitted', lang)}", "info")
    log_audit("task_submitted", uid, task_id, task.get("reward", 0))
    return jsonify({"success": True, "message": t("task_submitted", lang)})

@app.route("/balance")
@login_required
def balance_page():
    uid = session["user_id"]
    wallet = get_wallet(uid)
    wds = [w for w in load(WITHDRAWALS_FILE).values() if w.get("user_id") == uid]
    trs = load(TRANSFERS_FILE)
    sent = [t for t in trs.values() if t.get("sender_id") == uid]
    recv = [t for t in trs.values() if t.get("receiver_id") == uid]
    settings = get_settings()
    lang = session.get("lang", "en")
    return render_template("balance.html", wallet=wallet,
                            withdrawals=sorted(wds, key=lambda x: x.get("requested_at",""), reverse=True)[:10],
                            transfers_sent=sorted(sent, key=lambda x: x.get("time",""), reverse=True)[:10],
                            transfers_recv=sorted(recv, key=lambda x: x.get("time",""), reverse=True)[:10],
                            settings=settings, lang=lang)

@app.route("/withdraw", methods=["POST"])
@login_required
def withdraw():
    uid = session["user_id"]
    lang = session.get("lang", "en")
    amount = float(request.form.get("amount", 0))
    currency = request.form.get("currency", "naira")
    bank_info = request.form.get("bank_info", "").strip()
    settings = get_settings()
    wallet = get_wallet(uid)
    if amount < settings["min_withdrawal"]:
        return jsonify({"success": False, "message": f"{t('withdraw_min', lang)} ₦{settings['min_withdrawal']:,.0f}"})
    bal_key = "naira" if currency == "naira" else "dollar"
    if amount > wallet[bal_key]:
        return jsonify({"success": False, "message": t("insufficient_balance", lang)})
    if not bank_info:
        return jsonify({"success": False, "message": t("fill_all_fields", lang)})
    fee = amount * (settings["withdrawal_fee_percent"] / 100)
    net = amount - fee
    wid = f"WD_{short_id()}"
    wds = load(WITHDRAWALS_FILE)
    wds[wid] = {"id": wid, "user_id": uid, "amount": amount, "fee": fee, "net": net,
                "currency": currency, "bank_info": bank_info[:500], "status": "pending",
                "requested_at": now_str(), "processed_at": None, "note": ""}
    save(WITHDRAWALS_FILE, wds)
    upd_wallet(uid, bal_key, -amount)
    add_notif(uid, f"💸 {t('withdrawal_request', lang)} ₦{amount:,.2f}", "info")
    log_audit("withdraw_request", uid, wid, amount)
    return jsonify({"success": True, "message": f"{t('withdrawal_request', lang)} Net: ₦{net:,.2f}"})

@app.route("/exchange", methods=["POST"])
@login_required
def exchange():
    uid = session["user_id"]
    lang = session.get("lang", "en")
    from_curr = request.form.get("from_currency")
    amount = float(request.form.get("amount", 0))
    settings = get_settings()
    rate = settings["exchange_rate"]
    wallet = get_wallet(uid)
    if from_curr == "naira":
        if amount > wallet["naira"]:
            return jsonify({"success": False, "message": t("insufficient_balance", lang)})
        to_amount = amount / rate; to_curr = "dollar"
    else:
        if amount > wallet["dollar"]:
            return jsonify({"success": False, "message": t("insufficient_balance", lang)})
        to_amount = amount * rate; to_curr = "naira"
    exs = load(EXCHANGES_FILE)
    exs[f"EX_{short_id()}"] = {"user_id": uid, "from_currency": from_curr, "from_amount": amount,
                                "to_currency": to_curr, "to_amount": to_amount, "rate": rate, "time": now_str()}
    save(EXCHANGES_FILE, exs)
    upd_wallet(uid, from_curr, -amount)
    upd_wallet(uid, to_curr, to_amount)
    symbol = "$" if to_curr == "dollar" else "₦"
    return jsonify({"success": True, "message": f"{t('exchanged', lang)} {symbol}{to_amount:,.4f}"})

@app.route("/transfer", methods=["POST"])
@login_required
def transfer():
    uid = session["user_id"]
    lang = session.get("lang", "en")
    receiver_id = request.form.get("receiver_id", "").strip()
    amount = float(request.form.get("amount", 0))
    pin = request.form.get("pin", "")
    if receiver_id == uid:
        return jsonify({"success": False, "message": t("cannot_send_self", lang)})
    users = load(USERS_FILE)
    if receiver_id not in users:
        return jsonify({"success": False, "message": t("user_not_found", lang)})
    pins = load(PINS_FILE)
    if uid not in pins:
        return jsonify({"success": False, "message": t("pin_required", lang)})
    if not verify_pw(pin, pins[uid].get("pin_hash", "")):
        return jsonify({"success": False, "message": t("pin_wrong", lang)})
    wallet = get_wallet(uid)
    if amount > wallet["naira"]:
        return jsonify({"success": False, "message": t("insufficient_balance", lang)})
    trid = f"TR_{short_id()}"
    trs = load(TRANSFERS_FILE)
    trs[trid] = {"id": trid, "sender_id": uid, "receiver_id": receiver_id,
                 "amount": amount, "time": now_str(), "status": "completed"}
    save(TRANSFERS_FILE, trs)
    upd_wallet(uid, "naira", -amount)
    upd_wallet(receiver_id, "naira", amount)
    sname = users[uid].get("name", "User")
    rname = users[receiver_id].get("name", "User")
    add_notif(uid, f"💸 {t('money_sent', lang)} → {rname}: ₦{amount:,.2f}", "success")
    add_notif(receiver_id, f"💰 +₦{amount:,.2f} ← {sname}", "success")
    log_audit("transfer", uid, f"to:{receiver_id}", amount)
    return jsonify({"success": True, "message": f"{t('money_sent', lang)} → {rname}"})

@app.route("/set_pin", methods=["POST"])
@login_required
def set_pin():
    uid = session["user_id"]
    lang = session.get("lang", "en")
    pin = request.form.get("pin", "")
    if len(pin) != 4 or not pin.isdigit():
        return jsonify({"success": False, "message": t("pin_4digits", lang)})
    pins = load(PINS_FILE)
    pins[uid] = {"pin_hash": hash_pw(pin), "created": now_str()}
    save(PINS_FILE, pins)
    return jsonify({"success": True, "message": t("pin_set", lang)})

@app.route("/referrals")
@login_required
def referrals_page():
    uid = session["user_id"]
    refs = load(REFERRALS_FILE).get(uid, [])
    users = load(USERS_FILE)
    settings = get_settings()
    wallet = get_wallet(uid)
    user = users.get(uid, {})
    ref_link = f"{request.host_url}register?ref={uid}"
    ref_details = []
    for r in refs:
        rid = r.get("referred_id")
        ref_details.append({"name": users.get(rid, {}).get("name", "Unknown"),
                             "time": r.get("time", "")[:10],
                             "tasks_done": r.get("tasks_done", 0),
                             "bonus_paid": r.get("bonus_paid", False),
                             "tasks_needed": settings["referral_tasks_needed"]})
    lang = session.get("lang", "en")
    return render_template("referrals.html", ref_link=ref_link, referrals=ref_details,
                            wallet=wallet, settings=settings, user=user, lang=lang)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    uid = session["user_id"]
    lang = session.get("lang", "en")
    users = load(USERS_FILE)
    user = users.get(uid, {})
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:100]
        old_pw = request.form.get("old_password", "")
        new_pw = request.form.get("new_password", "")
        if name:
            users[uid]["name"] = name
            session["user_name"] = name
        if old_pw and new_pw:
            if not verify_pw(old_pw, user.get("password", "")):
                return jsonify({"success": False, "message": t("wrong_email_or_password", lang)})
            if len(new_pw) < 6:
                return jsonify({"success": False, "message": t("password_short", lang)})
            users[uid]["password"] = hash_pw(new_pw)
        save(USERS_FILE, users)
        return jsonify({"success": True, "message": t("profile_updated", lang)})
    bank = load(BANK_FILE).get(uid, {})
    pins = load(PINS_FILE)
    has_pin = uid in pins
    return render_template("profile.html", user=user, bank=bank,
                            has_pin=has_pin, lang=lang)

@app.route("/save_bank", methods=["POST"])
@login_required
def save_bank():
    uid = session["user_id"]
    lang = session.get("lang", "en")
    bd = load(BANK_FILE)
    bd[uid] = {"bank_name": request.form.get("bank_name", "")[:100],
               "account_number": request.form.get("account_number", "")[:20],
               "account_name": request.form.get("account_name", "")[:100],
               "type": request.form.get("type", "bank"), "updated": now_str()}
    save(BANK_FILE, bd)
    return jsonify({"success": True, "message": t("bank_saved", lang)})

@app.route("/notifications")
@login_required
def notif_page():
    uid = session["user_id"]
    n = load(NOTIF_FILE)
    notifs = n.get(uid, [])
    for item in notifs:
        item["read"] = True
    n[uid] = notifs
    save(NOTIF_FILE, n)
    lang = session.get("lang", "en")
    return render_template("notifications.html", notifications=notifs, lang=lang)

@app.route("/my_submissions")
@login_required
def my_submissions():
    uid = session["user_id"]
    subs = load(SUBMISSIONS_FILE)
    tasks = load(TASKS_FILE)
    my = []
    for s in subs.values():
        if s.get("user_id") == uid:
            task = tasks.get(s.get("task_id"), {})
            sc = dict(s)
            sc["task_title"] = task.get("title", "Unknown")
            sc["task_platform"] = task.get("platform", "")
            my.append(sc)
    my.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
    lang = session.get("lang", "en")
    return render_template("my_submissions.html", submissions=my, lang=lang)

@app.route("/api/user_lookup", methods=["POST"])
@login_required
def api_user_lookup():
    qid = request.json.get("user_id", "").strip()
    users = load(USERS_FILE)
    if qid in users and not users[qid].get("is_admin"):
        return jsonify({"found": True, "name": users[qid].get("name", "Unknown")})
    return jsonify({"found": False})

@app.route("/api/notif_count")
@login_required
def api_notif_count():
    n = load(NOTIF_FILE).get(session["user_id"], [])
    return jsonify({"count": sum(1 for x in n if not x.get("read"))})

# ============================================================
# ADMIN ROUTES
# ============================================================
@app.route("/admin")
@admin_required
def admin_dashboard():
    users = load(USERS_FILE)
    wallets = load(WALLETS_FILE)
    tasks = load(TASKS_FILE)
    subs = load(SUBMISSIONS_FILE)
    wds = load(WITHDRAWALS_FILE)
    total_users = len([u for u in users.values() if not u.get("is_admin")])
    active_tasks = len([t for t in tasks.values() if t.get("status") == "active"])
    pending_subs = len([s for s in subs.values() if s.get("status") == "pending"])
    pending_wds = len([w for w in wds.values() if w.get("status") == "pending"])
    total_naira = sum(w.get("naira", 0) for w in wallets.values())
    total_dollar = sum(w.get("dollar", 0) for w in wallets.values())
    recent = sorted(users.items(), key=lambda x: x[1].get("created", ""), reverse=True)[:5]
    lang = session.get("lang", "en")
    return render_template("admin/dashboard.html",
        total_users=total_users, active_tasks=active_tasks,
        pending_subs=pending_subs, pending_wds=pending_wds,
        total_naira=total_naira, total_dollar=total_dollar,
        recent_users=recent, settings=get_settings(), lang=lang)

@app.route("/admin/users")
@admin_required
def admin_users():
    users = load(USERS_FILE)
    wallets = load(WALLETS_FILE)
    q = request.args.get("q", "").lower()
    ul = []
    for k, u in users.items():
        if u.get("is_admin"): continue
        if q and q not in u.get("name","").lower() and q not in u.get("email","").lower() and q not in k.lower(): continue
        w = wallets.get(k, {})
        ul.append({"id": k, "name": u.get("name",""), "email": u.get("email",""),
                   "naira": w.get("naira", 0), "completed_tasks": w.get("completed_tasks", 0),
                   "banned": u.get("banned", False), "verified": u.get("verified", False),
                   "created": u.get("created","")[:10]})
    ul.sort(key=lambda x: x["created"], reverse=True)
    lang = session.get("lang", "en")
    return render_template("admin/users.html", users=ul, q=q, lang=lang)

@app.route("/admin/user/<uid>")
@admin_required
def admin_user_detail(uid):
    users = load(USERS_FILE)
    user = users.get(uid)
    if not user: return redirect(url_for("admin_users"))
    wallet = load(WALLETS_FILE).get(uid, {})
    subs = [s for s in load(SUBMISSIONS_FILE).values() if s.get("user_id") == uid]
    wds = [w for w in load(WITHDRAWALS_FILE).values() if w.get("user_id") == uid]
    trs = [t for t in load(TRANSFERS_FILE).values() if t.get("sender_id")==uid or t.get("receiver_id")==uid]
    lang = session.get("lang", "en")
    return render_template("admin/user_detail.html", user=user, user_id=uid,
        wallet=wallet, submissions=subs[-10:], withdrawals=wds[-10:],
        transfers=trs[-10:], bank=load(BANK_FILE).get(uid, {}),
        has_pin=uid in load(PINS_FILE), lang=lang)

@app.route("/admin/user/action", methods=["POST"])
@admin_required
def admin_user_action():
    action = request.form.get("action")
    uid = request.form.get("user_id")
    admin_id = session["user_id"]
    lang = session.get("lang", "en")
    users = load(USERS_FILE)
    if uid not in users:
        return jsonify({"success": False, "message": t("user_not_found", lang)})
    if action == "ban":
        users[uid]["banned"] = True; save(USERS_FILE, users)
        add_notif(uid, f"⛔ {t('account_banned', lang)}", "error")
        log_audit("ban", admin_id, uid)
        return jsonify({"success": True, "message": t("user_banned", lang)})
    elif action == "unban":
        users[uid]["banned"] = False; save(USERS_FILE, users)
        add_notif(uid, "✅ Account restored.", "success")
        log_audit("unban", admin_id, uid)
        return jsonify({"success": True, "message": t("user_unbanned", lang)})
    elif action == "adjust_balance":
        currency = request.form.get("currency", "naira")
        amount = float(request.form.get("amount", 0))
        mode = request.form.get("mode", "add")
        upd_wallet(uid, currency, amount, absolute=(mode=="set"))
        add_notif(uid, f"💰 Balance updated by admin", "info")
        log_audit("adjust_balance", admin_id, f"{uid}:{currency}:{mode}", amount)
        return jsonify({"success": True, "message": t("balance_adjusted", lang)})
    elif action == "message":
        msg = request.form.get("message", "").strip()[:500]
        if msg:
            add_notif(uid, f"📩 {t('from_admin', lang)}: {msg}", "info")
            log_audit("message_user", admin_id, uid)
            return jsonify({"success": True, "message": t("message_sent", lang)})
    elif action == "reset_pin":
        pins = load(PINS_FILE)
        pins.pop(uid, None)
        save(PINS_FILE, pins)
        add_notif(uid, f"🔐 {t('pin_reset', lang)}. Please set a new PIN.", "warning")
        log_audit("reset_pin", admin_id, uid)
        return jsonify({"success": True, "message": t("pin_reset", lang)})
    elif action == "make_admin":
        users[uid]["is_admin"] = True; save(USERS_FILE, users)
        log_audit("make_admin", admin_id, uid)
        return jsonify({"success": True, "message": "Admin granted!"})
    return jsonify({"success": False, "message": "Unknown action"})

@app.route("/admin/tasks")
@admin_required
def admin_tasks():
    tasks = load(TASKS_FILE)
    tl = []
    for tid, td in tasks.items():
        tc = dict(td); tc["id"] = tid; tl.append(tc)
    tl.sort(key=lambda x: x.get("created",""), reverse=True)
    lang = session.get("lang", "en")
    return render_template("admin/tasks.html", tasks=tl, lang=lang)

@app.route("/admin/create_task", methods=["POST"])
@admin_required
def admin_create_task():
    lang = session.get("lang", "en")
    title = request.form.get("title","").strip()[:200]
    if not title:
        return jsonify({"success": False, "message": t("fill_all_fields", lang)})
    tid = f"TASK_{short_id()}"
    tasks = load(TASKS_FILE)
    tasks[tid] = {"id": tid, "title": title,
                  "description": request.form.get("description","").strip()[:1000],
                  "platform": request.form.get("platform","other"),
                  "task_type": request.form.get("task_type","other"),
                  "link": request.form.get("link","").strip()[:500],
                  "reward": float(request.form.get("reward",0)),
                  "currency": request.form.get("currency","naira"),
                  "max_users": int(request.form.get("max_users",100)),
                  "status": "active", "completed_by": [],
                  "created": now_str(), "created_by": session["user_id"]}
    save(TASKS_FILE, tasks)
    log_audit("create_task", session["user_id"], tid, float(request.form.get("reward",0)))
    return jsonify({"success": True, "message": t("task_created", lang)})

@app.route("/admin/delete_task", methods=["POST"])
@admin_required
def admin_delete_task():
    lang = session.get("lang", "en")
    tid = request.form.get("task_id")
    tasks = load(TASKS_FILE)
    if tid in tasks:
        del tasks[tid]; save(TASKS_FILE, tasks)
        log_audit("delete_task", session["user_id"], tid)
        return jsonify({"success": True, "message": t("task_deleted", lang)})
    return jsonify({"success": False, "message": "Not found"})

@app.route("/admin/submissions")
@admin_required
def admin_submissions():
    subs = load(SUBMISSIONS_FILE)
    tasks = load(TASKS_FILE)
    users = load(USERS_FILE)
    status = request.args.get("status", "pending")
    sl = []
    for sid, s in subs.items():
        if s.get("status") != status: continue
        task = tasks.get(s.get("task_id"), {})
        user = users.get(s.get("user_id"), {})
        sc = dict(s); sc["sub_id"] = sid
        sc["task_title"] = task.get("title","Unknown")
        sc["user_name"] = user.get("name","Unknown")
        sc["user_email"] = user.get("email","")
        sl.append(sc)
    sl.sort(key=lambda x: x.get("submitted_at",""), reverse=True)
    lang = session.get("lang", "en")
    return render_template("admin/submissions.html", submissions=sl, status=status, lang=lang)

@app.route("/admin/review_submission", methods=["POST"])
@admin_required
def admin_review_submission():
    sid = request.form.get("sub_id")
    action = request.form.get("action")
    note = request.form.get("note","").strip()[:300]
    admin_id = session["user_id"]
    lang = session.get("lang", "en")
    subs = load(SUBMISSIONS_FILE)
    if sid not in subs:
        return jsonify({"success": False, "message": "Not found"})
    sub = subs[sid]
    uid = sub["user_id"]
    tid = sub["task_id"]
    if action == "approve":
        subs[sid].update({"status":"approved","reviewed_at":now_str(),"note":note})
        save(SUBMISSIONS_FILE, subs)
        reward = sub.get("reward",0); curr = sub.get("currency","naira")
        upd_wallet(uid, curr, reward)
        upd_wallet(uid, "completed_tasks", 1)
        upd_wallet(uid, "pending_tasks", -1)
        upd_wallet(uid, "total_earned", reward)
        tasks = load(TASKS_FILE)
        if tid in tasks:
            cb = tasks[tid].get("completed_by",[])
            if uid not in cb: cb.append(uid)
            tasks[tid]["completed_by"] = cb
            save(TASKS_FILE, tasks)
        # Referral bonus check
        users = load(USERS_FILE)
        ref_by = users.get(uid,{}).get("referred_by")
        if ref_by:
            refs = load(REFERRALS_FILE)
            ref_list = refs.get(ref_by,[])
            settings = get_settings()
            for i, r in enumerate(ref_list):
                if r.get("referred_id") == uid and not r.get("bonus_paid"):
                    r["tasks_done"] = r.get("tasks_done",0)+1
                    if r["tasks_done"] >= settings["referral_tasks_needed"]:
                        r["bonus_paid"] = True
                        bonus = settings["referral_bonus"]
                        upd_wallet(ref_by, "naira", bonus)
                        upd_wallet(ref_by, "referral_bonus_earned", bonus)
                        add_notif(ref_by, f"🎁 {t('referral_bonus_earned', lang)} +₦{bonus}", "success")
                    ref_list[i] = r
            refs[ref_by] = ref_list; save(REFERRALS_FILE, refs)
        symbol = "₦" if curr=="naira" else "$"
        add_notif(uid, f"✅ {t('submission_approved', lang)} +{symbol}{reward:,.2f}", "success")
        log_audit("approve_sub", admin_id, sid, reward)
        return jsonify({"success": True, "message": t("submission_approved", lang)})
    elif action == "reject":
        subs[sid].update({"status":"rejected","reviewed_at":now_str(),"note":note})
        save(SUBMISSIONS_FILE, subs)
        upd_wallet(uid, "pending_tasks", -1)
        add_notif(uid, f"❌ {t('submission_rejected', lang)} — {note or 'Proof invalid'}", "error")
        log_audit("reject_sub", admin_id, sid)
        return jsonify({"success": True, "message": t("submission_rejected", lang)})
    return jsonify({"success": False, "message": "Unknown action"})

@app.route("/admin/withdrawals")
@admin_required
def admin_withdrawals():
    wds = load(WITHDRAWALS_FILE)
    users = load(USERS_FILE)
    status = request.args.get("status","pending")
    wl = []
    for wid, w in wds.items():
        if w.get("status") != status: continue
        user = users.get(w.get("user_id"),{})
        wc = dict(w); wc["wd_id"] = wid
        wc["user_name"] = user.get("name","Unknown")
        wc["user_email"] = user.get("email","")
        wl.append(wc)
    wl.sort(key=lambda x: x.get("requested_at",""), reverse=True)
    lang = session.get("lang", "en")
    return render_template("admin/withdrawals.html", withdrawals=wl, status=status, lang=lang)

@app.route("/admin/process_withdrawal", methods=["POST"])
@admin_required
def admin_process_withdrawal():
    wid = request.form.get("wd_id")
    action = request.form.get("action")
    note = request.form.get("note","").strip()
    admin_id = session["user_id"]
    lang = session.get("lang", "en")
    wds = load(WITHDRAWALS_FILE)
    if wid not in wds:
        return jsonify({"success": False, "message": "Not found"})
    wd = wds[wid]; uid = wd["user_id"]
    if action == "approve":
        wds[wid].update({"status":"approved","processed_at":now_str(),"note":note})
        save(WITHDRAWALS_FILE, wds)
        upd_wallet(uid, "total_withdrawn", wd.get("amount",0))
        add_notif(uid, f"✅ {t('withdrawal_approved', lang)} Net: ₦{wd.get('net',0):,.2f}", "success")
        log_audit("approve_wd", admin_id, wid, wd.get("amount",0))
        return jsonify({"success": True, "message": t("withdrawal_approved", lang)})
    elif action == "reject":
        wds[wid].update({"status":"rejected","processed_at":now_str(),"note":note})
        save(WITHDRAWALS_FILE, wds)
        curr = wd.get("currency","naira")
        upd_wallet(uid, curr, wd.get("amount",0))
        add_notif(uid, f"❌ {t('withdrawal_rejected', lang)}", "error")
        log_audit("reject_wd", admin_id, wid)
        return jsonify({"success": True, "message": t("withdrawal_rejected", lang)})
    return jsonify({"success": False, "message": "Unknown action"})

@app.route("/admin/broadcast", methods=["GET","POST"])
@admin_required
def admin_broadcast():
    lang = session.get("lang", "en")
    if request.method == "POST":
        msg = request.form.get("message","").strip()[:1000]
        ntype = request.form.get("type","info")
        if not msg:
            return jsonify({"success": False, "message": t("fill_all_fields", lang)})
        users = load(USERS_FILE)
        count = 0
        for k, u in users.items():
            if not u.get("is_admin"):
                add_notif(k, f"📢 {t('admin_notice', lang)}: {msg}", ntype)
                count += 1
        log_audit("broadcast", session["user_id"], f"to {count} users")
        return jsonify({"success": True, "message": f"{t('broadcast_sent', lang)} ({count})"})
    return render_template("admin/broadcast.html", lang=lang)

@app.route("/admin/settings", methods=["GET","POST"])
@admin_required
def admin_settings():
    lang = session.get("lang", "en")
    if request.method == "POST":
        s = get_settings()
        for k in ["referral_bonus","referral_tasks_needed","withdrawal_fee_percent",
                  "min_withdrawal","max_withdrawal","exchange_rate"]:
            v = request.form.get(k)
            if v:
                s[k] = float(v)
        s["site_name"] = request.form.get("site_name", s["site_name"])[:50]
        s["maintenance"] = request.form.get("maintenance") == "1"
        s["announcement"] = request.form.get("announcement", "").strip()[:300]
        save(SETTINGS_FILE, s)
        return jsonify({"success": True, "message": t("settings_saved", lang)})
    return render_template("admin/settings.html", settings=get_settings(), lang=lang)

@app.route("/admin/logs")
@admin_required
def admin_logs():
    logs = sorted(load(AUDIT_FILE).values(), key=lambda x: x.get("time",""), reverse=True)[:100]
    lang = session.get("lang", "en")
    return render_template("admin/logs.html", logs=logs, lang=lang)

@app.route("/admin/transfers")
@admin_required
def admin_transfers():
    trs = load(TRANSFERS_FILE)
    users = load(USERS_FILE)
    tl = []
    for tid, tr in trs.items():
        tc = dict(tr); tc["tr_id"] = tid
        tc["sender_name"] = users.get(tr.get("sender_id"),{}).get("name","?")
        tc["receiver_name"] = users.get(tr.get("receiver_id"),{}).get("name","?")
        tl.append(tc)
    tl.sort(key=lambda x: x.get("time",""), reverse=True)
    lang = session.get("lang", "en")
    return render_template("admin/transfers.html", transfers=tl[:100], lang=lang)

@app.route("/admin/reverse_transfer", methods=["POST"])
@admin_required
def admin_reverse_transfer():
    trid = request.form.get("tr_id")
    admin_id = session["user_id"]
    lang = session.get("lang", "en")
    trs = load(TRANSFERS_FILE)
    if trid not in trs:
        return jsonify({"success": False, "message": "Not found"})
    tr = trs[trid]
    if tr.get("status") == "reversed":
        return jsonify({"success": False, "message": "Already reversed"})
    upd_wallet(tr["receiver_id"], "naira", -tr["amount"])
    upd_wallet(tr["sender_id"], "naira", tr["amount"])
    trs[trid].update({"status":"reversed","reversed_at":now_str(),"reversed_by":admin_id})
    save(TRANSFERS_FILE, trs)
    add_notif(tr["sender_id"], f"🔄 Transfer ₦{tr['amount']:,.2f} reversed → refunded", "info")
    add_notif(tr["receiver_id"], f"⚠️ Transfer ₦{tr['amount']:,.2f} reversed by admin", "warning")
    log_audit("reverse_transfer", admin_id, trid, tr["amount"])
    return jsonify({"success": True, "message": t("transfer_reversed", lang)})

# ============================================================
# RUN
# ============================================================
@app.route("/admin/add_user", methods=["POST"])
@admin_required
def admin_add_user():
    """Admin creates a user account without affecting admin session"""
    lang = session.get("lang", "en")
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    name = request.form.get("name", "").strip()[:100]

    if not email or not password or not name:
        return jsonify({"success": False, "message": t("fill_all_fields", lang)})
    if len(password) < 6:
        return jsonify({"success": False, "message": t("password_short", lang)})
    if "@" not in email:
        return jsonify({"success": False, "message": t("fill_all_fields", lang)})

    users = load(USERS_FILE)
    for u in users.values():
        if u.get("email", "").lower() == email:
            return jsonify({"success": False, "message": t("email_exists", lang)})

    uid = f"SP{short_id()}"
    is_admin_account = request.form.get("is_admin") == "1"
    user_data = {
        "id": uid, "name": name, "email": email,
        "password": hash_pw(password), "is_admin": is_admin_account,
        "banned": False, "verified": True,
        "created": now_str(), "last_login": now_str(),
        "referral_code": uid, "referred_by": None, "lang": "en"
    }
    users[uid] = user_data
    save(USERS_FILE, users)
    get_wallet(uid)
    add_notif(uid, f"🎉 Welcome to {APP_NAME}! Start earning today.", "success")
    log_audit("admin_create_user", session["user_id"], uid)
    return jsonify({"success": True, "message": f"✅ Account created: {name} ({uid})", "user_id": uid})

# Auto-create admin on import (for gunicorn workers)
ensure_admin()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 55)
    print(f"  🚀 {APP_NAME} Web App v{VERSION}")
    print(f"  🌐 URL: http://0.0.0.0:{port}")
    print(f"  👑 Admin Email: {ADMIN_EMAIL}")
    print("=" * 55)
    app.run(host="0.0.0.0", port=port, debug=False)
