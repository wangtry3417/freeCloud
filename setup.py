from setuptools import setup, find_packages

setup(
    name='trydb',  # 包名
    version='0.1.0',  # 版本號
    author='WTech',  # 作者
    author_email='wangtry3417@gmail.com',  # 作者郵件
    description='關於trydb 數據庫Py-package',  # 簡要描述
    long_description=open('README.md').read(),  # 詳細描述，通常從 README 文件中讀取
    long_description_content_type='text/markdown',  # 指定長描述的內容類型
    url='https://github.com/wangtry3417/freecloud.git',  # 包的URL
    packages=find_packages(where='src'),  # 自動發現包
    package_dir={'':'src'},
    classifiers=[  # 分類器，幫助用戶找到你的包
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Python版本要求
    install_requires=[  # 安裝依賴
        'numpy',  # 示例依賴
        'requests',
    ],
)
