from distutils.core import setup

version = '0.1.4'
setup(
  name = 'datk',
  packages = ['datk', 'datk.core'],
  version = version,
  description = 'Distributed Algorithms Toolkit for Python',
  author = 'Amin Manna',
  author_email = 'datk@mit.edu',
  license ='MIT',
  url = 'https://github.com/amin10/datk',
  download_url = 'https://github.com/amin10/datk/tarball/'+version,
  keywords = ['distributed', 'algorithms', 'toolkit', 'simulator'],
  classifiers = [
                  'Development Status :: 3 - Alpha',
                  'Programming Language :: Python :: 2.7',
                  'License :: OSI Approved :: MIT License',
                ],
  install_requires=['numpy', 'SciPy>=0.9.0']
)