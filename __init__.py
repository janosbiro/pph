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
import os
from tkinter import filedialog as tkFileDialog
from tkinter import *
import os

class PPHStat:
    '''root = tkinter.Tk()
    root.withdraw() #use to hide tkinter window
    
    currdir = os.getcwd()
    tempdir = tkFileDialog.askdirectory(parent=root, initialdir=currdir, title='Please select a directory')
    if len(tempdir) > 0:
        os.chdir(tempdir)
    '''
    
	#tulajlista function
    def ownership(self,df):
	    df['felt'] = self.df['Source'].astype(str).str[0]
	    df["felt2"] = self.df['Target'].astype(str).str[0]
	    own1 = self.df[(self.df['felt'] == "P") & (self.df['felt2'] == "O")]
	    own2 = self.df[(self.df['felt'] == "O") & (self.df['felt2'] == "P")]
	    ownerships=pd.concat([own1,own2])
	    #filter by ownership
	    viszony=pd.read_csv("viszony.csv")
	    viszony=viszony[viszony['tulaj']==1]
	    ownerships=ownerships[(ownerships["node1_role"].isin(viszony['viszony']))|(ownerships["node2_role"].isin(viszony['viszony']))]
	    
	    print(len(ownerships)," relations found.")
	    return ownerships
  
    
    #ownership(edges)[["Source","Target","id","name","node1_role", "node2_role"]].to_csv("P-O relations.csv", index=False)
	#Search for P-P relations
    def friendship(self,df):
	    df['felt'] = self.df['Source'].astype(str).str[0]
	    df["felt2"] = self.df['Target'].astype(str).str[0]
	    friendships = self.df[(df['felt'] == "P") & (df['felt2'] == "P")]
	    print(len(friendships),"friendship relations found.")
	    return friendships
    
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

    

	
    def preproc (part, win_final):
	    filtered_winfinal = win_final[win_final['TEXTSCORE']>0]
	    
	    ossz_kozbesz = pd.merge(part, filtered_winfinal, how = 'inner', on=['UID'])
	    
	    final_kozbesz = ossz_kozbesz[['UID', 'NOOFBIDDERS', 'SUBJECT', 'VALUE', 'CUR', 'VAT', 'VATRATE', 'PUBLIDATE', 'NAME', 'WHITELISTNAME', 'CITY']]
	    
	    final_kozbesz3 = final_kozbesz[(final_kozbesz['CUR'] == 'HUF') & final_kozbesz['NOOFBIDDERS']>0]
	    
	    final_kozbesz3 = final_kozbesz3.reset_index(drop=True)
	    
	    final_kozbesz3['VALUE'] = pd.to_numeric(final_kozbesz3['VALUE'])
	    
	    final_kozbesz3['VATRATE'] = pd.to_numeric(final_kozbesz3['VATRATE'], errors = 'coerce')
	    
	    return final_kozbesz3
    

    
	# Ez a függvény készíti el a Fideszes politikusok közbeszerzéssel kapcsolatos statisztikáit
    def stats(self,df,start,end):
        df=df[(df['PUBLIDATE'] > start) & (df['PUBLIDATE'] < end)]
        stat = pd.DataFrame(columns = ['ID','Nev', 'Nyert','Ertek_ossz', 'Atlag_ertek', 'Atlag_palyazo', 'Min_palyazo', 'Max_palyazo'])
        stat['ID']=pd.Series(list(set(self.merged_po2['name_y'])))
        stat=stat.set_index(['ID'])
        stat['Nev'] = pd.Series(list(set(self.merged_po2['name_y'])))
        stat['Nyert']=df[['PName','UID']].groupby(['PName']).agg(['count'])
        stat['Ertek_ossz']=df[['PName','VALUE']].groupby(['PName']).agg(['sum'])
        stat['Atlag_ertek']=df[['PName','VALUE']].groupby(['PName']).agg(['mean'])
        stat['Atlag_palyazo']=df[['PName','NOOFBIDDERS']].groupby(['PName']).agg(['mean'])
        stat['Min_palyazo']=df[['PName','NOOFBIDDERS']].groupby(['PName']).agg(['min'])
        stat['Max_palyazo']=df[['PName','NOOFBIDDERS']].groupby(['PName']).agg(['max'])
        #df.groupby(['PName']).agg([count'])

        return stat

#########################################################################
#Két intervallumon hasonlítja össze közbeszerzés táblában top x nevet
#start1,end1,start2,end2 a két időintervallum amit vizsgálunk, Formátum: 2014-01-01
#Output: A különböző és megegyező nevek a két idő intervallumban
#Összehasonlítás az összes megnyert pályázat értéke alapján történik
    def keres (self,df, start1,end1, start2,end2,x):
    
        idoszak1 = self.stats (df,start1,end1).sort_values(by=['Ertek_ossz'], ascending = False)
        idoszak2 = self.stats (df, start2, end2).sort_values(by=['Ertek_ossz'], ascending = False)
        
        metszet1 = idoszak1[:x].index.values
        metszet2 = idoszak2[:x].index.values
    
        metszet = np.intersect1d(metszet1, metszet2)
        
        kulonbseg = np.append(np.setdiff1d(metszet1, metszet2), np.setdiff1d(metszet2, metszet1))
        
        return metszet, kulonbseg
    print("to run the gecikereső use stats(df,start,end) function!")
    
    def __init__(self,tid):
        self.tempdir=input("Give me the folder, where data stored: ")
        os.chdir(self.tempdir)
        self.selfnodes = pd.read_csv("fidesz_nodes.csv")
        self.edges = pd.read_csv("fidesz_edges.csv")     
        self.nodes=self.selfnodes[["ID","name", "address", "org_relations","person_relations"]]
                ##here is the main process
        self.part  = pd.read_csv('part.csv')
        self.win_final = pd.read_csv('winner_resolved_final.csv')
        self.p_o = pd.read_csv('P-O relations.csv')
        self.fidesz_nodes = pd.read_csv("fidesz_nodes.csv")
        self.mapping = pd.read_csv('mapping.csv')
        
        self.final_kozbesz3 = self.preproc (self.part, self.win_final)
        
        
        self.fidesz_nodes = self.fidesz_nodes.rename(index=str, columns={'ID': 'Target'})
        self.p_o = self.p_o.drop(['name'], axis=1)
        self.merged_po = pd.merge(self.p_o, self.fidesz_nodes, how = 'inner', on = ['Target'])
        
        self.fidesz_nodes = self.fidesz_nodes.rename(index=str, columns={'Target': 'Source'})
        self.merged_po2 = pd.merge(self.merged_po, self.fidesz_nodes, how = 'inner', on = ['Source'])
        
        self.merged_po2 = self.merged_po2.reset_index(drop=True)
        
        self.merged_po2['name_x'] = self.merged_po2['name_x'].apply(self.cleanfirm)
        
        
        ####Innentől csináljuk meg az összekötést
        self.list_name_y = list(set(self.merged_po2['name_y']))
        
        self.dict_name_y = pd.DataFrame()
        
        for i in self.list_name_y:
            filtered_po = self.merged_po2[self.merged_po2['name_y'] == i]
            kuka=pd.DataFrame(list(set(filtered_po['name_x'])))
            kuka["id"]=[x for x in range(len(kuka))]
            self.dict_name_y=self.dict_name_y.append(kuka, ignore_index=True)
        del kuka
        
        # ebből készült a mapping df
        # közbeszerzést nyert cégek és fideszesek cégei
        self.list_firms = pd.Series(list(set(self.dict_name_y[0]))) 
        self.list_kozbesz = pd.Series(list(set(self.win_final['NAME'])))
        
        #########
        #Joinoljuk a mappingel
        self.dict_name_y=pd.merge(self.dict_name_y,self.mapping, how="left", left_on=0 ,right_on='0')
        self.dict_name_y=self.dict_name_y[["id",0,"1"]].dropna()
        
            ############
        #Összehúzzuk a közbesz táblával
        self.final_kozbesz3['NAME'] = self.final_kozbesz3['NAME'].apply(self.cleanfirm)
        self.final_kozbesz3=self.final_kozbesz3[["UID","NOOFBIDDERS","VALUE","PUBLIDATE","NAME","CITY"]]
        
        self.dict_name_y=pd.merge(self.dict_name_y,self.final_kozbesz3, how="left", left_on='1', right_on="NAME")
        self.dict_name_y["PName"]=self.dict_name_y["id"]
        self.dict_name_y=self.dict_name_y.set_index(["id"])
        
        ############
                
