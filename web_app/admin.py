from django.contrib import admin
from .models import HeroSlide, Event, GalleryCategorie, GalleryUpload, ClientLeads, Testimonies
from import_export.admin import ImportExportModelAdmin

admin.site.register(HeroSlide)

admin.site.register(Event)

admin.site.register(Testimonies)

admin.site.register(GalleryCategorie)

admin.site.register(GalleryUpload)




@admin.register(ClientLeads)
class ClientLeadsAdmin(ImportExportModelAdmin):
    list_display = ["first_name", "last_name", "email", "phone", "address", "date", "service", "message"]
    # form = ReqForm
    list_filter = ["service"]
    search_fields = ["first_name", "last_name", "email", "phone", "address"]
    pass
    


