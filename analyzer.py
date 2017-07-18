import pandas as pd
import matplotlib.pyplot as plt
from nltk import tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import statistics
import datetime
import sys

def dateparse (time_in_secs):
	return datetime.datetime.fromtimestamp(float(time_in_secs))#.date()


class DataFrameEmptyException(Exception):
	def __init__(self,msg):
		super().__init__(msg)
		self.msg = msg
	def show_msg(self):
		return self.msg



class ReviewAnalyzer:
	def __init__(self,filename='Reviews.csv'):
		# self.df = pd.read_csv(filename)
		self.df = pd.read_csv('Reviews.csv', parse_dates=True,date_parser=dateparse,index_col='Time',sep=',')


	def get_products(self):
		return self.df.ProductId.unique()

	def get_reviews_of_product(self,product_id):
		reviews = self.df.loc[self.df.ProductId==product_id]['Text']
		for review in reviews:
			yield review

	def get_prediction(self,score):
		#if -0.15 < score < 0.3:
		#	return 'neutral'
		#elif score > 0.3:
		#	return 'positive'
		#else:
		#	return 'negative'
		if -0.6 < score <= -0.2:
			return '2'
		elif -0.2 < score <= 0.2:
			return '3'
		elif 0.2 < score <= 0.6:
			return '4' 
		elif score > 0.6 :
			return '5'
		else:
			return '1'

	def get_prediction_for_reviews(self,product_id):
		analyzer  = SentimentIntensityAnalyzer()
		num_reviews = 0
		ratings = []
		for review in self.get_reviews_of_product(product_id):
			sentence_list = tokenize.sent_tokenize(review)
			paragraphSentiments = 0.0
			for sentence in sentence_list:
				vs = analyzer.polarity_scores(sentence)
				paragraphSentiments += vs["compound"]

			this_rating = round(paragraphSentiments/len(sentence_list), 4)

			ratings.append(self.get_prediction(this_rating))
			print("our prediction: ",self.get_prediction(this_rating))


			print("AVERAGE SENTIMENT FOR REVIEW: \t" + str(round(paragraphSentiments/len(sentence_list), 4)))
			this_rating = 0.0
		return statistics.mode(ratings)


	def plot_score_count_df_for_product(self,product_id):
		score_df = pd.DataFrame(r.df.loc[(r.df.ProductId == product_id)].groupby('Score').size(),columns=['Count'])
		# score_df = self.df.loc[self.df.ProductId==product_id][['Text','Score']].groupby('Score').count()
		print(score_df)
		if score_df.size:
			score_df.plot(kind='bar')
			plt.show()

		else:
			raise DataFrameEmptyException("No scores found for the product: "+product_id)

	def get_most_helpful_reviews(self,product_id):
		score_df = self.df.loc[self.df.ProductId==product_id].sort('HelpfulnessNumerator',ascending=False)
		return score_df.head(2).values

	def show_timeseries_plot(self,productId):
		self.df[self.df.ProductId == productId].Score.plot()
		plt.show()

if __name__ == '__main__':
	r = ReviewAnalyzer()
	print("*"*115)
	print("*"*40,"Welcome to Amazon Fine Food Analyzer","*"*40)
	print("*"*115)
	while True:
		print("Please select a product from  the product list to analyze")
		print(r.get_products())
		val  = input("Press e to elaborate, c to continue: ")
		if val == 'e':

			for product in r.get_products():
				print(product,end=",")

		print("")
		productId = input()
		print("""Please choose an operation: 
											 1 -> Get overall sentiment for product, 
											 2 -> get helpful review for product,
											 3 -> Get score plot
											 4 -> Get time series analysis of score for product
											 5 -> Quit""")

		option = input()
		try:
			if option == '1':
				print(r.get_prediction_for_reviews(productId))
			elif option == '2':
				for review in r.get_most_helpful_reviews(productId):
					print(review[8])
					print("%"*100)
			elif option == '3':
				r.plot_score_count_df_for_product(productId)
				print("%"*100)
			elif option == '4':
				r.show_timeseries_plot(productId)
			elif option == '5':
				sys.exit(0)
			else:
				print("Illegal option given")

		except Exception as e:
			print(e)
