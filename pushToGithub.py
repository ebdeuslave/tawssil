import os

def autoPush(fileToAdd, commitMsg):
    """
    Auto push to github
    """
    print(os.system(f'git add {fileToAdd} && git commit -m "{commitMsg}" && git push'))

if __name__ == '__main__':
    autoPush(".", "add package_id to order_data")