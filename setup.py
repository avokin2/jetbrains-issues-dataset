from setuptools import setup
from distutils.core import setup


setup(
    name='jetbrains-issues-dataset',
    packages=['jetbrains_issues_dataset', 'jetbrains_issues_dataset.idea'],
    version='1.0.4',
    license='MIT',
    description='Dataset of JetBrains issues',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    author='Andrey Vokin',
    author_email='andrey.vokin@gmail.com',
    url='https://github.com/avokin2/jetbrains-issues-dataset',
    download_url='https://github.com/avokin2/jetbrains-issues-dataset/archive/v_1.0.4.tar.gz',
    keywords=[],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
