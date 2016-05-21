import sys
import random
import time
import requests
from pixivpy3 import *

pixiv_username = ''
pixiv_password = ''

class pixiv_crewler():
	def __init__(self, **requests_kwargs):
		self.api = PixivAPI(**requests_kwargs)
		self.requests_kwargs = requests_kwargs
		print(pixiv_username, pixiv_password)
		self.api.login(pixiv_username, pixiv_password)
		self.image_type = ['thumb', 'origin']
		self.images_valid = { self.image_type[0]: False, self.image_type[1]: False }
		
	def get_image(self, keyword_list, sample = 500, advance_sample = 10):
		query = ' '.join(keyword_list)
		total_count = self.__get_total_count(query)
		while True:
			start_index = random.randint(1, total_count // sample + 1)
			tStart = time.time()
			print('start query')
			result = self.api.search_works(query, page = start_index, per_page = sample).response
			print('end query: ' + str(time.time() - tStart))
			sorted_result = sorted(result, reverse = True,\
				key = lambda _: _.stats.favorited_count.public + _.stats.favorited_count.private)
			result = sorted_result[random.randint(0, advance_sample)]
			images = { self.image_type[0]: result.image_urls.px_480mw, self.image_type[1]: result.image_urls.large }
			if self.__check_result_valid(images):
				return self.__get_returned_image(images)

	def __check_result_valid(self, images):
		for idx in range(2):
			self.images_valid[self.image_type[idx]] = self.__check_image_is_valid(images[self.image_type[idx]])
		print(self.images_valid)
		return self.images_valid[self.image_type[0]] or self.images_valid[self.image_type[1]]

	def __get_total_count(self, query):
		return self.api.search_works(query, page = 1, per_page = 1).pagination.total

	def __get_returned_image(self, images):
		if not self.images_valid[self.image_type[0]]:
			images[self.image_type[0]] = images[self.image_type[1]]
		elif not self.images_valid[self.image_type[1]]:
			images[self.image_type[1]] = images[self.image_type[0]]
		return images

	def __check_image_is_valid(self, image_url):
		print('check ' + image_url)	
		status = str(requests.get(image_url, **self.requests_kwargs))
		return '200' in status
