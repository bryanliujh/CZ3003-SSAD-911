from django.db import models
from django.urls import reverse

# Create your models here.
class IncidentReport( models.Model ):
	phone_number = models.CharField(max_length=10)
	nric = models.CharField(max_length=10)
	datetime = models.DateTimeField(auto_now_add=True)
	title = models.TextField(max_length=2000) #change to title
	detail = models.TextField(max_length=10000) #change to title
	location = models.CharField(max_length=1000)
	emergency_level = models.IntegerField(default=1)
	status = models.CharField(max_length=100)
	assigned_to_supervisor = models.CharField(max_length=100)
	longitude = models.FloatField(default=1.3483099)
	latitude = models.FloatField(default=103.68313469999998)

	def get_absolute_url(self):
		return reverse( 'system:detail', kwargs={'pk': self.pk} )

	def __str__( self ):
		 return 'ID: %s, %s %s' % (self.pk,self.phone_number, self.datetime)


from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Role(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	job = models.TextField(max_length=20, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Role.objects.create(user=instance, job='operator')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.role.save()
