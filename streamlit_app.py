# ═══════════════════════════════════════════════════════════════════
#  MARSO | مَارسُو  —  main.py
#  الهيكل الأساسي + نظام التنقل السفلي (MDBottomNavigation)
# ───────────────────────────────────────────────────────────────────
#  pip install kivy==2.2.1 kivymd==1.1.1
#  python main.py
# ═══════════════════════════════════════════════════════════════════

import os
os.environ["KIVY_NO_ENV_CONFIG"] = "1"

from kivy.lang        import Builder
from kivy.core.window import Window
from kivy.metrics     import dp, sp
from kivy.utils       import get_color_from_hex

from kivymd.app           import MDApp
from kivymd.uix.screen    import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

Window.size = (390, 844)   # محاكاة شاشة جوال على الحاسوب

# ─── ألوان هوية Marso البحرية الداكنة ───────────────────────────
# bg:#0A1628  surface:#0F1F3D  card:#1E293B
# accent:#38BDF8  green:#10B981  yellow:#F59E0B
# red:#EF4444  purple:#A78BFA   muted:#64748B

KV = """
#:import H  get_color_from_hex
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

# ──────────────────────────────────────────────────────────
#  بطاقة Placeholder موحّدة (تُعاد في كل شاشة)
# ──────────────────────────────────────────────────────────
<_Ph@MDCard>:
    p_icon : "help-circle-outline"
    p_color: H("#38BDF8")
    p_title: "شاشة"
    p_body : "قريباً..."
    orientation : "vertical"
    radius       : [18,18,18,18]
    padding      : dp(28)
    spacing      : dp(10)
    size_hint_y  : None
    height       : dp(248)
    md_bg_color  : H("#0F1F3D")
    elevation    : 2
    MDIcon:
        icon             : root.p_icon
        theme_icon_color : "Custom"
        icon_color       : root.p_color
        halign           : "center"
        font_size        : dp(66)
    MDLabel:
        text             : root.p_title
        halign           : "center"
        theme_text_color : "Custom"
        text_color       : root.p_color
        font_size        : sp(21)
        bold             : True
        size_hint_y      : None
        height           : dp(34)
    MDLabel:
        text             : root.p_body
        halign           : "center"
        theme_text_color : "Custom"
        text_color       : H("#64748B")
        font_size        : sp(13)
        size_hint_y      : None
        height           : dp(66)

# ──────────────────────────────────────────────────────────
#  1. الشاشة الرئيسية
# ──────────────────────────────────────────────────────────
<HomeScreen>:
    md_bg_color: H("#0A1628")
    ScrollView:
        do_scroll_x: False
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            padding: [dp(16),dp(20),dp(16),dp(20)]
            spacing: dp(14)
            MDLabel:
                text: "📊  القياسات الحيوية والحالة البحرية"
                halign: "center"
                theme_text_color: "Custom"
                text_color: H("#38BDF8")
                font_size: sp(16)
                bold: True
                size_hint_y: None
                height: dp(40)
            _Ph:
                p_icon : "home-analytics"
                p_color: H("#38BDF8")
                p_title: "الرئيسية"
                p_body : "• الموقع + الإحداثيات\
• الحرارة | الرياح | الموج | البحر\
• حالة الصيد (ممتاز / جيد / محظور)"
            MDCard:
                radius: [12,12,12,12]
                md_bg_color: H("#0D2A18")
                size_hint_y: None
                height: dp(50)
                elevation: 0
                MDLabel:
                    text: "✅  نشاط عالٍ للصيد — ظروف مثالية الآن"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: H("#10B981")
                    font_size: sp(14)
                    bold: True

# ──────────────────────────────────────────────────────────
#  2. الرسوم البيانية
# ──────────────────────────────────────────────────────────
<ChartsScreen>:
    md_bg_color: H("#0A1628")
    ScrollView:
        do_scroll_x: False
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            padding: [dp(16),dp(20),dp(16),dp(20)]
            spacing: dp(14)
            MDLabel:
                text: "📈  الرسوم البيانية"
                halign: "center"
                theme_text_color: "Custom"
                text_color: H("#10B981")
                font_size: sp(16)
                bold: True
                size_hint_y: None
                height: dp(40)
            _Ph:
                p_icon : "chart-areaspline"
                p_color: H("#10B981")
                p_title: "البيانات"
                p_body : "• منحنى كفاءة الصيد الساعي\
• منحنى المد والجزر\
• ذروة النشاط وأضعف الساعات"

# ──────────────────────────────────────────────────────────
#  3. الخريطة
# ──────────────────────────────────────────────────────────
<MapScreen>:
    md_bg_color: H("#0A1628")
    ScrollView:
        do_scroll_x: False
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            padding: [dp(16),dp(20),dp(16),dp(20)]
            spacing: dp(14)
            MDLabel:
                text: "🗺️  الخريطة التفاعلية"
                halign: "center"
                theme_text_color: "Custom"
                text_color: H("#F59E0B")
                font_size: sp(16)
                bold: True
                size_hint_y: None
                height: dp(40)
            _Ph:
                p_icon : "map-marker-radius"
                p_color: H("#F59E0B")
                p_title: "الخريطة"
                p_body : "• خريطة Satellite عبر WebView\
• تحديد الموقع بـ GPS\
• مواقع صيد موصى بها"

# ──────────────────────────────────────────────────────────
#  4. الأوقات الفلكية
# ──────────────────────────────────────────────────────────
<SolunarScreen>:
    md_bg_color: H("#0A1628")
    ScrollView:
        do_scroll_x: False
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            padding: [dp(16),dp(20),dp(16),dp(20)]
            spacing: dp(14)
            MDLabel:
                text: "🌙  الأوقات الفلكية"
                halign: "center"
                theme_text_color: "Custom"
                text_color: H("#A78BFA")
                font_size: sp(16)
                bold: True
                size_hint_y: None
                height: dp(40)
            _Ph:
                p_icon : "moon-waning-crescent"
                p_color: H("#A78BFA")
                p_title: "Solunar"
                p_body : "• Major Times و Minor Times\
• مرحلة القمر وعمره بالأيام\
• جدول فلكي أسبوعي"

# ──────────────────────────────────────────────────────────
#  5. الدليل
# ──────────────────────────────────────────────────────────
<GuideScreen>:
    md_bg_color: H("#0A1628")
    ScrollView:
        do_scroll_x: False
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            padding: [dp(16),dp(20),dp(16),dp(20)]
            spacing: dp(14)
            MDLabel:
                text: "📖  دليل الصياد"
                halign: "center"
                theme_text_color: "Custom"
                text_color: H("#38BDF8")
                font_size: sp(16)
                bold: True
                size_hint_y: None
                height: dp(40)
            _Ph:
                p_icon : "book-open-page-variant"
                p_color: H("#38BDF8")
                p_title: "الدليل"
                p_body : "• دليل أسماك الخليج العربي\
• نصائح احترافية للصياد\
• أفضل الطُعوم لكل نوع"

# ──────────────────────────────────────────────────────────
#  الشاشة الجذر — تحتضن كل شيء
# ──────────────────────────────────────────────────────────
<RootScreen>:
    md_bg_color: H("#0A1628")
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: top_bar
            title: "🎣  MARSO | مَارسُو"
            md_bg_color: H("#0F1F3D")
            specific_text_color: H("#38BDF8")
            elevation: 0
            right_action_items: [["refresh", app.on_refresh, "تحديث"]]

        ScreenManager:
            id: sm
            transition: FadeTransition()
            HomeScreen:
                name: "home"
            ChartsScreen:
                name: "charts"
            MapScreen:
                name: "map"
            SolunarScreen:
                name: "solunar"
            GuideScreen:
                name: "guide"

        MDBottomNavigation:
            id: bnav
            panel_color: H("#0F1F3D")
            text_color_normal: H("#334155")
            text_color_active: H("#38BDF8")
            selected_color_background: H("#1E3A5F")
            on_switch_tabs: app.on_tab_switch(*args)

            MDBottomNavigationItem:
                name: "home"
                text: "الرئيسية"
                icon: "home"
            MDBottomNavigationItem:
                name: "charts"
                text: "البيانات"
                icon: "chart-areaspline"
            MDBottomNavigationItem:
                name: "map"
                text: "الخريطة"
                icon: "map-marker"
            MDBottomNavigationItem:
                name: "solunar"
                text: "فلكي"
                icon: "moon-waning-crescent"
            MDBottomNavigationItem:
                name: "guide"
                text: "الدليل"
                icon: "book-open-variant"
"""

# ─── كلاسات الشاشات — فارغة الآن ───────────────────────────────
class HomeScreen(MDScreen):    pass
class ChartsScreen(MDScreen):  pass
class MapScreen(MDScreen):     pass
class SolunarScreen(MDScreen): pass
class GuideScreen(MDScreen):   pass
class RootScreen(MDScreen):    pass

# ─── التطبيق الرئيسي ────────────────────────────────────────────
class MarsoApp(MDApp):

    TITLES = {
        "home"    : "🎣  الرئيسية",
        "charts"  : "📈  الرسوم البيانية",
        "map"     : "🗺️  الخريطة",
        "solunar" : "🌙  الأوقات الفلكية",
        "guide"   : "📖  الدليل",
    }

    def build(self):
        self.theme_cls.theme_style     = "Dark"
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.primary_hue     = "400"
        self.theme_cls.accent_palette  = "Cyan"
        self.theme_cls.material_style  = "M3"
        self.title = "Marso | مَارسُو"
        Builder.load_string(KV)
        return RootScreen()

    def on_tab_switch(self, bnav_obj, tab_obj, tab_label, tab_text):
        name = tab_obj.name
        self.root.ids.sm.current    = name
        self.root.ids.top_bar.title = self.TITLES.get(name, "مَارسُو")

    def on_refresh(self, *args):
        print(f"[Marso] ⟳ تحديث — الشاشة: {self.root.ids.sm.current}")

if __name__ == "__main__":
    MarsoApp().run()
