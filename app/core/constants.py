"""
Domain constants shared across the application (Admin, Seeding, etc.)
"""

# Standard Vehicle Types
VEHICLE_TYPES = [
    ("sedan", "Sedan (Ekonomik - 3 Pax)"),
    ("luxury_sedan", "Lüks Sedan (VIP - 3 Pax)"),
    ("vito", "Mercedes Vito (Minivan - 7 Pax)"),
    ("vito_vip", "Mercedes Vito VIP (Ultra Lüks - 6 Pax)"),
    ("sprinter", "Mercedes Sprinter (Minibüs - 16 Pax)"),
    ("sprinter_vip", "Mercedes Sprinter VIP (Deri Koltuk - 10-14 Pax)"),
    ("midibus", "Midibüs (27-31 Pax)"),
    ("bus", "Otobüs (45+ Pax)")
]

# Standard Locations for Dropdowns
ISTANBUL_LOCATIONS = [
    ("İstanbul Havalimanı (IST)", "İstanbul Havalimanı (IST)"),
    ("Sabiha Gökçen Havalimanı (SAW)", "Sabiha Gökçen Havalimanı (SAW)"),
    ("Sultanahmet (Fatih)", "Sultanahmet (Fatih)"),
    ("Taksim (Beyoğlu)", "Taksim (Beyoğlu)"),
    ("Beşiktaş", "Beşiktaş"),
    ("Kadıköy", "Kadıköy"),
    ("Şişli", "Şişli"),
    ("Üsküdar", "Üsküdar"),
    ("Adalar", "Adalar"),
    ("Arnavutköy", "Arnavutköy"),
    ("Ataşehir", "Ataşehir"),
    ("Avcılar", "Avcılar"),
    ("Bağcılar", "Bağcılar"),
    ("Bahçelievler", "Bahçelievler"),
    ("Bakırköy", "Bakırköy"),
    ("Başakşehir", "Başakşehir"),
    ("Bayrampaşa", "Bayrampaşa"),
    ("Beykoz", "Beykoz"),
    ("Beylikdüzü", "Beylikdüzü"),
    ("Büyükçekmece", "Büyükçekmece"),
    ("Çatalca", "Çatalca"),
    ("Çekmeköy", "Çekmeköy"),
    ("Esenler", "Esenler"),
    ("Esenyurt", "Esenyurt"),
    ("Eyüpsultan", "Eyüpsultan"),
    ("Fatih", "Fatih"),
    ("Gaziosmanpaşa", "Gaziosmanpaşa"),
    ("Güngören", "Güngören"),
    ("Kağıthane", "Kağıthane"),
    ("Kartal", "Kartal"),
    ("Küçükçekmece", "Küçükçekmece"),
    ("Maltepe", "Maltepe"),
    ("Pendik", "Pendik"),
    ("Sancaktepe", "Sancaktepe"),
    ("Sarıyer", "Sarıyer"),
    ("Silivri", "Silivri"),
    ("Sultanbeyli", "Sultanbeyli"),
    ("Sultangazi", "Sultangazi"),
    ("Şile", "Şile"),
    ("Tuzla", "Tuzla"),
    ("Ümraniye", "Ümraniye"),
    ("Zeytinburnu", "Zeytinburnu")
]

# Features Configuration
FEATURE_DEFINITIONS = {
    "wifi": ("📶", "Ücretsiz Wi-Fi"),
    "ac": ("❄️", "Klima"),
    "water": ("💧", "Ücretsiz Su"),
    "leather": ("💺", "Deri Koltuk"),
    "usb": ("🔋", "USB Şarj"),
    "bluetooth": ("🎵", "Bluetooth Müzik"),
    "meeting": ("🤝", "Karşılama Hizmeti"),
    "disinfection": ("🧼", "Dezenfekte Araç"),
    "tv": ("📺", "TV / Eğlence"),
    "baby_seat": ("👶", "Bebek Koltuğu"),
    "table": ("🍽️", "Masa"),
    "fridge": ("🧊", "Buzdolabı"),
    "microphone": ("🎤", "Mikrofon"),
    "vip": ("🌟", "VIP Hizmet"),
    "private_driver": ("👔", "Özel Şoför"),
    "large_volume": ("👥", "Geniş İç Hacim")
}

# Derived list for SelectField choices
FEATURE_CHOICES = [(k, f"{v[0]} {v[1]}") for k, v in FEATURE_DEFINITIONS.items()]
