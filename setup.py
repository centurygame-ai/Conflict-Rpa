from setuptools import setup, find_packages

setup(
    name='conflict_rpa',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'openai>=1.28.1',
        'requests>=2.22.0',
    ],
    author='FanYangli',
    author_email='yong.feng@centurygame.com',
    description="A tool to rpa in your shell",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    entry_points='''
        [console_scripts]
        conflict_rpa=conflict_rpa.rpa:rpa
    ''',
)
