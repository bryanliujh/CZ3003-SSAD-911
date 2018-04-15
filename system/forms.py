from django import forms
from .models import IncidentReport

EMERGENCY_LEVEL = (
    (1,'LEVEL 1'),
    (2, 'LEVEL 2'),
    (3,'LEVEL 3'),
)

# Modal Form is bound compared to forms.Form
class AddReportForm( forms.ModelForm ):
	phone_number = forms.CharField( max_length = 10 )
	title = forms.CharField( required = True, widget= forms.TextInput, max_length=1000 )
	detail = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}))
	location = forms.CharField( max_length=1000 )
	emergency_level = forms.ChoiceField( choices = EMERGENCY_LEVEL )
	longitude = forms.CharField(widget=forms.HiddenInput(), initial=1.3483099)
	latitude = forms.CharField(widget=forms.HiddenInput(), initial=103.68313469999998)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in iter(self.fields):
			self.fields[field].widget.attrs.update({
				'class': 'form-control'
			})
        
		self.fields['phone_number'].widget.attrs\
			.update({
				'id': 'phone_number',
			})

		self.fields['nric'].widget.attrs \
			.update({
			'id': 'nric',
		})

		self.fields['location'].widget.attrs\
			.update({
				'id': 'location',
			})
		self.fields['longitude'].widget.attrs\
			.update({
				'id': 'longitude',
			})
		self.fields['latitude'].widget.attrs\
			.update({
				'id': 'latitude',
			})
	
	class Meta: 
		model = IncidentReport
		fields = ['phone_number','nric','title', 'detail', 'location','emergency_level','longitude','latitude' ]
