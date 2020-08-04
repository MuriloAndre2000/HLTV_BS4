from bs4 import BeautifulSoup
import requests as re
import pandas as pd
from datetime import datetime
import numpy as np
import time
import tqdm
url = "https://www.hltv.org/results?offset="
pd.options.mode.chained_assignment = None  # default='warn'

from fake_useragent import UserAgent
ua = UserAgent(cache=False)

def team_matches(team, df):
    return df.loc[(df['team1'] == team) | (df['team2'] == team)].reset_index(drop=True)

class hltv(object):
	"""docstring for ClassName"""
	def __init__(self, user_agent):
		self.user_agent = user_agent
		self.dataframe = pd.DataFrame()

	def results(self, num):
	    df = pd.DataFrame(columns = ['team1','score1','score2','team2', 'url', 'date'])
	    session = re.Session()
	    session.headers.update({'User-Agent': self.user_agent})
	    for index_of_page in range(num):
	        urlbyi = url+str(index_of_page*100)
	        soup = BeautifulSoup(session.get(urlbyi).content, 'html.parser')
	        date = 0
	        for line in soup.findAll("div", {"class": "result-con"}):
	            for a in line.find_all('a', {"class": "a-reset"}, href=True): 
	                if a.text: 
	                    urlinline = "https://www.hltv.org" + a["href"]
	            td = line.findAll("td")                
	            team1 = td[0].getText().replace('\n','')
	            score1 = td[1].getText().split(' - ')[0]
	            score2 = td[1].getText().split(' - ')[1]
	            team2 = td[2].getText().replace('\n','')
	                
	            df = df.append({'team1':team1, 'score1':score1, 'score2':score2, 'team2':team2, 'url': urlinline, 'date': date}, ignore_index=True)
	    self.dataframe = df


	def get_stats(self, index):
		matchurl = self.dataframe['url'][index]
		session = re.Session()
		session.headers.update({'User-Agent': self.user_agent})
		soupurl = BeautifulSoup(session.get(matchurl).content, 'html.parser')
		for link in soupurl.find_all('a', href=True):
			if link.text == "Detailed stats":
				self.dataframe.__getitem__('stats_url').__setitem__(index, "https://www.hltv.org" + link["href"])
		for date in soupurl.find_all('div', {"class": "date"}):
			self.dataframe.__getitem__('date').__setitem__(index, date['data-unix'])

		for event in soupurl.find_all('div', {"class": "event text-ellipsis"}):
			self.dataframe.__getitem__('event').__setitem__(index, event.text)

	def details(self, time_sleeps):
		self.dataframe['stats_url'] = np.zeros(len(self.dataframe))
		self.dataframe['event'] = np.zeros(len(self.dataframe))

		for index in tqdm.tqdm(self.dataframe.index):
			self.get_stats(index)
			self.user_agent = ua.random
			time.sleep(time_sleeps)

	def process(self, team):
		matches = team_matches(team, self.dataframe)
		result = []
		for index in matches.index:
			if matches['score1'][index] == matches['score2'][index]:
				result.append(0)
			elif matches['team1'][index] == team:
				if matches['score1'][index] > matches['score2'][index]:
					result.append(1)
				else: 
					result.append(-1)
		        	
			elif matches['team2'][index] == team:
				if matches['score1'][index] < matches['score2'][index]:
					result.append(1)
				else: 
					result.append(-1)
		matches['result'] = result
		return matches


