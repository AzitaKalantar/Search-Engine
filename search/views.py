from django.shortcuts import render
from django.db import connection
from .models import Sites
from django.core.paginator import Paginator
from django.http import QueryDict
import string
from nltk.corpus import wordnet
from nltk.tokenize import  word_tokenize
from nltk.corpus import stopwords
# Create your views here.

AI_keys = ['recognition', 'heuristics', 'turing', 'robotics', 'solving', 'locomotion', 'actuation', 
'electroactive', 'artificial', 'piezo', 'ai', 'regression', 'series', 'language', 'pattern', 'mining', 
'reasoning,', 'knowledge', 'motion', 'social', 'sensing', 'ocr', 'rnn', 'manipulation', 'linear', 'actuators',
'ani', 'deep', 'unsupervised', 'agi', 'processing', 'reinforcement', 'planning', 'perception', 'motors', 'agent',
 'classification', 'neural', 'nlg', 'intelligence', 'and', 'elastic', 'network', 'supervised', 'problem', 'polymers',
  'natural', 'nlp', 'asi', 'heuristic', 'ml', 'learning', 'machine']

GV_keys = ['graphical','animation', 'geometry', 'maps', 'video', 'wavelets','imaging', 'image',
 'equations','anisotropic','media','visualization', 'game', 'controller','restoration','display', 'films',
  'vision', 'pixelation','diffusion', 'pixel','visual', 'frame','mobile']

SE_keys = ['implementation','laravel', 'sheets', 'foxpro', 'mercurial', 'chyrp', 'vrml', 'programming', 'msxml', 'awk', 'abap', 
'language', 'ms', 'dreamweaver', 'unix', 'books', 'xaraya', 'tcl/tk', 'rapidweaver', 'haskell', 'encoding', 'coding',
 'asp', 'sqlite', 'ms-windows', 'ado.net', 'lists', 'pure', 'mysql', 'management', 'mantisbt', 'assembly', 'zikula', 
 'linked','rails', 'functional', 'jquery', 'os', 'vhdl', 'cvs', 'basic', 'visual', 'vi', 'learning', 'engineering',
 'apl', 'webkit', 'lisp', 'code', 'c++', 'extreme', 'html', 'gnustep', 'scala', 'sed', 'yui', 'wap/wml', 'project', 
 'style', 'openssl', 'development', 'intercal', 'corba', 'stata', 'openid', 'python', 'regex', 'xsl', 'ml', 'alice', 
 'oauth', 'fortran', 'erlang', 'cookies', 'mandriva', '.net', 'ms-dos', 'verilog', 'wsgi', 'postgresql', 'waterfall',
  'ruby', 'unified', 'umbraco', 'netcdf', 'delphi', 'rexx', 'latex', 'shells', 'ncurses', 'ocaml', 'wsdl', 'nxt-g', 
  'ravendb', 'agile', 'actionscript', 'postscript', 'json', 'inspector', 'forth', 'c#', 'url', 'mdn', 'pl/sql', 
  'smalltalk', 'drupal', 'modula-3', 'ascii', 'cascading', 'mpi', 'php', 'opencl', 'linux', 'sorting', 'wcf', 'simula',
   'idl', 'pi', 'backbone.js', 'ffmpeg', 'cobol', 'javascript', 'elixir', 'cgi', 'data', 'sql', 'cakephp', 'ada', 
   'object-oriented', 'go', 'gate', 'logo', 'bbc', 'debugging', 'ai', 'snobol', 'cocoa', 'swift', 'git', 'perl', 'web',
    'standards', 'labview', 'program', 'imagemagick', 'robots', 'asp.net', 'soap', 'subversion', 'ssh', 'ubuntu', 'pl/i', 
    'algol', 's-plus', 'codeigniter', 'prototyping', 'on', 'raspberry', 'machine', 'software', 'modeling', 'sgml', 'ssi',
     'xml', 'phprojekt', 'java', 'smil', 'and', 'c', 'dom', 'network', 'algorithms', 'metaquotes', 'tex', 'access', 'r', 
     'f#', 'objective-c', 'prolog', 'pascal', 'sas']

ARC_keys = [ 'micro', 'multiprocessing','microarchitecture','neumann','hardware',
 'operating', 'cache', 'electronics', 'digital','register', 'multicycle',
 'computer', 'storage', 'arithmetic', 'floating', 'on', 'unit', 'architectures', 'computing','architecture',
 'cpu', 'assembly', 'point', 'instruction', 'os', 'comparison']

NET_keys = ['port', 'icmp', 'smtp', 'nat', 'gateways', 'vpn', 'routers' , 'p2p', 'man', 'rss', 'e.', 'localhost', 
'ethernet', 'firewall', 'protocol', 'c.', 'client', 'peer', 'ip', 'packet', 'url', 'mac', 'repeaters', 'http', 'ftp',
 'adapter', 'dhcp', 'd', 'lan', 'tcp', 'hubs', 'network', 'bridges', 'udp', 'address', 'tcp','ip', 'wan',
  'voip', 'san', 'www', 'switches','server']

DB_keys = ['sql', 'microsoft', 'sap', 'neo4j', 'teradata', 'server', 'mongodb', 'view', 'seqel', 'robomongo', 
'db2', 'index', 'hadoop', 'toad', 'altibase', 'redis', 'informix', 'rdbms', 'dynamic', 'ibm', 'clustered', 'phpmyadmin',
 'hash', 'sybase', 'sqlite', 'couchdb', 'analyzer', 'performance', 'adabas', 'hdfs', 'orientdb', 'query', 'ase',
  'filemaker', 'key', 'mysql', 'mariadb', 'amazonrds', 'cloudera', 'postgressql', 'relational', 'oracle', 'developer',
   'sparse', 'table', 'solarwinds', 'database', 'nosql', 'dbms', 'retrieval', 'access', 'dbvisualizer', 'couchbase']

ALG_keys = ['delete', 'structure', 'binary', 'update', 'worst', 'stack', 'merging', 'insert', 
'array', 'hashing', 'queue', 'kruskal', 'hanoi', 'set', 'searching', 'dynamic', 'graph', 
'knapsack', 'best', 'deletion', 'of', 'greedy', 'entity', 'floyd-warshall', 'tree', 'tower', 
'average', 'sorting', 'linked', 'sort', 'huffman', 'traversing', 'list', 'insertion', 'search', 
'fibonacci', 'algorithms', 'problem','heap', 'complexity', 'data']

stop_words=set(stopwords.words("english"))

def mainSearchView(request) :
	return render(request , "base.html")

def SearchResultsView(request) :
	
	if request.method == 'GET':

		query= str(request.GET.get('q')).lower()
		query=query.translate(str.maketrans('','',string.punctuation))
		word_tokens = query.split()
		filtered_sentence = [w for w in word_tokens if not w in stop_words]

		synonyms=[]

		count=0
		for x in filtered_sentence:
	        
			for syn in wordnet.synsets(x):
				for l in syn.lemmas() :
					if(count<3):
						if l.name() not in synonyms:
							synonyms.append(l.name())
							count+=1
					else:
						break                        
			count=0
	        
		synonyms_string=' '.join(synonyms)
		query=" ".join([str(query),synonyms_string])
		print(synonyms_string)

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

