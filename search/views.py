from django.shortcuts import render
from django.db import connection
from .models import Sites
from django.core.paginator import Paginator
from django.http import QueryDict
# Create your views here.

def mainSearchView(request) :
	return render(request , "base.html")

def SearchResultsView(request) :
	
	if request.method == 'GET':

	#	with connection.cursor() as cursor:
	#		cursor.execute("SELECT url,title,first_par FROM sites WHERE MATCH(keywords)AGAINST(%s IN NATURAL LANGUAGE MODE)",[request.GET.get('q')])
		#sites = Sites.objects.raw("SELECT * FROM sites WHERE MATCH(keywords)AGAINST(%s IN NATURAL LANGUAGE MODE) LIMIT 100",[request.GET.get('q')])
		#title_matched_sites = Sites.objects.raw('SELECT * FROM sites WHERE MATCH(title)AGAINST( %s IN NATURAL LANGUAGE MODE) LIMIT 5',["\""+request.GET.get('q')+"\""])
		sites = Sites.objects.raw('(SELECT * FROM sites WHERE MATCH(title)AGAINST( %s IN NATURAL LANGUAGE MODE) LIMIT 2) UNION (SELECT * FROM sites WHERE MATCH(keywords)AGAINST(%s IN NATURAL LANGUAGE MODE) )',["\""+request.GET.get('q')+"\"",request.GET.get('q')])
		#print("***title_matched_sites",len(title_matched_sites))
		#print("***sites",len(sites))
		#print("***title_matched_sites and sites", len(title_matched_sites)  )
		paginator = Paginator(sites, 12) # Show 25 contacts per page.
		page_number = request.GET.get('page')
		page_obj = paginator.get_page(page_number)

		
		ordinary_dict = {'q' : request.GET.get('q')}
		query_dict = QueryDict('', mutable=True)
		query_dict.update(ordinary_dict)
		
		print(query_dict.urlencode())

	return render(request , "search.html",{'sites' : page_obj  , 'searched' : request.GET.get('q') ,"base_url" : query_dict.urlencode() })

