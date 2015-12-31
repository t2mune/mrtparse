from setuptools import setup, find_packages

setup(
    name='mrtparse',

    version='1.4',

    description='mrtparse is a module to read and analyze the MRT format data.',

    url='https://github.com/YoshiyukiYamauchi/mrtparse',

    author='Tetsumune KISO, Yoshiyuki YAMAUCHI, Nobuhiro ITOU',

    author_email='t2mune@gmail.com, info@greenhippo.co.jp, js333123@gmail.com',

    license='Apache License 2.0',

    platforms='any',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords=['mrt', 'bgp'],

    packages=['mrtparse'],

    include_package_data=True,

    use_2to3=True,
)
