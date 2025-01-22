import subprocess
import datetime

def get_cmd(path):
    if(path!=""):
        return "git -C " + path + " "
    else:
        return "git "

def get_git_branch_name(path=""):
    """ get the current branch name """
    
    return subprocess.check_output(get_cmd(path)+"rev-parse --abbrev-ref HEAD", shell=True).rstrip().decode("utf-8")

def get_git_branch_head_SHA1(path=""):
    """ get the HEAD commit hash """
    return subprocess.check_output(get_cmd(path)+"rev-parse HEAD", shell=True).rstrip().decode("utf-8")[0:8]

def get_git_origin_url(path=""):
    return subprocess.check_output(get_cmd(path)+"remote get-url origin", shell=True).rstrip().decode("utf-8")

def get_git_current_tag(path=""):
    tmp = subprocess.check_output(get_cmd(path)+"describe --tags --exact-match HEAD", shell=True).rstrip().decode("utf-8")
    if "fatal:" not in tmp:
        return tmp
    return get_git_branch_name(path)

def get_doc_version(path=""):
    return "%s\nbranch: %s sha: %s at: %s" % (
        get_git_origin_url(path),
        get_git_branch_name(path),
        get_git_branch_head_SHA1(path),
        datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

def get_doc_version_oneline(path=""):
    return "%s:%s sha: %s" % (
        get_git_origin_url(path),
        get_git_current_tag(path),
        get_git_branch_head_SHA1(path))

if __name__ == "__main__":
    print(get_git_branch_name())
    print(get_git_branch_head_SHA1())
    print(datetime.datetime.utcnow())
    print(get_doc_version())
