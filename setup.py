from setuptools import find_packages,setup
from typing import List

def get_requirements(file_path:str)->List[str]:
    '''
    function to return package requirements
    
    '''
    requirements=[]
    hyphen='-e .'
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n","") for req in requirements]
        if hyphen in requirements:
            requirements.remove(hyphen)
    return requirements
        

setup(
    name='ml-proj-1',
    version='0.0.1',
    author='Srikar',
    author_email='psrikar2005@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)