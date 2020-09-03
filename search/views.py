from django.shortcuts import render
from django.db import connection
from .models import Sites
from django.core.paginator import Paginator
from django.http import QueryDict
import string
from nltk.corpus import wordnet
from nltk.tokenize import  word_tokenize
from nltk.corpus import stopwords
from django.db.models.expressions import RawSQL

# Create your views here.

AI_keys = [ 'heuristics','robotics','artificial','artificial intelligence','ai','regression','mining', 
'sensing', 'ocr', 'rnn','actuators','ani','unsupervised', 'agi','agent','classification', 'neural', 
'nlg', 'intelligence','supervised','nlp', 'asi', 'heuristic', 'ml', 'learning', 'machine learning']

GV_keys = ['graphical','animation','maps', 'video','imaging', 'image','media','visualization', 'game',
 'controller','display', 'films','vision', 'pixelation','diffusion', 'pixel','visual', 'frame']

SE_keys = ['implementation','laravel', 'foxpro', 'mercurial', 'chyrp', 'vrml', 'programming', 'msxml', 'awk', 'abap', 
'language', 'ms', 'dreamweaver', 'unix','xaraya','rapidweaver', 'haskell', 'encoding','coding',
 'asp', 'sqlite', 'ms-windows', 'ado.net', 'mysql', 'management', 'mantisbt', 'assembly', 'zikula', 
 'linked','rails','jquery', 'vhdl', 'cvs','visual', 'vi', 'learning',
 'apl', 'webkit', 'lisp', 'code', 'c++', 'extreme', 'html', 'gnustep', 'scala', 'sed', 'yui', 'wap/wml',
 'openssl', 'development', 'intercal', 'corba', 'stata', 'openid', 'python', 'regex', 'xsl', 'ml', 'alice', 
 'oauth', 'fortran', 'erlang', 'cookies', 'mandriva', '.net', 'ms-dos', 'verilog', 'wsgi', 'postgresql', 'waterfall',
  'ruby', 'unified', 'umbraco', 'netcdf', 'delphi', 'rexx', 'latex', 'shells', 'ncurses', 'ocaml', 'wsdl', 'nxt-g', 
  'ravendb', 'agile', 'actionscript', 'postscript', 'json', 'inspector', 'forth', 'c#', 'url', 'mdn', 'pl/sql', 
  'smalltalk', 'drupal', 'modula-3', 'ascii', 'cascading', 'mpi', 'php', 'opencl', 'linux', 'wcf', 'simula',
   'idl', 'pi', 'backbone.js', 'ffmpeg', 'cobol', 'javascript', 'elixir', 'cgi', 'sql', 'cakephp', 'ada', 
   'object-oriented', 'go', 'gate', 'bbc', 'debugging','snobol', 'cocoa', 'swift', 'git', 'perl', 'web',
    'labview', 'program', 'imagemagick', 'robots', 'asp.net', 'soap', 'subversion', 'ssh', 'ubuntu', 'pl/i', 
    'algol', 's-plus', 'codeigniter', 'prototyping', 'on', 'raspberry','software', 'modeling', 'sgml', 'ssi',
     'xml', 'phprojekt', 'java', 'smil', 'and', 'c', 'dom','metaquotes', 'tex','r', 
     'f#', 'objective-c', 'prolog', 'pascal', 'sas']

ARC_keys = [ 'micro', 'multiprocessing','microarchitecture','neumann','hardware',
 'operating', 'cache', 'electronics', 'digital','register', 'multicycle',
 'computer', 'storage', 'arithmetic', 'floating','architectures','architecture',
 'cpu', 'assembly', 'instruction', 'os']

NET_keys = ['port', 'icmp', 'smtp', 'nat', 'gateways', 'vpn', 'routers' , 'p2p', 'man', 'rss', 'e.', 'localhost', 
'ethernet', 'firewall', 'protocol', 'c.', 'client', 'peer', 'ip', 'packet', 'url', 'mac', 'repeaters', 'http', 'ftp',
 'adapter', 'dhcp','lan', 'tcp', 'hubs','bridges', 'udp', 'address', 'tcp', 'wan',
  'voip', 'san', 'www', 'switches','server','network','web']

DB_keys = ['sql', 'microsoft', 'sap', 'neo4j', 'teradata', 'server', 'mongodb','seqel', 'robomongo', 
'db2', 'index', 'hadoop', 'toad', 'altibase', 'redis', 'informix', 'rdbms', 'ibm', 'clustered', 'phpmyadmin',
 'hash', 'sybase', 'sqlite', 'couchdb','adabas', 'hdfs', 'orientdb', 'query', 'ase',
  'filemaker','mysql', 'mariadb', 'amazonrds', 'cloudera', 'postgressql', 'relational', 'oracle', 'developer',
   'sparse', 'table', 'solarwinds', 'database', 'nosql', 'dbms', 'retrieval','dbvisualizer', 'couchbase']

ALG_keys = [ 'structure', 'binary', 'update', 'stack', 'merging', 'insert', 
'array', 'hashing', 'queue', 'kruskal', 'hanoi', 'set', 'searching', 'graph', 
'knapsack','greedy', 'entity', 'floyd-warshall', 'tree',
'average', 'sorting', 'linked', 'sort', 'huffman', 'traversing', 'list', 'insertion', 'search', 
'fibonacci', 'algorithms','heap', 'complexity', 'data']

dictionary = {
			0 : AI_keys,
			1 : GV_keys,
			2 : SE_keys,
			3 : ARC_keys,
			4 : NET_keys,
			5 : DB_keys,
			6 : ALG_keys
				}
all_classes = [{"name" : "Artificial Intelligence","num":0},
				{"name" :"Graphical visualization","num":1},
				{"name" :"Software Engineering","num":2},
				{"name" : "Architecture And OS","num":3},
				{"name" : "Network","num":4},
				{"name" : "Database","num":5},
				{"name" : "Data Structure And Algorithm","num":6}]

stop_words=set(stopwords.words("english"))

def mainSearchView(request) :
	return render(request , "base.html")

def SearchResultsView(request) :
	if request.method == 'GET':

		query= str(request.GET.get('q')).lower()
		query=query.translate(str.maketrans('','',string.punctuation))
		word_tokens = query.split()

		filtered_sentence = [w for w in word_tokens if not w in stop_words]
		#print(filtered_sentence)
		synonyms= set([])

		count=0
		for x in filtered_sentence:
	        
			for syn in wordnet.synsets(x):
				for l in syn.lemmas() :
					if(count<3):
						if l.name() not in synonyms:
							synonyms.add(l.name())
							count+=1
					else:
						break
			synonyms.add(x)	                        
			count=0

	        
		synonyms_string=' '.join(list(synonyms))
		print(synonyms_string)
		query = synonyms_string.split()
		matched_dic = {}
		if request.GET.get('action') == 'post':
			max_keys=request.GET.get('selected_classes').split(",")
			for i in range(len(max_keys)) :
				max_keys[i]=int(max_keys[i])
		else :
			for key , value in dictionary.items() :
				matched_num = 0
				for word in query :
					if word in value :
						matched_num +=1
						
				matched_dic[key] = matched_num

			#print(matched_dic)

			max_value = max(matched_dic.values())
			if max_value !=0 :
				max_keys = [k for k, v in matched_dic.items() if v == max_value]
			else :
				max_keys=[]



		print("max_keys",max_keys)
		query_by_classes = "SELECT 1 FROM dual WHERE false"
		query_params = []
		if len(max_keys) > 0 :
			query_params.append("\""+request.GET.get('q')+"\"")
			query_by_classes = "SELECT id FROM sites WHERE MATCH(title)AGAINST(%s IN NATURAL LANGUAGE MODE) AND (class = "+str(max_keys[0])

			for i in range(1,len(max_keys)) :
				query_by_classes = query_by_classes + " OR class = " + str(max_keys[i])

			query_by_classes=query_by_classes + ")"
		print(query_by_classes)

	#	with connection.cursor() as cursor:
	#		cursor.execute("SELECT url,title,first_par FROM sites WHERE MATCH(keywords)AGAINST(%s IN NATURAL LANGUAGE MODE)",[request.GET.get('q')])
		#sites = Sites.objects.raw("SELECT * FROM sites WHERE MATCH(keywords)AGAINST(%s IN NATURAL LANGUAGE MODE) LIMIT 100",[request.GET.get('q')])
		#title_matched_sites = Sites.objects.raw('SELECT * FROM sites WHERE MATCH(title)AGAINST( %s IN NATURAL LANGUAGE MODE) LIMIT 5',["\""+request.GET.get('q')+"\""])
		
		#sites = Sites.objects.raw(query_by_classes , query_params)
		# params = []
		# params.append(request.GET.get('q'))
		# if len(query_params) > 0 :
		# 	params.append(request.GET.get('q'))
		# params.append(synonyms_string)
		
		# sites = Sites.objects.raw(
		# 	'(SELECT * FROM sites WHERE MATCH(title)AGAINST( %s IN NATURAL LANGUAGE MODE) LIMIT 2) '+
		# 	query_by_classes+
		# 	'UNION (SELECT * FROM sites WHERE MATCH(keywords)AGAINST(%s IN NATURAL LANGUAGE MODE) )'
		# 	,params)

		s = Sites.objects.raw(
		 	'(SELECT * FROM sites WHERE title = %s LIMIT 2) '
		 	,[request.GET.get('q')])

		for si in s :
			print("title",si.title)

		exact_title_sites = Sites.objects.filter(title=request.GET.get('q'))[0:2]
		#class_matched_sites = Sites.objects.filter(id__in=RawSQL(query_by_classes,query_params))[0:6]

		l=[]
		[l.append(x.id) for x in exact_title_sites]
		class_matched_sites = (

			Sites.objects.filter(id__in=RawSQL(query_by_classes,query_params)).exclude(id__in=l)[0:4]
		)

		[l.append(x.id) for x in class_matched_sites]

		title_matched_sites = (

			Sites.objects.filter(id__in=RawSQL("(SELECT id FROM sites WHERE MATCH(title)AGAINST( %s IN NATURAL LANGUAGE MODE))",[request.GET.get('q')])).exclude(id__in=l)[0:4]
		)

		[l.append(x.id) for x in title_matched_sites]

		keywords_matched_sites = (

			Sites.objects.filter(id__in=RawSQL("(SELECT id FROM sites WHERE MATCH(keywords)AGAINST( %s IN NATURAL LANGUAGE MODE))",[synonyms_string])).exclude(id__in=l)
		)

		#title_matched_sites = Sites.objects.filter(id__in=RawSQL("(SELECT id FROM sites WHERE MATCH(title)AGAINST( %s IN NATURAL LANGUAGE MODE))",[request.GET.get('q')]))
		
		#keywords_matched_sites = Sites.objects.filter(id__in=RawSQL("(SELECT id FROM sites WHERE MATCH(keywords)AGAINST( %s IN NATURAL LANGUAGE MODE))",[synonyms_string]))

		sites = exact_title_sites.union(class_matched_sites).union(title_matched_sites).union(keywords_matched_sites)

		exact_title_len = len(exact_title_sites)
		class_matched_len = len(class_matched_sites)
		title_matched_len = len(title_matched_sites)
		keywords_matched_len = len(keywords_matched_sites)


		print("exact_title_len",exact_title_len)
		print("class_matched_len",class_matched_len)
		print("title_matched_len",title_matched_len)
		print("keywords_matched_len",keywords_matched_len)



		paginator = Paginator(sites, 12) # Show 25 contacts per page.
		page_number = request.GET.get('page')
		page_obj = paginator.get_page(page_number)
		
		ordinary_dict = {'q' : request.GET.get('q')}
		query_dict = QueryDict('', mutable=True)
		query_dict.update(ordinary_dict)
		
		print(query_dict.urlencode())

	# if request.GET.get('action') == 'post':
	# 	print("hiiiiiiiiii")
	# 	return render(request , "main.html",{'sites' : page_obj  , 'searched' : request.GET.get('q') ,
	# 		"base_url" : query_dict.urlencode(),"exact_title_len":exact_title_len,"class_matched_len":class_matched_len,
	# 		"title_matched_len":title_matched_len,"keywords_matched_len":keywords_matched_len,"class_search": max_keys ,"all_classes":all_classes})
	# else :
		return render(request , "search.html",{'sites' : page_obj  , 'searched' : request.GET.get('q') ,
			"base_url" : query_dict.urlencode(),"exact_title_len":exact_title_len,"class_matched_len":class_matched_len,
			"title_matched_len":title_matched_len,"keywords_matched_len":keywords_matched_len,"class_search": max_keys ,"all_classes":all_classes})
	
	if request.method == 'POST':
		query= str(request.POST.get('q')).lower()
		query=query.translate(str.maketrans('','',string.punctuation))
		word_tokens = query.split()

		filtered_sentence = [w for w in word_tokens if not w in stop_words]
		#print(filtered_sentence)
		synonyms= set([])

		count=0
		for x in filtered_sentence:
	        
			for syn in wordnet.synsets(x):
				for l in syn.lemmas() :
					if(count<3):
						if l.name() not in synonyms:
							synonyms.add(l.name())
							count+=1
					else:
						break
			synonyms.add(x)	                        
			count=0

	        
		synonyms_string=' '.join(list(synonyms))
		print(synonyms_string)
		query = synonyms_string.split()
		matched_dic = {}

		max_keys_name = request.POST.getlist('option')
		max_keys = []
		for c in all_classes :
			if c["name"] in max_keys_name :
				max_keys.append(c["num"])
			
		print("max_keys",max_keys)
		# for k in range(len(max_keys)):
		# 	max_keys[k]=int(max_keys[k])

		
		query_by_classes = "SELECT 1 FROM dual WHERE false"
		query_params = []
		if len(max_keys) > 0 :
			query_params.append("\""+request.POST.get('q')+"\"")
			query_by_classes = "SELECT id FROM sites WHERE MATCH(title)AGAINST(%s IN NATURAL LANGUAGE MODE) AND (class = "+str(max_keys[0])

			for i in range(1,len(max_keys)) :
				query_by_classes = query_by_classes + " OR class = " + str(max_keys[i])

			query_by_classes=query_by_classes + ")"
		print(query_by_classes)



		s = Sites.objects.raw(
		 	'(SELECT * FROM sites WHERE title = %s LIMIT 2) '
		 	,[request.POST.get('q')])

		for si in s :
			print("title",si.title)

		exact_title_sites = Sites.objects.filter(title=request.POST.get('q'))[0:2]
		#class_matched_sites = Sites.objects.filter(id__in=RawSQL(query_by_classes,query_params))[0:6]

		l=[]
		[l.append(x.id) for x in exact_title_sites]
		class_matched_sites = (

			Sites.objects.filter(id__in=RawSQL(query_by_classes,query_params)).exclude(id__in=l)[0:4]
		)

		[l.append(x.id) for x in class_matched_sites]

		title_matched_sites = (

			Sites.objects.filter(id__in=RawSQL("(SELECT id FROM sites WHERE MATCH(title)AGAINST( %s IN NATURAL LANGUAGE MODE))",[request.GET.get('q')])).exclude(id__in=l)[0:4]
		)

		[l.append(x.id) for x in title_matched_sites]

		keywords_matched_sites = (

			Sites.objects.filter(id__in=RawSQL("(SELECT id FROM sites WHERE MATCH(keywords)AGAINST( %s IN NATURAL LANGUAGE MODE))",[synonyms_string])).exclude(id__in=l)
		)


		sites = exact_title_sites.union(class_matched_sites).union(title_matched_sites).union(keywords_matched_sites)

		exact_title_len = len(exact_title_sites)
		class_matched_len = len(class_matched_sites)
		title_matched_len = len(title_matched_sites)
		keywords_matched_len = len(keywords_matched_sites)


		print("exact_title_len",exact_title_len)
		print("class_matched_len",class_matched_len)
		print("title_matched_len",title_matched_len)
		print("keywords_matched_len",keywords_matched_len)

		paginator = Paginator(sites, 12) # Show 25 contacts per page.
		page_number = request.POST.get('page')
		page_obj = paginator.get_page(page_number)
		
		ordinary_dict = {'q' : request.POST.get('q')}
		query_dict = QueryDict('', mutable=True)
		query_dict.update(ordinary_dict)
		
		print(query_dict.urlencode())

		return render(request , "search.html",{'sites' : page_obj  , 'searched' : request.POST.get('q'),
			"base_url" : query_dict.urlencode(),"exact_title_len":exact_title_len,"class_matched_len":class_matched_len,
			"title_matched_len":title_matched_len,"keywords_matched_len":keywords_matched_len,"class_search": max_keys ,"all_classes":all_classes})


# def SearchResultsView2(request):
	
# 	if request.method == 'POST':

# 		query= str('database').lower()
# 		query=query.translate(str.maketrans('','',string.punctuation))
# 		word_tokens = query.split()

# 		filtered_sentence = [w for w in word_tokens if not w in stop_words]
# 		#print(filtered_sentence)
# 		synonyms= set([])

# 		count=0
# 		for x in filtered_sentence:
	        
# 			for syn in wordnet.synsets(x):
# 				for l in syn.lemmas() :
# 					if(count<3):
# 						if l.name() not in synonyms:
# 							synonyms.add(l.name())
# 							count+=1
# 					else:
# 						break
# 			synonyms.add(x)	                        
# 			count=0

	        
# 		synonyms_string=' '.join(list(synonyms))
# 		print(synonyms_string)
# 		query = synonyms_string.split()
# 		matched_dic = {}

# 		max_keys = [0]


# 		print("max_keys",max_keys)
# 		query_by_classes = "SELECT 1 FROM dual WHERE false"
# 		query_params = []
# 		if len(max_keys) > 0 :
# 			query_params.append("\""+'database'+"\"")
# 			query_by_classes = "SELECT id FROM sites WHERE MATCH(title)AGAINST(%s IN NATURAL LANGUAGE MODE) AND (class = "+str(max_keys[0])

# 			for i in range(1,len(max_keys)) :
# 				query_by_classes = query_by_classes + " OR class = " + str(max_keys[i])

# 			query_by_classes=query_by_classes + ")"
# 		print(query_by_classes)



# 		# s = Sites.objects.raw(
# 		#  	'(SELECT * FROM sites WHERE title = %s LIMIT 2) '
# 		#  	,['database'])

# 		# for si in s :
# 		# 	print("title",si.title)

# 		exact_title_sites = Sites.objects.filter(title='database')[0:2]
# 		#class_matched_sites = Sites.objects.filter(id__in=RawSQL(query_by_classes,query_params))[0:6]

# 		l=[]
# 		[l.append(x.id) for x in exact_title_sites]
# 		class_matched_sites = (

# 			Sites.objects.filter(id__in=RawSQL(query_by_classes,query_params)).exclude(id__in=l)[0:4]
# 		)

# 		[l.append(x.id) for x in class_matched_sites]

# 		title_matched_sites = (

# 			Sites.objects.filter(id__in=RawSQL("(SELECT id FROM sites WHERE MATCH(title)AGAINST( %s IN NATURAL LANGUAGE MODE))",[request.GET.get('q')])).exclude(id__in=l)[0:4]
# 		)

# 		[l.append(x.id) for x in title_matched_sites]

# 		keywords_matched_sites = (

# 			Sites.objects.filter(id__in=RawSQL("(SELECT id FROM sites WHERE MATCH(keywords)AGAINST( %s IN NATURAL LANGUAGE MODE))",[synonyms_string])).exclude(id__in=l)[0:4]
# 		)


# 		sites = exact_title_sites.union(class_matched_sites).union(title_matched_sites).union(keywords_matched_sites)

# 		exact_title_len = len(exact_title_sites)
# 		class_matched_len = len(class_matched_sites)
# 		title_matched_len = len(title_matched_sites)
# 		keywords_matched_len = len(keywords_matched_sites)

# 		print("exact_title_len",exact_title_len)
# 		print("class_matched_len",class_matched_len)
# 		print("title_matched_len",title_matched_len)
# 		print("keywords_matched_len",keywords_matched_len)

# 		paginator = Paginator(sites, 12) # Show 25 contacts per page.
# 		page_number = request.POST.get('page')
# 		page_obj = paginator.get_page(page_number)
		
# 		ordinary_dict = {'q' : 'database'}
# 		query_dict = QueryDict('', mutable=True)
# 		query_dict.update(ordinary_dict)
		
# 		print(query_dict.urlencode())

# 	if request.is_ajax():
# 		return render(request , "base.html")

# 	return render(request , "search.html",{'sites' : page_obj  , 'searched' : 'database',
# 		"base_url" : query_dict.urlencode(),"exact_title_len":exact_title_len,"class_matched_len":class_matched_len,
# 		"title_matched_len":title_matched_len,"keywords_matched_len":keywords_matched_len,"class_search": max_keys ,"all_classes":all_classes})
