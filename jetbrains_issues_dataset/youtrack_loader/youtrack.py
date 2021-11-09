import json
import logging
import time
from typing import Union, List

import requests

ISSUES_QUERY = "issues?query={}&fields=" \
               "id,idReadable,summary,description," \
               "project(shortName),created,resolved,reporter(login,name,ringId),commentsCount," \
               "customFields(id,name,value(id,name,login,ringId))," \
               "comments(id,created,text,author(login,name,ringId))," \
               "links(direction,linkType(name,sourceToTarget,targetToSource,directed,aggregation),issues(id,idReadable))" \
               "&$skip={}&$top={}"

ACTIVITIES_QUERY = "activities/?issueQuery={}&categories=CommentsCategory,AttachmentsCategory,AttachmentRenameCategory," \
                   "CustomFieldCategory,DescriptionCategory,IssueCreatedCategory,IssueResolvedCategory,LinksCategory," \
                   "ProjectCategory,IssueVisibilityCategory,SprintCategory,SummaryCategory,TagsCategory" \
                   "&fields=id,idReadable,timestamp,targetMember,target(id," \
                   "reporter(login,name,ringId),created,idReadable,text,issue(id),customFields(id,name,value(id,name,login,ringId)))," \
                   "memberName,added(id,login,name,text),removed(id,login,name,text)&$skip={}&$top={}"

ACTIVITIES_PER_ISSUE_QUERY = "issues/{issue_id}/activities?categories=CommentsCategory,AttachmentsCategory," \
                             "AttachmentRenameCategory,CustomFieldCategory,DescriptionCategory,IssueCreatedCategory," \
                             "IssueResolvedCategory,LinksCategory,ProjectCategory,IssueVisibilityCategory," \
                             "SprintCategory,SummaryCategory,TagsCategory" \
                             "&fields=id,idReadable,timestamp,targetMember," \
                             "target(id,project(shortName),reporter(login,name,ringId),idReadable,text,issue(id)," \
                             "customFields(id,name,value(id,name,login,ringId))),memberName," \
                             "added(id,login,name,ringId,text,bundle(id,name))," \
                             "removed(id,login,name,text,bundle(id,name))" \
                             "&$skip={skip}&$top={top}"


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
        self.activities_per_issue_url = self.new_api_url + ACTIVITIES_PER_ISSUE_QUERY

    def download_activities_per_issue(self, issue_ids, file_path):
        total_activities = 0
        for i, issue_id in enumerate(issue_ids):
            skip = 0
            while True:
                request_url = self.activities_per_issue_url.format(issue_id=issue_id, skip=skip, top=self.page_size)
                activity_list = None
                attempt = 1
                while attempt < 5:
                    try:
                        response = requests.get(request_url, headers=self.headers, verify=False)
                        activity_list = response.json()
                        break
                    except Exception as e:
                        logging.exception(e)
                        time.sleep(3)
                    attempt += 1

                if activity_list is None:
                    raise Exception("Failed to retrieve activities")

                self.check_response(activity_list)

                with open(file_path, 'a+', encoding='utf-8') as writer:
                    for activity in activity_list:
                        activity['element_type'] = 'activity'
                        activity['issue_id'] = issue_id
                        line = json.dumps(activity, ensure_ascii=False)
                        writer.write(line + '\n')

                skip += len(activity_list)
                total_activities += len(activity_list)

                if len(activity_list) < self.page_size:
                    break
            logging.info(f"Loaded {skip} activities for issue {i} / {len(issue_ids)}")
        return total_activities

    def download_activities(self, query, file_path) -> int:
        skip = 0
        while True:
            request_url = self.activity_list_url.format(query, skip, self.page_size)

            activity_list = None
            attempt = 1
            while attempt < 5:
                try:
                    response = requests.get(request_url, headers=self.headers, verify=False)
                    activity_list = response.json()
                    break
                except Exception as e:
                    logging.exception(e)
                    time.sleep(3)
                attempt += 1

            if activity_list is None:
                raise Exception("Failed to retrieve activities")

            self.check_response(activity_list)

            with open(file_path, 'a+', encoding='utf-8') as writer:
                for activity in activity_list:
                    activity['element_type'] = 'activity'
                    line = json.dumps(activity, ensure_ascii=False)
                    writer.write(line + '\n')

            if len(activity_list) < self.page_size:
                break

            skip += len(activity_list)
        return skip + len(activity_list)

    def download_issues(self, query, file_path, return_ids=False) -> Union[int, List[str]]:
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

        with open(file_path, 'a+', encoding='utf-8') as writer:
            for issue in all_issues:
                issue['element_type'] = 'issue'
                line = json.dumps(issue, ensure_ascii=False).encode('utf-8', 'replace').decode('utf-8')
                try:
                    writer.write(line + '\n')
                except Exception as e:
                    logging.exception(issue['id'])
                    raise e

        if return_ids:
            return [issue['id'] for issue in all_issues]
        else:
            return len(all_issues)

    @staticmethod
    def check_response(json_response):
        if 'error' in json_response:
            raise Exception(json_response['error'])
        # print('read {} items'.format(len(json_response)))
