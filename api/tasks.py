from blender_server.celery import app
import json
import socket
import requests
import os
from django.conf import settings

@app.task
def sendToBlender(data):
	try:
		files = getFiles(data['media_data'], data['media_url'], data['code'])
		#override url de imagenes
		data['media_url'] = files
		js = json.dumps(data)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(('127.0.0.1', 13373))
		s.send(js)
		result = json.loads(s.recv(1024))
		s.close()
		return result
	except Exception as e:
		err = {'TASK-error': e}
		return err


def download_file(frm, to):
	local_filename = frm.split('/')[-1]
	r = requests.get(frm, stream=True)
	if not os.path.exists(to):
		os.makedirs(to)
	with open(to + "/" + local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
				f.flush()
	return local_filename

def getFiles(flist, url, code):
	path = os.path.join(settings.TMP_ROOT, code)
	for f in flist:
		download_file(url + f, path)
	return path