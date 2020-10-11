import os
import tempfile

import requests
import urllib3
import zipfile

IDE_PREFIX = 'IDE: '
OS_PREFIX = 'OS: '
JRE_PREFIX = 'JRE: '
JVM_PREFIX = 'JVM: '
JVM_ARGS_PREFIX = 'JVM Args: '
LOADED_BUNDLED_PLUGINS_PREFIX = 'Loaded bundled plugins: '
LOADED_CUSTOM_PLUGINS_PREFIX = 'Loaded custom plugins: '

MAX_ATTACHMENT_SIZE = 50 * 1024 * 1024

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

YOUTRACK_SERVER_URL = "https://youtrack-staging.labs.intellij.net"

ISSUE_ATTACHMENTS_QUERY = YOUTRACK_SERVER_URL + "/api/issues?query={}&fields=id,idReadable,attachments(name,size,extension,removed,url)"
ADD_COMMENT_REQUEST = YOUTRACK_SERVER_URL + "/api/issues/{}/comments"

IDEA_LOG_EXTENSION = ['log', 'zip', 'tar.gz']


def _download_attachments(issue_readable_id, token, ):
    result = []

    headers = _get_headers(token)
    request_url = ISSUE_ATTACHMENTS_QUERY.format(issue_readable_id)
    response = requests.get(request_url, headers=headers, verify=False)
    attachments_response = response.json()
    if len(attachments_response) == 0 or 'attachments' not in attachments_response[0]:
        print('error')
        return []

    temp_dir = tempfile.gettempdir()

    attachment_list = attachments_response[0]['attachments']
    for i, attachment in enumerate(attachment_list):
        if 'removed' in attachment and attachment['removed'] == 'True':
            continue
        if 'extension' in attachment and attachment['extension'] not in IDEA_LOG_EXTENSION:
            continue
        if 'size' in attachment and attachment['size'] > MAX_ATTACHMENT_SIZE:
            continue
        if 'url' not in attachment:
            continue
        url = attachment['url']
        extension = attachment['extension']
        full_url = YOUTRACK_SERVER_URL + url

        attachment_path = '{}/attachment_{}_{}.{}'.format(temp_dir, issue_readable_id, i, extension)

        _download_file(full_url, attachment_path)
        result.append(attachment_path)

    return result


def _download_file(url, file_name):
    with requests.get(url, stream=True, verify=False) as r:
        r.raise_for_status()
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def _get_headers(token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if token is not None:
        headers["Authorization"] = "Bearer {}".format(token)

    return headers


def _inspect_idea_log(file_path):
    filename, file_extension = os.path.splitext(file_path)
    if file_extension == '.zip':
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            inner_files = zip_ref.namelist()
            if 'idea.log' not in inner_files:
                return None
            zip_ref.extract('idea.log', path=temp_dir)
        file_path = temp_dir + '/' + 'idea.log'

    return _parse_idea_log(file_path)


def _parse_idea_log(file_path):
    result = {}
    with open(file_path) as fp:
        for line in fp:
            line = line[76:]
            if line.startswith(IDE_PREFIX):
                result['ide'] = line[len(IDE_PREFIX):].strip()
            if line.startswith(OS_PREFIX):
                result['os'] = line[len(OS_PREFIX):].strip()

            if line.startswith(JRE_PREFIX):
                result['JRE'] = line[len(JRE_PREFIX):].strip()
            if line.startswith(JVM_PREFIX):
                result['JVM'] = line[len(JVM_PREFIX):].strip()
            if line.startswith(JVM_ARGS_PREFIX):
                result['JVM Args'] = line[len(JVM_ARGS_PREFIX):].strip()

            if line.startswith(LOADED_BUNDLED_PLUGINS_PREFIX):
                result['Bundled plugins'] = line[len(LOADED_BUNDLED_PLUGINS_PREFIX):].strip()
            if line.startswith(LOADED_CUSTOM_PLUGINS_PREFIX):
                result['Custom plugins'] = line[len(LOADED_CUSTOM_PLUGINS_PREFIX):].strip()

    return result


def _build_idea_log_info_markdown_comment(idea_log_info):
    result = '* IDE: ' + idea_log_info['ide'] + '\n'
    result += '* OS: ' + idea_log_info['os'] + '\n'

    result += '<details>\n'
    result += '<summary>JRE, JVM</summary>\n\n'
    result += '  * JRE: ' + idea_log_info['JRE'] + '\n'
    result += '  * JVM: ' + idea_log_info['JVM'] + '\n'
    result += '  * JVM Args: ' + idea_log_info['JVM Args'] + '\n'
    result += '</details>\n'

    result += '<details>\n' + \
              '<summary>Custom plugins</summary>\n\n'
    for plugin in _get_plugins_from_text(idea_log_info['Custom plugins']):
        result += '  * ' + plugin + '\n'
    result += '</details>\n'

    result += '<details>\n' + \
              '<summary>Disabled plugins</summary>\n\n'
    for plugin in _get_plugins_from_text(idea_log_info['Disabled plugins']):
        result += '  * ' + plugin + '\n'
    result += '</details>\n'

    return result


def _add_comment(issue_readable_id, comment_text, token):
    json_data = {
        "text": comment_text
    }
    headers = _get_headers(token)
    request_url = ADD_COMMENT_REQUEST.format(issue_readable_id)
    response = requests.post(request_url, headers=headers, json=json_data, verify=False)

    return response.status_code


def _get_plugins_from_text(plugins_text):
    plugins = plugins_text.split(', ')
    plugins.sort()
    return plugins


bot_token = open('token.txt').read()


downloaded_attachments = _download_attachments('WI-54307', bot_token)
for attachment in downloaded_attachments:
    inspection = _inspect_idea_log(attachment)
    if inspection is not None:
        comment = _build_idea_log_info_markdown_comment(inspection)
        _add_comment('25-2878556', comment, bot_token)
        print(inspection)

