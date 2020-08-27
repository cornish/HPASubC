from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import requests, json

# CHANGE LOG:
# 08-26-2020 TC rewrote to target multiple versions of HPA

ip_address = '138.197.13.129'
#ip_address = '127.0.0.1:5000' # localhost, for testing

def main():
	tissues = ['heart muscle',]
	ensg_ids = ['ENSG00000000003',]
	print(get_images(18,ensg_ids,tissues))

def get_genes(hpa_version):
	url = 'http://%s/hpasubc/api_v1/hpa_v%s/genes' % (ip_address,hpa_version)
	response = requests.get(url)
	genes = []
	if(response.ok):
		json_data = json.loads(response.content)
		genes = [x['ensg_id'] for x in json_data['data']]
	else:
		print('Error: %s' % response.status_code)
	return genes

def get_tissues(hpa_version):
	url = 'http://%s/hpasubc/api_v1/hpa_v%s/tissues' % (ip_address,hpa_version)
	response = requests.get(url)
	tissues = []
	if(response.ok):
		json_data = json.loads(response.content)
		tissues = [x['name'] for x in json_data['data']]
	else:
		print('Error: %s' % response.status_code)
	return tissues

def get_images(hpa_version,ensg_ids,tissues):
	url = 'http://%s/hpasubc/api_v1/hpa_v%s/images' % (ip_address,hpa_version)
	payload = {'ensg_ids':ensg_ids,'tissues':tissues}
	response = requests.post(url,json=payload)
	images = []
	if(response.ok):
		json_data = json.loads(response.content)
		images = [x for x in json_data['data']]
	else:
		print('Error: %s' % response.status_code)
		print(response.content)
	return images

if __name__ == '__main__':
	main()