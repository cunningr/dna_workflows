from distutils.core import setup
setup(
    name='dna_workflows',
    packages=['dna_workflows'],
    package_data={
    'dna_workflows': ['module']
    },
    version='0.0.22',
    license='MIT',
    description='dna_workflows is a basic workflow engine for executing DNA Workflows packages',
    author='Richard Cunningham',
    author_email='cunningr@gmail.com',
    url='https://github.com/cunningr/dna_workflows',
    download_url='https://github.com/cunningr/dna_workflows',
    keywords=['DNA Center', 'Cisco', 'workflow'],
    install_requires=[
      'jinja2',
      'ipaddress',
      'argparse',
      'requests',
      'netaddr',
      'pyyaml',
      'coloredlogs',
      'tabulate',
      'sdtables>=1.0.8',
      'dnacentersdk',
      'ISE'
    ],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6'
    ],
    # scripts=['bin/dna_workflows'],
    entry_points={
        'console_scripts': [
            'dna_workflows = dna_workflows.wf_client:main'
        ]
    }
)
