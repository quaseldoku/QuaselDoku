import os

def find_project_root(current_dir):
    '''
    function for retrieving project root which is needed at places where relative paths where specified in parameters.yml.
    this seems hacky since kedro should provide a way to access to context and therefore project root from within a pipeline,
    but i could not find find anything on that in the documentation. 
    '''

    project_root = current_dir

    # look for 'data' folder by climbing up dir hierarchy
    while True:
        if os.path.exists(project_root + '/data'):
            return project_root
        project_root = os.path.split(project_root)[0]

