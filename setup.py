from distutils.core import setup


setup(
    name='jetbrains-issues-dataset',
    packages=['jetbrains_issues_dataset', 'jetbrains_issues_dataset.idea'],
    version='1.0.5',
    license='MIT',
    description='Dataset of JetBrains issues',
    long_description='Datasets of IDEA issues. See https://github.com/avokin2/jetbrains-issues-dataset',
    author='Andrey Vokin',
    author_email='andrey.vokin@gmail.com',
    url='https://github.com/avokin2/jetbrains-issues-dataset',
    download_url='https://github.com/avokin2/jetbrains-issues-dataset/archive/v_1.0.5.tar.gz',
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
