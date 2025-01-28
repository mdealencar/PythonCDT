from skbuild import setup

setup(
    name="PythonCDT",
    version="0.0.1",
    author="Leica Geosystems",
    author_email="",
    license="MPL-2.0",
    url="https://github.com/artem-ogre/PythonCDT",
    description="Constrained Delaunay Triangulation",
    long_description="",
    zip_safe=False,
    extras_require={"test": ["pytest>=6.0"]},
    python_requires=">=3.6",
)
