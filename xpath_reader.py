import os
def read_EX_xpath(path: str, xpath_dict: dict):
    assert path.split('.')[-1] == 'html', "Expecting an HTML file."

    xpath = None
    for key in path.split('.')[0].split('_')[:2]:
        if key in xpath_dict:
            xpath = xpath_dict[key]
            break
    if xpath is None:
        for key in path.split('.')[0].split('-')[:2]:
            if key in xpath_dict:
                xpath = xpath_dict[key]
                break
    if xpath is None:
        print(f'No xpath found for {path}.')
    return xpath

def read_TBDW_xpath(path: str, xpath_dict: dict):
    assert path.split('.')[-1] == 'html', "Expecting an HTML file."
    path = os.path.normpath(path)
    path = path.split(os.sep)
    assert len(path) >= 2 and path[-2].isdigit() and 1 <= int(path[-2]) <= 51, "Expecting each sample to be inside its website folder."
    return xpath_dict[path[-2]]