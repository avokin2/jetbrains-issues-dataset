from distutils.core import setup

setup(
    name='jetbrains-issues-dataset',
    packages=['jetbrains_issues_dataset',
              'jetbrains_issues_dataset.idea',
              'jetbrains_issues_dataset.youtrack_loader'],
    version='1.0.10',
    license='MIT',
    description='Dataset of JetBrains issues',
    author='Andrey Vokin',
    author_email='andrey.vokin@gmail.com',
    url='https://github.com/avokin2/jetbrains-issues-dataset',
    download_url='https://github.com/avokin2/jetbrains-issues-dataset/archive/v_1.0.10.tar.gz',
    keywords=[],
    install_requires=[
        'urllib3',
        'python-dateutil',
        'requests',
        'tqdm'
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'youtrack_downloader=jetbrains_issues_dataset.youtrack_loader.download_activities:main',
        ],
    },
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
