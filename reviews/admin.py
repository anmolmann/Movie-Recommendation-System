from django.contrib import admin

# Register your models here.

from .models import Wine, Review, Cluster, Fake

class ReviewAdmin(admin.ModelAdmin):
    model = Review
    list_display = ('wine', 'user_id','rating', 'user_name', 'comment', 'pub_date')
    list_filter = ['pub_date', 'user_name']
    search_fields = ['comment']
    

class ClusterAdmin(admin.ModelAdmin):
    model = Cluster
    list_display = ['name', 'get_members']


admin.site.register(Wine)
admin.site.register(Fake)
admin.site.register(Review, ReviewAdmin)

# We have just imported and registered the model class Cluster,
# and associated a ClusterAdmin class that will better visualise
# cluster information (name and members) in the admin interface.
admin.site.register(Cluster, ClusterAdmin)