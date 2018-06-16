import pandas as pd
import numpy as np
import networkx as nx
import networkx as nx
from bokeh.io import show, output_file
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4
import matplotlib as plt
import Levenshtein
from datetime import datetime

class PPHStat:
   	nodes = pd.read_csv("fidesz_nodes.csv")
   	edges = pd.read_csv("fidesz_edges.csv")     
   	nodes=nodes[["ID","name", "address", "org_relations","person_relations"]]
	#tulajlista function
	def ownership(df):
	    df['felt'] = df['Source'].astype(str).str[0]
	    df["felt2"] = df['Target'].astype(str).str[0]
	    own1 = df[(df['felt'] == "P") & (df['felt2'] == "O")]
	    own2 = df[(df['felt'] == "O") & (df['felt2'] == "P")]
	    ownerships=pd.concat([own1,own2])
	    #filter by ownership
	    viszony=pd.read_csv("viszony.csv")
	    viszony=viszony[viszony['tulaj']==1]
	    ownerships=ownerships[(ownerships["node1_role"].isin(viszony['viszony']))|(ownerships["node2_role"].isin(viszony['viszony']))]
	    
	    print(len(ownerships)," relations found.")
	    return ownerships
  
	edges=edges[["Source","Target","id","name","node1_role", "node2_role","start_time","end_time"]]
	ownership(edges)[["Source","Target","id","name","node1_role", "node2_role"]].to_csv("P-O relations.csv", index=False)
	#Search for P-P relations
	def friendship(df):
	    df['felt'] = df['Source'].astype(str).str[0]
	    df["felt2"] = df['Target'].astype(str).str[0]
	    friendships = df[(df['felt'] == "P") & (df['felt2'] == "P")]
	    print(len(friendships),"friendship relations found.")
	    return friendships
	friend_edges=friendship(edges)
	friend_ids=friend_edges["Source"],friend_edges["Target"]
	halo = pd.read_csv('list_firms.csv',index_col=0,header=None)[1]
	kozbesz = pd.read_csv('list_kozbesz.csv',index_col=0,header=None)[1]
	def cleanfirm(firmname):
	    """
	    cleans common misspellings and abbreviations
	    in firms names
	    puts them in lowercase
	    """
	    return firmname.lower().replace(
		'korlátolt felelősségű társaság','kft').replace(
		'korlátolt felelősségü társaság','kft').replace(
		'korlátotl felelősségű társaság','kft').replace(
		'korlátolt felelısségő társaság','kft').replace(
		'korlátolt felelősség társaság','kft').replace(
		'korlátolt felelősségá társaság','kft').replace(
		'korlátolt felelősságű társaság','kft').replace(
		'korlátozott felelősségű társaság','kft').replace(
		'korlátolt felelőségű társaság','kft').replace(
		'kolrátolt felelősségű társaság','kft').replace(
		'korlátol felelősségű társaság','kft').replace(
		'korlát felelősségű társaság','kft').replace(
		'korlátolt felelősségű társaság','kft').replace(
		'korlátolt felelősségő társaság','kft').replace(
		'korlátolt felelősségűbtársaság','kft').replace(
		'korlátolt felelősségű táraság','kft').replace(
		'korlátolt felelősségű táűrsaság','kft').replace(
		'korlátolt felelősségű társasát','kft').replace(
		'korlátolt felelősségű társasád','kft').replace(
		'korlátolt felelősségű társasát','kft').replace(
		' kereskedelmi és szolgáltató',' k & sz').replace(
		' szolgáltató és kereskedelmi',' k & sz').replace(
		'tanácsadó és szolgáltató kft', 't & sz kft').replace(
		'kereskedelmi kft', 'kkft').replace(
		'építőipari kft', 'ékft').replace(
		'betéti társaság','bt').replace(
		'közhasznú társaság','kht').replace(
		'zártkörűen működő részvénytársaság','zrt').replace(
		'részvénytársaság','rt').replace(
		'kft.','kft').replace(
		'bt.','bt').replace(
		'rt.','rt').replace(
		'zrt.','zrt')

		
	def split_lev(narray1,narray2,splitnum=3,limit=0.75):
	    """
	    takes 2 arrays, calcuates pairwise Levenshtein
	    distance rates between them
	    --
	    splits the task to splitnum chunks to save memory
	    returns pairs with similarity higyhar than limit
	    """
	    chunks = np.array_split(narray2,splitnum)
	    dflist = []
	    i = 1
	    for chunk in chunks:
		print(i,' of ',splitnum)
		i += 1
		df = pd.DataFrame(np.array(pd.core.reshape.util.cartesian_product([narray1, chunk])).T)
		df['rate'] = df.apply(lambda x: Levenshtein.ratio(x[0],x[1]),axis=1)
		dflist.append(df[(df['rate'] >= limit)].copy())
	    return pd.concat(dflist)
	df = split_lev(ch,ck,10,0.8)
	df[df['rate'] > 0.9].sort_values('rate').to_csv("mapping.csv")

	##here is the main process
	part  = pd.read_csv('part.csv')
	win_final = pd.read_csv('winner_resolved_final.csv')
	p_o = pd.read_csv('P-O relations.csv')
	fidesz_nodes = pd.read_csv('fidesz_nodes.csv')
	mapping = pd.read_csv('mapping.csv')
	def preproc (part, win_final):
	    filtered_winfinal = win_final[win_final['TEXTSCORE']>0]
	    
	    ossz_kozbesz = pd.merge(part, filtered_winfinal, how = 'inner', on=['UID'])
	    
	    final_kozbesz = ossz_kozbesz[['UID', 'NOOFBIDDERS', 'SUBJECT', 'VALUE', 'CUR', 'VAT', 'VATRATE', 'PUBLIDATE', 'NAME', 'WHITELISTNAME', 'CITY']]
	    
	    final_kozbesz3 = final_kozbesz[(final_kozbesz['CUR'] == 'HUF') & final_kozbesz['NOOFBIDDERS']>0]
	    
	    final_kozbesz3 = final_kozbesz3.reset_index(drop=True)
	    
	    final_kozbesz3['VALUE'] = pd.to_numeric(final_kozbesz3['VALUE'])
	    
	    final_kozbesz3['VATRATE'] = pd.to_numeric(final_kozbesz3['VATRATE'], errors = 'coerce')
	    
	    return final_kozbesz3


	final_kozbesz3 = preproc (part, win_final)


	fidesz_nodes = fidesz_nodes.rename(index=str, columns={'ID': 'Target'})
	p_o = p_o.drop(['name'], axis=1)
	merged_po = pd.merge(p_o, fidesz_nodes, how = 'inner', on = ['Target'])

	fidesz_nodes = fidesz_nodes.rename(index=str, columns={'Target': 'Source'})
	merged_po2 = pd.merge(merged_po, fidesz_nodes, how = 'inner', on = ['Source'])

	merged_po2 = merged_po2.reset_index(drop=True)

	merged_po2['name_x'] = merged_po2['name_x'].apply(cleanfirm)


	####Innentől csináljuk meg az összekötést
	list_name_y = list(set(merged_po2['name_y']))

	dict_name_y = pd.DataFrame()

	for i in list_name_y:
	    filtered_po = merged_po2[merged_po2['name_y'] == i]
	    kuka=pd.DataFrame(list(set(filtered_po['name_x'])))
	    kuka["id"]=[i for x in range(len(kuka))]
	    dict_name_y=dict_name_y.append(kuka, ignore_index=True)
	del kuka

	#dict_name_y[dict_name_y[0].apply(lambda x: 'közgép' in x.lower())]

	#########
	#Joinoljuk a mappingel
	dict_name_y=pd.merge(dict_name_y,mapping, how="left", left_on=0 ,right_on='0')
	dict_name_y=dict_name_y[["id",0,"1"]].dropna()

	############
	#Összehúzzuk a közbesz táblával
	final_kozbesz3['NAME'] = final_kozbesz3['NAME'].apply(cleanfirm)
	final_kozbesz3=final_kozbesz3[["UID","NOOFBIDDERS","VALUE","PUBLIDATE","NAME","CITY"]]

	dict_name_y=pd.merge(dict_name_y,final_kozbesz3, how="left", left_on='1', right_on="NAME")
	dict_name_y["PName"]=dict_name_y["id"]
	dict_name_y=dict_name_y.set_index(["id"])

	############
	def stats(df,start,end):
	    df=df[(df['PUBLIDATE'] > start) & (df['PUBLIDATE'] < end)]
	    stat = pd.DataFrame(columns = ['ID','Nev', 'Nyert','Ertek_ossz', 'Atlag_ertek', 'Atlag_palyazo', 'Min_palyazo', 'Max_palyazo'])
	    stat['ID']=pd.Series(list(set(merged_po2['name_y'])))
	    stat=stat.set_index(['ID'])
	    stat['Nev'] = pd.Series(list(set(merged_po2['name_y'])))
	    stat['Nyert']=df[['PName','UID']].groupby(['PName']).agg(['count'])
	    stat['Ertek_ossz']=df[['PName','VALUE']].groupby(['PName']).agg(['sum'])
	    stat['Atlag_ertek']=df[['PName','VALUE']].groupby(['PName']).agg(['mean'])
	    stat['Atlag_palyazo']=df[['PName','NOOFBIDDERS']].groupby(['PName']).agg(['mean'])
	    stat['Min_palyazo']=df[['PName','NOOFBIDDERS']].groupby(['PName']).agg(['min'])
	    stat['Max_palyazo']=df[['PName','NOOFBIDDERS']].groupby(['PName']).agg(['max'])
	    #df.groupby(['PName']).agg([count'])

	    return stat
	print("to run the gecikereső use stats(df,start,end) function!")
