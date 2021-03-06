#!/usr/bin/python

import json
import os
import sys
import requests
import logging

params_file = sys.argv[1]
f = open(params_file, "r")
params = json.load(f)

api = params['api']

headers = {'Content-Type': 'application/json;charset=ISO-8859-1'}
for taxonomy_params in params['taxonomies']:
    taxonomy = {'name' : taxonomy_params['name'], 'language': taxonomy_params['language']}
    post_resp = requests.post(api + '/taxonomies', data=json.dumps(taxonomy), headers=headers)
    if post_resp.status_code != 201:
        logging.error("[POST_TAXONOMY] Received non 201 response. Got {}".format(post_resp.status_code))
    else:
        taxonomy_id = post_resp.json()['id']
        url = api + '/taxonomies/' + taxonomy_id + '/topics'
        topics_file = taxonomy_params['topics_file']
        with open(topics_file) as file:
            for line in file:
                topic = json.loads(line)
                topic['taxonomyId'] = taxonomy_id
                post_resp = requests.post(url, data=json.dumps(topic), headers=headers)
                if post_resp.status_code != 201:
                    logging.error("[POST_TOPICS] Received non 201 response. Got {}".format(post_resp.status_code))
                else:
                    logging.info("[POST_TOPICS] Received {}".format(post_resp.status_code))
        rules_file = taxonomy_params['rules_file']
        with open(rules_file) as file:
            for line in file:
                rule = json.loads(line)
                rule['taxonomy'] = taxonomy_id
                print(rule)
                post_resp = requests.post((api + "/rules"), data=json.dumps(rule), headers=headers)
                if post_resp.status_code != 201:
                    logging.error("[POST_RULE] Received non 201 response. Got {}".format(post_resp.status_code))
                    logging.error(post_resp.reason)
        corpora_params = taxonomy_params['corpora']
        for corpus_params in corpora_params:
            schema = corpus_params['schema']
            post_resp = requests.post((api + "/schemas"), data=json.dumps(schema), headers=headers)
            if post_resp.status_code != 201:
                logging.error("[POST_TOPICS] Received non 201 response. Got {}".format(post_resp.status_code))
            else:
                schema_id = post_resp.json()['id']
                corpus = {"name": corpus_params["corpus_name"], "language": corpus_params["language"], "schemaId": schema_id, "taxonomyId": taxonomy_id}
                post_resp = requests.post((api + "/corpora"), data=json.dumps(corpus), headers=headers)
                if post_resp.status_code != 201:
                    logging.error("[POST_CORPUS] Received non 201 response. Got {}".format(post_resp.status_code))
                else:
                    corpus_id = post_resp.json()['id']
                    documents_file = corpus_params["documents_file"]
                    if os.path.exists(documents_file):
                        with open(documents_file) as f:
                            for line in f:
                                document = json.loads(line)
                                url = api + '/corpora/' + corpus_id + '/documents'
                                post_resp = requests.post(url, data=json.dumps(document), headers=headers)
                                if post_resp.status_code != 201:
                                    logging.error("[POST_DOCUMENT] Received non 201 response. Got {}".format(post_resp.status_code))
                                else:
                                    logging.info(post_resp.content)
