import json
import time
import requests

ISSUES_QUERY = "issues?query={}&fields=id,idReadable,commentsCount,summary,description,customFields(name," \
               "value(login)),comments(text,author(login))&$skip={}&$top={}"

ACTIVITIES_QUERY = "activities/?issueQuery={}&categories=IssueCreatedCategory,DescriptionCategory,SummaryCategory," \
                   "CustomFieldCategory,CommentsCategory&fields=id,idReadable,timestamp,targetMember,target(id," \
                   "reporter(login),idReadable,summary,description,text,issue(id),customFields(id,name,value(login,name)))," \
                   "memberName,added(id,login,name,text),removed(id,login,name,text)&$skip={}&$top={}"


class YouTrack:
    def __init__(self, url, token, page_size=1000):
        self.url = url
        self.new_api_url = url + "api/"
        self.old_api_url = url + "rest/"
        self.headers = {
            "Accept": "application/json"
        }
        if token is not None:
            self.headers["Authorization"] = "Bearer {}".format(token)

        self.page_size = page_size
        self.activity_list_url = self.new_api_url + ACTIVITIES_QUERY
        self.issue_list_url = self.new_api_url + ISSUES_QUERY

    def download_activities(self, query, file_path):
        skip = 0
        while True:
            print("skip: {}".format(skip))
            request_url = self.activity_list_url.format(query, skip, self.page_size)

            activity_list = None
            attempt = 1
            while attempt < 5:
                try:
                    response = requests.get(request_url, headers=self.headers, verify=False)
                    activity_list = response.json()
                    break
                except Exception:
                    time.sleep(3)
                attempt += 1

            if activity_list is None:
                raise Exception("Fail to retrieve activities")

            self.check_response(activity_list)

            with open(file_path, 'a+', encoding='utf-8') as writer:
                for activity in activity_list:
                    line = json.dumps(activity, ensure_ascii=False)
                    writer.write(line + '\n')

            if len(activity_list) < self.page_size:
                break

            skip += len(activity_list)

    def query_all_issues(self, query):
        skip = 0
        all_issues = []
        while True:
            response = requests.get(self.issue_list_url.format(query, skip, self.page_size), headers=self.headers,
                                    verify=False)
            loaded_issues = response.json()
            self.check_response(loaded_issues)

            if len(loaded_issues) == 0:
                break

            skip += len(loaded_issues)
            all_issues += loaded_issues

        return all_issues

    @staticmethod
    def check_response(json_response):
        if 'error' in json_response:
            raise Exception(json_response['error'])
        print('read {} items'.format(len(json_response)))
