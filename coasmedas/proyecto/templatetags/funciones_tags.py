import locale
from django.template import Library
register = Library()
# locale.setlocale(locale.LC_ALL, 'en_US')

@register.filter
def total(value, arg):
	return sum(d[arg] for d in value)

@register.filter
def total_prone(value, arg):
	total = 0
	for d in value:
		if d['id']==1:			
			total = total + d[arg]
	return total	

@register.filter
def total_faer(value, arg):
	total = 0
	for d in value:
		if d['id']==2:			
			total = total + d[arg]
	return total	

@register.filter
def format_money_total(value, arg):
	total=sum(d[arg] for d in value)  
	return '${:20,.2f}'.format(total)#locale.currency(total, grouping=True)


@register.filter
def format_money_total_prone(value, arg):
	total = 0
	for d in value:
		if d['id']==1:			
			total = total + d[arg]
	return '${:20,.2f}'.format(total)#locale.currency(total, grouping=True)	

@register.filter
def format_money_total_faer(value, arg):
	total = 0
	for d in value:
		if d['id']==2:			
			total = total + d[arg]
	return '${:20,.2f}'.format(total)#locale.currency(total, grouping=True)	