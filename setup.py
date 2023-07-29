import os
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

import numpy
import mpi4py


class custom_build_ext(build_ext):

    user_options = build_ext.user_options + [('mpicc', None, 'MPICC')]

    def initialize_options(self):
        try:
            compiler = str(mpi4py.get_config()['mpicc'])
        except KeyError:
            compiler = 'mpicc'

        self.mpicc = os.getenv('MPICC', compiler)

        build_ext.initialize_options(self)

    def finalize_options(self):
        build_ext.finalize_options(self)

    def build_extensions(self):
        # turns out set_executables only works for linker_so, but for compiler_so
        self.compiler.compiler_so[0] = self.mpicc
        self.compiler.linker_so[0] = self.mpicc
        build_ext.build_extensions(self)


def find_version(path):
    import re
    # path shall be a plain ascii text file.
    s = open(path, 'rt').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", s, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Version not found")


extensions = [Extension('mpsort.binding', ['mpsort/binding.pyx', 'radixsort.c', 'mp-mpiu.c', 'mpsort-mpi.c'],
                        include_dirs=['./', numpy.get_include()],
                        depends=['mpsort.h', 'mpsort-mpi.h', 'mp-mpiu.h'])]

setup(name="mpsort",
      version=find_version("mpsort/version.py"),
      author="Yu Feng",
      author_email="rainwoodman@gmail.com",
      url="http://github.com/rainwoodman/mpsort",
      description="python binding of MP-sort, a peta scale sorting routine",
      zip_safe=False,
      package_dir={'mpsort': 'mpsort'},
      packages=['mpsort', 'mpsort.tests'],
      install_requires=['cython', 'numpy', 'mpi4py'],
      ext_modules=extensions,
      license='BSD-2-Clause',
      cmdclass={'build_ext': custom_build_ext})
