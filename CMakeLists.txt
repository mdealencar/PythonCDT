cmake_minimum_required(VERSION 3.18.0)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

project(
    ${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

include(FetchContent)
FetchContent_Declare(
  CDT
  GIT_REPOSITORY https://github.com/artem-ogre/CDT.git
  GIT_TAG 2068d015b9db3c92481e869b0c1f669b96a1d70a
  SOURCE_SUBDIR CDT
)
FetchContent_MakeAvailable(CDT)

pybind11_add_module(${SKBUILD_PROJECT_NAME} MODULE cdt_bindings.cpp)
target_link_libraries(${SKBUILD_PROJECT_NAME} PRIVATE pybind11::module)
target_link_libraries(${SKBUILD_PROJECT_NAME} PRIVATE CDT::CDT)
# Exposed to Python as condeltri.__version__; scikit-build-core sets
# PROJECT_VERSION from [project].version in pyproject.toml.
target_compile_definitions(${SKBUILD_PROJECT_NAME} PRIVATE VERSION_INFO=${PROJECT_VERSION})
install(TARGETS ${SKBUILD_PROJECT_NAME} LIBRARY DESTINATION .)

# PEP 561: a compiled extension is opaque to type checkers, so ship the stubs
# describing its API alongside it (keep condeltri.pyi in sync with
# cdt_bindings.cpp).
install(FILES ${SKBUILD_PROJECT_NAME}.pyi py.typed DESTINATION .)
