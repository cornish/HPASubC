from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import requests, json

def main():
	tissues = ['heart muscle',]
	ensg_ids = ['ENSG00000000003',]
	#print get_tissues()
	print(get_images(ensg_ids,tissues))
	#print get_genes()

def get_genes():
	url = 'http://138.197.13.129/hpasubc/api_v1/hpa_v18/genes'
	response = requests.get(url)
	genes = []
	if(response.ok):
		json_data = json.loads(response.content)
		genes = [x['ensg_id'] for x in json_data['data']]
	else:
		print('Error: %s' % response.status_code)
	return genes

def get_tissues():
	url = 'http://138.197.13.129/hpasubc/api_v1/hpa_v18/tissues'
	response = requests.get(url)
	tissues = []
	if(response.ok):
		json_data = json.loads(response.content)
		tissues = [x['name'] for x in json_data['data']]
	else:
		print('Error: %s' % response.status_code)
	return tissues

def get_images(ensg_ids,tissues):
	url = 'http://138.197.13.129/hpasubc/api_v1/hpa_v18/images'
	#url = 'http://127.0.0.1:5000/hpasubc/api_v1/hpa_v18/images'
	payload = {'ensg_ids':ensg_ids,'tissues':tissues}
	response = requests.post(url,json=payload)
	images = []
	if(response.ok):
		print(response.content)
		json_data = json.loads(response.content)
		images = [x for x in json_data['data']]
	else:
		print('Error: %s' % response.status_code)
		print(response.content)
	return images

if __name__ == '__main__':
	main()