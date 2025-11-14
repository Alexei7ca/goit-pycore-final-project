from setuptools import setup, find_packages

setup(
    name='personal-assistant-bot',
    version='1.0.0',
    description='A comprehensive command-line assistant for managing contacts and notes.',
    author='project-group-10',
    packages=find_packages(),
    install_requires=['customtkinter'],
    entry_points={
        'console_scripts': [
            'assistant-bot = assistant.main:main',
            'assistant-gui = assistant.gui:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)