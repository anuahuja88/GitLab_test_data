import requests
import re
GITLAB_URL = 'https://eng-git.canterbury.ac.nz'
PROJECT_NAME='seng302-2023%2Fteam-100'
PRIVATE_TOKEN = 'glpat-Ke9CQWHMsEQv-QUp4oBH'
PROJECT_ID = '15298' 
TAGS = ['sprint_2.1', 'sprint_3.2', 'sprint_4.5', 'sprint_5.4', 'sprint_6.3', 'sprint_7.1']  # Replace with your list of tags
END2END_PATH = 'src/test/resources/features/end2end'
INTEGRATION_PATH = 'src/test/resources/features/integration'


END2END={}
INTEGRATION={}
def get_repository_tree(project_id, tag, path=''):
    url = f'{GITLAB_URL}/api/v4/projects/{PROJECT_NAME}/repository/tree'
    headers = {'PRIVATE-TOKEN': PRIVATE_TOKEN}
    params = {'ref': tag, 'path': path, 'recursive': True}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository tree for tag '{tag}': {e}")
        print("Response content:", response.content)
        print("HTTP status code:", response.status_code)
        return []

# Function to get file content for a given tag
def get_file_content(project_id, tag, file_path):
    url = f'{GITLAB_URL}/api/v4/projects/{project_id}/repository/files/{file_path}/raw'
    headers = {'PRIVATE-TOKEN': PRIVATE_TOKEN}
    params = {'ref': tag}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.text

# Function to loop through files for each tag and print their contents
def loop_through_files_for_tags(project_id, tags, directory_path):
    for tag in tags:
        if (directory_path == END2END_PATH):

            END2END[tag] = 0
        elif (directory_path == INTEGRATION_PATH):
            INTEGRATION[tag] = 0
        try:
            print(f"\nProcessing tag: {tag}")
            
            # Get the list of files in the specified directory for the current tag
            files = get_repository_tree(project_id, tag, directory_path)
            print(f"Files in '{directory_path}' for tag '{tag}':")
            
            for file in files:
                if file['type'] == 'blob':  # Ensure it's a file, not a directory
                    file_path = f"{directory_path}/{file['name']}"
                    print(f"\nFetching content for file: {file_path}")
                    
                    # Get the content of the file
                    content = get_file_content(project_id, tag, file_path.replace('/', '%2F'))
                    print(content)
                    analyze_scenario(content, tag, directory_path)
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred for tag '{tag}': {e}")
            
def analyze_scenario(content, tag, file_path):
    # Count the number of scenarios and examples
    scenario_count = 0
    scenario_outline_count = 0
    example_count = 0
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('Scenario:') and not line.strip().startswith('#'):
            scenario_count += 1
        elif line.strip().startswith('Scenario Outline:') and not line.strip().startswith('#'):
            scenario_outline_count += 1
        elif line.strip().startswith('|'):
            example_count += 1
    if (scenario_outline_count > 0): 
        example_count -= scenario_outline_count
    if (file_path == END2END_PATH):

        END2END[tag] += scenario_count
        END2END[tag] += example_count
    elif (file_path == INTEGRATION_PATH):
        INTEGRATION[tag] += scenario_count
        INTEGRATION[tag] += example_count

    print(f"Number of scenarios: {scenario_count}")
    print(f"Number of scenario outlines: {scenario_outline_count}")
    print(f"Number of examples: {example_count}")
# Main script
if __name__ == "__main__":
    loop_through_files_for_tags(PROJECT_ID, TAGS, END2END_PATH)
    loop_through_files_for_tags(PROJECT_ID, TAGS, INTEGRATION_PATH)
    print("END2END tests: ",END2END)
    print("INTEGRATION tests: ",INTEGRATION)